import requests
import zipfile
import os
import logging
import pandas as pd
import mysql.connector
from mysql.connector import Error
import psycopg2
from psycopg2 import Error as PostgresError
from concurrent.futures import ThreadPoolExecutor
import time
from airflow.utils.log.logging_mixin import LoggingMixin

# Configure logging
log_file = '/opt/airflow/data/logs/flight_pipeline.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Create file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

def get_logger():
    """Get a configured logger instance."""
    logger = LoggingMixin().log
    logger.addHandler(file_handler)
    return logger

def download_and_extract():
    """Download and extract the flight dataset."""
    logger = get_logger()
    
    try:
        # Create data directory if it doesn't exist
        logger.info("Creating data directory...")
        os.makedirs('/opt/airflow/data', exist_ok=True)
        
        # Download the file
        url = "https://www.kaggle.com/api/v1/datasets/download/mahatiratusher/flight-price-dataset-of-bangladesh"
        zip_path = "/opt/airflow/data/flight-price-dataset-of-bangladesh.zip"
        
        logger.info("Starting download of dataset...")
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("Request timed out while downloading dataset")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while downloading dataset: {str(e)}")
            raise
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.error("Rate limit exceeded for Kaggle API. Please try again later.")
            else:
                logger.error(f"HTTP error occurred: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while downloading dataset: {str(e)}")
            raise
        
        # Write the file
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info("Download complete. Starting extraction...")
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('/opt/airflow/data')
        
        logger.info("Dataset downloaded and extracted successfully!")
        
    except Exception as e:
        logger.error(f"Unexpected error in download_and_extract: {str(e)}")
        raise

def load_data_to_mysql():
    """Load flight data into MySQL database."""
    logger = get_logger()
    
    try:
        # Read CSV file
        logger.info("Reading CSV file...")
        df = pd.read_csv('/opt/airflow/data/flight-price-dataset-of-bangladesh.csv')
        
        # Connect to MySQL
        logger.info("Connecting to MySQL...")
        connection = mysql.connector.connect(
            host='mysql',
            database='flight_db',
            user='root',
            password='rootpassword'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create table
            logger.info("Creating table if not exists...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS flight_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Airline VARCHAR(255),
                Source VARCHAR(255),
                `Source Name` VARCHAR(255),
                Destination VARCHAR(255),
                `Destination Name` VARCHAR(255),
                `Departure Date & Time` VARCHAR(255),
                `Arrival Date & Time` VARCHAR(255),
                `Duration (hrs)` DOUBLE,
                Stopovers VARCHAR(255),
                `Aircraft Type` VARCHAR(255),
                Class VARCHAR(255),
                `Booking Source` VARCHAR(255),
                `Base Fare (BDT)` DECIMAL(10, 2),
                `Tax & Surcharge (BDT)` DECIMAL(10, 2),
                `Total Fare (BDT)` DECIMAL(10, 2),
                Seasonality VARCHAR(255),
                `Days Before Departure` INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            
            # Insert data
            logger.info("Inserting data...")
            for _, row in df.iterrows():
                insert_query = """
                INSERT INTO flight_data (
                    Airline, Source, `Source Name`, Destination, `Destination Name`,
                    `Departure Date & Time`, `Arrival Date & Time`, `Duration (hrs)`,
                    Stopovers, `Aircraft Type`, Class, `Booking Source`,
                    `Base Fare (BDT)`, `Tax & Surcharge (BDT)`, `Total Fare (BDT)`,
                    Seasonality, `Days Before Departure`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = tuple(row)
                cursor.execute(insert_query, values)
            
            connection.commit()
            logger.info("Data loaded successfully!")
            
    except Error as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection closed")

def validate_flight_data():
    """Validate the flight data in MySQL database."""
    logger = get_logger()
    
    try:
        # Connect to MySQL
        logger.info("Connecting to MySQL for data validation...")
        connection = mysql.connector.connect(
            host='mysql',
            database='flight_db',
            user='root',
            password='rootpassword'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # 1. Check required columns exist with correct data types
            logger.info("Checking required columns and data types...")
            required_columns = {
                'id': 'int',
                'Airline': 'varchar(255)',
                'Source': 'varchar(255)',
                'Source Name': 'varchar(255)',
                'Destination': 'varchar(255)',
                'Destination Name': 'varchar(255)',
                'Departure Date & Time': 'varchar(255)',
                'Arrival Date & Time': 'varchar(255)',
                'Duration (hrs)': 'double',
                'Stopovers': 'varchar(255)',
                'Aircraft Type': 'varchar(255)',
                'Class': 'varchar(255)',
                'Booking Source': 'varchar(255)',
                'Base Fare (BDT)': 'decimal(10,2)',
                'Tax & Surcharge (BDT)': 'decimal(10,2)',
                'Total Fare (BDT)': 'decimal(10,2)',
                'Seasonality': 'varchar(255)',
                'Days Before Departure': 'int',
                'created_at': 'timestamp'
            }
            
            cursor.execute("DESCRIBE flight_data")
            existing_columns = {row['Field']: row['Type'] for row in cursor.fetchall()}
            
            for col, expected_type in required_columns.items():
                if col not in existing_columns:
                    raise ValueError(f"Missing required column: {col}")
                if existing_columns[col].lower() != expected_type.lower():
                    logger.warning(f"Column {col} has type {existing_columns[col]}, expected {expected_type}")
            
            # 2. Check for null values in critical fields
            logger.info("Checking for null values in critical fields...")
            critical_fields = [
                'Airline', 'Source', 'Destination', 
                'Departure Date & Time', 'Arrival Date & Time',
                'Base Fare (BDT)', 'Tax & Surcharge (BDT)', 'Total Fare (BDT)'
            ]
            
            # Build the null check query with properly escaped column names
            null_conditions = []
            for field in critical_fields:
                null_conditions.append(f"`{field}` IS NULL")
            
            null_check_query = f"""
            SELECT COUNT(*) as null_count
            FROM flight_data
            WHERE {' OR '.join(null_conditions)}
            """
            
            cursor.execute(null_check_query)
            null_count = cursor.fetchone()['null_count']
            if null_count > 0:
                logger.warning(f"Found {null_count} rows with null values in critical fields")
            
            # 3. Validate numeric values
            logger.info("Validating numeric values...")
            numeric_validation_query = """
            SELECT COUNT(*) as invalid_count
            FROM flight_data
            WHERE `Base Fare (BDT)` < 0 
               OR `Tax & Surcharge (BDT)` < 0 
               OR `Total Fare (BDT)` < 0
               OR `Duration (hrs)` < 0
               OR `Days Before Departure` < 0
               OR `Base Fare (BDT)` > 1000000  -- Reasonable upper limit
               OR `Tax & Surcharge (BDT)` > 1000000
               OR `Total Fare (BDT)` > 1000000
            """
            cursor.execute(numeric_validation_query)
            invalid_numeric = cursor.fetchone()['invalid_count']
            if invalid_numeric > 0:
                logger.warning(f"Found {invalid_numeric} rows with invalid numeric values")
            
            # 4. Validate string fields
            logger.info("Validating string fields...")
            string_validation_query = """
            SELECT COUNT(*) as empty_count
            FROM flight_data
            WHERE TRIM(`Airline`) = '' 
               OR TRIM(`Source`) = '' 
               OR TRIM(`Destination`) = ''
               OR TRIM(`Aircraft Type`) = ''
               OR TRIM(`Class`) = ''
               OR TRIM(`Booking Source`) = ''
               OR TRIM(`Seasonality`) = ''
            """
            cursor.execute(string_validation_query)
            empty_strings = cursor.fetchone()['empty_count']
            if empty_strings > 0:
                logger.warning(f"Found {empty_strings} rows with empty string values")
            
            # 5. Validate date fields
            logger.info("Validating date fields...")
            date_validation_query = """
            SELECT COUNT(*) as invalid_dates
            FROM flight_data
            WHERE STR_TO_DATE(`Departure Date & Time`, '%Y-%m-%d %H:%i:%s') IS NULL
               OR STR_TO_DATE(`Arrival Date & Time`, '%Y-%m-%d %H:%i:%s') IS NULL
               OR STR_TO_DATE(`Departure Date & Time`, '%Y-%m-%d %H:%i:%s') > STR_TO_DATE(`Arrival Date & Time`, '%Y-%m-%d %H:%i:%s')
            """
            cursor.execute(date_validation_query)
            invalid_dates = cursor.fetchone()['invalid_dates']
            if invalid_dates > 0:
                logger.warning(f"Found {invalid_dates} rows with invalid date formats or illogical date sequences")
            
            # 6. Check for data consistency
            logger.info("Checking data consistency...")
            consistency_query = """
            SELECT COUNT(*) as inconsistent_count
            FROM flight_data
            WHERE ABS((`Base Fare (BDT)` + `Tax & Surcharge (BDT)`) - `Total Fare (BDT)`) > 0.01
               OR `Duration (hrs)` > 24  -- Unreasonable flight duration
               OR `Days Before Departure` > 365  -- Unreasonable booking window
            """
            cursor.execute(consistency_query)
            inconsistent_rows = cursor.fetchone()['inconsistent_count']
            if inconsistent_rows > 0:
                logger.warning(f"Found {inconsistent_rows} rows with inconsistent data")
            
            # 7. Check for duplicate entries
            logger.info("Checking for duplicate entries...")
            duplicate_check_query = """
            SELECT COUNT(*) as duplicate_count
            FROM (
                SELECT 
                    `Airline`, `Source`, `Destination`, 
                    `Departure Date & Time`, `Arrival Date & Time`,
                    COUNT(*) as count
                FROM flight_data
                GROUP BY 
                    `Airline`, `Source`, `Destination`, 
                    `Departure Date & Time`, `Arrival Date & Time`
                HAVING COUNT(*) > 1
            ) as duplicates
            """
            cursor.execute(duplicate_check_query)
            duplicate_count = cursor.fetchone()['duplicate_count']
            if duplicate_count > 0:
                logger.warning(f"Found {duplicate_count} sets of duplicate flight entries")
            
            # Log summary
            logger.info("Data validation completed successfully!")
            logger.info(f"Summary of findings:")
            logger.info(f"- Null values in critical fields: {null_count}")
            logger.info(f"- Invalid numeric values: {invalid_numeric}")
            logger.info(f"- Empty string values: {empty_strings}")
            logger.info(f"- Invalid date formats/sequences: {invalid_dates}")
            logger.info(f"- Inconsistent data: {inconsistent_rows}")
            logger.info(f"- Duplicate entries: {duplicate_count}")
            
    except Error as e:
        logger.error(f"Error during data validation: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection closed")

def transform_and_kpis_analysis():
    """Transform data and compute KPIs in MySQL database."""
    logger = get_logger()
    
    try:
        # Connect to MySQL
        logger.info("Connecting to MySQL for data transformation and KPI computation...")
        connection = mysql.connector.connect(
            host='mysql',
            database='flight_db',
            user='root',
            password='rootpassword'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 1. Create KPI tables
            logger.info("Creating KPI tables...")
            
            # Table for airline metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS airline_metrics (
                airline VARCHAR(255) PRIMARY KEY,
                avg_fare DECIMAL(10,2),
                booking_count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Table for seasonal metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS seasonal_metrics (
                season VARCHAR(255),
                avg_fare DECIMAL(10,2),
                booking_count INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (season)
            )
            """)
            
            # Table for route metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS route_metrics (
                source VARCHAR(255),
                destination VARCHAR(255),
                booking_count INT,
                avg_fare DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source, destination)
            )
            """)
            
            # 2. Update Total Fare if needed
            logger.info("Updating Total Fare calculations...")
            cursor.execute("""
            UPDATE flight_data 
            SET `Total Fare (BDT)` = `Base Fare (BDT)` + `Tax & Surcharge (BDT)`
            WHERE ABS((`Base Fare (BDT)` + `Tax & Surcharge (BDT)`) - `Total Fare (BDT)`) > 0.01
            """)
            
            # 3. Compute and store airline metrics
            logger.info("Computing airline metrics...")
            cursor.execute("""
            INSERT INTO airline_metrics (airline, avg_fare, booking_count)
            SELECT 
                Airline,
                AVG(`Total Fare (BDT)`) as avg_fare,
                COUNT(*) as booking_count
            FROM flight_data
            GROUP BY Airline
            ON DUPLICATE KEY UPDATE
                avg_fare = VALUES(avg_fare),
                booking_count = VALUES(booking_count)
            """)
            
            # 4. Compute and store seasonal metrics
            logger.info("Computing seasonal metrics...")
            cursor.execute("""
            INSERT INTO seasonal_metrics (season, avg_fare, booking_count)
            SELECT 
                Seasonality,
                AVG(`Total Fare (BDT)`) as avg_fare,
                COUNT(*) as booking_count
            FROM flight_data
            GROUP BY Seasonality
            ON DUPLICATE KEY UPDATE
                avg_fare = VALUES(avg_fare),
                booking_count = VALUES(booking_count)
            """)
            
            # 5. Compute and store route metrics
            logger.info("Computing route metrics...")
            cursor.execute("""
            INSERT INTO route_metrics (source, destination, booking_count, avg_fare)
            SELECT 
                Source,
                Destination,
                COUNT(*) as booking_count,
                AVG(`Total Fare (BDT)`) as avg_fare
            FROM flight_data
            GROUP BY Source, Destination
            ON DUPLICATE KEY UPDATE
                booking_count = VALUES(booking_count),
                avg_fare = VALUES(avg_fare)
            """)
            
            # 6. Log summary of computed metrics
            logger.info("Fetching summary of computed metrics...")
            
            # Airline metrics summary
            cursor.execute("""
            SELECT 
                COUNT(*) as total_airlines,
                AVG(avg_fare) as overall_avg_fare,
                SUM(booking_count) as total_bookings
            FROM airline_metrics
            """)
            airline_summary = cursor.fetchone()
            logger.info(f"Airline Metrics Summary:")
            logger.info(f"- Total Airlines: {airline_summary[0]}")
            logger.info(f"- Overall Average Fare: {airline_summary[1]:.2f}")
            logger.info(f"- Total Bookings: {airline_summary[2]}")
            
            # Seasonal metrics summary
            cursor.execute("""
            SELECT 
                COUNT(*) as total_seasons,
                AVG(avg_fare) as overall_avg_fare,
                SUM(booking_count) as total_bookings
            FROM seasonal_metrics
            """)
            seasonal_summary = cursor.fetchone()
            logger.info(f"Seasonal Metrics Summary:")
            logger.info(f"- Total Seasons: {seasonal_summary[0]}")
            logger.info(f"- Overall Average Fare: {seasonal_summary[1]:.2f}")
            logger.info(f"- Total Bookings: {seasonal_summary[2]}")
            
            # Route metrics summary
            cursor.execute("""
            SELECT 
                COUNT(*) as total_routes,
                AVG(avg_fare) as overall_avg_fare,
                SUM(booking_count) as total_bookings
            FROM route_metrics
            """)
            route_summary = cursor.fetchone()
            logger.info(f"Route Metrics Summary:")
            logger.info(f"- Total Routes: {route_summary[0]}")
            logger.info(f"- Overall Average Fare: {route_summary[1]:.2f}")
            logger.info(f"- Total Bookings: {route_summary[2]}")
            
            connection.commit()
            logger.info("Data transformation and KPI computation completed successfully!")
            
    except Error as e:
        logger.error(f"Error during data transformation and KPI computation: {e}")
        raise
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection closed")

def load_to_postgres():
    """Load data from MySQL to PostgreSQL."""
    logger = get_logger()
    
    mysql_conn = None
    postgres_conn = None
    mysql_cursors = {}
    postgres_cursor = None
    
    def create_mysql_connection():
        return mysql.connector.connect(
            host='mysql',
            database='flight_db',
            user='root',
            password='rootpassword',
            connect_timeout=30,
            connection_timeout=30
        )
    
    try:
        # Connect to both databases
        logger.info("Connecting to MySQL and PostgreSQL...")
        mysql_conn = create_mysql_connection()
        
        # First connect to default postgres database to create our database
        temp_postgres_conn = psycopg2.connect(
            host='postgres',
            database='airflow',  # Connect to default database first
            user='airflow',
            password='airflow',
            port=5432
        )
        
        # Create flight_analytics database if it doesn't exist
        temp_postgres_conn.autocommit = True
        temp_cursor = temp_postgres_conn.cursor()
        temp_cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'flight_analytics'")
        exists = temp_cursor.fetchone()
        if not exists:
            logger.info("Creating flight_analytics database...")
            temp_cursor.execute('CREATE DATABASE flight_analytics')
        temp_cursor.close()
        temp_postgres_conn.close()
        
        # Now connect to our newly created database
        postgres_conn = psycopg2.connect(
            host='postgres',
            database='flight_analytics',
            user='airflow',
            password='airflow',
            port=5432
        )
        
        if mysql_conn.is_connected() and postgres_conn:
            # Create a separate cursor for each table
            for table in ['airline_metrics', 'seasonal_metrics', 'route_metrics', 'flight_data']:
                mysql_cursors[table] = mysql_conn.cursor(dictionary=True)
            
            postgres_cursor = postgres_conn.cursor()
            
            # Create tables in PostgreSQL
            logger.info("Creating PostgreSQL tables...")
            
            # Create airline metrics table
            postgres_cursor.execute("""
            CREATE TABLE IF NOT EXISTS airline_metrics (
                airline VARCHAR(255) PRIMARY KEY,
                avg_fare DECIMAL(10,2),
                booking_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create seasonal metrics table
            postgres_cursor.execute("""
            CREATE TABLE IF NOT EXISTS seasonal_metrics (
                season VARCHAR(255) PRIMARY KEY,
                avg_fare DECIMAL(10,2),
                booking_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create route metrics table
            postgres_cursor.execute("""
            CREATE TABLE IF NOT EXISTS route_metrics (
                source VARCHAR(255),
                destination VARCHAR(255),
                booking_count INTEGER,
                avg_fare DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source, destination)
            )
            """)
            
            # Create raw flight data table
            postgres_cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_data (
                id SERIAL PRIMARY KEY,
                airline VARCHAR(255),
                source VARCHAR(255),
                source_name VARCHAR(255),
                destination VARCHAR(255),
                destination_name VARCHAR(255),
                departure_date_time TIMESTAMP,
                arrival_date_time TIMESTAMP,
                duration_hrs DOUBLE PRECISION,
                stopovers VARCHAR(255),
                aircraft_type VARCHAR(255),
                class VARCHAR(255),
                booking_source VARCHAR(255),
                base_fare_bdt DECIMAL(10,2),
                tax_surcharge_bdt DECIMAL(10,2),
                total_fare_bdt DECIMAL(10,2),
                seasonality VARCHAR(255),
                days_before_departure INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            postgres_conn.commit()
            
            def load_table(table_name, query, cursor):
                max_retries = 3
                retry_delay = 5  # seconds
                chunk_size = 10000
                
                # Map MySQL column names to PostgreSQL column names
                column_mapping = {
                    'Source Name': 'source_name',
                    'Destination Name': 'destination_name',
                    'Departure Date & Time': 'departure_date_time',
                    'Arrival Date & Time': 'arrival_date_time',
                    'Duration (hrs)': 'duration_hrs',
                    'Aircraft Type': 'aircraft_type',
                    'Booking Source': 'booking_source',
                    'Base Fare (BDT)': 'base_fare_bdt',
                    'Tax & Surcharge (BDT)': 'tax_surcharge_bdt',
                    'Total Fare (BDT)': 'total_fare_bdt',
                    'Days Before Departure': 'days_before_departure'
                }
                
                for attempt in range(max_retries):
                    try:
                        logger.info(f"Loading {table_name} (attempt {attempt + 1}/{max_retries})...")
                        
                        # Check if MySQL connection is still alive
                        if not mysql_conn.is_connected():
                            logger.info(f"MySQL connection lost, reconnecting...")
                            mysql_conn.reconnect(attempts=3, delay=5)
                            cursor = mysql_conn.cursor(dictionary=True)
                        
                        # Clear existing data
                        postgres_cursor.execute(f"TRUNCATE TABLE {table_name}")
                        postgres_conn.commit()
                        
                        # Get total count for progress tracking
                        count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_query"
                        cursor.execute(count_query)
                        total_rows = cursor.fetchone()['total']
                        logger.info(f"Total rows to load for {table_name}: {total_rows}")
                        
                        # Execute main query
                        cursor.execute(query)
                        
                        # Process in chunks
                        rows_processed = 0
                        while True:
                            rows = cursor.fetchmany(chunk_size)
                            if not rows:
                                break
                                
                            # Map column names for PostgreSQL
                            if table_name == 'flight_data':
                                mapped_columns = []
                                for col in rows[0].keys():
                                    mapped_columns.append(column_mapping.get(col, col.lower()))
                            else:
                                mapped_columns = [col.lower() for col in rows[0].keys()]
                            
                            # Prepare insert statement with properly quoted column names
                            placeholders = ','.join(['%s'] * len(mapped_columns))
                            insert_query = f"""
                            INSERT INTO {table_name} ({','.join(f'"{col}"' for col in mapped_columns)})
                            VALUES ({placeholders})
                            """
                            
                            # Insert chunk
                            postgres_cursor.executemany(insert_query, [tuple(row.values()) for row in rows])
                            postgres_conn.commit()
                            
                            rows_processed += len(rows)
                            logger.info(f"Loaded {rows_processed}/{total_rows} rows into {table_name}")
                        
                        logger.info(f"Successfully loaded all {rows_processed} rows into {table_name}")
                        return
                            
                    except mysql.connector.Error as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Error loading {table_name}: {e}. Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            # Try to reconnect
                            try:
                                mysql_conn.reconnect(attempts=3, delay=5)
                                cursor = mysql_conn.cursor(dictionary=True)
                            except:
                                pass
                        else:
                            logger.error(f"Failed to load {table_name} after {max_retries} attempts: {e}")
                            raise
                    except Exception as e:
                        logger.error(f"Unexpected error loading {table_name}: {e}")
                        raise
            
            # Define queries for each table
            queries = {
                'airline_metrics': "SELECT * FROM airline_metrics",
                'seasonal_metrics': "SELECT * FROM seasonal_metrics",
                'route_metrics': "SELECT * FROM route_metrics",
                'flight_data': """
                SELECT 
                    id, Airline, Source, `Source Name`, Destination, `Destination Name`,
                    STR_TO_DATE(`Departure Date & Time`, '%Y-%m-%d %H:%i:%s') as departure_date_time,
                    STR_TO_DATE(`Arrival Date & Time`, '%Y-%m-%d %H:%i:%s') as arrival_date_time,
                    `Duration (hrs)`, Stopovers, `Aircraft Type`, Class, `Booking Source`,
                    `Base Fare (BDT)`, `Tax & Surcharge (BDT)`, `Total Fare (BDT)`,
                    Seasonality, `Days Before Departure`, created_at
                FROM flight_data
                """
            }
            
            # Load tables in parallel using ThreadPoolExecutor with reduced workers
            logger.info("Starting parallel data loading...")
            with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced from 4 to 2 workers
                futures = [
                    executor.submit(load_table, table_name, query, mysql_cursors[table_name])
                    for table_name, query in queries.items()
                ]
                
                # Wait for all tasks to complete
                for future in futures:
                    future.result()
            
            logger.info("All tables loaded successfully!")
            
    except (Error, PostgresError) as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        # Close connections in reverse order of creation
        if postgres_cursor:
            postgres_cursor.close()
        for cursor in mysql_cursors.values():
            cursor.close()
        if postgres_conn:
            postgres_conn.close()
        if mysql_conn and mysql_conn.is_connected():
            mysql_conn.close()
        logger.info("Database connections closed")
