import os
import sys
import re
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from src.agents.tools import satellite_search_tool, analysis_tool, report_generator_tool
from datetime import datetime, timedelta

# Test parameters
city = "Bengaluru"
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

print("--- Step 1: Search ---")
search_result = satellite_search_tool.func(city, start_date, end_date)
print(search_result)

# Extract path from result (simulating agent)
file_path = search_result.strip()
if os.path.exists(file_path):
    print(f"\nExtracted Path: {file_path}")
    
    print("\n--- Step 2: Analysis ---")
    analysis_result = analysis_tool.func(file_path)
    print(analysis_result)
    
    # Extract values from analysis (simulating agent)
    # Analysis Results for Bengaluru:
    # - Average NO2: 4.17 µg/m³ (Good)
    # - Peak NO2: 8.33 µg/m³
    
    avg_match = re.search(r"Average NO2: ([\d\.]+) µg/m³", analysis_result)
    max_match = re.search(r"Peak NO2: ([\d\.]+) µg/m³", analysis_result)
    cat_match = re.search(r"\((.*?)\)", analysis_result) # Matches (Good)
    
    if avg_match and max_match:
        avg_no2 = float(avg_match.group(1))
        max_no2 = float(max_match.group(1))
        # Simple extraction for category from the line with Average NO2
        category = "Unknown"
        lines = analysis_result.split('\n')
        for line in lines:
            if "Average NO2" in line and "(" in line:
                category = line.split("(")[1].replace(")", "").strip()
        
        print(f"\nExtracted Stats: Avg={avg_no2}, Max={max_no2}, Cat={category}")
        
        print("\n--- Step 3: Reporting ---")
        try:
            report_result = report_generator_tool.func(city, start_date, end_date, avg_no2, max_no2, category)
            print(report_result)
            
            print("\n--- Step 4: Notification (Test Fix) ---")
            from src.agents.tools import notification_tool
            # Test calling without date to verify optional parameter
            notify_result = notification_tool.func(city, avg_no2, category)
            print(f"Notification Result: {notify_result}")
            
        except Exception as e:
            print(f"Reporting Failed: {e}")
            import traceback
            traceback.print_exc()

else:
    print("Could not extract file path")
