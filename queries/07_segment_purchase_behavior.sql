-- Business Question: How do purchasing behavior, order volume, and revenue contribution vary across customer segments?
WITH order_value AS (
    SELECT o.order_id,o.customer_id,
           SUM(oi.quantity*oi.unit_price)-MAX(o.discount_amount) AS net_order_value
    FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
    WHERE o.order_status='Completed'
    GROUP BY o.order_id,o.customer_id
)
SELECT c.customer_segment,COUNT(DISTINCT ov.customer_id) AS customers,COUNT(*) AS orders,
       ROUND(SUM(ov.net_order_value),2) AS revenue,
       ROUND(AVG(ov.net_order_value),2) AS avg_order_value,
       ROUND(SUM(ov.net_order_value)/NULLIF(COUNT(DISTINCT ov.customer_id),0),2) AS revenue_per_customer,
       ROUND(COUNT(*)::numeric/NULLIF(COUNT(DISTINCT ov.customer_id),0),2) AS orders_per_customer
FROM order_value ov JOIN customers c ON c.customer_id=ov.customer_id
GROUP BY c.customer_segment ORDER BY revenue DESC;
