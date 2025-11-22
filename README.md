# 🤖 Agentic Air Quality Monitor

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-purple.svg)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Autonomous AI agents for air quality monitoring with real-time alerts and government-compliant reporting.**

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```bash
# Pushover (for notifications)
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_API_TOKEN=your_pushover_api_token

# OpenAI (for AI agents)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o-mini

# Google Earth Engine
EE_PROJECT_ID=your_ee_project_id
```

### 3. Run the Application

**Option A: Web UI**
```bash
streamlit run main.py
```
Then open http://localhost:8501

**Option B: Command Line**
```bash
python run_agents.py --city "Bengaluru"
```

---

## ✨ Features

### 🤖 **4 Autonomous AI Agents**
- **🛰️ Data Scout** - Fetches satellite data from Google Earth Engine
- **🔬 Analyst** - Analyzes NO₂ levels and categorizes air quality
- **📄 Reporter** - Generates professional PDF reports
- **📱 Alert Manager** - Sends instant Pushover notifications

### 📱 **Real-Time Notifications**
- Instant alerts to your phone via Pushover
- Priority-based (silent → emergency siren)
- Daily summaries for multiple cities

### 📄 **Government Reports**
- **Regulatory Compliance Report** - CPCB & WHO standards
- **Prevention Guide** - Strategies for individuals, communities, businesses, government

---

## 📂 Project Structure

```
agentic_air_quality/
├── main.py                    # Streamlit web UI
├── run_agents.py              # CLI interface
├── test_notification.py       # Test Pushover
├── requirements.txt           # Dependencies
├── .env                       # API credentials
│
└── src/
    ├── agents/
    │   ├── agents.py          # 4 AI agents
    │   └── tools.py           # Agent tools
    └── core/
        ├── notifications.py   # Pushover service
        └── report_generator.py # PDF generation
```

---

## 🎯 Usage

### Web UI
1. Launch: `streamlit run main.py`
2. Enter city name and date
3. Click "🚀 START AGENT MISSION"
4. View results and check your phone for notification

### Command Line
```bash
# Basic usage
python run_agents.py --city "Bengaluru"

# Specific date range
python run_agents.py --city "Delhi" --start-date "2025-11-20" --end-date "2025-11-21"

# Without notifications
python run_agents.py --city "Mumbai" --no-alerts

# Without reports
python run_agents.py --city "Chennai" --no-reports
```

---

## 📱 Notification Example

```
🔴 Air Quality Alert for Bengaluru

NO₂ Level: 95.5 µg/m³
Category: Poor
Date: 2025-11-21

Health Advisory:
🚫 Limit outdoor activities.
Children and elderly should stay indoors.
```

---

## 📊 Air Quality Categories

| NO₂ (µg/m³) | Category | Notification |
|-------------|----------|--------------|
| 0-40 | Good | 🟢 Silent |
| 40-80 | Moderate | 🟡 Normal |
| 80-180 | Poor | 🟠 Persistent |
| 180-280 | Very Poor | 🔴 High Priority |
| >280 | Severe | 🚨 Emergency |

---

## 🛠️ Technologies

- **AI Framework:** CrewAI, LangChain, OpenAI GPT-4
- **Satellite Data:** Google Earth Engine, Sentinel-5P
- **Notifications:** Pushover API
- **Reports:** ReportLab (PDF)
- **UI:** Streamlit

---

## 💰 Cost

- **Pushover:** $5 one-time (after 30-day trial)
- **OpenAI API:** ~$0.01-0.05 per run
- **Google Earth Engine:** Free for research
- **Monthly:** ~$3-20

---

## 🧪 Testing

```bash
# Test Pushover notifications
python test_notification.py

# Test CLI
python run_agents.py --city "Bengaluru"

# Test Web UI
streamlit run main.py
```

---

## 📚 Documentation

- **START_HERE.md** - Complete user guide
- **AGENTIC_ROADMAP.md** - Future enhancements

---

## 🎓 Example Workflows

### Daily Monitoring
```python
from src.agents.agents import run_satellite_crew

run_satellite_crew(
    city="Delhi",
    start_date="2025-11-20",
    end_date="2025-11-21",
    send_alerts=True,
    generate_reports=False
)
```

### Weekly Reports
```python
run_satellite_crew(
    city="Bengaluru",
    start_date="2025-11-14",
    end_date="2025-11-21",
    send_alerts=False,
    generate_reports=True
)
```

---

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Copernicus Sentinel-5P** - Satellite NO₂ data
- **Google Earth Engine** - Geospatial platform
- **CrewAI** - Multi-agent framework
- **Pushover** - Notification service

---

## 🚀 Getting Started Checklist

- [ ] Install dependencies: `uv pip install -r requirements.txt`
- [ ] Create `.env` from `.env.example`
- [ ] Add Pushover credentials
- [ ] Add OpenAI API key
- [ ] Test: `python test_notification.py`
- [ ] Run: `streamlit run main.py` or `python run_agents.py --city "Bengaluru"`

---

**🌍 Built for cleaner air and healthier communities**
