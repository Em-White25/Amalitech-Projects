-- Create VIEW: customer_order_summary to show summary of all orders placed by each customer
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
CREATE OR REPLACE VIEW low_stock_report AS
SELECT 
    product_id,
    product_name,
    stock_quantity,
    reorder_level,
    (reorder_level - stock_quantity) AS shortage
FROM products
WHERE stock_quantity < reorder_level;


-- Create VIEW: customer_spending_tier to show customer spending trends
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



