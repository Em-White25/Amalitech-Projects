import random
import csv
from datetime import datetime, timedelta
import os

# Customer data
first_names = ['Basit', 'Jason', 'James', 'Hakeem', 'Jemima', 'Courage', 'Deborah', 'Kwaku', 
            'Kwesi', 'Kwame', 'Enoch', 'Peter', 'Richard', 'Eugenia']

#last names
last_names = ['Johnson', 'Adjei', 'Osei', 'Kwakye', 'Agu-White', 'Amoako', 'Class-Peters', 'Wikireh', 
              'Boateng', 'Essuman', 'Obeng', 'Sokpor', 'Adjei']

#status of the event
status = ['Viewed', 'Purchased']


# Product data
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'description': 'Wireless mouse with 2.4GHz wireless technology', 'price': 29.99, 'category': 'Electronics'},
    {'id': 2, 'name': 'Keyboard', 'description': 'Mechanical gaming keyboard with RGB backlighting', 'price': 89.99, 'category': 'Electronics'},
    {'id': 3, 'name': 'Headphones', 'description': 'Noise-cancelling headphones with 30-hour battery life', 'price': 199.99, 'category': 'Electronics'},
    {'id': 4, 'name': 'Mousepad', 'description': 'Gaming mousepad with anti-slip surface', 'price': 19.99, 'category': 'Accessories'},
    {'id': 5, 'name': 'Webcam', 'description': 'HD webcam with privacy shutter', 'price': 49.99, 'category': 'Electronics'},
    {'id': 6, 'name': 'Laptop Stand', 'description': 'Adjustable laptop stand for ergonomic positioning', 'price': 39.99, 'category': 'Accessories'},
    {'id': 7, 'name': 'USB Hub', 'description': '4-port USB 3.0 hub with power adapter', 'price': 24.99, 'category': 'Electronics'},
    {'id': 8, 'name': 'Wireless Charger', 'description': 'Fast wireless charging pad for smartphones', 'price': 34.99, 'category': 'Electronics'},
    {'id': 9, 'name': 'Bluetooth Speaker', 'description': 'Portable waterproof Bluetooth speaker', 'price': 79.99, 'category': 'Electronics'},
    {'id': 10, 'name': 'Smart Watch', 'description': 'Fitness tracker with heart rate monitor', 'price': 149.99, 'category': 'Electronics'}
]


#generate 100 customers
customers = []
for i in range(1, 101): 
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"
    user_id = f"user_{i:03d}" 
    
    customers.append({
        "user_id": user_id,
        "name": full_name
    })



# Random customer
customer = random.choice(customers)
user_id = customer['user_id']
user_name = customer['name']

# Random action
action = random.choice(status)

# Random product
product = random.choice(products)
product_name= f'Product: {product['name']}'
product_description= f'Description: {product['description']}' 
product_price= f'Price: {product['price']}'




#write to csv file
## number of files to create
file_num = 2


# Generate events for each file
for file_num in range(1, 3):
    events = []
    for _ in range(200):
        # Random customer
        customer = random.choice(customers)
        user_id = customer['user_id']
        user_name = customer['name']

        # Random action
        action = random.choice(status)

        # Random product
        product = random.choice(products)
        product_name = f'Product: {product["name"]}'
        product_description = f'Description: {product["description"]}' 
        product_price = f'Price: {product["price"]}'

        # Current time
        event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create event row
        event_row = [user_id, user_name, action, product_name, product_description, product_price, event_time]
        events.append(event_row)

    # Save events to CSV file
    csv_file_path = os.path.join('data', 'csv_data', f'events_{file_num}.csv')
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['User ID', 'User Name', 'Action', 'Product Name', 'Product Description', 'Product Price', 'Event Time'])
        writer.writerows(events)

    print(f"Successfully generated 200 events and saved to {csv_file_path}")

'''
    CLEAN THIS UP LATER. THINGS TO ADD:
    - randomize the number of events per file
    - randomize the number the event times 
    - maybe add more products
    - add error handling
'''