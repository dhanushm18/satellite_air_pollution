import ee
import os
from dotenv import load_dotenv

load_dotenv()

try:
    project_id = os.getenv('EE_PROJECT_ID')
    if project_id:
        ee.Initialize(project=project_id)
    else:
        # Try high volume as fallback
        ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
except Exception as e:
    print(f"Init failed: {e}")
    exit(1)

print("Checking bands for COPERNICUS/S5P/OFFL/L3_NO2")
collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')
first_image = collection.first()
if first_image:
    bands = first_image.bandNames().getInfo()
    for b in bands:
        print(b)
else:
    print("Collection is empty or not accessible")
