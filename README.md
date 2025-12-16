# Security Metrics Dashboard: Python + SQL for Infosec

<img width="1913" height="1004" alt="image" src="https://github.com/user-attachments/assets/2ffa4602-e519-4527-a04e-10b42a2721e4" />  


## 📊 Project Overview

**What is this?**
This project demonstrates practical Python and SQL skills for security professionals. It uses 3 example spreadsheets that simulate real daily routines of security professionals (incidents, vulnerabilities, phishing campaigns) and then uses Python and SQL to create an executive dashboard.

**Why it matters:**
Shows how to automate security reporting by combining Python's data processing with SQL's querying power - replacing manual Excel work with reproducible code.

## 🚀 Quick Start

### **Step 1: Get the files**
```bash
# Download the project files
git clone https://github.com/ThiagoMaria-SecurityIT/security-dashboard-Python-SQL.git
cd security-dashboard
```

### **Step 2: Set up Python environment**
```bash
# Create virtual environment (keeps packages organized)
python -m venv venv

# Activate it:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### **Step 3: Install what you need**

Install: `pip install -r requirements.txt`  

or   

```bash
pip install pandas matplotlib seaborn openpyxl
```

### **Step 4: Run it!**
```bash
# Make sure these 3 files are in the folder:
# 1. incident_trend_dashboard.csv
# 2. vulnerability_hotspots.csv  
# 3. phishing_campaign_roi.csv

python security_dashboard_loader.py
```

## 📁 What's in the Project

**Data Files (Simulated Real Security Data):**
- `incident_trend_dashboard.csv` - 50 security incidents from a port company
- `vulnerability_hotspots.csv` - Vulnerability scan results  
- `phishing_campaign_roi.csv` - Phishing test campaigns and results

**Code File:**
- `security_dashboard_loader.py` - Main script that does everything

## 🖼️ What You Get

After running the script, you'll get:

1. **`security_dashboard_latest.png`** - Professional 7-chart dashboard
2. **`dashboard_query_results.xlsx`** - All the data in Excel
3. **`security_analysis.db`** - SQLite database for your own queries

**Dashboard shows:**
- Incident response times (MTTR) over months
- Most common attack types (pie chart)
- Departments with most vulnerabilities (bar chart)  
- Phishing click rate trends
- Vulnerability aging heatmap
- Executive summary with recommendations

## 🔧 How It Works: The Python + SQL Magic

The project demonstrates this workflow:
```
CSV Files → Python loads → SQL Database → SQL Queries → Python Charts
```

**Simple example from the code:**
```python
# Python loads CSV
import pandas as pd
data = pd.read_csv('incidents.csv')

# Python sends to SQL database  
data.to_sql('incidents', database_connection)

# SQL queries the data, Python makes charts
results = pd.read_sql_query("""
    SELECT month, COUNT(*) as incidents 
    FROM incidents 
    GROUP BY month
""", database_connection)

results.plot(kind='bar')  # Python visualization
```

## 📚 Learning Points

**For Security Professionals:**
- Automate your monthly security reports
- Show trends to management with clear visuals  
- Track if security improvements are working

**For Python/SQL Learners:**
- See how SQL queries filter data before visualization
- Learn pandas for data processing
- Create professional charts with matplotlib
- Build a complete project from data to dashboard

## 💡 Use Your Own Data

Want to try with real security data?

1. Export your incident/vulnerability/phishing data to CSV
2. Replace the 3 example CSV files (keep similar column names)
3. Run the same script - it works with your data!

## ❓ Common Issues

| Problem | Fix |
|---------|-----|
| "Module not found" | Run `pip install pandas matplotlib seaborn openpyxl` |
| CSV files missing | Download all 3 CSV files to same folder |
| Dashboard looks wrong | Make sure all 3 CSV files are in correct format |

## 🤖 AI Development Transparency  

This project was developed through an **AI-human collaborative process** using DeepSeek as a coding assistant. The workflow illustrates how modern security professionals can leverage AI tools effectively:

**Development Approach:**
- **Human Direction**: Security domain expertise, project requirements, and strategic oversight
- **AI Assistance**: Code generation, syntax suggestions, and implementation details
- **Collaborative Review**: Iterative refinement with human validation at each stage

**Transparency Points:**
1. The core concept, security metrics, and dashboard requirements were human-defined
2. AI assisted with Python/SQL implementation, code optimization, and error handling
3. All generated code was reviewed, tested, and validated for security best practices
4. The final solution represents a synthesis of human expertise and AI productivity tools

**Why This Matters:** This project serves as a case study in **responsible AI-assisted development** - demonstrating how security professionals can maintain oversight while benefiting from AI coding assistance.

## 📄 License

MIT License - free to use, modify, and share.

---

*This project shows real-world Python+SQL skills - for my Python and SQL portfolio, data analysis, and automating security reports!*

---

## About Me & Contact

**Thiago Maria - From Brazil to the World 🌎**  
*Senior Information Security Professional | Security Risk & Compliance Specialist | AI Security Researcher | Software Developer | Post-Quantum Cryptography Enthusiast*

My passion for programming and my professional background in security analysis led me to create this GitHub account to share my knowledge of security information, cybersecurity, Python, and AI development practices. My work primarily focuses on prioritizing security in organizations while ensuring usability and productivity.

**Core Philosophy:** I believe in **transparent AI collaboration** - using artificial intelligence as a tool to enhance human expertise, not replace it. This project exemplifies how security professionals can maintain full oversight while leveraging AI for technical implementation.

Let's Connect:  

👇🏽 Click on the badges below:  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/thiago-cequeira-99202239/)  
[![Hugging Face](https://img.shields.io/badge/🤗Hugging_Face-AI_projects-yellow)](https://huggingface.co/ThiSecur)

