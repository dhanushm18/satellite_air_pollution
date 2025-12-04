import ee
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Force high volume if needed
# os.environ['EE_USE_HIGHVOLUME'] = 'true'

try:
    project_id = os.getenv('EE_PROJECT_ID')
    if project_id:
        print(f"Init with project: {project_id}")
        ee.Initialize(project=project_id)
    else:
        print("Init default/high-volume")
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except Exception as e:
    print(f"Init failed: {e}")
    exit(1)

# Coordinates for Bengaluru
lat = 12.9716
lon = 77.5946
roi = ee.Geometry.Point([lon, lat]).buffer(5000) # 5km buffer

end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

print(f"Fetching stats for {start_date} to {end_date}...")

try:
    collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2') \
        .select('tropospheric_NO2_column_number_density') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date)

    count = collection.size().getInfo()
    print(f"Found {count} images")

    if count > 0:
        # Reduce region to get mean
        image = collection.mean()
        stats = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=1000,
            bestEffort=True
        ).getInfo()
        
        print("Stats:", stats)
        val = stats.get('tropospheric_NO2_column_number_density')
        if val:
            print(f"Mean NO2: {val} mol/m^2")
            print(f"Mean NO2: {val * 46000} µg/m³ (approx)")
    else:
        print("No images found")

except Exception as e:
    print(f"Error: {e}")
