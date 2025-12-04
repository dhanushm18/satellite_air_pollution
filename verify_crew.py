import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from src.agents.agents import run_satellite_crew

def test_callback(step_output):
    """Callback for testing"""
    print(f"\n[Callback] Agent Step: {str(step_output)[:100]}...")

if __name__ == "__main__":
    print("🚀 Starting CrewAI Verification...")
    
    city = "Bengaluru"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        result = run_satellite_crew(
            city=city,
            start_date=start_date,
            end_date=end_date,
            send_alerts=True,
            generate_reports=True,
            log_callback=test_callback
        )
        
        print("\n✅ Crew Execution Successful!")
        print("Result:", result)
        
    except Exception as e:
        print(f"\n❌ Crew Execution Failed: {e}")
        import traceback
        traceback.print_exc()
