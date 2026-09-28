-- Q2: What percentage of each signup cohort keeps purchasing?
WITH first_purchase AS (
    SELECT customer_id, DATE_TRUNC('month',MIN(order_date))::date AS cohort_month
    FROM orders WHERE order_status='Completed' GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month',order_date)::date AS activity_month
    FROM orders WHERE order_status='Completed'
),
cohort_activity AS (
    SELECT f.cohort_month, a.activity_month,
           ((EXTRACT(YEAR FROM a.activity_month)-EXTRACT(YEAR FROM f.cohort_month))*12
             + EXTRACT(MONTH FROM a.activity_month)-EXTRACT(MONTH FROM f.cohort_month))::int AS month_number,
           COUNT(DISTINCT a.customer_id) AS retained_customers
    FROM first_purchase f JOIN activity a ON a.customer_id=f.customer_id
    WHERE a.activity_month>=f.cohort_month
    GROUP BY 1,2,3
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers
    FROM first_purchase GROUP BY cohort_month
)
SELECT ca.cohort_month, ca.month_number, cs.cohort_customers, ca.retained_customers,
       ROUND(100.0*ca.retained_customers/NULLIF(cs.cohort_customers,0),2) AS retention_pct
FROM cohort_activity ca JOIN cohort_size cs USING (cohort_month)
ORDER BY ca.cohort_month, ca.month_number;
