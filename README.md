# E-Commerce Customer & Revenue Analytics

**Stack: Python + PostgreSQL + SQL**

A portfolio-ready business analytics case study using synthetic e-commerce data. The project focuses on revenue growth, customer retention, RFM segmentation, lifetime value, product performance, repeat purchases, customer segments, and discount behavior.

## Dataset

- 10,000 customers
- 120 products
- 60,000 orders
- 60,000 order items
- 60,000 payment records
- Date range: 2025-01-07 to 2026-06-30

## Tables

`customers` → customer master and signup cohorts  
`products` → product/category catalogue  
`orders` → order-level facts  
`order_items` → products and quantities in each order  
`payments` → payment outcomes and amounts

## Business Questions

1. Is revenue growing month over month?
2. How well do customer cohorts retain over time?
3. Which customers are champions, at-risk, or lapsed?
4. Which customer segments generate the greatest lifetime value?
5. Which products and categories drive revenue?
6. How quickly do customers make a second purchase?
7. How does purchasing behavior differ across customer segments?
8. Are discounted orders associated with different order-value patterns?

## SQL Skills Demonstrated

CTEs, multi-table joins, `GROUP BY`, `CASE`, window functions, `LAG`, `ROW_NUMBER`, `RANK`, `NTILE`, conditional aggregation, `DATE_TRUNC`, date arithmetic, running/windowed aggregates, and `NULLIF`.

## Run

```bash
cd data
python generate_data.py
cd ..
createdb ecommerce_analytics
psql -d ecommerce_analytics -f schema.sql
psql -d ecommerce_analytics -f load_data.sql
psql -d ecommerce_analytics -f queries/01_monthly_revenue_growth.sql
```

## Repository Structure

```text
ecommerce-customer-revenue-analytics/
├── README.md
├── schema.sql
├── load_data.sql
├── requirements.txt
├── data/
│   ├── generate_data.py
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── payments.csv
└── queries/
    ├── 01_monthly_revenue_growth.sql
    ├── 02_cohort_retention.sql
    ├── 03_rfm_customer_segmentation.sql
    ├── 04_customer_lifetime_value.sql
    ├── 05_product_category_performance.sql
    ├── 06_repeat_purchase_analysis.sql
    ├── 07_segment_purchase_behavior.sql
    └── 08_discount_revenue_analysis.sql
```

## Resume Entry

**E-Commerce Customer & Revenue Analytics | Python, PostgreSQL, SQL**

> Analyzed 60,000+ orders across 10,000+ customers to evaluate revenue growth, customer retention, purchasing behavior, and product performance; built cohort and RFM analyses using CTEs and window functions to identify high-value and at-risk customer segments and derive customer-retention and category-level insights.
