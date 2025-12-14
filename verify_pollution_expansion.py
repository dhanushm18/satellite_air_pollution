import os
import sys
from dotenv import load_dotenv
import json

# Add current directory to path
sys.path.append(os.getcwd())
load_dotenv()

from src.agents.tools import satellite_search_tool, analysis_tool
from datetime import datetime, timedelta

def verify():
    city = "Bengaluru"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

    print(f"Testing satellite search tool for {city}...")
    
    # 1. Test Search
    file_path = satellite_search_tool.func(city, start_date, end_date)
    print(f"Reference File: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ File not created!")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Check structure
    pollutants = data.get('pollutants', {})
    if 'so2' in pollutants and 'co' in pollutants and 'o3' in pollutants:
        print("✅ Pollutant data structure present")
        print(f"Sample CO: {pollutants['co']}")
    else:
        print("❌ Missing pollutant structure")

    # 2. Test Analysis
    print("\nTesting Analysis Tool...")
    analysis = analysis_tool.func(file_path)
    print(analysis)
    
    if "cigarettes" in analysis.lower() and "SO2" in analysis:
        print("\n✅ Verification SUCCESS: Found cigarette equivalent and new pollutants.")
    else:
        print("\n❌ Verification FAILED: Missing new data in analysis.")

if __name__ == "__main__":
    verify()
