-- Business Question: What is the overall repeat purchase rate, and how many days on average does it take for a customer to make a second purchase?
WITH purchases AS (
    SELECT customer_id,order_id,order_date,
           ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date,order_id) AS purchase_number
    FROM orders WHERE order_status='Completed'
),
first_second AS (
    SELECT customer_id,
           MIN(CASE WHEN purchase_number=1 THEN order_date END) AS first_purchase_date,
           MIN(CASE WHEN purchase_number=2 THEN order_date END) AS second_purchase_date
    FROM purchases GROUP BY customer_id
)
SELECT COUNT(*) AS customers_with_purchase,
       COUNT(CASE WHEN second_purchase_date IS NOT NULL THEN 1 END) AS repeat_customers,
       ROUND(100.0*COUNT(CASE WHEN second_purchase_date IS NOT NULL THEN 1 END)
             /NULLIF(COUNT(*),0),2) AS repeat_purchase_rate_pct,
       ROUND(AVG(CASE WHEN second_purchase_date IS NOT NULL THEN DATEDIFF(second_purchase_date, first_purchase_date) END),1) AS avg_days_to_second_purchase
FROM first_second;
