from src.core.notifications import NotificationService
import os
from dotenv import load_dotenv

load_dotenv()

def debug_email():
    print("🔍 Checking Email Configuration...")
    email_from = os.getenv('EMAIL_FROM')
    email_pass = os.getenv('EMAIL_PASSWORD')
    email_to = os.getenv('EMAIL_TO')
    
    print(f"   EMAIL_FROM Set: {bool(email_from)}")
    print(f"   EMAIL_PASSWORD Set: {bool(email_pass)}")
    print(f"   EMAIL_TO Set: {bool(email_to)}")
    
    if not (email_from and email_pass and email_to):
        print("❌ Missing credentials. Please populate .env with EMAIL_FROM, EMAIL_PASSWORD, and EMAIL_TO.")
        return

    print("\n📧 Attempting to send test email...")
    service = NotificationService()
    
    try:
        # Using the new send_air_quality_alert method which uses send_email internally
        result = service.send_air_quality_alert(
            city="Bengaluru [TEST]",
            no2_level=150,
            category="Poor",
            cigarettes=3.5
        )
        
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email failed to send (Function returned False).")
            
    except Exception as e:
        print(f"❌ Exception during send: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_email()
