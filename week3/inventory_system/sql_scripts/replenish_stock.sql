-- Create a procedure to automatically replenish stock
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

