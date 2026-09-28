-- Q5: Which products and categories drive revenue?
WITH product_sales AS (
    SELECT p.product_id,p.product_name,p.category,SUM(oi.quantity) AS units_sold,
           COUNT(DISTINCT o.order_id) AS orders,
           SUM(oi.quantity*oi.unit_price) AS gross_revenue
    FROM order_items oi JOIN orders o ON o.order_id=oi.order_id
    JOIN products p ON p.product_id=oi.product_id
    WHERE o.order_status='Completed'
    GROUP BY p.product_id,p.product_name,p.category
),
ranked AS (
    SELECT *,RANK() OVER(PARTITION BY category ORDER BY gross_revenue DESC) AS product_rank_in_category,
           SUM(gross_revenue) OVER(PARTITION BY category) AS category_revenue
    FROM product_sales
)
SELECT product_id,product_name,category,units_sold,orders,ROUND(gross_revenue,2) AS gross_revenue,
       product_rank_in_category,
       ROUND(100.0*gross_revenue/NULLIF(category_revenue,0),2) AS share_of_category
FROM ranked ORDER BY category,product_rank_in_category;
