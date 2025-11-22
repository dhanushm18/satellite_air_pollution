"""
Notification Service for Air Quality Alerts
Supports Pushover and Email notifications
"""
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class NotificationService:
    """Handle notifications via Pushover and Email"""
    
    def __init__(self):
        # Pushover configuration
        self.pushover_user_key = os.getenv('PUSHOVER_USER_KEY')
        self.pushover_api_token = os.getenv('PUSHOVER_API_TOKEN')
        self.pushover_url = "https://api.pushover.net/1/messages.json"
        
        # Email configuration
        self.email_smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.email_smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Support multiple email recipients (comma-separated)
        email_to_raw = os.getenv('EMAIL_TO', '')
        self.email_to_list = [email.strip() for email in email_to_raw.split(',') if email.strip()]
        # Keep backward compatibility with single email
        self.email_to = self.email_to_list[0] if self.email_to_list else None
        
    def send_pushover(
        self, 
        message: str, 
        title: str = "Air Quality Alert",
        priority: int = 0,
        sound: str = "pushover"
    ) -> bool:
        """
        Send notification via Pushover
        
        Args:
            message: Notification message
            title: Notification title
            priority: -2 (lowest) to 2 (emergency)
            sound: Notification sound
            
        Returns:
            bool: True if sent successfully
        """
        if not self.pushover_user_key or not self.pushover_api_token:
            print("⚠️ Pushover credentials not configured in .env file")
            return False
            
        try:
            data = {
                "token": self.pushover_api_token,
                "user": self.pushover_user_key,
                "message": message,
                "title": title,
                "priority": priority,
                "sound": sound,
                "timestamp": int(datetime.now().timestamp())
            }
            
            response = requests.post(self.pushover_url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Pushover notification sent: {title}")
                return True
            else:
                print(f"❌ Pushover error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Pushover notification: {str(e)}")
            return False
    
    def send_air_quality_alert(
        self,
        city: str,
        no2_level: float,
        category: str,
        date: str = None
    ) -> bool:
        """
        Send air quality alert
        
        Args:
            city: City name
            no2_level: NO2 level in µg/m³
            category: Air quality category
            date: Date of measurement
            
        Returns:
            bool: True if sent successfully
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Determine priority based on category
        priority_map = {
            "Good": -1,
            "Moderate": 0,
            "Poor": 0,
            "Very Poor": 1,
            "Severe": 2
        }
        priority = priority_map.get(category, 0)
        
        # Determine sound based on severity
        sound_map = {
            "Good": "none",
            "Moderate": "pushover",
            "Poor": "persistent",
            "Very Poor": "persistent",
            "Severe": "siren"
        }
        sound = sound_map.get(category, "pushover")
        
        # Create message
        emoji_map = {
            "Good": "🟢",
            "Moderate": "🟡",
            "Poor": "🟠",
            "Very Poor": "🔴",
            "Severe": "🚨"
        }
        emoji = emoji_map.get(category, "⚠️")
        
        message = f"""{emoji} Air Quality Alert for {city}

NO₂ Level: {no2_level:.1f} µg/m³
Category: {category}
Date: {date}

Health Advisory:
"""
        
        if category == "Good":
            message += "✅ Air quality is good. Safe for outdoor activities."
        elif category == "Moderate":
            message += "⚠️ Sensitive individuals should limit prolonged outdoor exertion."
        elif category == "Poor":
            message += "🚫 Limit outdoor activities. Children and elderly should stay indoors."
        elif category == "Very Poor":
            message += "🚨 Avoid outdoor activities. Use air purifiers indoors."
        else:  # Severe
            message += "🆘 EMERGENCY: Stay indoors. Close all windows. Use N95 masks if you must go out."
        
        title = f"{emoji} {city}: {category} Air Quality"
        
        return self.send_pushover(message, title, priority, sound)
    
    def send_daily_summary(
        self,
        cities_data: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Send daily summary for multiple cities
        
        Args:
            cities_data: Dict with city names as keys and data as values
                        Each value should have: no2_level, category
                        
        Returns:
            bool: True if sent successfully
        """
        message = "📊 Daily Air Quality Summary\n\n"
        
        for city, data in cities_data.items():
            no2 = data.get('no2_level', 0)
            category = data.get('category', 'Unknown')
            emoji_map = {
                "Good": "🟢",
                "Moderate": "🟡",
                "Poor": "🟠",
                "Very Poor": "🔴",
                "Severe": "🚨"
            }
            emoji = emoji_map.get(category, "⚠️")
            message += f"{emoji} {city}: {no2:.1f} µg/m³ ({category})\n"
        
        # Add summary statistics
        total_cities = len(cities_data)
        good_cities = sum(1 for d in cities_data.values() if d.get('category') == 'Good')
        severe_cities = sum(1 for d in cities_data.values() if d.get('category') in ['Very Poor', 'Severe'])
        
        message += f"\n📈 Summary:\n"
        message += f"Total Cities: {total_cities}\n"
        message += f"Good Air Quality: {good_cities}\n"
        message += f"Needs Attention: {severe_cities}\n"
        
        return self.send_pushover(
            message,
            title="Daily Air Quality Summary",
            priority=0,
            sound="pushover"
        )
    
    def send_email(
        self,
        subject: str,
        body: str,
        html_body: str = None,
        recipients: list = None
    ) -> bool:
        """
        Send email notification to multiple recipients
        
        Args:
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            recipients: List of email addresses (optional, uses self.email_to_list if not provided)
            
        Returns:
            bool: True if sent successfully to at least one recipient
        """
        if not self.email_from or not self.email_password:
            print("⚠️ Email credentials not configured in .env file")
            return False
        
        # Use provided recipients or default to configured list
        recipient_list = recipients if recipients else self.email_to_list
        
        if not recipient_list:
            print("⚠️ No email recipients configured in .env file")
            return False
        
        success_count = 0
        failed_recipients = []
        
        try:
            # Send to each recipient
            for recipient in recipient_list:
                try:
                    # Create message
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = self.email_from
                    msg['To'] = recipient
                    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
                    
                    # Attach plain text
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Attach HTML if provided
                    if html_body:
                        msg.attach(MIMEText(html_body, 'html'))
                    
                    # Send email
                    with smtplib.SMTP(self.email_smtp_server, self.email_smtp_port) as server:
                        server.starttls()
                        server.login(self.email_from, self.email_password)
                        server.send_message(msg)
                    
                    print(f"✅ Email sent to {recipient}: {subject}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to send email to {recipient}: {str(e)}")
                    failed_recipients.append(recipient)
            
            # Report results
            if success_count > 0:
                print(f"📧 Successfully sent to {success_count}/{len(recipient_list)} recipients")
                if failed_recipients:
                    print(f"⚠️ Failed recipients: {', '.join(failed_recipients)}")
                return True
            else:
                print(f"❌ Failed to send email to all recipients")
                return False
                
        except Exception as e:
            print(f"❌ Email sending error: {str(e)}")
            return False
    
    def send_air_quality_email(
        self,
        city: str,
        no2_level: float,
        category: str,
        date: str = None
    ) -> bool:
        """
        Send air quality alert via email
        
        Args:
            city: City name
            no2_level: NO2 level in µg/m³
            category: Air quality category
            date: Date of measurement
            
        Returns:
            bool: True if sent successfully
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Emoji map
        emoji_map = {
            "Good": "🟢",
            "Moderate": "🟡",
            "Poor": "🟠",
            "Very Poor": "🔴",
            "Severe": "🚨"
        }
        emoji = emoji_map.get(category, "⚠️")
        
        # Color map for HTML
        color_map = {
            "Good": "#10B981",
            "Moderate": "#F59E0B",
            "Poor": "#F97316",
            "Very Poor": "#EF4444",
            "Severe": "#DC2626"
        }
        color = color_map.get(category, "#6B7280")
        
        # Health advisory
        if category == "Good":
            advisory = "✅ Air quality is good. Safe for outdoor activities."
        elif category == "Moderate":
            advisory = "⚠️ Sensitive individuals should limit prolonged outdoor exertion."
        elif category == "Poor":
            advisory = "🚫 Limit outdoor activities. Children and elderly should stay indoors."
        elif category == "Very Poor":
            advisory = "🚨 Avoid outdoor activities. Use air purifiers indoors."
        else:  # Severe
            advisory = "🆘 EMERGENCY: Stay indoors. Close all windows. Use N95 masks if you must go out."
        
        # Plain text body
        subject = f"{emoji} Air Quality Alert: {city} - {category}"
        
        body = f"""Air Quality Alert for {city}

NO₂ Level: {no2_level:.1f} µg/m³
Category: {category}
Date: {date}

Health Advisory:
{advisory}

---
This is an automated alert from the Agentic Air Quality Monitoring System.
"""
        
        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                   color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
        .metric {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; 
                  border-left: 4px solid {color}; }}
        .metric-label {{ color: #6b7280; font-size: 14px; margin-bottom: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: {color}; }}
        .advisory {{ background: {color}22; padding: 20px; border-radius: 8px; margin-top: 20px; 
                    border-left: 4px solid {color}; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{emoji} Air Quality Alert</h1>
            <h2>{city}</h2>
        </div>
        <div class="content">
            <div class="metric">
                <div class="metric-label">NO₂ Level</div>
                <div class="metric-value">{no2_level:.1f} µg/m³</div>
            </div>
            <div class="metric">
                <div class="metric-label">Air Quality Category</div>
                <div class="metric-value">{category}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Date</div>
                <div class="metric-value">{date}</div>
            </div>
            <div class="advisory">
                <h3>Health Advisory</h3>
                <p>{advisory}</p>
            </div>
        </div>
        <div class="footer">
            <p>This is an automated alert from the Agentic Air Quality Monitoring System</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body, html_body)
    
    def send_combined_alert(
        self,
        city: str,
        no2_level: float,
        category: str,
        date: str = None,
        send_pushover: bool = True,
        send_email: bool = True
    ) -> Dict[str, bool]:
        """
        Send alert via both Pushover and Email
        
        Args:
            city: City name
            no2_level: NO2 level in µg/m³
            category: Air quality category
            date: Date of measurement
            send_pushover: Whether to send Pushover notification
            send_email: Whether to send email
            
        Returns:
            dict: Status of each notification method
        """
        results = {}
        
        if send_pushover:
            results['pushover'] = self.send_air_quality_alert(city, no2_level, category, date)
        
        if send_email:
            results['email'] = self.send_air_quality_email(city, no2_level, category, date)
        
        return results
    
    def send_regulatory_alert(
        self,
        city: str,
        violation_type: str,
        details: str
    ) -> bool:
        """
        Send regulatory compliance alert
        
        Args:
            city: City name
            violation_type: Type of violation
            details: Violation details
            
        Returns:
            bool: True if sent successfully
        """
        message = f"""🚨 Regulatory Alert

City: {city}
Violation: {violation_type}

Details:
{details}

Action Required:
Immediate investigation and corrective measures needed.
"""
        
        return self.send_pushover(
            message,
            title=f"⚠️ Regulatory Alert: {city}",
            priority=1,
            sound="persistent"
        )


# Convenience function
def send_alert(city: str, no2_level: float, category: str, date: str = None) -> bool:
    """Quick function to send air quality alert"""
    service = NotificationService()
    return service.send_air_quality_alert(city, no2_level, category, date)


if __name__ == "__main__":
    # Test notification
    service = NotificationService()
    service.send_air_quality_alert(
        city="Bengaluru",
        no2_level=95.5,
        category="Poor",
        date="2025-11-21"
    )
