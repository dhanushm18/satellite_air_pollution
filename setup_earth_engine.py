"""
ee_setup_check.py
Quick helper to verify Google Earth Engine setup: try high-volume endpoint,
then (if needed) initialize with a Cloud Project or a service account key.
"""
import os
import subprocess
import textwrap
import sys

try:
    import ee
except ImportError:
    print("❌ The 'earthengine' Python package is not installed.")
    print("Install with: pip install earthengine-api")
    sys.exit(1)

def list_gcloud_projects():
    try:
        result = subprocess.run(["gcloud", "projects", "list", "--format=value(projectId)"],
                                capture_output=True, text=True, check=True)
        projects = [p.strip() for p in result.stdout.splitlines() if p.strip()]
        if projects:
            print("📋 Detected gcloud projects (project IDs):")
            for p in projects:
                print("  -", p)
        else:
            print("ℹ️ gcloud is installed but no projects returned (or none visible to your gcloud account).")
    except FileNotFoundError:
        print("⚠️ 'gcloud' CLI not found. Install and authenticate with `gcloud auth login` if you want to use it here.")
    except subprocess.CalledProcessError as e:
        print("⚠️ Error running `gcloud projects list`:", e)
    except Exception as e:
        print("⚠️ Unexpected error listing projects:", e)

def try_highvolume():
    print("\n🔁 Trying high-volume endpoint (no project required)...")
    try:
        ee.Initialize(opt_url="https://earthengine-highvolume.googleapis.com")
        # quick test: get count of images in a known collection
        coll = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
        count = coll.size().getInfo()
        print(f"✅ High-volume endpoint initialized. Found {count} images in COPERNICUS/S5P/OFFL/L3_NO2.")
        print("Tip: set environment variable EE_USE_HIGHVOLUME=true to use this endpoint in your apps.")
        return True
    except Exception as ex:
        print("❌ High-volume endpoint failed:", ex)
        return False

def initialize_with_project(project_id=None):
    print("\n🔁 Trying to initialize Earth Engine with a Cloud Project...")

    # Prefer Application Default Credentials if available
    # If GOOGLE_APPLICATION_CREDENTIALS is set to a service account key JSON, that will be used.
    if project_id:
        print(f"Using project id: {project_id}")

    try:
        # Initialize with optional project; if credentials are not found it will prompt
        ee.Initialize(project=project_id)
        coll = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
        count = coll.size().getInfo()
        print(f"✅ Earth Engine initialized with project '{project_id or '(default)'}'. Collection size: {count}")
        return True
    except Exception as ex:
        print("❌ Initialization with project failed:", ex)
        return False

def initialize_with_service_account(sa_email=None, key_path=None, project_id=None):
    print("\n🔁 Trying service account authentication...")
    if not sa_email or not key_path:
        print("⚠️ Service account email and key path required for this mode.")
        return False

    if not os.path.exists(key_path):
        print("⚠️ Service account key file not found at:", key_path)
        return False

    try:
        # Earth Engine supports oauth2 service account credentials via oauth2client
        from oauth2client.service_account import ServiceAccountCredentials
        scopes = ["https://www.googleapis.com/auth/earthengine",
                  "https://www.googleapis.com/auth/cloud-platform"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scopes=scopes)
        ee.Initialize(credentials=credentials, project=project_id)
        coll = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
        count = coll.size().getInfo()
        print(f"✅ Initialized using service account {sa_email}. Collection size: {count}")
        return True
    except Exception as ex:
        print("❌ Service account initialization failed:", ex)
        return False

def main():
    print("🔧 Setting up Google Earth Engine (GEE) verification helper\n")
    list_gcloud_projects()

    # Check for helpful env vars
    ee_project = os.environ.get("EE_PROJECT_ID")
    ee_highvolume = os.environ.get("EE_USE_HIGHVOLUME", "").lower() in ("1","true","yes")
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    sa_email = os.environ.get("EE_SERVICE_ACCOUNT")  # optional helper var

    print("\nEnvironment summary:")
    print("  EE_PROJECT_ID:", ee_project or "(not set)")
    print("  EE_USE_HIGHVOLUME:", ee_highvolume)
    print("  GOOGLE_APPLICATION_CREDENTIALS:", gac or "(not set)")
    print("  EE_SERVICE_ACCOUNT:", sa_email or "(not set)")

    # 1) Try high-volume endpoint if user enabled or as default attempt
    if ee_highvolume or not ee_project:
        ok = try_highvolume()
        if ok:
            return

    # 2) Try to initialize using ADC (Application Default Credentials) and project
    if ee_project:
        ok = initialize_with_project(project_id=ee_project)
        if ok:
            return

    # 3) If service account key path is provided, try that
    if sa_email and gac:
        ok = initialize_with_service_account(sa_email=sa_email, key_path=gac, project_id=ee_project)
        if ok:
            return

    # 4) Fallback: instruct the user to authenticate interactively
    print("\n📘 Interactive authentication fallback:")
    print(textwrap.dedent("""
      If you are using a personal account, run:
        >>> earthengine authenticate
      or in Python:
        >>> import ee
        >>> ee.Authenticate()   # will open a browser for OAuth
        >>> ee.Initialize()

      If you want to use a service account (recommended for server environments):
        1. Create a service account in Google Cloud Console.
        2. Download the JSON key file and set:
             export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
           (or set the env var in your OS)
        3. Optionally set the service account email in EE_SERVICE_ACCOUNT and EE_PROJECT_ID, then re-run this script.
    """))

if __name__ == "__main__":
    main()
