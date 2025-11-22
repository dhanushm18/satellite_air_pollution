# Google Earth Engine Setup Guide

## Quick Setup for Air Quality Monitoring System

### Step 1: Get Your Earth Engine Project ID

1. **Go to Google Earth Engine**: https://code.earthengine.google.com/
2. **Sign in** with your Google account
3. **Register** for Earth Engine (if you haven't already)
   - Click "Get Started" or "Register"
   - Fill out the registration form
   - Wait for approval (usually instant for non-commercial use)

4. **Find Your Project ID**:
   - Once logged in, look at the top of the page
   - You'll see a project dropdown or your project ID displayed
   - It usually looks like: `ee-yourname` or `your-project-name-123456`
   - **Copy this Project ID**

### Step 2: Authenticate Earth Engine

Open a terminal in your project directory and run:

```bash
# Activate your conda environment first
conda activate satellite_downscaling

# Run Earth Engine authentication
earthengine authenticate
```

This will:
1. Open a browser window
2. Ask you to sign in with Google
3. Give you an authorization code
4. Paste the code back in the terminal

### Step 3: Add Project ID to .env File

Open your `.env` file and add/update this line:

```
EE_PROJECT_ID=your-project-id-here
```

Replace `your-project-id-here` with the actual Project ID you copied in Step 1.

Example:
```
EE_PROJECT_ID=ee-dhanushm
```

### Step 4: Verify Setup

Test if Earth Engine is working:

```python
import ee

# Initialize with your project
ee.Initialize(project='your-project-id-here')

# Test query
collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2')
print(f"✅ Earth Engine working! Found {collection.size().getInfo()} images")
```

### Common Issues

#### Issue: "Caller does not have required permission"
**Solution**: Your Project ID is incorrect or not set in `.env`
- Double-check the Project ID in Earth Engine console
- Make sure `.env` file has `EE_PROJECT_ID=your-actual-id`
- Restart the Flask app after changing `.env`

#### Issue: "Please authenticate Earth Engine"
**Solution**: Run `earthengine authenticate` in terminal

#### Issue: "Project not found"
**Solution**: 
- Make sure you've registered for Earth Engine
- Wait for approval email (check spam folder)
- Use the exact Project ID from the Earth Engine console

### Your Current .env Should Look Like:

```
# Pushover Notifications
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_api_token

# Email Configuration
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_TO=recipient1@email.com,recipient2@email.com
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4o-mini

# Google Earth Engine
EE_PROJECT_ID=your-project-id-here
```

### After Setup

1. **Restart Flask**: Stop and restart `python app.py`
2. **Test the system**: Click "Launch Monitoring System" on the homepage
3. **Check for errors**: Look at the terminal output for any Earth Engine errors

---

## Need Help?

If you're still having issues:
1. Check that you're logged into the correct Google account
2. Verify your Earth Engine registration is approved
3. Make sure the Project ID matches exactly (case-sensitive)
4. Try re-authenticating: `earthengine authenticate --force`
