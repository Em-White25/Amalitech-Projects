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
