import random
import time
from datetime import datetime
from faker import Faker
import json

class HeartbeatGenerator:
    def __init__(self, num_customers=50):
        self.fake = Faker()
        # Generate a pool of customer IDs with simple format CUST001, CUST002, etc.
        self.customer_ids = [f"CUST{str(i+1).zfill(3)}" for i in range(num_customers)]
        self.current_customer_index = 0
        
        # Define normal heart rate ranges (in bpm)
        self.normal_resting_range = (60, 100)  # Normal resting heart rate
        self.exercise_range = (100, 160)       # Exercise heart rate
        self.sleep_range = (40, 60)            # Sleep heart rate
        
    def generate_heart_rate(self, customer_id):
        """
        Generate a realistic heart rate value with some variation.
        Uses the customer_id to ensure consistent patterns for each customer.
        """
        # Use customer_id to create a consistent pattern
        random.seed(hash(customer_id) + int(time.time() / 30))  # Change pattern every 30 seconds
        
        # Randomly choose a state (resting, exercise, or sleep)
        state = random.choices(
            ['resting', 'exercise', 'sleep'],
            weights=[0.7, 0.2, 0.1]  # 70% resting, 20% exercise, 10% sleep
        )[0]
        
        # Generate base heart rate based on state
        if state == 'resting':
            base_rate = random.randint(*self.normal_resting_range)
        elif state == 'exercise':
            base_rate = random.randint(*self.exercise_range)
        else:  # sleep
            base_rate = random.randint(*self.sleep_range)
        
        # Add more natural variation
        variation = random.gauss(0, 3)  # Gaussian distribution for more natural variation
        heart_rate = base_rate + variation
        
        # Ensure heart rate stays within reasonable bounds
        return max(30, min(200, int(heart_rate)))
    
    def generate_record(self):
        """Generate a single heartbeat record."""
        # Use round-robin selection instead of random choice for better distribution
        customer_id = self.customer_ids[self.current_customer_index]
        self.current_customer_index = (self.current_customer_index + 1) % len(self.customer_ids)
        
        return {
            'customer_id': customer_id,
            'timestamp': datetime.utcnow().isoformat(),
            'heart_rate': self.generate_heart_rate(customer_id)
        }
    
    def generate_batch(self, num_records=1):
        """Generate multiple heartbeat records."""
        return [self.generate_record() for _ in range(num_records)]

def main():
    # Create generator with 50 customers
    generator = HeartbeatGenerator(num_customers=50)
    
    print("Starting to generate heartbeat data...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate a single record
            record = generator.generate_record()
            
            # Print the record in a readable format
            print(f"\nCustomer: {record['customer_id']}")
            print(f"Timestamp: {record['timestamp']}")
            print(f"Heart Rate: {record['heart_rate']} bpm")
            
            # Wait for 1 second before generating next record
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping data generation...")

if __name__ == "__main__":
    main() 