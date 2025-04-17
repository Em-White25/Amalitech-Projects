-- Create a procedure to automatically replenish stock when the product is below the reorder level
CREATE OR REPLACE PROCEDURE replenish_stock()
LANGUAGE plpgsql
AS $$
DECLARE
    p RECORD;					-- p is a variable that will hold one row(RECORD) of the from the products table at a time.
    qty_to_add INT;				-- stores how much quantity of items to be added.
BEGIN
    -- Loop through products that are low in stock
    FOR p IN 		-- for record in products less than the reorder level
        SELECT product_id, stock_quantity, reorder_level 
        FROM products 
        WHERE stock_quantity < reorder_level
    LOOP
        -- Calculate how much stock to add to reach 100% of reorder level
        qty_to_add := CEIL((p.reorder_level * 1.00) - p.stock_quantity);

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

