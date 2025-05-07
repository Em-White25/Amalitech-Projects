-- Connect to the database
\c heartbeat_db;

-- Create the heartbeat_records table
CREATE TABLE heartbeat_records (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    heart_rate INTEGER NOT NULL,
    is_anomaly BOOLEAN DEFAULT FALSE,
    anomaly_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX idx_heartbeat_customer_id ON heartbeat_records(customer_id);
CREATE INDEX idx_heartbeat_timestamp ON heartbeat_records(timestamp);
CREATE INDEX idx_heartbeat_anomaly ON heartbeat_records(is_anomaly);

-- Add constraints
ALTER TABLE heartbeat_records
    ADD CONSTRAINT valid_heart_rate CHECK (heart_rate >= 30 AND heart_rate <= 200); 