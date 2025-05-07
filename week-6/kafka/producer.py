import json
from kafka import KafkaProducer
import time
from heartbeat_data_generator import HeartbeatGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HeartbeatProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='heartbeat-data'):
        """
        Initialize the Kafka producer and heartbeat generator.
        
        Args:
            bootstrap_servers (str): Kafka broker address
            topic (str): Kafka topic name
        """
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,   # Retry failed requests
            max_in_flight_requests_per_connection=1  # Ensure ordering
        )
        
        # Initialize heartbeat generator
        self.generator = HeartbeatGenerator(num_customers=10)
        self.topic = topic
        
    def send_record(self, record):
        """
        Send a single heartbeat record to Kafka.
        
        Args:
            record (dict): Heartbeat record to send
        """
        try:
            # Send the record to Kafka
            future = self.producer.send(self.topic, value=record)
            
            # Wait for the send to complete
            future.get(timeout=10)
            
            print(f"Sent heartbeat data for customer {record['customer_id']}: {record['heart_rate']} bpm")
            return True
            
        except Exception as e:
            print(f"Error sending record: {e}")
            return False
    
    def run(self, interval=1.0):
        """
        Continuously generate and send heartbeat data.
        
        Args:
            interval (float): Time between records in seconds
        """
        print(f"Starting to produce heartbeat data to topic: {self.topic}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Generate a record
                record = self.generator.generate_record()
                
                # Send to Kafka
                self.send_record(record)
                
                # Wait for the specified interval
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nStopping producer...")
        finally:
            # Ensure all messages are sent before closing
            self.producer.flush()
            self.producer.close()

def main():
    # Get Kafka configuration from environment variables or use defaults
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    topic = os.getenv('KAFKA_TOPIC', 'heartbeat-data')
    
    # Create and run the producer
    producer = HeartbeatProducer(
        bootstrap_servers=bootstrap_servers,
        topic=topic
    )
    producer.run()

if __name__ == "__main__":
    main() 