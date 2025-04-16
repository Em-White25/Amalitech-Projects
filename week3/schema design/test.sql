-- 1. Check if all essential tables exist
-- This helps ensure the schema was successfully created
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('customers', 'products', 'orders', 'order_details', 'inventory_logs');

-- 2. Insert a new test customer
INSERT INTO customers (customer_name, email, phone_number, country, city)
VALUES ('Test User', 'test.user@example.com', '0551234567', 'Ghana', 'Accra');

-- 3. Insert new test products
INSERT INTO products (product_name, category, price, stock_quantity, reorder_level, product_description)
VALUES 
('Mechanical Keyboard', 'Electronics', 75.00, 50, 10, 'RGB backlit keyboard'),
('Noise Cancelling Headphones', 'Electronics', 150.00, 40, 10, 'Over-ear noise cancelling');

-- 4. Check stock before placing order
SELECT product_id, product_name, stock_quantity FROM products WHERE product_name IN ('Mechanical Keyboard', 'Noise Cancelling Headphones');

-- 5. Place an order for test products
-- First, find the customer_id and product_ids just inserted
SELECT customer_id FROM customers WHERE customer_name = 'Test User';
SELECT product_id FROM products WHERE product_name = 'Mechanical Keyboard';
SELECT product_id FROM products WHERE product_name = 'Noise Cancelling Headphones';

-- Assume IDs returned are: customer_id = 4, product_id_1 = 104, product_id_2 = 105 (adjust as needed)

-- Call the place_order function
SELECT place_order(
    4, -- test customer_id
    'processing', 
    ARRAY[104, 105], -- product_ids
    ARRAY[2, 3] -- quantities
);

-- 6. Check order and order_details
SELECT * FROM orders WHERE customer_id = 4 ORDER BY order_date DESC LIMIT 1;
SELECT * FROM order_details WHERE order_id = (SELECT MAX(order_id) FROM orders WHERE customer_id = 4);

-- 7. Check stock after order
SELECT product_id, product_name, stock_quantity FROM products WHERE product_id IN (104, 105);

-- 8. Check inventory logs
SELECT * FROM inventory_logs WHERE product_id IN (104, 105) ORDER BY changed_at DESC;

-- 9. Test views
-- View: customer_order_summary
SELECT * FROM customer_order_summary WHERE customer_id = 4;

-- View: low_stock_report
SELECT * FROM low_stock_report;

-- View: customer_spending_tier
SELECT * FROM customer_spending_tier WHERE customer_id = 4;
