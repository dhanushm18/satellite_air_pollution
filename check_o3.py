import ee
import os
from dotenv import load_dotenv

load_dotenv()

try:
    project_id = os.getenv('EE_PROJECT_ID')
    if project_id:
        ee.Initialize(project=project_id)
    else:
        ee.Initialize()
    
    # Try to get info for Tropospheric Ozone
    print("Checking COPERNICUS/S5P/OFFL/L3_O3_TCL...")
    collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_O3_TCL') \
        .limit(1)
    
    count = collection.size().getInfo()
    print(f"Count: {count}")
    
    if count > 0:
        img = collection.first()
        print("Bands:", img.bandNames().getInfo())
    
except Exception as e:
    print(f"Error: {e}")
