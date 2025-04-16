-- This function simulates the order process
-- It accepts products, inserts into orders, and order_details
-- deducts stocks from products and logs each deduction in inventory_logs

CREATE OR REPLACE FUNCTION place_order(
    p_customer_id INT, -- the customer placing the order
    p_status VARCHAR, -- order status
    p_product_ids INT[], -- product id(s)
    p_quantities INT[] -- quantities
)
RETURNS VOID AS $$
DECLARE
    v_order_id INT;
    v_total_amount NUMERIC(10, 2) := 0;
    i INT;
    v_unit_price NUMERIC(10, 2);
    v_total_price NUMERIC(10, 2);
    v_discount NUMERIC(10, 2) := 0; -- New variable for discount
BEGIN
    -- Insert into orders (temporarily zero total_amount)
    INSERT INTO orders (customer_id, order_date, total_amount, status)
    VALUES (p_customer_id, CURRENT_DATE, 0, p_status)
    RETURNING order_id INTO v_order_id;

    -- Loop through products array
    FOR i IN 1 .. array_length(p_product_ids, 1) LOOP
        -- Get unit price
        SELECT price INTO v_unit_price FROM products WHERE product_id = p_product_ids[i];

        -- Calculate item total
        v_total_price := v_unit_price * p_quantities[i];

        -- Check if the product qualifies for a bulk discount (if quantity >= 10, 7% off; >= 20, 15% off)
        IF p_quantities[i] >= 10 THEN
            v_discount := v_total_price * 0.07; -- 7% off for 10 or more
        ELSIF p_quantities[i] >= 5 THEN
            v_discount := v_total_price * 0.15; -- 15% off for 5 or more
        ELSE
            v_discount := 0; -- No discount for less than 5
        END IF;

        -- Apply the discount to the item total
        v_total_price := v_total_price - v_discount;

        -- Insert into order_details with discounted price
        INSERT INTO order_details (order_id, product_id, quantity, unit_price, total_amount)
        VALUES (v_order_id, p_product_ids[i], p_quantities[i], v_unit_price, v_total_price);

        -- Update product stock
        UPDATE products
        SET stock_quantity = stock_quantity - p_quantities[i]
        WHERE product_id = p_product_ids[i];

        -- Insert into inventory_logs
        INSERT INTO inventory_logs (product_id, change_quantity, change_type)
        VALUES (p_product_ids[i], -p_quantities[i], 'sale');

        -- Add to order total
        v_total_amount := v_total_amount + v_total_price;
    END LOOP;

    -- Update total_amount in orders
    UPDATE orders SET total_amount = v_total_amount WHERE order_id = v_order_id;

    RAISE NOTICE 'Order % placed successfully with total $%s after discount', v_order_id, v_total_amount;
END;
$$ LANGUAGE plpgsql;

