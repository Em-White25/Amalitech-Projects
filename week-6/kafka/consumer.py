import json
import psycopg2
from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HeartbeatConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='heartbeat-data'):
        """
        Initialize the Kafka consumer and database connection.
        
        Args:
            bootstrap_servers (str): Kafka broker address
            topic (str): Kafka topic name
        """
        # Store topic for later use
        self.topic = topic
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='heartbeat-processor'
        )
        
        # Database configuration
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'heartbeat_db'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
        }
        
        # Initialize database connection
        self.conn = self._create_db_connection()
        self.cursor = self.conn.cursor()
        
        # Define heart rate thresholds
        self.min_heart_rate = 30
        self.max_heart_rate = 200
        self.warning_threshold_high = 160
        self.warning_threshold_low = 40
        
    def _create_db_connection(self):
        """Create and return a PostgreSQL database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            logger.info("Successfully connected to PostgreSQL database")
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def validate_heart_rate(self, heart_rate, customer_id):
        """
        Validate heart rate and check for anomalies.
        
        Args:
            heart_rate (int): Heart rate value to validate
            customer_id (str): Customer ID for logging
            
        Returns:
            tuple: (is_valid, is_anomaly, message)
        """
        if heart_rate < self.min_heart_rate:
            return False, True, f"Critical: Heart rate too low ({heart_rate} bpm)"
        elif heart_rate > self.max_heart_rate:
            return False, True, f"Critical: Heart rate too high ({heart_rate} bpm)"
        elif heart_rate > self.warning_threshold_high:
            return True, True, f"Warning: Elevated heart rate ({heart_rate} bpm)"
        elif heart_rate < self.warning_threshold_low:
            return True, True, f"Warning: Low heart rate ({heart_rate} bpm)"
        return True, False, "Normal heart rate"
    
    def store_record(self, record, is_anomaly=False, anomaly_message=None):
        """
        Store heartbeat record in PostgreSQL.
        
        Args:
            record (dict): Heartbeat record to store
            is_anomaly (bool): Whether the record contains an anomaly
            anomaly_message (str): Description of the anomaly if any
        """
        try:
            self.cursor.execute("""
                INSERT INTO heartbeat_records 
                (customer_id, timestamp, heart_rate, is_anomaly, anomaly_message)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                record['customer_id'],
                record['timestamp'],
                record['heart_rate'],
                is_anomaly,
                anomaly_message
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error storing record: {e}")
            self.conn.rollback()
            return False
    
    def process_record(self, record):
        """
        Process a single heartbeat record.
        
        Args:
            record (dict): Heartbeat record to process
        """
        try:
            # Validate heart rate
            is_valid, is_anomaly, message = self.validate_heart_rate(
                record['heart_rate'],
                record['customer_id']
            )
            
            if is_valid:
                # Store the record
                if self.store_record(record, is_anomaly, message if is_anomaly else None):
                    if is_anomaly:
                        logger.warning(f"Customer {record['customer_id']}: {message}")
                    else:
                        logger.info(f"Stored normal heartbeat for customer {record['customer_id']}: {record['heart_rate']} bpm")
            else:
                logger.error(f"Customer {record['customer_id']}: {message}")
                
        except Exception as e:
            logger.error(f"Error processing record: {e}")
    
    def run(self):
        """Start consuming and processing heartbeat data."""
        logger.info(f"Starting to consume from topic: {self.topic}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            for message in self.consumer:
                self.process_record(message.value)
                
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.cursor.close()
            self.conn.close()
            self.consumer.close()

def main():
    # Get configuration from environment variables or use defaults
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic = os.getenv('KAFKA_TOPIC', 'heartbeat-data')
    
    # Create and run the consumer
    consumer = HeartbeatConsumer(
        bootstrap_servers=bootstrap_servers,
        topic=topic
    )
    consumer.run()

if __name__ == "__main__":
    main() 