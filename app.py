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

def get_city_no2_stats(city_name, lat, lon):
    """Fetch 30-day average NO2 data for a city"""
    try:
        roi = ee.Geometry.Point([lon, lat]).buffer(5000)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
            .select('tropospheric_NO2_column_number_density') \
            .filterBounds(roi) \
            .filterDate(start_date, end_date)
            
        # Check if we have images
        count = collection.size().getInfo()
        if count == 0:
            return 0
            
        image = collection.mean()
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=1000,
            bestEffort=True
        ).getInfo()
        
        val = stats.get('tropospheric_NO2_column_number_density')
        if val:
            # Convert to µg/m³ (Assuming effective mixing height of ~230m)
            return round(val * 200000, 2)
        return 0
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
    
    city_data = []
    for city in cities:
        val = get_city_no2_stats(city['name'], city['lat'], city['lon'])
        city_data.append({
            'name': city['name'],
            'lat': city['lat'],
            'lon': city['lon'],
            'value': val
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
