# ✅ Email Alerts Added!

I've successfully added **email notification functionality** to your agentic air quality system!

## 🎯 What's New

### Email Features
- ✅ **Beautiful HTML Emails** with color-coded alerts
- ✅ **Plain Text Fallback** for compatibility
- ✅ **Combined Alerts** - Send both Pushover AND email
- ✅ **Automatic Styling** based on air quality category

---

## 📧 Email Configuration

### Step 1: Add to .env file

```bash
# Email Configuration
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Multiple recipients supported (comma-separated)
EMAIL_TO=recipient1@example.com,recipient2@example.com,recipient3@example.com

EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

**Note:** You can add as many email recipients as you want by separating them with commas.

### Step 2: Get Gmail App Password

For Gmail users:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create an app password for "Mail"
5. Use that password in `EMAIL_PASSWORD`

---

## 🧪 Test Email

```bash
python test_email.py
```

This will send a test email to verify everything works!

---

## 📱 How to Use

### Option 1: Email Only
```python
from src.core.notifications import NotificationService

service = NotificationService()
service.send_air_quality_email(
    city="Bengaluru",
    no2_level=95.5,
    category="Poor"
)
```

### Option 2: Pushover Only
```python
service.send_air_quality_alert(
    city="Bengaluru",
    no2_level=95.5,
    category="Poor"
)
```

### Option 3: Both (Recommended!)
```python
results = service.send_combined_alert(
    city="Bengaluru",
    no2_level=95.5,
    category="Poor",
    send_pushover=True,  # Phone notification
    send_email=True      # Email notification
)

print(results)  # {'pushover': True, 'email': True}
```

---

## 🎨 Email Design

The emails are beautifully designed with:
- **Color-coded headers** (green for Good, red for Severe, etc.)
- **Gradient backgrounds**
- **Clean metrics display**
- **Health advisory box**
- **Responsive design**

### Example Email:
```
🔴 Air Quality Alert
Bengaluru

NO₂ Level: 95.5 µg/m³
Category: Poor
Date: 2025-11-21

Health Advisory:
🚫 Limit outdoor activities. Children and elderly should stay indoors.
```

---

## 🔧 Supported Email Providers

- ✅ Gmail (smtp.gmail.com:587)
- ✅ Outlook (smtp-mail.outlook.com:587)
- ✅ Yahoo (smtp.mail.yahoo.com:587)
- ✅ Custom SMTP servers

Just update `EMAIL_SMTP_SERVER` and `EMAIL_SMTP_PORT` in .env

---

## 🎯 Next Steps

1. Add email credentials to `.env`
2. Run `python test_email.py`
3. Check your inbox!
4. Agents will now send BOTH Pushover AND Email alerts automatically

---

**Your agentic system now sends alerts via:**
- 📱 Pushover (phone notifications)
- 📧 Email (beautiful HTML emails)

Both work together automatically! 🎉
