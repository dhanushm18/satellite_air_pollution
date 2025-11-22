"""
Command-Line Interface for Agentic Air Quality Monitor
Run autonomous agents from the terminal
"""
import argparse
from datetime import datetime, timedelta
from src.agents.agents import run_satellite_crew


def main():
    parser = argparse.ArgumentParser(
        description='🤖 Agentic Air Quality Monitor - Autonomous AI Agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor Bengaluru for today
  python run_agents.py --city "Bengaluru"
  
  # Monitor Delhi for a specific date range
  python run_agents.py --city "Delhi" --start-date "2025-11-20" --end-date "2025-11-21"
  
  # Monitor without sending alerts
  python run_agents.py --city "Mumbai" --no-alerts
  
  # Monitor without generating reports
  python run_agents.py --city "Chennai" --no-reports
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--city',
        type=str,
        required=True,
        help='City name to monitor (e.g., "Bengaluru", "Delhi", "Mumbai")'
    )
    
    # Optional arguments
    parser.add_argument(
        '--start-date',
        type=str,
        default=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        help='Start date in YYYY-MM-DD format (default: yesterday)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date in YYYY-MM-DD format (default: today)'
    )
    
    parser.add_argument(
        '--no-alerts',
        action='store_true',
        help='Disable Pushover notifications'
    )
    
    parser.add_argument(
        '--no-reports',
        action='store_true',
        help='Disable PDF report generation'
    )
    
    args = parser.parse_args()
    
    # Display configuration
    print("="*60)
    print("🤖 AGENTIC AIR QUALITY MONITOR")
    print("="*60)
    print(f"\n📍 City: {args.city}")
    print(f"📅 Date Range: {args.start_date} to {args.end_date}")
    print(f"📱 Notifications: {'✅ Enabled' if not args.no_alerts else '❌ Disabled'}")
    print(f"📄 Reports: {'✅ Enabled' if not args.no_reports else '❌ Disabled'}")
    print("\n" + "="*60)
    print("🚀 Launching Autonomous Agents...")
    print("="*60 + "\n")
    
    try:
        # Run the agent crew
        result = run_satellite_crew(
            city=args.city,
            start_date=args.start_date,
            end_date=args.end_date,
            send_alerts=not args.no_alerts,
            generate_reports=not args.no_reports
        )
        
        print("\n" + "="*60)
        print("✅ MISSION COMPLETE!")
        print("="*60)
        print(f"\n{result}\n")
        
        if not args.no_reports:
            print("📄 PDF reports saved in: reports/")
        
        if not args.no_alerts:
            print("📱 Pushover notification sent to your device")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ MISSION FAILED")
        print("="*60)
        print(f"\nError: {str(e)}\n")
        
        # Helpful error messages
        if "OPENAI_API_KEY" in str(e):
            print("⚠️  Missing OpenAI API Key")
            print("   Add to .env file: OPENAI_API_KEY=your_key_here\n")
        elif "PUSHOVER" in str(e):
            print("⚠️  Missing Pushover Credentials")
            print("   Add to .env file:")
            print("   PUSHOVER_USER_KEY=your_user_key")
            print("   PUSHOVER_API_TOKEN=your_api_token\n")
        else:
            print("💡 Troubleshooting:")
            print("   1. Check .env file has all API keys")
            print("   2. Verify internet connection")
            print("   3. Test with: python test_notification.py\n")
        
        print("="*60)
        exit(1)


if __name__ == "__main__":
    main()
