-- Business Question: How is monthly revenue growing over time, and what is the month-over-month (MoM) growth rate?
WITH monthly AS (
    SELECT DATE_TRUNC('month', o.order_date)::date AS month,
           SUM(p.payment_amount) AS revenue,
           COUNT(DISTINCT o.order_id) AS orders,
           COUNT(DISTINCT o.customer_id) AS active_customers
    FROM orders o
    JOIN payments p ON p.order_id = o.order_id
    WHERE o.order_status='Completed' AND p.payment_status='Paid'
    GROUP BY 1
)
SELECT month, revenue, orders, active_customers,
       LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
       ROUND(100.0*(revenue-LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month),0),2) AS mom_growth_pct
FROM monthly ORDER BY month;
