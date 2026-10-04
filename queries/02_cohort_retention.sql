-- Business Question: What percentage of customer cohorts are retained over successive months following their initial purchase?
WITH first_purchase AS (
    SELECT customer_id, DATE_FORMAT(MIN(order_date), '%Y-%m-01') AS cohort_month
    FROM orders WHERE order_status='Completed' GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, DATE_FORMAT(order_date, '%Y-%m-01') AS activity_month
    FROM orders WHERE order_status='Completed'
),
cohort_activity AS (
    SELECT f.cohort_month, a.activity_month,
           (YEAR(a.activity_month) - YEAR(f.cohort_month)) * 12 + (MONTH(a.activity_month) - MONTH(f.cohort_month)) AS month_number,
           COUNT(DISTINCT a.customer_id) AS retained_customers
    FROM first_purchase f JOIN activity a ON a.customer_id=f.customer_id
    WHERE a.activity_month>=f.cohort_month
    GROUP BY f.cohort_month, a.activity_month
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM first_purchase GROUP BY cohort_month
)
SELECT ca.cohort_month, ca.month_number, cs.cohort_customers, ca.retained_customers,
       ROUND(100.0*ca.retained_customers/NULLIF(cs.cohort_customers,0),2) AS retention_pct
FROM cohort_activity ca JOIN cohort_size cs USING (cohort_month)
ORDER BY ca.cohort_month, ca.month_number;
