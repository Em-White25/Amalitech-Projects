-- Create VIEW: customer_order_summary
/*
	* This VIEW joins customers, orders, and order_details tables
	* Counts how many products were ordered per order
	* Groups the data by customer and order
	* Sorts the results from the newest to the oldest
*/

CREATE OR REPLACE VIEW customer_order_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_date,
    o.total_amount,
    COUNT(od.product_id) AS total_items_ordered
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_id, c.customer_name, o.order_id, o.order_date, o.total_amount
ORDER BY o.order_date DESC;


-- Create VIEW: low_stock_report to show products that need restocking
/*
	This view filters products that have less stock than their reorder level.
	It calculates the shortage amount.
*/

CREATE OR REPLACE VIEW low_stock_report AS
SELECT 
    product_id,
    product_name,
    stock_quantity,
    reorder_level,
    (reorder_level - stock_quantity) AS shortage
FROM products
WHERE stock_quantity < reorder_level;


-- Create VIEW: customer_spending_tier
/*
	This VIEW segments customers based on their how much they spend. 
	It assigns a spending tier to each customer
	* GOLD for customers who spend more than 500 
	* SILVER for customers who spend between 100 and 500
	* BRONZE for customers who spend less than 100
*/

CREATE OR REPLACE VIEW customer_spending_tier AS
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.total_amount) AS total_spent,
    CASE 
        WHEN SUM(o.total_amount) < 100 THEN 'Bronze'
        WHEN SUM(o.total_amount) BETWEEN 100 AND 500 THEN 'Silver'
        ELSE 'Gold'
    END AS spending_tier
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;



