import random
import csv
from datetime import timedelta, datetime
import os
import time

# --- Data Definitions ---
first_names = ['Basit', 'Jason', 'James', 'Hakeem', 'Jemima', 'Courage', 'Deborah', 'Kwaku',
               'Kwesi', 'Kwame', 'Enoch', 'Peter', 'Richard', 'Eugenia']
last_names = ['Johnson', 'Adjei', 'Osei', 'Kwakye', 'Agu-White', 'Amoako', 'Class-Peters', 'Wikireh',
              'Boateng', 'Essuman', 'Obeng', 'Sokpor', 'Adjei']
event_status = ['Viewed', 'Purchased']
products_data = [
    {'id': 1, 'name': 'Wireless Mouse', 'description': 'Wireless mouse with 2.4GHz wireless technology', 'price': 29.99, 'category': 'Electronics'},
    {'id': 2, 'name': 'Keyboard', 'description': 'Mechanical gaming keyboard with RGB backlighting', 'price': 89.99, 'category': 'Electronics'},
    {'id': 3, 'name': 'Headphones', 'description': 'Noise-cancelling headphones with 30-hour battery life', 'price': 199.99, 'category': 'Electronics'},
    {'id': 4, 'name': 'Mousepad', 'description': 'Gaming mousepad with anti-slip surface', 'price': 19.99, 'category': 'Accessories'},
    {'id': 5, 'name': 'Webcam', 'description': 'HD webcam with privacy shutter', 'price': 49.99, 'category': 'Electronics'},
    {'id': 6, 'name': 'Laptop Stand', 'description': 'Adjustable laptop stand for ergonomic positioning', 'price': 39.99, 'category': 'Accessories'},
    {'id': 7, 'name': 'USB Hub', 'description': '4-port USB 3.0 hub with power adapter', 'price': 24.99, 'category': 'Electronics'},
    {'id': 8, 'name': 'Wireless Charger', 'description': 'Fast wireless charging pad for smartphones', 'price': 34.99, 'category': 'Electronics'},
    {'id': 9, 'name': 'Bluetooth Speaker', 'description': 'Portable waterproof Bluetooth speaker', 'price': 79.99, 'category': 'Electronics'},
    {'id': 10, 'name': 'Smart Watch', 'description': 'Fitness tracker with heart rate monitor', 'price': 149.99, 'category': 'Electronics'},
    {'id': 11, 'name': 'Samsung TV 55 inch', 'description': '55 inch Samsung UHD Display', 'price': 4499.99, 'category': 'Electronics'},
    {'id': 12, 'name': 'PlayStation Dualshock 4', 'description': 'Black playstation game controller', 'price': 98.99, 'category': 'Accessories'}
]

# --- Generate Customers ---
num_customers = 100
customers = []
for i in range(1, num_customers + 1):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    customer_name = f"{first_name} {last_name}"
    customer_id = f"user_{i:03d}"
    customers.append({"user_id": customer_id, "name": customer_name})

# --- Configuration for File Generation ---
output_directory = os.path.join('data', 'csv_data')
os.makedirs(output_directory, exist_ok=True)  # make the directory if it doesn't exist
file_counter = 1
events_per_file = 200
generate_interval = 20  # generate a new file every 20 seconds

# Time range for random timestamps
now = datetime.now()
time_difference = timedelta(days=30)  # 30 days range

# --- Event Generation and Writing Loop ---
while True:
    events = []
    for _ in range(events_per_file):
        customer = random.choice(customers)
        user_id = customer['user_id']
        user_name = customer['name']

        status = random.choice(event_status)
        product = random.choice(products_data)
        product_name = f"Product: {product['name']}"
        product_description = f"Description: {product['description']}"
        product_price = f"Price: {product['price']}"

 # Generate a random timestamp within the last 30 days and the current time
        random_seconds = random.randint(0, int(time_difference.total_seconds()))
        random_past_time = now - timedelta(seconds=random_seconds)
        event_time = random_past_time.strftime("%Y-%m-%d %H:%M:%S")

        event_row = [user_id, user_name, status, product_name, product_description, product_price, event_time]
        events.append(event_row)

    # Save events to CSV file
    csv_file_path = os.path.join(output_directory, f'events_{file_counter}.csv')
    try:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['User ID', 'User Name', 'Status', 'Product Name', 'Product Description', 'Product Price', 'Event Time'])
            writer.writerows(events)
        print(f"Successfully generated {events_per_file} events and saved to {csv_file_path}")
        file_counter += 1
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

    time.sleep(generate_interval)

