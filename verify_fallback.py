import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.getcwd())
load_dotenv()

from src.agents.tools import satellite_search_tool

# Test parameters: Future dates to force "no data" from Earth Engine
city = "Bengaluru"
start_date = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
end_date = (datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d')

print(f"--- Testing Fallback for {city} ---")
print(f"Searching for future dates: {start_date} to {end_date}")

# This should fail in EE but succeed via fallback
result = satellite_search_tool.func(city, start_date, end_date)
print(f"\nResult: {result}")

if os.path.exists(result):
    print("\n✅ SUCCESS: Fallback returned a valid file path.")
else:
    print("\n❌ FAILURE: Fallback did not return a valid file path.")
