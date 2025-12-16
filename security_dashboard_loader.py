"""
================================================================================
SECURITY METRICS DASHBOARD LOADER
================================================================================
This script:
1. LOADS your existing CSV files (incidents, vulnerabilities, phishing)
2. PROCESSES and validates the data
3. CREATES a professional dashboard with 6 main charts + 3 mini-charts
4. SAVES results for sharing
================================================================================
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# =============================================================================
# 1. CONFIGURATION & DATA LOADING
# =============================================================================
print("🔐 SECURITY DASHBOARD - DATA LOADER & VISUALIZER")
print("=" * 60)

# Define your CSV file names
CSV_FILES = {
    'incidents': 'incident_trend_dashboard.csv',
    'vulnerabilities': 'vulnerability_hotspots.csv', 
    'phishing': 'phishing_campaign_roi.csv'
}

# Check if files exist
missing_files = []
for file_type, filename in CSV_FILES.items():
    if not os.path.exists(filename):
        missing_files.append(filename)

if missing_files:
    print(f"❌ ERROR: Missing CSV file(s): {', '.join(missing_files)}")
    print("Please ensure these files are in the same directory as this script.")
    exit(1)

# Load all CSV files
print("\n📥 LOADING CSV FILES...")
try:
    incidents_df = pd.read_csv(CSV_FILES['incidents'])
    vulnerabilities_df = pd.read_csv(CSV_FILES['vulnerabilities'])
    phishing_df = pd.read_csv(CSV_FILES['phishing'])
    
    print(f"   ✓ Loaded '{CSV_FILES['incidents']}': {len(incidents_df)} incident records")
    print(f"   ✓ Loaded '{CSV_FILES['vulnerabilities']}': {len(vulnerabilities_df)} vulnerability records")
    print(f"   ✓ Loaded '{CSV_FILES['phishing']}': {len(phishing_df)} phishing campaign records")
    
except Exception as e:
    print(f"❌ ERROR loading CSV files: {e}")
    exit(1)

# =============================================================================
# 2. DATA VALIDATION & PREPROCESSING
# =============================================================================
print("\n⚙️  VALIDATING & PREPARING DATA...")

# Ensure date columns are datetime format
date_columns = {
    'incidents': ['Date_Reported', 'Date_Resolved'],
    'vulnerabilities': ['First_Detected'],
    'phishing': ['Launch_Date', 'Follow_up_Date']
}

for df_name, df in [('incidents', incidents_df), ('vulnerabilities', vulnerabilities_df), ('phishing', phishing_df)]:
    for col in date_columns.get(df_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

# Calculate derived metrics
if 'Response_Time_Min' in incidents_df.columns:
    incidents_df['Response_Time_Hours'] = incidents_df['Response_Time_Min'] / 60

if 'Click_Rate' in phishing_df.columns:
    phishing_df['Click_Rate_Percent'] = phishing_df['Click_Rate'].str.rstrip('%').astype(float)

print("   ✓ Data validation complete")

# =============================================================================
# 3. CREATE SQLITE DATABASE FOR ADVANCED QUERIES
# =============================================================================
print("\n💾 CREATING ANALYSIS DATABASE...")

DB_NAME = 'security_analysis.db'
conn = sqlite3.connect(DB_NAME)

# Load DataFrames into database
incidents_df.to_sql('incidents', conn, if_exists='replace', index=False)
vulnerabilities_df.to_sql('vulnerabilities', conn, if_exists='replace', index=False)
phishing_df.to_sql('phishing_campaigns', conn, if_exists='replace', index=False)

print(f"   ✓ Database '{DB_NAME}' created with 3 tables")

# =============================================================================
# 4. EXECUTE DASHBOARD QUERIES
# =============================================================================
print("\n📊 EXECUTING DASHBOARD QUERIES...")

# Query 1: MTTR Trend by Month
mttr_query = """
SELECT 
    strftime('%Y-%m', Date_Reported) as Month,
    COUNT(*) as Total_Incidents,
    SUM(CASE WHEN Severity = 'Critical' THEN 1 ELSE 0 END) as Critical_Incidents,
    ROUND(AVG(Response_Time_Min) / 60.0, 1) as Avg_Response_Hours
FROM incidents 
WHERE Status = 'Resolved' AND Response_Time_Min IS NOT NULL
GROUP BY Month 
ORDER BY Month;
"""
mttr_df = pd.read_sql_query(mttr_query, conn)

# Query 2: Top Incident Types
incident_type_query = """
SELECT 
    Incident_Type,
    COUNT(*) as Count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM incidents), 1) as Percentage
FROM incidents 
GROUP BY Incident_Type 
ORDER BY Count DESC
LIMIT 6;
"""
incident_type_df = pd.read_sql_query(incident_type_query, conn)

# Query 3: Vulnerability Hotspots
vuln_hotspot_query = """
SELECT 
    Department,
    COUNT(*) as Total_Vulnerabilities,
    SUM(CASE WHEN Severity = 'Critical' THEN 1 ELSE 0 END) as Critical_Count,
    ROUND(AVG(Days_Open), 1) as Avg_Days_Open
FROM vulnerabilities 
WHERE Solution_Status = 'Open'
GROUP BY Department 
ORDER BY Critical_Count DESC
LIMIT 5;
"""
vuln_hotspot_df = pd.read_sql_query(vuln_hotspot_query, conn)

# Query 4: Phishing Trend
phishing_trend_query = """
SELECT 
    Launch_Date,
    Campaign_Name,
    Department,
    CAST(REPLACE(Click_Rate, '%', '') AS FLOAT) as Click_Rate_Percent
FROM phishing_campaigns 
ORDER BY Launch_Date;
"""
phishing_trend_df = pd.read_sql_query(phishing_trend_query, conn)
phishing_trend_df['Launch_Date'] = pd.to_datetime(phishing_trend_df['Launch_Date'])

# Query 5: Incident Severity
severity_query = "SELECT Severity, COUNT(*) as Count FROM incidents GROUP BY Severity"
severity_df = pd.read_sql_query(severity_query, conn)

# Query 6: Vulnerability Aging
vuln_age_query = """
SELECT 
    Department,
    CASE 
        WHEN Days_Open < 30 THEN '< 30 days'
        WHEN Days_Open BETWEEN 30 AND 90 THEN '30-90 days'
        WHEN Days_Open BETWEEN 91 AND 180 THEN '91-180 days'
        ELSE '> 180 days'
    END as Age_Group,
    COUNT(*) as Count
FROM vulnerabilities 
WHERE Solution_Status = 'Open'
GROUP BY Department, Age_Group
HAVING COUNT(*) > 0
ORDER BY Department, 
    CASE Age_Group
        WHEN '< 30 days' THEN 1
        WHEN '30-90 days' THEN 2
        WHEN '91-180 days' THEN 3
        ELSE 4
    END;
"""
vuln_age_df = pd.read_sql_query(vuln_age_query, conn)
vuln_age_pivot = vuln_age_df.pivot(index='Department', columns='Age_Group', values='Count').fillna(0)

# Query 7: Top Vulnerability Types for mini-chart
vuln_type_query = """
SELECT 
    Vulnerability_Title,
    COUNT(*) as Count
FROM vulnerabilities 
WHERE Solution_Status = 'Open'
GROUP BY Vulnerability_Title
ORDER BY Count DESC
LIMIT 5;
"""
vuln_type_df = pd.read_sql_query(vuln_type_query, conn)
vuln_type_df['Short_Title'] = vuln_type_df['Vulnerability_Title'].str[:25] + '...'

# Query 8: Vulnerability Status
status_query = """
SELECT 
    Solution_Status,
    COUNT(*) as Count
FROM vulnerabilities 
GROUP BY Solution_Status;
"""
status_df = pd.read_sql_query(status_query, conn)

# Query 9: Critical Vulnerabilities by Department
critical_vuln_query = """
SELECT 
    Department,
    COUNT(*) as Critical_Count
FROM vulnerabilities 
WHERE Severity = 'Critical' AND Solution_Status = 'Open'
GROUP BY Department
ORDER BY Critical_Count DESC
LIMIT 5;
"""
critical_df = pd.read_sql_query(critical_vuln_query, conn)

conn.close()
print("   ✓ 9 dashboard queries executed successfully")

# =============================================================================
# 5. CREATE VISUAL DASHBOARD (COMPACT VERSION)
# =============================================================================
print("\n🎨 CREATING COMPACT VISUAL DASHBOARD...")

# Set up a more compact dashboard
plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(16, 9))  # More reasonable size
fig.suptitle('SECURITY METRICS DASHBOARD', fontsize=15, fontweight='bold', y=0.98)

# Create a 3x3 grid layout with tighter spacing
gs = GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.2, height_ratios=[1, 1, 0.8])

# ========== CHART 1: MTTR TREND (Top-left) ==========
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(mttr_df['Month'], mttr_df['Avg_Response_Hours'], 
         marker='o', linewidth=2, markersize=5, color='#2E86AB')
ax1.fill_between(mttr_df['Month'], mttr_df['Avg_Response_Hours'], alpha=0.2, color='#2E86AB')
ax1.set_title('MTTR Trend', fontsize=12, fontweight='bold', pad=8)
ax1.set_ylabel('Hours', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='x', rotation=45, labelsize=9)


# ========== CHART 2: INCIDENT TYPE PIE (Top-center) ==========
ax2 = fig.add_subplot(gs[0, 1])
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
wedges, texts, autotexts = ax2.pie(incident_type_df['Count'], 
                                   labels=None,  # Remove labels from chart
                                   autopct='%1.0f%%',  # Just percentages, no decimals
                                   colors=colors,
                                   startangle=90,
                                   textprops={'fontsize': 8})
ax2.set_title('Incident Types', fontsize=12, fontweight='bold', pad=8)
# Add legend instead of chart labels
ax2.legend(wedges, incident_type_df['Incident_Type'], 
           title="Types", fontsize=7, title_fontsize=8, 
           loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# ========== CHART 3: VULNERABILITY HOTSPOTS (Top-right) ==========
ax3 = fig.add_subplot(gs[0, 2])
departments = vuln_hotspot_df['Department']
vuln_counts = vuln_hotspot_df['Total_Vulnerabilities']
critical_counts = vuln_hotspot_df['Critical_Count']
bar_width = 0.3  # Narrower bars
index = range(len(departments))
bars1 = ax3.bar(index, vuln_counts, bar_width, label='Total', color='#FECA57', alpha=0.8)
bars2 = ax3.bar([i + bar_width for i in index], critical_counts, bar_width, 
                label='Critical', color='#FF6B6B', alpha=0.8)
ax3.set_title('Vuln Hotspots', fontsize=12, fontweight='bold', pad=8)
ax3.set_xlabel('Department', fontsize=9)
ax3.set_ylabel('Count', fontsize=9)
ax3.set_xticks([i + bar_width / 2 for i in index])
ax3.set_xticklabels([dept[:10] + '...' if len(dept) > 10 else dept for dept in departments], 
                   rotation=45, ha='right', fontsize=8)
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3, axis='y')
# Remove value labels to reduce clutter

# ========== CHART 4: PHISHING TREND (Middle-left) ==========
ax4 = fig.add_subplot(gs[1, 0])
ax4.plot(phishing_trend_df['Launch_Date'], phishing_trend_df['Click_Rate_Percent'], 
         marker='s', linewidth=1.5, markersize=4, color='#10AC84')
ax4.set_title('Phishing Click Rate', fontsize=12, fontweight='bold', pad=8)
ax4.set_ylabel('Click Rate (%)', fontsize=9)
ax4.set_xlabel('Date', fontsize=9)
ax4.grid(True, alpha=0.3)
ax4.tick_params(axis='x', rotation=45, labelsize=8)
# Add simplified trend line without label
if len(phishing_trend_df) > 1:
    z = np.polyfit(range(len(phishing_trend_df)), phishing_trend_df['Click_Rate_Percent'], 1)
    p = np.poly1d(z)
    ax4.plot(phishing_trend_df['Launch_Date'], p(range(len(phishing_trend_df))), 
             "r--", alpha=0.7, linewidth=1)

# ========== CHART 5: SEVERITY DONUT (Middle-center) ==========
ax5 = fig.add_subplot(gs[1, 1])
severity_colors = {'Critical': '#FF3838', 'High': '#FF9F1A', 'Medium': '#FFE156', 'Low': '#17C37B'}
wedges, texts, autotexts = ax5.pie(severity_df['Count'], 
                                   labels=severity_df['Severity'],
                                   autopct='%1.0f%%',
                                   colors=[severity_colors.get(s, '#999999') for s in severity_df['Severity']],
                                   startangle=90,
                                   wedgeprops=dict(width=0.3, edgecolor='w'),
                                   textprops={'fontsize': 8})
ax5.set_title('Incident Severity', fontsize=12, fontweight='bold', pad=8)

# ========== CHART 6: VULNERABILITY AGING HEATMAP (Middle-right) ==========
ax6 = fig.add_subplot(gs[1, 2])
if not vuln_age_pivot.empty:
    im = ax6.imshow(vuln_age_pivot, cmap='YlOrRd', aspect='auto')
    ax6.set_title('Vuln Aging', fontsize=12, fontweight='bold', pad=8)
    ax6.set_xlabel('Days Open', fontsize=9)
    ax6.set_ylabel('Department', fontsize=9)
    ax6.set_xticks(range(len(vuln_age_pivot.columns)))
    ax6.set_xticklabels(vuln_age_pivot.columns, rotation=45, ha='right', fontsize=8)
    ax6.set_yticks(range(len(vuln_age_pivot.index)))
    ax6.set_yticklabels([dept[:8] + '...' if len(dept) > 8 else dept for dept in vuln_age_pivot.index], 
                       fontsize=8)
    # Only show text for values > threshold
    for i in range(len(vuln_age_pivot.index)):
        for j in range(len(vuln_age_pivot.columns)):
            value = vuln_age_pivot.iloc[i, j]
            if value > 2:  # Only label significant values
                ax6.text(j, i, int(value), ha='center', va='center', 
                        color='black' if value < vuln_age_pivot.values.max()/2 else 'white',
                        fontsize=7, fontweight='bold')
    plt.colorbar(im, ax=ax6, label='Count')
else:
    ax6.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=10)
    ax6.set_title('Vuln Aging', fontsize=12, fontweight='bold', pad=8)
    ax6.axis('off')

# ========== MINI-CHARTS GRID (Bottom - Full width) ==========
ax7 = fig.add_subplot(gs[2, :])
gs_inner = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[2, :], wspace=0.25)

# Subchart 7a: Top Vulnerability Types
ax7a = fig.add_subplot(gs_inner[0, 0])
if not vuln_type_df.empty:
    bars = ax7a.barh(range(len(vuln_type_df)), vuln_type_df['Count'], color='#FF6B6B', height=0.6)
    ax7a.set_title('Top Vuln Types', fontsize=10, fontweight='bold', pad=6)
    ax7a.set_yticks(range(len(vuln_type_df)))
    # Truncate long titles more aggressively
    short_titles = [title[:15] + '...' if len(title) > 15 else title 
                    for title in vuln_type_df['Short_Title']]
    ax7a.set_yticklabels(short_titles, fontsize=7)
    ax7a.invert_yaxis()
    ax7a.set_xlabel('Count', fontsize=8)
else:
    ax7a.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=9)
    ax7a.set_title('Top Vuln Types', fontsize=10, fontweight='bold', pad=6)
    ax7a.axis('off')

# Subchart 7b: Vulnerability Status Breakdown
ax7b = fig.add_subplot(gs_inner[0, 1])
status_colors = ['#FF6B6B' if status == 'Open' else '#4ECDC4' for status in status_df['Solution_Status']]
wedges, texts, autotexts = ax7b.pie(status_df['Count'], labels=status_df['Solution_Status'], 
         colors=status_colors, autopct='%1.0f%%', startangle=90, 
         textprops={'fontsize': 7})
ax7b.set_title('Vuln Status', fontsize=10, fontweight='bold', pad=6)

# Subchart 7c: Critical Vulnerabilities by Department
ax7c = fig.add_subplot(gs_inner[0, 2])
if not critical_df.empty and critical_df['Critical_Count'].sum() > 0:
    bars = ax7c.bar(range(len(critical_df)), critical_df['Critical_Count'], 
                    color='#FF3838', width=0.5)
    ax7c.set_title('Critical Vulns', fontsize=10, fontweight='bold', pad=6)
    ax7c.set_xlabel('Dept', fontsize=8)
    ax7c.set_ylabel('Count', fontsize=8)
    ax7c.set_xticks(range(len(critical_df)))
    # Truncate department names
    short_depts = [dept[:8] + '...' if len(dept) > 8 else dept 
                   for dept in critical_df['Department']]
    ax7c.set_xticklabels(short_depts, rotation=45, fontsize=7, ha='right')
else:
    ax7c.text(0.5, 0.5, 'No critical', ha='center', va='center', fontsize=8)
    ax7c.set_title('Critical Vulns', fontsize=10, fontweight='bold', pad=6)
    ax7c.axis('off')

plt.tight_layout(rect=[0, 0.02, 1, 0.96])

# =============================================================================
# 6. FINALIZE & SAVE DASHBOARD
# =============================================================================
plt.tight_layout(rect=[0, 0.02, 1, 0.96])

# Save dashboard
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
dashboard_filename = f'security_dashboard_{timestamp}.png'
plt.savefig(dashboard_filename, dpi=150, bbox_inches='tight')
plt.savefig('security_dashboard_latest.png', dpi=150, bbox_inches='tight')

print(f"   ✓ Dashboard saved as '{dashboard_filename}'")
print(f"   ✓ Also saved as 'security_dashboard_latest.png' for easy access")

# Display dashboard
plt.show()

# =============================================================================
# 7. SAVE QUERY RESULTS FOR FURTHER ANALYSIS
# =============================================================================
print("\n💾 SAVING QUERY RESULTS FOR REPORTING...")

# Create an Excel file with all query results
with pd.ExcelWriter('dashboard_query_results.xlsx', engine='openpyxl') as writer:
    mttr_df.to_excel(writer, sheet_name='MTTR_Trend', index=False)
    incident_type_df.to_excel(writer, sheet_name='Incident_Types', index=False)
    vuln_hotspot_df.to_excel(writer, sheet_name='Vuln_Hotspots', index=False)
    phishing_trend_df.to_excel(writer, sheet_name='Phishing_Trend', index=False)
    severity_df.to_excel(writer, sheet_name='Severity_Distribution', index=False)
    vuln_age_df.to_excel(writer, sheet_name='Vuln_Aging', index=False)
    vuln_type_df.to_excel(writer, sheet_name='Top_Vuln_Types', index=False)
    status_df.to_excel(writer, sheet_name='Vuln_Status', index=False)
    critical_df.to_excel(writer, sheet_name='Critical_Vulns', index=False)

print("   ✓ Query results saved to 'dashboard_query_results.xlsx'")

# =============================================================================
# 8. FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("✅ DASHBOARD GENERATION COMPLETE!")
print("=" * 60)
print("\n📋 OUTPUT FILES CREATED:")
print(f"   1. 📊 Dashboard Image:     '{dashboard_filename}'")
print(f"   2. 📊 Latest Dashboard:    'security_dashboard_latest.png'")
print(f"   3. 📈 Analysis Database:   '{DB_NAME}' (SQLite)")
print(f"   4. 📑 Query Results:      'dashboard_query_results.xlsx'")

print("\n📊 DASHBOARD CONTAINS 9 VISUALIZATIONS:")
print("   • 🔧 MTTR Trend Line Chart")
print("   • 🍕 Incident Type Pie Chart")
print("   • 🗼 Vulnerability Hotspots Bar Chart")
print("   • 📉 Phishing Trend Line Chart")
print("   • 🍩 Severity Distribution Donut Chart")
print("   • 🔥 Vulnerability Aging Heatmap")
print("   • 🔓 Top Vulnerability Types (horizontal bars)")
print("   • 📋 Vulnerability Status (pie chart)")
print("   • 💥 Critical Vulnerabilities by Department")

print("\n🔄 TO UPDATE DASHBOARD WITH NEW DATA:")
print("   1. Replace CSV files with updated data")
print("   2. Run this script again: python security_dashboard_loader.py")
print("   3. New dashboard with timestamp will be generated")

print("\n🎯 PRESENTATION READY:")
print("   • Use 'security_dashboard_latest.png' for C-suite presentations")
print("   • Use 'dashboard_query_results.xlsx' for detailed analysis")
print("   • Schedule weekly runs for automated reporting")
