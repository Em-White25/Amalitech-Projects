-- DROP TABLES IF THEY EXIST(OPTIONAL).
--  NOTE:Do not run in production. Run if tables are empty -- because this is irreversible
DROP TABLE IF EXISTS inventory_logs, order_details, orders, products, customers;

-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY NOT NULL,	-- an auto-increment customer_id column
    customer_name VARCHAR(100) NOT NULL,	-- name of customer
    email VARCHAR(100) UNIQUE,			-- unique email of customer
    phone_number VARCHAR(20) NOT NULL,		-- phone number of the customer
    country VARCHAR(50) NOT NULL,		-- country of the residence
    city VARCHAR(50) NOT NULL			-- city of residence
);

-- Products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY NOT NULL,	-- auto increment primary key
    product_name VARCHAR(100) NOT NULL,		-- product's name
    category VARCHAR(50) NOT NULL,		-- category of the product
    price NUMERIC(10, 2) NOT NULL,		-- price of the product
    stock_quantity INT NOT NULL,		-- quantity of product in stock
    reorder_level INT NOT NULL,			-- level to trigger reordering
    product_description TEXT			-- product description
);

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY NOT NULL,				-- auto-incrementing primary key (order_id)
    customer_id INT NOT NULL REFERENCES customers(customer_id),		-- references customer_id on customers table
    order_date DATE NOT NULL,						-- the date the order was placed
    total_amount NUMERIC(10, 2) NOT NULL,				-- total amount of the order
    status VARCHAR(20) NOT NULL						-- the status of the order
);

-- Order Details table
CREATE TABLE order_details (
    details_id SERIAL PRIMARY KEY NOT NULL,
    order_id INT NOT NULL REFERENCES orders(order_id),		-- references order_id on orders table
    product_id INT NOT NULL REFERENCES products(product_id),	-- references product_id on products tab;e
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL
);


-- Inventory table
CREATE TABLE inventory_logs (
    log_id SERIAL PRIMARY KEY NOT NULL,
    product_id INT NOT NULL REFERENCES products(product_id),	-- references product_id on products table 
    change_quantity INT NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- Insert Initial Data for Simulation
-- =====================================================

-- Insert customers table
INSERT INTO customers (customer_id, customer_name, email, phone_number, country, city)
VALUES 
  ('James Appiah', 'ja.appiah@example.com', '0245242798', 'USA', 'New York'),
  ('Araba Smith', 'arab.smith@example.com', '0547298224', 'USA', 'Chicago'),
  ('Joseph Lartey', 'joe.lartey@example.com', '0502334922', 'Canada', 'Toronto'),
  ('Bob Okala', 'bobok@example.com', '0551234567', 'Germany', 'Munich');

-- Insert products table
INSERT INTO products (product_id, product_name, category, price, stock_quantity, reorder_level, product_description)
VALUES 
  (101, 'Wireless Mouse', 'Electronics', 25.99, 120, 20, '2.4GHz wireless mouse with ergonomic design'),
  ('Laptop Stand', 'Accessories', 35.50, 80, 15, 'Aluminum adjustable stand for laptops'),
  ('USB-C Hub', 'Electronics', 45.00, 60, 10, 'Multiport adapter with HDMI, USB 3.0, and card reader'),
  ('Noise Cancelling Headphones', 'Electronics', 150.00, 40, 10, 'Over-ear noise cancelling'),
  ('Laptop Bag', 'Accessories', 75.00, 50, 10, 'HP Laptop bag for size 15"6 laptops. (Color: Gray)' );

