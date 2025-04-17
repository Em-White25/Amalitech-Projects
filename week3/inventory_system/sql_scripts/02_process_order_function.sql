/*
	The function handles the complete order process and workflow of: 
	* Adding to orders
	* Adding to order details
	* Deducts from products
	* Logs changes in the inventory
*/
CREATE OR REPLACE FUNCTION place_order(
    p_customer_id INT,				 	-- takes customer placing the order
    p_status VARCHAR,				 	-- order status
    p_product_ids INT[], 			 	-- takes the list products (an array of product id(s))
    p_quantities INT[]				 	-- quantity of products ordered 
)
RETURNS VOID AS $$
DECLARE
    v_order_id INT;					-- creates a local variable for order_id in the function
    v_total_amount NUMERIC(10, 2) := 0;			-- holds the total amount of the order
    i INT;						-- variable for a counter for looping
    v_unit_price NUMERIC(10, 2);			-- stores the unit price of the product
    v_total_price NUMERIC(10, 2);			-- stores the total price of the order made
    v_discount NUMERIC(10, 2) := 0; 			-- stores a the discount value
BEGIN
    -- A new order is processed and the order_id is inserted into the local variable v_order_id
    INSERT INTO orders (customer_id, order_date, total_amount, status)
    VALUES (p_customer_id, CURRENT_DATE, 0, p_status)
    RETURNING order_id INTO v_order_id;

    -- Loop through products array. Process each product in the order

    FOR i IN 1 .. array_length(p_product_ids, 1) LOOP
        -- Get unit price
        SELECT price INTO v_unit_price FROM products WHERE product_id = p_product_ids[i];

        -- Calculate item total
        v_total_price := v_unit_price * p_quantities[i];

        -- Check if the product qualifies for a bulk discount (if quantity >= 10, 7% off; >= 20, 15% off)
        IF p_quantities[i] >= 10 THEN
            v_discount := v_total_price * 0.07; -- 7% off for 10 or more
        ELSIF p_quantities[i] >= 20 THEN
            v_discount := v_total_price * 0.15; -- 15% off for 5 or more
        ELSE
            v_discount := 0; -- No discount for less than 10. The economy is hard!
        END IF;

        -- Apply the discount to the item total. Subtract the discount from the total price
        v_total_price := v_total_price - v_discount;

        -- Insert each order into the order_details with discounted price
        INSERT INTO order_details (order_id, product_id, quantity, unit_price, total_amount)
        VALUES (v_order_id, p_product_ids[i], p_quantities[i], v_unit_price, v_total_price);

        -- Update the product's stock after
        UPDATE products
        SET stock_quantity = stock_quantity - p_quantities[i]
        WHERE product_id = p_product_ids[i];

        -- Log the change into the inventory table.
        INSERT INTO inventory_logs (product_id, change_quantity, change_type)
        VALUES (p_product_ids[i], -p_quantities[i], 'sale');

        -- Add the total order cost
        v_total_amount := v_total_amount + v_total_price;
    END LOOP;

    -- Update total amount (final order)
    UPDATE orders SET total_amount = v_total_amount WHERE order_id = v_order_id;

    -- show a message confirming order: displays the order id and total
    RAISE NOTICE 'Order % placed successfully with total $%s after discount', v_order_id, v_total_amount;
END;
$$ LANGUAGE plpgsql;

