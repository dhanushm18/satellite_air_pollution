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
        no2_level: float, # Metric (unused in display)
        category: str,
        cigarettes: float = 0.0,
        date: str = None
    ) -> bool:
        """
        Send air quality alert via Email (HTML formatted)
        """
        if date is None:
            date = datetime.now().strftime('%B %d, %Y')
        
        # Color mapping
        color_map = {
            "Good": "#4CAF50", # Green
            "Moderate": "#FFC107", # Amber
            "Poor": "#FF9800", # Orange
            "Very Poor": "#F44336", # Red
            "Severe": "#B71C1C" # Dark Red
        }
        bg_color = color_map.get(category, "#607D8B")
        
        # Suggestions Map
        # Suggestions Map (Expanded for Self-Awareness & Health)
        suggestions = {
            "Good": [
                "✅ Perfect time for outdoor cardio or marathons.",
                "🏠 VENTILATE: Open all windows to flush out indoor CO2.",
                "👶 Ideal for infants and elderly to soak in sun.",
                "🧘‍♀️ Practice deep breathing exercises outdoors.",
                "⚡ Maximize solar energy usage if applicable."
            ],
            "Moderate": [
                "⚠️ Sensitive groups (asthma/heart conditions) should carry inhalers.",
                "🚘 Close car windows while driving in traffic.",
                "🏃‍♂️ Reduce intensity of outdoor exercise (jog instead of sprint).",
                "🥛 Stay hydrated to keep airways moist.",
                "🔄 Recirculate indoor air during peak traffic hours."
            ],
            "Poor": [
                "🚫 CUT OUTDOOR EXERCISE: Switch to indoor gym/yoga.",
                "😷 COMMUTING: Wear an N95 mask if walking/biking.",
                "🧒 CHILDREN: Limit playground time to <30 mins.",
                "🥗 DIET: Increase intake of antioxidants (Vitamin C/E).",
                "🌬️ PURIFIERS: Run HEPA filters in bedrooms at night.",
                "🧂 STEAM INHALATION: Consider before sleep to clear airways."
            ],
            "Very Poor": [
                "🚨 AVOID OUTDOORS: Walk only if necessary.",
                "😷 MANDATORY N95/N99 MASK: Cloth masks are ineffective.",
                "🏢 WORK FROM HOME: If employer permits.",
                "🚿 Wash face/hands immediately after returning indoors.",
                "🥘 COOKING: Use exhaust fans; avoid frying to reduce indoor PM2.5.",
                "🌱 INDOOR PLANTS: Snake Plant/Areca Palm can help slightly."
            ],
            "Severe": [
                "🆘 HEALTH EMERGENCY: Breathlessness possible even in healthy adults.",
                "🛑 SEAL WINDOWS: Use wet towels in door gaps if drafts enter.",
                "💨 DO NOT EXERCISE: Even indoors, keep activity low.",
                "💊 ASTHMATICS: Keep relief medication immediately accessible.",
                "🩺 CHECK OXYGEN: Monitor SpO2 levels if feeling dizzy.",
                "🌫️ AIR PURIFIER: Run on 'Turbo' mode 24/7."
            ]
        }
        
        advice_list = suggestions.get(category, ["Monitor local health advisories."])
        advice_html = "".join([f"<li>{item}</li>" for item in advice_list])
        
        # HTML Email Body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                <div style="background-color: {bg_color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">Air Quality Alert: {city}</h1>
                    <p style="margin: 5px 0 0 0; font-size: 18px;">Status: <strong>{category.upper()}</strong></p>
                </div>
                
                <div style="padding: 20px;">
                    <p style="font-size: 16px;">
                        The air quality in <strong>{city}</strong> is currently categorized as <strong style="color: {bg_color};">{category}</strong>.
                    </p>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid {bg_color}; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #333;">Health Recommendations:</h3>
                        <ul style="margin-bottom: 0; padding-left: 20px;">
                            {advice_html}
                        </ul>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px; text-align: center;">
                        Generated by National Air Quality Monitoring Bureau | {date}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_body = f"Air Quality Alert: {city}\nStatus: {category}\n\nRecommendations:\n" + "\n".join([f"- {item}" for item in advice_list])
        
        subject = f"Air Quality Alert: {category} in {city}"
        
        # Only send Email, ignore Pushover
        print(f"📧 Sending formatted email alert for {city}...")
        return self.send_email(subject, plain_body, html_body)
    
    def send_daily_summary(
        self,
        cities_data: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Send daily summary via Email (HTML formatted)
        """
        # Build HTML Rows
        rows = ""
        for city, data in cities_data.items():
            category = data.get('category', 'Unknown')
            # Color mapping
            color_map = {
                "Good": "#4CAF50", "Moderate": "#FFC107", "Poor": "#FF9800",
                "Very Poor": "#F44336", "Severe": "#B71C1C"
            }
            color = color_map.get(category, "grey")
            
            rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>{city}</strong></td>
                <td style="padding: 12px; border-bottom: 1px solid #ddd; color: {color}; font-weight: bold;">{category}</td>
            </tr>
            """
            
        date_str = datetime.now().strftime('%B %d, %Y')
        
        # HTML Body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px;">
                <div style="background-color: #1a237e; color: white; padding: 20px; text-align: center;">
                    <h2 style="margin: 0;">Daily Air Quality Summary</h2>
                    <p style="margin: 5px 0 0 0;">{date_str}</p>
                </div>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 12px; text-align: left;">City</th>
                        <th style="padding: 12px; text-align: left;">Status</th>
                    </tr>
                    {rows}
                </table>
                <p style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
                    National Air Quality Monitoring Bureau
                </p>
            </div>
        </body>
        </html>
        """
        
        plain_body = "Daily Summary:\n" + "\n".join([f"{c}: {d.get('category')}" for c, d in cities_data.items()])
        
        print(f"📧 Sending daily summary email for {len(cities_data)} cities...")
        return self.send_email(f"Daily Air Quality Summary - {date_str}", plain_body, html_body)
    
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
        cigarettes: float = 0.0,
        date: str = None
    ) -> bool:
        """
        Send air quality alert via email
        
        Args:
            city: City name
            no2_level: AQI or Main Metric
            category: Air quality category
            cigarettes: Cigarette equivalent
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

AQI: {int(no2_level)}
Category: {category}
Cigarette Equivalent: ~{cigarettes:.1f} cigarettes/day
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
                <div class="metric-label">Air Quality Index (AQI)</div>
                <div class="metric-value">{int(no2_level)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Cigarette Equivalent</div>
                <div class="metric-value">~{cigarettes:.1f} / day</div>
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
        cigarettes: float = 0.0,
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
            results['pushover'] = self.send_air_quality_alert(city, no2_level, category, cigarettes, date)
        
        if send_email:
            results['email'] = self.send_air_quality_email(city, no2_level, category, cigarettes, date)
        
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
