# 🗂️ Inventory Management Database

## 🔧 Tools Used

- **PostgreSQL** – Relational database used for storing and managing inventory data.
- **Docker** – Used to containerize and run PostgreSQL services locally.
- **pgAdmin (Desktop)** – GUI client for managing and querying the PostgreSQL database.
- **SQL** – For creating schema and performing database operations.

---

## 🧱 Database Schema Overview

This database is designed to manage a basic **inventory and order management system**. It includes information on customers, products, orders, inventory changes, and order details.

**Entity Relationships:**

- **Customers** place multiple **Orders**
- **Orders** contain multiple **Order Details**
- **Products** are referenced in both **Order Details** and **Inventory Logs**

---

## 🧮 Tables & Column Descriptions

### 1. `customers`

Stores customer information.

| Column         | Data Type     | Description                    |
|----------------|---------------|--------------------------------|
| customer_id    | SERIAL (PK)   | Unique identifier              |
| customer_name  | VARCHAR(100)  | Full name of the customer      |
| email          | VARCHAR(100)  | Email address                  |
| phone_number   | VARCHAR(20)   | Contact number                 |
| country        | VARCHAR(50)   | Country of residence           |
| city           | VARCHAR(50)   | City of residence              |

---

### 2. `products`

Stores product information.

| Column         | Data Type     | Description                          |
|----------------|---------------|--------------------------------------|
| product_id     | SERIAL (PK)   | Unique identifier                    |
| product_name   | VARCHAR(100)  | Name of the product                  |
| category       | VARCHAR(50)   | Product category          |
| price          | NUMERIC(10,2) | Price per unit                       |
| stock_quantity | INT           | Quantity currently in stock          |
| reorder_level  | INT           | Threshold to trigger reordering      |
| product_description    | TEXT          | Additional product description       |

---

### 3. `orders`

Stores order data and links to customers.

| Column         | Data Type     | Description                          |
|----------------|---------------|--------------------------------------|
| order_id       | SERIAL (PK)   | Unique identifier                    |
| customer_id    | INT (FK)      | Reference to `customers.customer_id` |
| order_date     | DATE          | Date of the order                    |
| total_amount   | NUMERIC(10,2) | Total order value                    |
| status         | VARCHAR(20)   | Status (e.g. pending, completed)     |

---

### 4. `order_details`

Details the individual details in an order.

| Column         | Data Type     | Description                           |
|----------------|---------------|---------------------------------------|
| details_id     | SERIAL (PK)   | Unique identifier                     |
| order_id       | INT (FK)      | Reference to `orders.order_id`        |
| product_id     | INT (FK)      | Reference to `products.product_id`    |
| quantity       | INT           | Number of units ordered               |
| unit_price     | NUMERIC(10,2) | Price per unit at time of order       |
| total_amount   | NUMERIC(10,2) | Total cost = quantity × unit_price    |

---

### 5. `inventory_logs`

Tracks stock changes such as restocks or sales.

| Column         | Data Type     | Description                              |
|----------------|---------------|------------------------------------------|
| log_id         | SERIAL (PK)   | Unique identifier                        |
| product_id     | INT (FK)      | Reference to `products.product_id`       |
| change_quantity| INT           | Number of items added or removed         |
| change_type    | VARCHAR(50)   | e.g. `restock`, `sale`, `return`         |
| changed_at     | TIMESTAMP     | When the inventory change occurred       |

---

## 🔗 Relationships

- **1 customer → M orders**
- **1 order → M order_details**
- **1 product → M order_details**
- **1 product → M inventory logs**

---

## 🖼️ ERD (Entity Relationship Diagram)

![ERD](ERD.png)

---
![Schema Creation Script](sql_scripts/01_schema_creation.sql)

---
# Phase 2: Placement and Inventory Management

### 📦 `place_order` Function

This PL/pgSQL function handles the complete order placement workflow in the system. It:

- Accepts a customer's ID, order status, an array of product IDs, and their respective quantities.
- Calculates individual item prices, applies quantity-based discounts (7% for ≥10, 15% for ≥20).
- Inserts records into `orders` and `order_details` tables.
- Updates the stock levels in the `products` table.
- Logs each transaction in the `inventory_logs` table.
- Computes and updates the total order amount.
- Provides a confirmation message with the order ID and final total.

This encapsulated logic ensures transactional integrity and reflects real-time inventory updates.

--- 
![Process Order Logic](sql_scripts/02_process_order_functions.sql)
---

### 🛠️ Inventory Chnge Logging Trigger

This trigger setup ensures all **manual updates** to a product's stock are automatically logged for auditing purposes.

- **Function:** `log_inventory_change()`
  - Triggered after any manual `UPDATE` to the `stock_quantity` field in the `products` table.
  - Records the product ID, quantity changed, current timestamp, and marks it as a `'manual_update'`.
  - Helps distinguish between automated stock changes (e.g., from orders) and manual inventory adjustments.

- **Trigger:** `track_inventory_changes`
  - Executes the above function after stock changes, maintaining a transparent history of inventory modifications.

> 🔒 _Future enhancement: Include staff/user information for accountability._
![Schema Creation Script](/sql_scripts/03_trigger_functions.sql)


---

# Phase 3: Monitoring and Reporting
Created a views to provide business insghts. The various views tables provides insights into customer order summaries, products with low stocks that need restocking, and customer spending habits.

![Schema Creation Script](sql_scripts/05_business_insights_views.sql)
## 🧪 Simulated Data for Views

To demonstrate the functionality of the reporting views, we simulate some order data using the existing customers and products.

---

### 🛒 Simulate Order Placements

```sql
-- Place an order for customer 4 (Bob Okala)
SELECT place_order(
    4, 
    'processing', 
    ARRAY[102, 103],  -- Laptop Stand and USB-C Hub
    ARRAY[2, 3]       -- 2 Stands, 3 Hubs
);

-- Place another order for customer 3 (Joseph Lartey)
SELECT place_order(
    3, 
    'processing', 
    ARRAY[102], 
    ARRAY[25]         -- 25 Laptop Stands (triggers a discount and low stock alert)
);
```

---

### 🔍 View Outputs (Sample Data)

#### 📦 `customer_order_summary`

Displays the total number of items each customer ordered per order.

| customer_id | customer_name  | order_id | order_date | total_amount | total_items_ordered |
|-------------|----------------|----------|------------|--------------|----------------------|
| 3           | Joseph Lartey  | 2        | 2025-04-16 | 755.00       | 70                   |
| 4           | Bob Okala      | 1        | 2025-04-16 | 205.50       | 10                   |

---

#### 🧯 `low_stock_report`

Lists products where the current stock is below the reorder threshold.

| product_id | product_name  | stock_quantity | reorder_level | shortage |
|------------|---------------|----------------|----------------|----------|
| 102        | Laptop Stand  | 53             | 60             | 7        |

---

#### 💰 `customer_spending_tier`

Segments customers by their total spending amount.

| customer_id | customer_name  | total_spent | spending_tier |
|-------------|----------------|-------------|----------------|
| 3           | Joseph Lartey  | 755.00      | Gold           |
| 4           | Bob Okala      | 205.50      | Silver         |

> ℹ️ Note: Order IDs, dates, and totals are dynamically generated based on insert time and logic within the `place_order` function.

--- 


# Phase 4: Stock Replenishments and automation


### Procedure: Automatically Replenish Stock When Product is Below Reorder Level

Created a procedure `replenish_stock` to automatically replenishes stock for products that are below their reorder level in the `products` table. It updates the stock quantity and logs the replenishment in the `inventory_logs` table.

### Logic
   - The procedure loops through all products in the `products` table where the stock quantity is less than the reorder level.
   - For each product, the required quantity is calculated as the difference between the reorder level and the current stock quantity. 
   - The stock quantity of the product is updated by adding the calculated quantity to reach the reorder level
   - A record is inserted into the `inventory_logs` table to track the replenishment, including the product ID, quantity added, and the type of change (`'replenishment'`):
   - A notification (`RAISE NOTICE`) is displayed to inform which product has been replenished and by how much:

This procedure ensures that products that fall below their reorder level are automatically replenished and logged in the system, while notifying the user about the changes made.

![Schema Creation Script](sql_scripts/04_restock_procedure.sql)
