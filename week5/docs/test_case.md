Field | Details
Test Case | 01. Test if CSV files are created correctly with correct headers and at least one event.
          | 02. Test if 200 events were created successfully
          | 03. Test if data was written to data/csv_data directory
          | 04. Test if file was named incrementally as they are written. 
Input | Run data_generator.py script
Expected Output | New CSV files with user_id, user_name, action, product_name, product_description, product_price, event_time columns and at least 1 event
Actual Output | 200 Events created successfully. All files created with headers and has at least one event. Files named incrementally.. eg. events_01, events_02
Result | Pass
