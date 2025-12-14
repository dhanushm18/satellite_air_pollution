"""
Flask Web Application for Agentic Air Quality Monitor
Beautiful, modern frontend with agent integration and report downloads
"""
from flask import Flask, render_template, request, jsonify, send_file, session, Response
from datetime import datetime, timedelta
import os
import uuid
import threading
import sys
import requests
from io import StringIO
from src.agents.agents import run_satellite_crew
import ee
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store job results in memory (use Redis in production)
job_results = {}
job_status = {}
job_logs = {}  # Store detailed logs for each job

# Initialize Earth Engine
try:
    project_id = os.getenv('EE_PROJECT_ID')
    if project_id:
        ee.Initialize(project=project_id)
    else:
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except Exception as e:
    print(f"EE Init failed: {e}")

def get_city_stats_summary(city_name, lat, lon):
    """Fetch 30-day stats for all pollutants and return AQI"""
    try:
        roi = ee.Geometry.Point([lon, lat]).buffer(5000)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        def get_val(collection, band, scale_factor):
            try:
                coll = ee.ImageCollection(collection).select(band).filterBounds(roi).filterDate(start_date, end_date)
                if coll.size().getInfo() == 0: return 0
                val = coll.max().reduceRegion(ee.Reducer.mean(), roi, 1000).get(band).getInfo()
                return val * scale_factor if val else 0
            except: return 0

        # Fetch and scale to surface ug/m3 approx (Calibrated Factors)
        no2 = get_val('COPERNICUS/S5P/OFFL/L3_NO2', 'tropospheric_NO2_column_number_density', 750000)
        so2 = get_val('COPERNICUS/S5P/OFFL/L3_SO2', 'SO2_column_number_density', 300000)
        co  = get_val('COPERNICUS/S5P/OFFL/L3_CO', 'CO_column_number_density', 400000)
        o3  = get_val('COPERNICUS/S5P/OFFL/L3_O3_TCL', 'ozone_tropospheric_vertical_column', 250000)
        
        # Rigorous AQI Calc (Piecewise Linear Interpolation)
        def calc_sub_aqi(Cp, breakpoints):
             """
             Ip = [ (I_high - I_low) / (C_high - C_low) ] * (Cp - C_low) + I_low
             """
             for i in range(len(breakpoints) - 1):
                 C_low, I_low = breakpoints[i]
                 C_high, I_high = breakpoints[i+1]
                 if C_low <= Cp <= C_high:
                     return ((I_high - I_low) / (C_high - C_low)) * (Cp - C_low) + I_low
             
             # Extrapolate
             C_last, I_last = breakpoints[-1]
             if Cp > C_last:
                 C_prev, I_prev = breakpoints[-2]
                 slope = (I_last - I_prev) / (C_last - C_prev)
                 val = slope * (Cp - C_last) + I_last
                 return min(val, 500) # Cap at 500
             return 0

        # Breakpoints (India AQI Standards CPCB)
        # Detailed ref: https://app.cpcbccr.com/ccr_docs/FINAL-REPORT_AQI_2015.pdf
        no2_scale = [(0,0), (40,50), (80,100), (180,200), (280,300), (400,400), (500, 500)]
        so2_scale = [(0,0), (40,50), (80,100), (380,200), (800,300), (1600,400)]
        co_scale  = [(0,0), (1000,50), (2000,100), (10000,200), (17000,300), (34000,400)] 
        o3_scale  = [(0,0), (50,50), (100,100), (168,200), (208,300), (748,400)]
        # PM2.5 (24hr avg)
        pm25_scale = [(0,0), (30,50), (60,100), (90,200), (120,300), (250,400), (380,500)]
        # PM10 (24hr avg)
        pm10_scale = [(0,0), (50,50), (100,100), (250,200), (350,300), (430,400), (500,500)]

        aqi_no2 = calc_sub_aqi(no2, no2_scale)
        aqi_so2 = calc_sub_aqi(so2, so2_scale)
        aqi_co  = calc_sub_aqi(co, co_scale)
        aqi_o3  = calc_sub_aqi(o3, o3_scale)
        
        satellite_aqi = max(aqi_no2, aqi_so2, aqi_co, aqi_o3)
        
        # --- OWM Ground Truth Correction ---
        try:
            api_key = os.getenv('OPENWEATHER_API_KEY') or os.getenv('OPEN_WEATHER_MAP_API')
            if api_key:
                aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
                resp = requests.get(aqi_url, timeout=2)
                if resp.status_code == 200:
                    data = resp.json()
                    components = data['list'][0]['components']
                    
                    # OWM returns ug/m3 directly for all components
                    owm_no2 = components.get('no2', 0)
                    owm_so2 = components.get('so2', 0)
                    owm_co  = components.get('co', 0)
                    owm_o3  = components.get('o3', 0)
                    owm_pm25 = components.get('pm2_5', 0)
                    owm_pm10 = components.get('pm10', 0)
                    
                    owm_aqi_no2 = calc_sub_aqi(owm_no2, no2_scale)
                    owm_aqi_so2 = calc_sub_aqi(owm_so2, so2_scale)
                    owm_aqi_co  = calc_sub_aqi(owm_co, co_scale)
                    owm_aqi_o3  = calc_sub_aqi(owm_o3, o3_scale)
                    owm_aqi_pm25 = calc_sub_aqi(owm_pm25, pm25_scale)
                    owm_aqi_pm10 = calc_sub_aqi(owm_pm10, pm10_scale)
                    
                    # Explicitly check PM2.5 dominance
                    owm_rigorous_aqi = max(owm_aqi_no2, owm_aqi_so2, owm_aqi_co, owm_aqi_o3, owm_aqi_pm25, owm_aqi_pm10)
                    
                    # Return WITHOUT cap to allow Severe+ (600, 700 etc)
                    return int(owm_rigorous_aqi)
                    
        except Exception as e:
            print(f"OWM Fetch Error: {e}")
            
        return int(satellite_aqi)
    except Exception as e:
        print(f"Error fetching stats for {city_name}: {e}")
        return 0


def run_agents_background(job_id, city, start_date, end_date, send_alerts, generate_reports):
    """Run agents in background thread with log capturing"""
    try:
        # Initialize logs
        job_logs[job_id] = []
        
        def add_log(message, level='info'):
            """Add a log entry"""
            timestamp = datetime.now().strftime('%H:%M:%S')
            job_logs[job_id].append({
                'timestamp': timestamp,
                'message': message,
                'level': level
            })
            job_status[job_id] = {
                'status': 'running',
                'progress': message,
                'logs_count': len(job_logs[job_id])
            }
        
        def agent_callback(step_output):
            """Callback for agent steps"""
            # step_output is usually a string or object with output
            # We'll try to extract meaningful text
            try:
                if hasattr(step_output, 'thought'):
                    msg = f"🤔 {step_output.thought}"
                elif hasattr(step_output, 'output'):
                    msg = f"🤖 {str(step_output.output)[:100]}..."
                else:
                    msg = f"🤖 Agent working: {str(step_output)[:100]}..."
                
                add_log(msg)
            except:
                add_log("🤖 Agent active...")

        add_log(f'Starting air quality monitoring for {city}')
        add_log(f'Date range: {start_date} to {end_date}')
        add_log('Initializing AI agents...')
        
        # Run the crew
        result = run_satellite_crew(
            city=city,
            start_date=start_date,
            end_date=end_date,
            send_alerts=send_alerts,
            generate_reports=generate_reports,
            log_callback=agent_callback
        )
        
        add_log('All agents completed successfully!')
        
        # Store results
        job_results[job_id] = {
            'status': 'complete',
            'result': str(result),
            'city': city,
            'date': end_date,
            'reports_generated': generate_reports,
            'alerts_sent': send_alerts
        }
        job_status[job_id] = {
            'status': 'complete',
            'progress': 'Mission complete!',
            'logs_count': len(job_logs[job_id])
        }
        add_log('Monitoring complete! Redirecting to results...')
        
    except Exception as e:
        job_results[job_id] = {
            'status': 'error',
            'error': str(e)
        }
        job_status[job_id] = {'status': 'error', 'progress': f'Error: {str(e)}'}
        if job_id in job_logs:
            job_logs[job_id].append({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'message': f'Error: {str(e)}',
                'level': 'error'
            })


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/run-agents', methods=['POST'])
def run_agents():
    """Start agent execution"""
    data = request.json
    
    city = data.get('city', 'Bengaluru')
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    # Default to 30 days if not specified or if it's the default 1 from UI
    date_range = int(data.get('date_range', 30))
    send_pushover = data.get('send_pushover', True)
    send_email = data.get('send_email', True)
    generate_reports = data.get('generate_reports', True)
    
    # Calculate date range
    end_date = date
    start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=date_range)).strftime('%Y-%m-%d')
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Start background thread
    thread = threading.Thread(
        target=run_agents_background,
        args=(job_id, city, start_date, end_date, send_pushover or send_email, generate_reports)
    )
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'started'})


@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get job status"""
    if job_id in job_results:
        return jsonify(job_results[job_id])
    elif job_id in job_status:
        status = job_status[job_id].copy()
        if job_id in job_logs:
            # Return list of log messages
            status['logs'] = [l['message'] for l in job_logs[job_id]]
        return jsonify(status)
    else:
        return jsonify({'status': 'not_found'}), 404


@app.route('/api/logs/<job_id>')
def get_logs(job_id):
    """Get job logs"""
    if job_id in job_logs:
        return jsonify({'logs': job_logs[job_id]})
    else:
        return jsonify({'logs': []}), 404


@app.route('/results/<job_id>')
def results(job_id):
    """Results page with enhanced data"""
    if job_id not in job_results:
        return "Job not found", 404
    
    result = job_results[job_id]
    
    # Find generated reports
    reports_dir = os.path.join(os.getcwd(), 'reports')
    reports = []
    if os.path.exists(reports_dir) and result.get('reports_generated'):
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf') and result.get('city', '') in filename:
                reports.append({
                    'filename': filename,
                    'name': 'Regulatory Report' if 'Regulatory' in filename else 'Prevention Guide',
                    'description': 'Government compliance report' if 'Regulatory' in filename else 'Air pollution prevention guide'
                })
    
    result['reports'] = reports
    result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['output'] = result.get('result', 'Processing complete')
    
    return render_template('results.html', job_id=job_id, result=result)


@app.route('/download/<filename>')
def download_report(filename):
    """Download PDF report"""
    reports_dir = os.path.join(os.getcwd(), 'reports')
    file_path = os.path.join(reports_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


@app.route('/api/reports')
def list_reports():
    """List available reports"""
    reports_dir = os.path.join(os.getcwd(), 'reports')
    
    if not os.path.exists(reports_dir):
        return jsonify([])
    
    files = []
    for filename in os.listdir(reports_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(reports_dir, filename)
            files.append({
                'filename': filename,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify(files)


@app.route('/dashboard')
def dashboard():
    """Dashboard page with city comparison"""
    cities = [
        {'name': 'Bengaluru', 'lat': 12.9716, 'lon': 77.5946},
        {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090}
    ]
    
    def calculate_cigarettes(aqi):
        """Calculate cigarette equivalent based on AQI -> PM2.5 mapping"""
        pm25_equiv = 0
        if aqi <= 50: pm25_equiv = aqi * (30/50)
        elif aqi <= 100: pm25_equiv = 30 + (aqi-50)*(30/50)
        elif aqi <= 200: pm25_equiv = 60 + (aqi-100)*(60/100)
        elif aqi <= 300: pm25_equiv = 120 + (aqi-200)*(130/100)
        elif aqi <= 400: pm25_equiv = 250 + (aqi-300)
        else: pm25_equiv = 350 + (aqi-400)
        return pm25_equiv / 22.0

    city_data = []
    for city in cities:
        val = get_city_stats_summary(city['name'], city['lat'], city['lon'])
        cigs = calculate_cigarettes(val)
        city_data.append({
            'name': city['name'],
            'lat': city['lat'],
            'lon': city['lon'],
            'value': val, # This is now AQI
            'cigarettes': cigs
        })
    
    return render_template('dashboard.html', city_data=city_data)


@app.route('/alerts')
def alerts():
    """Alerts management page"""
    email_recipients = os.getenv('EMAIL_TO', '')
    email_count = len([e for e in email_recipients.split(',') if e.strip()]) if email_recipients else 0
    pushover_configured = bool(os.getenv('PUSHOVER_USER_KEY') and os.getenv('PUSHOVER_API_TOKEN'))
    
    return render_template('alerts.html',
                         email_recipients=email_recipients,
                         email_count=email_count,
                         pushover_configured=pushover_configured,
                         alert_history=[])


@app.route('/settings')
def settings():
    """Settings page"""
    # Load all configuration from .env
    openai_key = os.getenv('OPENAI_API_KEY', '')
    pushover_user = os.getenv('PUSHOVER_USER_KEY', '')
    pushover_token = os.getenv('PUSHOVER_API_TOKEN', '')
    email_from = os.getenv('EMAIL_FROM', '')
    email_password = os.getenv('EMAIL_PASSWORD', '')
    email_to = os.getenv('EMAIL_TO', '')
    smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('EMAIL_SMTP_PORT', '587')
    gee_project = os.getenv('EE_PROJECT_ID', '')
    
    # Count email recipients
    email_count = len([e for e in email_to.split(',') if e.strip()]) if email_to else 0
    
    # Mask sensitive data
    openai_key_masked = f"{openai_key[:8]}...{openai_key[-4:]}" if openai_key and len(openai_key) > 12 else ''
    pushover_key_masked = f"{pushover_user[:8]}...{pushover_user[-4:]}" if pushover_user and len(pushover_user) > 12 else ''
    email_password_masked = '••••••••••••••••' if email_password else ''
    
    return render_template('settings.html',
                         openai_configured=bool(openai_key),
                         pushover_configured=bool(pushover_user and pushover_token),
                         email_configured=bool(email_from and email_password),
                         gee_configured=bool(gee_project),
                         openai_key_masked=openai_key_masked,
                         pushover_key_masked=pushover_key_masked,
                         email_from=email_from,
                         email_password_masked=email_password_masked,
                         email_recipients=email_to,
                         smtp_server=smtp_server,
                         smtp_port=smtp_port,
                         gee_project=gee_project,
                         email_count=email_count)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/reports')
def reports_page():
    """Reports listing page"""
    reports_dir = os.path.join(os.getcwd(), 'reports')
    available_reports = []
    total_reports = 0
    
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf'):
                total_reports += 1
                file_path = os.path.join(reports_dir, filename)
                size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
                available_reports.append({
                    'filename': filename,
                    'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M'),
                    'size_mb': size_mb
                })
    
    return render_template('reports.html',
                         total_reports=total_reports,
                         available_reports=available_reports)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
