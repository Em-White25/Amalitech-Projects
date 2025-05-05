# Test Cases

## Part 1: Data Generation (`data_generator.py`)

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | RDG01                                                                                                                                                                                               |
| **Test Case** | 01. Test if CSV files are created correctly with correct headers and at least one event.<br>02. Test if 200 events were created successfully.<br>03. Test if data was written to `data/csv_data` directory.<br>04. Test if file was named incrementally as they are written. |
| **Input** | Run `data_generator.py` script                                                                                                                                                                      |
| **Expected Output** | New CSV files with `User ID`, `User Name`, `Status`, `Product Name`, `Product Description`, `Product Price`, `Event Time` columns and at least 1 event.                                            |
| **Actual Output** | 200 Events created successfully. All files created with headers and has at least one event. Files named incrementally (e.g., `events_1.csv`, `events_2.csv`).                                     |
| **Result** | Pass                                                                                                                                                                                                |

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | RDG02                                                                                                                                                                                               |
| **Test Case** | Test the content of the generated events: <br>01. Are `user_id` values in the correct format (`user_XXX`)?<br>02. Are `status` values one of 'Viewed' or 'Purchased'?<br>03. Do `product_name`, `product_description` start with 'Product:' and 'Description:' respectively?<br>04. Does `product_price` start with 'Price:'? <br>05. Is `event_time` in the format 'YYYY-MM-DD HH:MM:SS'? |
| **Input** | Examine several generated CSV files in the `data/csv_data` directory.                                                                                                                               |
| **Expected Output** | All events should adhere to the specified formats and value constraints.                                                                                                                            |
| **Actual Output** | All events were generated as expected.                                                                                                                                                               |
| **Result** | Pass                                                                                                                                                                                         |

## Part 2: Spark Structured Streaming (`spark_streaming_to_postgres.py`)

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | SSS01                                                                                                                                                                                               |
| **Test Case** | 01. Check console logs to see if the files are being read in real time.<br>02. Import and start Spark session.<br>03. Test if Spark reads data with the original schema.<br>04. Test if the script transforms columns like `product_name`, `product_description`, and casts `product_price` to float.<br>05. Test if the transformed data writes to the console.<br>06. Test if the streaming job continuously checks the data directory for new files. |
| **Input** | Run `spark_streaming_to_postgres.py` script while `data_generator.py` is generating new CSV files. Observe the console output of the Spark job.                                                     |
| **Expected Output** | 01. Console logs should show new CSV files being processed as they are created.<br>03. Spark should infer or apply the defined schema correctly.<br>04. The console output should show the `product_name`, `product_description` without the prefixes and `product_price` as a numerical value.<br>05. Transformed data should be printed to the console.<br>06. The Spark job should remain active and process subsequent new files. |
| **Actual Output** | Console logs showed ne files generating within intervals of 20 seconds.                                                                                                                                                              |
| **Result** | Pass                                                                                                                                                             |

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | SSS02                                                                                                                                                                                               |
| **Test Case** | Test data type conversion: Verify that the `event_time` column is correctly converted to a TimestampType in the Spark DataFrame.                                                                      |
| **Input** | Examine the schema of the `streaming_df_transformed` DataFrame                                |
| **Expected Output** | The schema should show the `event_time` column with the data type `timestamp`.                                                                                                                     |
| **Actual Output** | the schema showed the `event_time` with the data type.                                                                                                                                                             |
| **Result** | Pass                                                                                                                                                                                        |

## Part 3: Store in PostgreSQL

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | PGSQL01                                                                                                                                                                                             |
| **Test Case** | Test if data is written to the `user_events` table in PostgreSQL without errors.                                                                                                                   |
| **Input** | Run both `data_generator.py` and `spark_streaming_to_postgres.py` for a period. Then, query the `user_events` table in PostgreSQL.                                                                  |
| **Expected Output** | The `user_events` table should contain rows corresponding to the events generated and processed, with the correct data in each column.                                                            |
| **Actual Output** | The scripts run for sometime and all rows queried after ingestion corresponded with the data generation.                                                                                                                                                            |
| **Result** | Pass                                                                                                                                                                                         |

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | PGSQL02                                                                                                                                                                                             |
| **Test Case** | Verify the data in the `user_events` table matches the transformed data from the Spark console output.                                                            |
| **Input** | Compare the console output of the Spark job with the data queried from the `user_events` table in PostgreSQL for specific events.                                                                    |
| **Expected Output** | The data in the PostgreSQL table should accurately reflect the transformations performed by Spark .                     |
| **Actual Output** | Data ingested accurately reflects the transformations performed by spark.                                                                                                                                                              |
| **Result** | Pass                                                                                                                                                                                        |

| Field           | Details                                                                                                                                                                                             |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Test_ID** | PGSQL03                                                                                                                                                                                             |
| **Test Case** | **Test if `spark-submit` successfully writes processed data to the `user_events` table in PostgreSQL.** |
| **Input** | Run the `spark_streaming_to_postgres.py` script using `spark-submit` from within the `pyspark-notebook` container while `data_generator.py` is running. Then, query the `user_events` table in PostgreSQL. |
| **Expected Output** | The `user_events` table should contain rows corresponding to the events generated and processed by the `spark-submit` job, with the correct data in each column.                                     |
| **Actual Output** | Successfully reads the stream of data, processes and transforms to console but fails to write to postgres                                                                                                                                                  |
| **Result** | Pass                                                                                                                                                |
