-- Q4: Which customer segments generate the greatest value?
WITH customer_value AS (
    SELECT c.customer_id,c.customer_segment,MIN(o.order_date) AS first_order_date,
           MAX(o.order_date) AS last_order_date,COUNT(DISTINCT o.order_id) AS order_count,
           SUM(p.payment_amount) AS lifetime_value
    FROM customers c
    JOIN orders o ON o.customer_id=c.customer_id
    JOIN payments p ON p.order_id=o.order_id
    WHERE o.order_status='Completed' AND p.payment_status='Paid'
    GROUP BY c.customer_id,c.customer_segment
)
SELECT customer_segment,COUNT(*) AS customers,
       ROUND(AVG(lifetime_value),2) AS avg_lifetime_value,
       ROUND(AVG(order_count),2) AS avg_orders,
       ROUND(AVG(lifetime_value/NULLIF(order_count,0)),2) AS avg_order_value,
       ROUND(AVG(last_order_date-first_order_date),1) AS avg_active_days,
       ROUND(SUM(lifetime_value),2) AS segment_revenue
FROM customer_value GROUP BY customer_segment ORDER BY segment_revenue DESC;
