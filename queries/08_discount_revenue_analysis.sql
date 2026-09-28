-- Q8: Are discounted orders associated with different purchasing behavior?
WITH order_metrics AS (
    SELECT o.order_id,c.customer_segment,o.discount_amount,
           SUM(oi.quantity*oi.unit_price) AS gross_value,
           SUM(oi.quantity*oi.unit_price)-o.discount_amount AS net_value
    FROM orders o JOIN customers c ON c.customer_id=o.customer_id
    JOIN order_items oi ON oi.order_id=o.order_id
    WHERE o.order_status='Completed'
    GROUP BY o.order_id,c.customer_segment,o.discount_amount
)
SELECT CASE WHEN discount_amount>0 THEN 'Discounted' ELSE 'Non-discounted' END AS order_type,
       customer_segment,COUNT(*) AS orders,
       ROUND(AVG(gross_value),2) AS avg_gross_order_value,
       ROUND(AVG(discount_amount),2) AS avg_discount,
       ROUND(AVG(net_value),2) AS avg_net_order_value,
       ROUND(100.0*SUM(discount_amount)/NULLIF(SUM(gross_value),0),2) AS discount_rate_pct
FROM order_metrics
GROUP BY 1,2 ORDER BY customer_segment,order_type;
