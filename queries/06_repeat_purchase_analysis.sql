-- Q6: How quickly do customers make a second purchase?
WITH purchases AS (
    SELECT customer_id,order_id,order_date,
           ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date,order_id) AS purchase_number
    FROM orders WHERE order_status='Completed'
),
first_second AS (
    SELECT customer_id,
           MIN(order_date) FILTER(WHERE purchase_number=1) AS first_purchase_date,
           MIN(order_date) FILTER(WHERE purchase_number=2) AS second_purchase_date
    FROM purchases GROUP BY customer_id
)
SELECT COUNT(*) AS customers_with_purchase,
       COUNT(*) FILTER(WHERE second_purchase_date IS NOT NULL) AS repeat_customers,
       ROUND(100.0*COUNT(*) FILTER(WHERE second_purchase_date IS NOT NULL)
             /NULLIF(COUNT(*),0),2) AS repeat_purchase_rate_pct,
       ROUND(AVG(second_purchase_date-first_purchase_date)
             FILTER(WHERE second_purchase_date IS NOT NULL),1) AS avg_days_to_second_purchase
FROM first_second;
