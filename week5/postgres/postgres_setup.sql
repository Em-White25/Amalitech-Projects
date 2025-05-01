/*

Create an order_events table
*/
DROP TABLE IF EXISTS user_events;
CREATE TABLE user_events (
    user_id TEXT,
    user_name TEXT,
    status TEXT,
    product_name TEXT,
    product_description TEXT,
    product_price FLOAT,
    event_time TIMESTAMP
);
