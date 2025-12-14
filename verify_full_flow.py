import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())
load_dotenv()

from src.agents.agents import run_satellite_crew
from datetime import datetime, timedelta

def verify_full_flow():
    city = "Bengaluru"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    print(f"🚀 Starting full verification for {city}...")
    
    try:
        # Run the crew
        result = run_satellite_crew(
            city=city,
            start_date=start_date,
            end_date=end_date,
            send_alerts=False, # Don't actually spam alerts
            generate_reports=True,
            log_callback=lambda x: print(f"Agent: {str(x)[:100]}...")
        )
        
        print("\n✅ Crew execution successful!")
        print("Result Summary:", str(result)[:200])
        
        # Check if report was generated
        reports_dir = "reports"
        files = [f for f in os.listdir(reports_dir) if f.startswith(f"Regulatory_Report_{city}")]
        if files:
            print(f"✅ Regulatory Report generated: {files[0]}")
        else:
            print("❌ Regulatory Report NOT found!")
            
    except Exception as e:
        print(f"❌ Execution Failed: {e}")

if __name__ == "__main__":
    verify_full_flow()
