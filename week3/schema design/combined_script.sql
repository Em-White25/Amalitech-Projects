-- =====================================================
-- PHASE 1: DROP TABLES & CREATE SCHEMA
-- =====================================================

-- Drop all tables if they already exist to reset the schema (use with caution)
DROP TABLE IF EXISTS inventory_logs, order_details, orders, products, customers;

-- Create table to store customer information
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

-- Create table to store product information
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    reorder_level INT NOT NULL,
    product_description TEXT
);

-- Create table to store orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY NOT NULL,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL
);

-- Create table to store details of each order (line items)
CREATE TABLE order_details (
    details_id SERIAL PRIMARY KEY NOT NULL,
    order_id INT NOT NULL REFERENCES orders(order_id),
    product_id INT NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL
);

-- Create inventory log to track stock changes
CREATE TABLE inventory_logs (
    log_id SERIAL PRIMARY KEY NOT NULL,
    product_id INT NOT NULL REFERENCES products(product_id),
    change_quantity INT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Insert Initial Data for Simulation
-- =====================================================

-- Insert customers
INSERT INTO customers (customer_id, customer_name, email, phone_number, country, city)
VALUES 
  ('James Appiah', 'ja.appiah@example.com', '0245242798', 'USA', 'New York'),
  ('Araba Smith', 'arab.smith@example.com', '0547298224', 'USA', 'Chicago'),
  ('Joseph Lartey', 'joe.lartey@example.com', '0502334922', 'Canada', 'Toronto'),
  ('Bob Okala', 'bobok@example.com', '0551234567', 'Germany', 'Munich');

-- Insert products
INSERT INTO products (product_id, product_name, category, price, stock_quantity, reorder_level, product_description)
VALUES 
  (101, 'Wireless Mouse', 'Electronics', 25.99, 120, 20, '2.4GHz wireless mouse with ergonomic design'),
  ('Laptop Stand', 'Accessories', 35.50, 80, 15, 'Aluminum adjustable stand for laptops'),
  ('USB-C Hub', 'Electronics', 45.00, 60, 10, 'Multiport adapter with HDMI, USB 3.0, and card reader'),
  ('Noise Cancelling Headphones', 'Electronics', 150.00, 40, 10, 'Over-ear noise cancelling'),
  ('Laptop Bag', 'Accessories', 75.00, 50, 10, 'HP Laptop bag for size 15"6 laptops. (Color: Gray)' );

-- =====================================================
-- PHASE 2: Create Order Placement Logic
-- =====================================================

-- Create function to place an order
-- This function handles the complete order workflow:
-- 1. Adds to orders
-- 2. Adds to order_details
-- 3. Deducts product stock
-- 4. Logs the inventory change

CREATE OR REPLACE FUNCTION place_order(
    p_customer_id INT,
    p_status VARCHAR,
    p_product_ids INT[],
    p_quantities INT[]
)
RETURNS VOID AS $$
DECLARE
    v_order_id INT;
    v_total_amount NUMERIC(10, 2) := 0;
    i INT;
    v_unit_price NUMERIC(10, 2);
    v_total_price NUMERIC(10, 2);
    v_discount NUMERIC(10, 2) := 0;
BEGIN
    -- Insert new order
    INSERT INTO orders (customer_id, order_date, total_amount, status)
    VALUES (p_customer_id, CURRENT_DATE, 0, p_status)
    RETURNING order_id INTO v_order_id;

    -- Process each product in the order
    FOR i IN 1 .. array_length(p_product_ids, 1) LOOP
        SELECT price INTO v_unit_price FROM products WHERE product_id = p_product_ids[i];

        v_total_price := v_unit_price * p_quantities[i];

        -- Apply discount logic
        IF p_quantities[i] >= 20 THEN
            v_discount := v_total_price * 0.15;
        ELSIF p_quantities[i] >= 10 THEN
            v_discount := v_total_price * 0.07;
        ELSE
            v_discount := 0;
        END IF;

        -- Subtract discount
        v_total_price := v_total_price - v_discount;

        -- Insert order details
        INSERT INTO order_details (order_id, product_id, quantity, unit_price, total_amount)
        VALUES (v_order_id, p_product_ids[i], p_quantities[i], v_unit_price, v_total_price);

        -- Update stock
        UPDATE products
        SET stock_quantity = stock_quantity - p_quantities[i]
        WHERE product_id = p_product_ids[i];

        -- Log inventory change
        INSERT INTO inventory_logs (product_id, change_quantity, change_type)
        VALUES (p_product_ids[i], -p_quantities[i], 'sale');

        -- Accumulate total
        v_total_amount := v_total_amount + v_total_price;
    END LOOP;

    -- Update order total
    UPDATE orders SET total_amount = v_total_amount WHERE order_id = v_order_id;

    RAISE NOTICE 'Order % placed successfully with total $%s after discount', v_order_id, v_total_amount;
END;
$$ LANGUAGE plpgsql;

-- Create trigger function to log inventory changes after update
CREATE OR REPLACE FUNCTION log_inventory_change() 
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO inventory_logs (product_id, change_quantity, change_type, changed_at)
    VALUES (NEW.product_id, NEW.stock_quantity - OLD.stock_quantity, 'manual_update', CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically log inventory changes
CREATE TRIGGER track_inventory_changes
AFTER UPDATE OF stock_quantity
ON products
FOR EACH ROW
EXECUTE FUNCTION log_inventory_change();

-- =====================================================
-- PHASE 3: Create Views for Analysis
-- =====================================================

-- View to show customer order summaries
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

-- View to list low stock products
CREATE OR REPLACE VIEW low_stock_report AS
SELECT 
    product_id,
    product_name,
    stock_quantity,
    reorder_level,
    (reorder_level - stock_quantity) AS shortage
FROM products
WHERE stock_quantity < reorder_level;

-- View to show customer spending levels
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

-- =====================================================
-- PHASE 4: Stock Replenishment Procedure
-- =====================================================

-- Procedure to automatically replenish stock
CREATE OR REPLACE PROCEDURE replenish_stock()
LANGUAGE plpgsql
AS $$
DECLARE
    p RECORD;
    qty_to_add INT;
BEGIN
    -- Loop through products that are low in stock
    FOR p IN 
        SELECT product_id, stock_quantity, reorder_level 
        FROM products 
        WHERE stock_quantity < reorder_level
    LOOP
        -- Calculate how much stock to add to reach 125% of reorder level
        qty_to_add := CEIL((p.reorder_level * 1.25) - p.stock_quantity);

        -- Update product stock
        UPDATE products 
        SET stock_quantity = stock_quantity + qty_to_add
        WHERE product_id = p.product_id;

        -- Log replenishment
        INSERT INTO inventory_logs (product_id, change_quantity, change_type)
        VALUES (p.product_id, qty_to_add, 'replenishment');

        RAISE NOTICE 'Replenished product % with quantity %', p.product_id, qty_to_add;
    END LOOP;
END;
$$;

-- ===============================
-- End of Script
-- ===============================
