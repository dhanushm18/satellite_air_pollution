import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from src.agents.tools import satellite_search_tool
from datetime import datetime, timedelta

# Test parameters
city = "Bengaluru"
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

print(f"Testing satellite search tool for {city} from {start_date} to {end_date}...")

try:
    # Access the underlying function of the tool
    result = satellite_search_tool.func(city, start_date, end_date)
    print("Result:", result)
except Exception as e:
    print(f"Error: {e}")
