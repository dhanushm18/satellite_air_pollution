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

**Web UI (Flask)**
```bash
python app.py
```
Then open http://localhost:5000

**Command Line**
```bash
python run_agents.py --city "Bengaluru"
```

---

## ✨ Features

### 🤖 **4 Autonomous AI Agents**
- **🛰️ Data Scout** - Fetches satellite data from Google Earth Engine
- **🔬 Analyst** - Analyzes NO₂ levels and categorizes air quality
- **📄 Reporter** - Generates professional PDF reports
- **📱 Alert Manager** - Sends instant Pushover & Email notifications

### 📱 **Real-Time Notifications**
- Instant alerts to your phone via Pushover
- Email notifications with detailed analysis
- Priority-based (silent → emergency siren)

### 📄 **Government Reports**
- **Regulatory Compliance Report** - CPCB & WHO standards
- **Prevention Guide** - Strategies for individuals, communities, businesses, government

---

## 📂 Project Structure

```
agentic_air_quality/
├── app.py                     # Flask web application
├── run_agents.py              # CLI interface
├── requirements.txt           # Dependencies
├── .env                       # API credentials
├── templates/                 # HTML templates
├── static/                    # CSS, JS, Images
│
└── src/
    ├── agents/
    │   ├── agents.py          # 4 AI agents
    │   └── tools.py           # Agent tools
    └── core/
        ├── notifications.py   # Notification service
        └── report_generator.py # PDF generation
```

---

## 🎯 Usage

### Web UI
1. Launch: `python app.py`
2. Open http://localhost:5000
3. Enter city name and date
4. Click "Launch Monitoring System"
5. View real-time progress and download reports

### Command Line
```bash
# Basic usage
python run_agents.py --city "Bengaluru"

# Specific date range
python run_agents.py --city "Delhi" --start-date "2025-11-20" --end-date "2025-11-21"
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
- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Notifications:** Pushover API, SMTP (Email)
- **Reports:** ReportLab (PDF)

---

## 💰 Cost

- **Pushover:** $5 one-time (after 30-day trial)
- **OpenAI API:** ~$0.01-0.05 per run
- **Google Earth Engine:** Free for research
- **Monthly:** ~$3-20

---

## 🧪 Testing

```bash
# Test CLI
python run_agents.py --city "Bengaluru"

# Test Web UI
python app.py
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
