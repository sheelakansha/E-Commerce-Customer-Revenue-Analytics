import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Setup output directory
os.makedirs('results', exist_ok=True)

# DB connection configuration for MySQL
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'ecommerce_analytics'),
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}

def get_connection():
    try:
        import pymysql
        return pymysql.connect(**DB_CONFIG)
    except Exception:
        import mysql.connector
        return mysql.connector.connect(**DB_CONFIG)

conn = get_connection()

# List of queries
query_files = [
    '01_monthly_revenue_growth.sql',
    '02_cohort_retention.sql',
    '03_rfm_customer_segmentation.sql',
    '04_customer_lifetime_value.sql',
    '05_product_category_performance.sql',
    '06_repeat_purchase_analysis.sql',
    '07_segment_purchase_behavior.sql',
    '08_discount_revenue_analysis.sql'
]

dataframes = {}

print("--- Running MySQL Queries and Saving CSVs ---")
for qfile in query_files:
    filepath = os.path.join('queries', qfile)
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    df = pd.read_sql_query(sql, conn)
    csv_name = qfile.replace('.sql', '.csv')
    csv_path = os.path.join('results', csv_name)
    df.to_csv(csv_path, index=False)
    dataframes[qfile] = df
    print(f"Saved {csv_path} ({len(df)} rows)")

# Additional Pareto & Median calculations directly from DB
# 1. Top 20% customer revenue share
pareto_sql = """
WITH cust_rev AS (
    SELECT c.customer_id, SUM(p.payment_amount) as total_rev
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN payments p ON p.order_id = o.order_id
    WHERE o.order_status = 'Completed' AND p.payment_status = 'Paid'
    GROUP BY c.customer_id
),
ranked AS (
    SELECT total_rev,
           NTILE(5) OVER (ORDER BY total_rev DESC) as quintile
    FROM cust_rev
)
SELECT 
    quintile,
    COUNT(*) as cust_count,
    SUM(total_rev) as total_rev,
    ROUND(100.0 * SUM(total_rev) / (SELECT SUM(total_rev) FROM cust_rev), 2) as rev_pct
FROM ranked
GROUP BY quintile ORDER BY quintile;
"""
df_pareto = pd.read_sql_query(pareto_sql, conn)
top_20_rev_pct = df_pareto[df_pareto['quintile'] == 1]['rev_pct'].values[0]

# 2. Median days to second purchase
median_days_sql = """
WITH purchases AS (
    SELECT customer_id, order_date,
           ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date, order_id) AS purchase_number
    FROM orders WHERE order_status='Completed'
),
first_second AS (
    SELECT customer_id,
           MIN(CASE WHEN purchase_number=1 THEN order_date END) AS first_date,
           MIN(CASE WHEN purchase_number=2 THEN order_date END) AS second_date
    FROM purchases GROUP BY customer_id
)
SELECT DATEDIFF(second_date, first_date) as days_diff
FROM first_second WHERE second_date IS NOT NULL;
"""
df_median = pd.read_sql_query(median_days_sql, conn)
median_days = float(df_median['days_diff'].median())

# 3. RFM Tier Revenue Share & At-Risk Revenue
df_rfm = dataframes['03_rfm_customer_segmentation.sql']
rfm_tier_summary = df_rfm.groupby('customer_tier').agg(
    customer_count=('customer_id', 'count'),
    total_revenue=('monetary', 'sum')
).reset_index()
total_rfm_rev = rfm_tier_summary['total_revenue'].sum()
rfm_tier_summary['rev_share_pct'] = (100.0 * rfm_tier_summary['total_revenue'] / total_rfm_rev).round(2)

at_risk_row = rfm_tier_summary[rfm_tier_summary['customer_tier'] == 'At-Risk High-Value']
at_risk_rev_pct = at_risk_row['rev_share_pct'].values[0] if len(at_risk_row) > 0 else 0
at_risk_count = at_risk_row['customer_count'].values[0] if len(at_risk_row) > 0 else 0

# 4. Cohort Month-3 Retention %
df_cohort = dataframes['02_cohort_retention.sql']
m3_retention = df_cohort[df_cohort['month_number'] == 3]['retention_pct'].mean().round(2)

# 5. Discounted vs Non-Discounted AOV
df_disc = dataframes['08_discount_revenue_analysis.sql']
disc_summary = df_disc.groupby('order_type').agg(
    total_orders=('orders', 'sum'),
    avg_net_aov=('avg_net_order_value', 'mean'),
    avg_gross_aov=('avg_gross_order_value', 'mean'),
    avg_discount=('avg_discount', 'mean')
).reset_index()

disc_row = disc_summary[disc_summary['order_type'] == 'Discounted']
disc_aov = disc_row['avg_net_aov'].values[0] if len(disc_row) > 0 else 0
disc_gross = disc_row['avg_gross_aov'].values[0] if len(disc_row) > 0 else 0
avg_disc_amt = disc_row['avg_discount'].values[0] if len(disc_row) > 0 else 0
nondisc_row = disc_summary[disc_summary['order_type'] == 'Non-discounted']
nondisc_aov = nondisc_row['avg_net_aov'].values[0] if len(nondisc_row) > 0 else disc_gross

# 6. Repeat purchase rate
df_repeat = dataframes['06_repeat_purchase_analysis.sql']
repeat_rate = df_repeat['repeat_purchase_rate_pct'].values[0]
avg_days_to_2nd = df_repeat['avg_days_to_second_purchase'].values[0]

print("\n--- INSIGHTS METRICS ---")
print(f"Top 20% Customers Revenue Share: {top_20_rev_pct}%")
print(f"Median Days to 2nd Purchase: {median_days} days")
print(f"Average Days to 2nd Purchase: {avg_days_to_2nd} days")
print(f"Repeat Purchase Rate: {repeat_rate}%")
print(f"Month-3 Average Cohort Retention: {m3_retention}%")
print(f"Discounted AOV: ${disc_aov:.2f} vs Non-Discounted AOV: ${nondisc_aov:.2f}")
print(f"At-Risk High-Value Customers Revenue Share: {at_risk_rev_pct}% ({at_risk_count} customers)")

# Set aesthetic styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'Helvetica', 'font.family': 'sans-serif'})

# Chart 1: Monthly Revenue Trend
df_m = dataframes['01_monthly_revenue_growth.sql'].copy()
df_m['month'] = pd.to_datetime(df_m['month'])

fig, ax1 = plt.subplots(figsize=(10, 5))
color = '#1f77b4'
ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax1.set_ylabel('Revenue ($)', color=color, fontsize=12, fontweight='bold')
line1 = ax1.plot(df_m['month'], df_m['revenue'], color=color, marker='o', linewidth=2.5, label='Monthly Revenue ($)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.yaxis.set_major_formatter('${x:,.0f}')

ax2 = ax1.twinx()
color = '#ff7f0e'
ax2.set_ylabel('MoM Growth (%)', color=color, fontsize=12, fontweight='bold')
line2 = ax2.plot(df_m['month'], df_m['mom_growth_pct'], color=color, linestyle='--', marker='s', linewidth=2, label='MoM Growth (%)')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Monthly Revenue Trend & MoM Growth Rate', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig('results/monthly_revenue_trend.png', dpi=300)
plt.close()
print("Saved results/monthly_revenue_trend.png")

# Chart 2: Cohort Retention Heatmap
df_c = dataframes['02_cohort_retention.sql'].copy()
pivot_c = df_c.pivot(index='cohort_month', columns='month_number', values='retention_pct')

plt.figure(figsize=(11, 6))
sns.heatmap(pivot_c, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Retention Rate (%)'}, vmin=0, vmax=100)
plt.title('Customer Cohort Retention Rate (%) Over Time', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Months Since First Purchase', fontsize=12, fontweight='bold')
plt.ylabel('Cohort Month', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('results/cohort_retention_heatmap.png', dpi=300)
plt.close()
print("Saved results/cohort_retention_heatmap.png")

# Chart 3: Revenue Share by RFM Tier
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(rfm_tier_summary['customer_tier'], rfm_tier_summary['rev_share_pct'], color=['#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#1f77b4'])
ax.set_xlabel('Revenue Share (%)', fontsize=12, fontweight='bold')
ax.set_title('Revenue Share by RFM Customer Segment', fontsize=14, fontweight='bold', pad=15)
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', ha='left', va='center', fontweight='bold')
plt.xlim(0, max(rfm_tier_summary['rev_share_pct']) + 8)
plt.tight_layout()
plt.savefig('results/rfm_revenue_share.png', dpi=300)
plt.close()
print("Saved results/rfm_revenue_share.png")

# Generate Jupyter Notebook analytics.ipynb
notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# E-Commerce Customer Revenue Analytics — Visualizations & Insights\n",
    "This notebook loads the analytical results from MySQL and generates visual charts for revenue trends, cohort retention, and RFM customer segmentation."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "# Load query results\n",
    "df_monthly = pd.read_csv('results/01_monthly_revenue_growth.csv')\n",
    "df_cohort = pd.read_csv('results/02_cohort_retention.csv')\n",
    "df_rfm = pd.read_csv('results/03_rfm_customer_segmentation.csv')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Monthly Revenue & Growth Trend"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "df_monthly['month'] = pd.to_datetime(df_monthly['month'])\n",
    "fig, ax1 = plt.subplots(figsize=(10, 5))\n",
    "ax1.plot(df_monthly['month'], df_monthly['revenue'], color='#1f77b4', marker='o', linewidth=2.5, label='Revenue ($)')\n",
    "ax1.set_ylabel('Revenue ($)', color='#1f77b4', fontsize=12)\n",
    "ax2 = ax1.twinx()\n",
    "ax2.plot(df_monthly['month'], df_monthly['mom_growth_pct'], color='#ff7f0e', linestyle='--', marker='s', label='MoM Growth (%)')\n",
    "ax2.set_ylabel('MoM Growth (%)', color='#ff7f0e', fontsize=12)\n",
    "plt.title('Monthly Revenue Trend & MoM Growth Rate', fontsize=14)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Cohort Retention Heatmap"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "pivot_c = df_cohort.pivot(index='cohort_month', columns='month_number', values='retention_pct')\n",
    "plt.figure(figsize=(11, 6))\n",
    "sns.heatmap(pivot_c, annot=True, fmt='.1f', cmap='YlGnBu', vmin=0, vmax=100)\n",
    "plt.title('Customer Cohort Retention Rate (%)', fontsize=14)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. RFM Revenue Distribution"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "tier_rev = df_rfm.groupby('customer_tier')['monetary'].sum().reset_index()\n",
    "tier_rev['share_pct'] = (100.0 * tier_rev['monetary'] / tier_rev['monetary'].sum()).round(2)\n",
    "plt.figure(figsize=(9, 5))\n",
    "plt.barh(tier_rev['customer_tier'], tier_rev['share_pct'], color='#2ca02c')\n",
    "plt.xlabel('Revenue Share (%)')\n",
    "plt.title('Revenue Share by RFM Tier')\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open('analytics.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=1)

print("Saved analytics.ipynb")
conn.close()
