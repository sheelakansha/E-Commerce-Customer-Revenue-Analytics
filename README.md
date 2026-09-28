# E-Commerce Customer & Revenue Analytics

**Stack: Python (pandas, matplotlib, seaborn) + PostgreSQL + SQL + Jupyter Notebook**

A comprehensive business analytics case study evaluating revenue growth, customer retention, RFM segmentation, customer lifetime value (CLV), product category performance, and discount sensitivity across 60,000+ transaction records.

---

## Key Insights

Based on empirical SQL query outputs executed on the transaction dataset:

1. **Pareto Revenue Concentration**: The top **20% of customers** account for **49.05% of total business revenue** ($169.2M out of $344.9M), demonstrating strong revenue reliance on core buyers.
2. **At-Risk High-Value Revenue**: **19.45% of total cumulative revenue** ($67.14M across 914 customers) belongs to the *"At-Risk High-Value"* RFM segment—buyers with high historical spending who have not purchased recently.
3. **Speed to Second Purchase**: The median interval to a customer's second purchase is **26.0 days** (average: 40.4 days), with an overall customer repeat purchase rate of **95.75%**.
4. **Cohort Retention Stability**: Customer cohorts experience initial decay post-signup but stabilize at an average **43.10% retention rate by Month 3**.
5. **Discount Impact on Order Value**: Discounted orders produce an average Net Order Value of **$3,585.62** against a Gross Order Value of **$5,292.09**, representing an average promotional markdown rate of **26.6%** ($1,706.47 average discount per order).

---

## Visual Analytics

### 1. Monthly Revenue Trend & MoM Growth
![Monthly Revenue Trend](results/monthly_revenue_trend.png)

### 2. Cohort Retention Heatmap (%)
![Cohort Retention Heatmap](results/cohort_retention_heatmap.png)

### 3. Revenue Share by RFM Customer Segment
![Revenue Share by RFM Segment](results/rfm_revenue_share.png)

---

## Strategic Recommendations

1. **Targeted Win-Back Campaign for At-Risk VIPs**:
   - **Action**: Launch automated win-back workflows (exclusive previews, VIP loyalty perks) targeting the 914 *"At-Risk High-Value"* customers who control **19.45% ($67.14M)** of historical revenue.
2. **Day 21 Post-Purchase Re-Engagement Triggers**:
   - **Action**: Deploy automated email and SMS recommendations at **Day 21 after first purchase** to capture customers right before the **26-day median repeat purchase window**.
3. **Onboarding Strategy to Boost Month-3 Retention**:
   - **Action**: Introduce a structured 30-day post-purchase drip sequence to arrest early cohort drop-off and elevate the **43.10% Month-3 retention baseline**.
4. **Promotional Margin Guardrails**:
   - **Action**: Replace flat discounts with minimum order value (MOV) thresholds to protect margins, as current discounting erodes average order value by **$1,706.47 per transaction (26.6% markdown)**.

---

## Synthetic Data & Modeling Assumptions

> ⚠️ **Note**: All data in this project is synthetic and procedurally generated via [`data/generate_data.py`](data/generate_data.py).

### Built-in Modeling Assumptions:
- **Timeline**: 10,000 customers acquired across an 18-month window (Jan 2025 – June 2026).
- **Order Distribution**: Transaction frequencies follow an exponential inter-arrival distribution per customer tier (VIP, Corporate, Retail).
- **Pricing & Catalogue**: 120 products distributed across 5 categories (Electronics, Clothing, Home, Books, Beauty) with unit prices ranging from $10 to $500.
- **Order Fulfillment & Payment**: 85% completed, 10% pending, 5% cancelled; payment status synchronized with order status.

---

## SQL Skills Demonstrated

CTEs, multi-table joins, `GROUP BY`, `CASE`, window functions (`LAG`, `ROW_NUMBER`, `RANK`, `NTILE`), conditional aggregation (`FILTER`), `DATE_TRUNC`, date arithmetic, running/windowed aggregates, `PERCENTILE_CONT`, and `NULLIF`.

---

## Run & Execution

### 1. Generate Data & Setup Database

```bash
# Generate synthetic dataset
cd data
python generate_data.py
cd ..

# Standard PostgreSQL commands (Default Port: 5432)
createdb ecommerce_analytics
psql -d ecommerce_analytics -f schema.sql
psql -d ecommerce_analytics -f load_data.sql
psql -d ecommerce_analytics -f queries/01_monthly_revenue_growth.sql
```

> **Custom Port Note**: If PostgreSQL is running on a non-standard port (e.g., Port `1234`), specify `-p 1234 -U postgres` or set environment variables:
> ```powershell
> # PowerShell:
> $env:PGPORT="1234"; $env:PGUSER="postgres"
> createdb -p 1234 -U postgres ecommerce_analytics
> psql -p 1234 -U postgres -d ecommerce_analytics -f schema.sql
> psql -p 1234 -U postgres -d ecommerce_analytics -f load_data.sql
> ```

### 2. Export Query Results & Generate Visualizations

```bash
# Run Python pipeline to execute all 8 queries, export CSVs, generate charts, and build Jupyter notebook
python export_and_visualize.py

# Launch Jupyter Notebook for interactive exploration
jupyter notebook analytics.ipynb
```

---

## Repository Structure

```text
ecommerce-customer-revenue-analytics/
├── README.md
├── schema.sql
├── load_data.sql
├── export_and_visualize.py
├── analytics.ipynb
├── requirements.txt
├── data/
│   ├── generate_data.py
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── payments.csv
├── queries/
│   ├── 01_monthly_revenue_growth.sql
│   ├── 02_cohort_retention.sql
│   ├── 03_rfm_customer_segmentation.sql
│   ├── 04_customer_lifetime_value.sql
│   ├── 05_product_category_performance.sql
│   ├── 06_repeat_purchase_analysis.sql
│   ├── 07_segment_purchase_behavior.sql
│   └── 08_discount_revenue_analysis.sql
└── results/
    ├── 01_monthly_revenue_growth.csv
    ├── 02_cohort_retention.csv
    ├── 03_rfm_customer_segmentation.csv
    ├── 04_customer_lifetime_value.csv
    ├── 05_product_category_performance.csv
    ├── 06_repeat_purchase_analysis.csv
    ├── 07_segment_purchase_behavior.csv
    ├── 08_discount_revenue_analysis.csv
    ├── monthly_revenue_trend.png
    ├── cohort_retention_heatmap.png
    └── rfm_revenue_share.png
```

---

## Resume Entry

**E-Commerce Customer & Revenue Analytics | Python, PostgreSQL, SQL, Matplotlib**

> Analyzed 60,000+ transactions across 10,000+ customers using PostgreSQL and Python; built cohort retention models, RFM segmentation, and CLV frameworks using CTEs and window functions; generated automated visualizations revealing 49.05% Pareto revenue concentration and $67.14M at-risk revenue to inform targeted retention and discounting strategies.
