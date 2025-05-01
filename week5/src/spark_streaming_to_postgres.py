from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from pyspark.sql.functions import regexp_extract, col, to_timestamp
import os
import psycopg2
from pyspark.sql import DataFrame
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path

# load environment variable
dotenv_path = Path('../') / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- 1. Initialize Spark Session ---
spark = SparkSession.builder.appName("StructuredStreamingIngestion").getOrCreate()

# --- 2. Define Schema for Streaming Data ---
streaming_schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("user_name", StringType(), True),
    StructField("status", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("product_description", StringType(), True),
    StructField("product_price", StringType(), True),  # Corrected field name
    StructField("event_time", StringType(), True)
])

# --- 3. Read Streaming Data from CSV Files ---
streaming_df = spark.readStream \
    .format("csv") \
    .schema(streaming_schema) \
    .option("header", "true") \
    .option("maxFilesPerTrigger", 1) \
    .load("/app/data/csv_data/*.csv")

# --- 4. Transform Streaming Data ---
streaming_df_transformed = streaming_df.withColumn(
    "product_name", regexp_extract(col("product_name"), "Product: (.*)", 1)
).withColumn(
    "product_description", regexp_extract(col("product_description"), "Description: (.*)", 1)
).withColumn(
    "product_price", regexp_extract(col("product_price"), "Price: (.*)", 1).cast("float")  # Corrected field name and conversion
).withColumn(
    "event_time", to_timestamp(col("event_time"))
).select(
    "user_id", "user_name", "status", "product_name", "product_description", "product_price", "event_time" # Corrected field names
).drop()

streaming_df_transformed.printSchema()

query_debug = streaming_df_transformed.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

# --- 7. Define Function to Write Batch to PostgreSQL with Duplicate Handling ---
def write_to_postgres(df: DataFrame, epoch_id: int) -> None:
    """Writes a Spark DataFrame batch to a PostgreSQL table using psycopg2."""
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    table_name = os.getenv("POSTGRES_TABLE")

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        data_to_insert = []
        for row in df.toLocalIterator():
            row_dict = row.asDict()
            cleaned_row: Dict[str, any] = {
                "user_id": row_dict["user_id"],
                "user_name": row_dict["user_name"],
                "status": row_dict["status"],
                "product_name": row_dict["product_name"],  # Corrected field name
                "product_description": row_dict["product_description"], # Corrected field name
                "product_price": row_dict["product_price"],  # Corrected field name
                "event_time": row_dict["event_time"],
            }
            data_to_insert.append(cleaned_row)

        if data_to_insert:
            columns = data_to_insert[0].keys()
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            insert_statement = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
            """
            values_to_insert = [tuple(row.values()) for row in data_to_insert]
            cursor.executemany(insert_statement, values_to_insert)
            conn.commit()
            print(f"Batch {epoch_id} ({len(data_to_insert)} rows) written to PostgreSQL using psycopg2.")
        else:
            print(f"Batch {epoch_id} contained no data to write.")

    except psycopg2.Error as e:
        print(f"Error writing batch {epoch_id} to PostgreSQL (psycopg2): {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- 8. Write Streaming Data to PostgreSQL ---
query_postgres = streaming_df_transformed.writeStream \
    .outputMode("append") \
    .foreachBatch(write_to_postgres) \
    .start()

# --- 9. Keep Streaming Query Active (for continuous processing) ---
query_debug.awaitTermination(10)
query_postgres.awaitTermination()
