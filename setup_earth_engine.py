"""
Quick script to register Earth Engine with a cloud project
"""
import ee

print("🔧 Setting up Earth Engine...")
print()

# Try to get available projects
try:
    # This will show you available projects
    import subprocess
    result = subprocess.run(['gcloud', 'projects', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        print("📋 Your Google Cloud Projects:")
        print(result.stdout)
    else:
        print("⚠️ gcloud not installed or not configured")
except Exception as e:
    print(f"⚠️ Could not list projects: {e}")

print()
print("=" * 60)
print("OPTION 1: Use Earth Engine's Default Project (Recommended)")
print("=" * 60)
print()
print("Earth Engine can create a default project for you automatically.")
print("This is the easiest option and works for most users.")
print()

try:
    # Try to initialize with high-volume endpoint (no project needed)
    ee.Initialize(opt_url='https://earthengine-highvolume.googleapis.com')
    print("✅ SUCCESS! Earth Engine initialized with high-volume endpoint")
    print()
    print("Add this to your .env file:")
    print("EE_USE_HIGHVOLUME=true")
    print()
    
    # Test it
    collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')
    count = collection.size().getInfo()
    print(f"✅ Test successful! Found {count} images in Sentinel-5P collection")
    
except Exception as e1:
    print(f"❌ High-volume endpoint failed: {e1}")
    print()
    print("=" * 60)
    print("OPTION 2: Create a Cloud Project")
    print("=" * 60)
    print()
    print("Follow these steps:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Click 'Select a project' → 'New Project'")
    print("3. Name it: 'earth-engine-project'")
    print("4. Click 'Create'")
    print("5. Copy the Project ID (looks like: earth-engine-project-123456)")
    print("6. Add to .env: EE_PROJECT_ID=your-project-id-here")
    print()
    print("Then run this script again to verify.")
