import sys
import os
sys.path.append(os.getcwd())

from src.agents.tools import report_generator_tool
from datetime import datetime

def verify_report():
    print("Testing report generator tool...")
    try:
        result = report_generator_tool.run(
            city="Bengaluru-Test", 
            start_date="2025-12-01", 
            end_date="2025-12-14", 
            aqi=150.5, 
            cigarettes=6.8, 
            category="Poor", 
            pollutant_data="{'no2': 45.2, 'so2': 12.1, 'co': 500.0, 'o3': 30.5}"
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    verify_report()
