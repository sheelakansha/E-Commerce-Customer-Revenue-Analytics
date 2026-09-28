-- Q3: Which customers are champions, at-risk, or lapsed?
WITH customer_rfm AS (
    SELECT c.customer_id, c.customer_segment, MAX(o.order_date) AS last_order_date,
           COUNT(DISTINCT o.order_id) AS frequency, SUM(p.payment_amount) AS monetary
    FROM customers c
    JOIN orders o ON o.customer_id=c.customer_id
    JOIN payments p ON p.order_id=o.order_id
    WHERE o.order_status='Completed' AND p.payment_status='Paid'
    GROUP BY c.customer_id,c.customer_segment
),
scored AS (
    SELECT *, CURRENT_DATE-last_order_date AS recency_days,
           NTILE(4) OVER (ORDER BY CURRENT_DATE-last_order_date DESC) AS recency_quartile,
           NTILE(4) OVER (ORDER BY frequency) AS frequency_quartile,
           NTILE(4) OVER (ORDER BY monetary) AS monetary_quartile
    FROM customer_rfm
)
SELECT customer_id, customer_segment, recency_days, frequency, ROUND(monetary,2) AS monetary,
       recency_quartile, frequency_quartile, monetary_quartile,
       CASE
         WHEN monetary_quartile=4 AND recency_quartile=4 AND frequency_quartile>=3 THEN 'Champions'
         WHEN monetary_quartile>=3 AND frequency_quartile>=3 AND recency_quartile>=3 THEN 'Loyal Customers'
         WHEN monetary_quartile=4 AND recency_quartile<=2 THEN 'At-Risk High-Value'
         WHEN recency_quartile=1 AND frequency_quartile<=2 THEN 'Lapsed Customers'
         WHEN recency_quartile>=3 AND frequency_quartile<=2 THEN 'New / Promising'
         ELSE 'Regular Customers'
       END AS customer_tier
FROM scored ORDER BY monetary DESC;
