"""
Agent Tools for Agentic Air Quality Monitor
Simplified tools using CrewAI @tool decorator
"""
from crewai.tools import tool
import ee
import geemap
import os
from datetime import datetime
from geopy.geocoders import Nominatim
import numpy as np
import rasterio
from src.core.notifications import NotificationService
from src.core.report_generator import RegulatoryReportGenerator

# Initialize Earth Engine
try:
    # Try with project ID first if available
    project_id = os.getenv('EE_PROJECT_ID')
    if project_id and not project_id.startswith('AIza'):  # Not an API key
        ee.Initialize(project=project_id)
        print(f"✅ Earth Engine initialized with project: {project_id}")
    elif os.getenv('EE_USE_HIGHVOLUME', 'false').lower() == 'true':
        # Try high-volume endpoint (no project required)
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
        print("✅ Earth Engine initialized (high-volume endpoint)")
    else:
        # Default initialization
        ee.Initialize()
        print("✅ Earth Engine initialized (default mode)")
except Exception as e1:
    print(f"⚠️ Primary initialization failed: {e1}")
    try:
        # Fallback to high-volume endpoint
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
        print("✅ Earth Engine initialized (high-volume endpoint - fallback)")
    except Exception as e2:
        print(f"❌ Earth Engine initialization failed: {e2}")
        print("Please check your authentication: earthengine authenticate")
        print("Or set EE_PROJECT_ID in .env file")


@tool("Search and Download Satellite Data")
def satellite_search_tool(city: str, start_date: str, end_date: str) -> str:
    """
    Searches for Sentinel-5P NO2 data for a specific city and date range, and downloads it as a GeoTIFF.
    
    Args:
        city: City name (e.g., "Bengaluru", "Delhi")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Success message with file path or error message
    """
    try:
        # Get coordinates
        geolocator = Nominatim(user_agent="agent_scout")
        location = geolocator.geocode(city)
        if not location:
            return f"Error: Could not find coordinates for {city}"
        
        # Create 50km buffer
        center_lat, center_lon = location.latitude, location.longitude
        roi = ee.Geometry.Point([center_lon, center_lat]).buffer(25000).bounds()
        
        # Search data
        collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
            .select('tropospheric_NO2_column_number_density') \
            .filterBounds(roi) \
            .filterDate(start_date, end_date)
        
        count = collection.size().getInfo()
        if count == 0:
            return f"No data found for {city} between {start_date} and {end_date}."
        
        # Download (using mean composite)
        image = collection.mean()
        
        output_dir = "agent_downloads"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{city}_{start_date}_{end_date}.tif".replace(" ", "_")
        output_path = os.path.abspath(os.path.join(output_dir, filename))
        
        # Download using Earth Engine's getDownloadURL (more reliable)
        try:
            import requests
            
            # Get download URL
            url = image.getDownloadURL({
                'region': roi,
                'scale': 1000,
                'crs': 'EPSG:4326',
                'format': 'GEO_TIFF'
            })
            
            # Download the file
            print(f"📥 Downloading satellite data for {city}...")
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ Downloaded {os.path.getsize(output_path)} bytes")
                return f"Successfully downloaded NO2 data for {city} to: {output_path}"
            else:
                return f"Error: File was not created or is empty: {output_path}"
                
        except Exception as download_error:
            return f"Error downloading data: {str(download_error)}"
        
    except Exception as e:
        return f"Error fetching data: {str(e)}"


@tool("Analyze Air Quality")
def analysis_tool(file_path: str) -> str:
    """
    Analyzes a satellite NO2 GeoTIFF file to determine air quality levels and trends.
    
    Args:
        file_path: Path to the GeoTIFF file
    
    Returns:
        Analysis results with NO2 levels and category
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
        
        # Read the file
        with rasterio.open(file_path) as src:
            data = src.read(1)
            # Handle nodata
            data[data == src.nodata] = np.nan
        
        # Basic Stats
        mean_no2 = np.nanmean(data)
        max_no2 = np.nanmax(data)
        
        # Convert to µg/m³ (approximate conversion)
        mean_ugm3 = mean_no2 * 46000
        max_ugm3 = max_no2 * 46000
        
        # Categorize
        if mean_ugm3 <= 40: category = "Good"
        elif mean_ugm3 <= 80: category = "Moderate"
        elif mean_ugm3 <= 180: category = "Poor"
        elif mean_ugm3 <= 280: category = "Very Poor"
        else: category = "Severe"
        
        return f"""Analysis Results for {os.path.basename(file_path)}:
- Average NO2: {mean_ugm3:.2f} µg/m³ ({category})
- Peak NO2: {max_ugm3:.2f} µg/m³
- Data Points: {data.size}
- Valid Pixels: {np.count_nonzero(~np.isnan(data))}"""
        
    except Exception as e:
        return f"Error analyzing file: {str(e)}"


@tool("Send Pushover Notification")
def notification_tool(city: str, no2_level: float, category: str, date: str = None) -> str:
    """
    Sends air quality alerts via Pushover and Email notification services.
    
    Args:
        city: City name
        no2_level: NO2 level in µg/m³
        category: Air quality category (Good, Moderate, Poor, Very Poor, Severe)
        date: Date of measurement (optional)
    
    Returns:
        Success or failure message
    """
    try:
        from src.core.notifications import NotificationService
        
        service = NotificationService()
        
        # Send both Pushover and Email alerts
        results = service.send_combined_alert(
            city=city,
            no2_level=no2_level,
            category=category,
            date=date or datetime.now().strftime('%Y-%m-%d'),
            send_pushover=True,
            send_email=True
        )
        
        messages = []
        if results.get('pushover'):
            messages.append("✅ Pushover notification sent")
        else:
            messages.append("⚠️ Pushover notification failed")
            
        if results.get('email'):
            messages.append("✅ Email notification sent")
        else:
            messages.append("⚠️ Email notification failed")
        
        return f"Notifications sent for {city}:\n" + "\n".join(messages)
            
    except Exception as e:
        return f"Error sending notifications: {str(e)}"


@tool("Generate Regulatory Reports")
def report_generator_tool(city: str, start_date: str, end_date: str, avg_no2: float, max_no2: float, category: str) -> str:
    """
    Generates comprehensive PDF reports for government compliance and air pollution prevention.
    
    Args:
        city: City name
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        avg_no2: Average NO2 level in µg/m³
        max_no2: Maximum NO2 level in µg/m³
        category: Air quality category
    
    Returns:
        Paths to generated PDF reports
    """
    try:
        data = {
            'average_no2': avg_no2,
            'max_no2': max_no2,
            'category': category
        }
        
        generator = RegulatoryReportGenerator()
        
        # Generate regulatory report
        report_path = generator.generate_regulatory_report(
            city=city,
            start_date=start_date,
            end_date=end_date,
            data=data,
            include_recommendations=True
        )
        
        # Generate prevention guide
        guide_path = generator.generate_prevention_guide(city)
        
        return f"""✅ Reports generated successfully:

1. Regulatory Compliance Report: {report_path}
2. Air Pollution Prevention Guide: {guide_path}

These reports include:
- Compliance assessment with CPCB and WHO standards
- Health impact analysis
- Source attribution
- Policy recommendations
- Prevention strategies for individuals, communities, businesses, and government"""
        
    except Exception as e:
        return f"Error generating reports: {str(e)}"
