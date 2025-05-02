# Project Overview: Real-Time Spark Structured Streaming (ETL - Data Ingestion)

## Table of Contents
1. [Introduction](#1-introduction)
2. [Project Goals](#2-project-goals)
3. [System Architecture](#3-system-architecture)
4. [Technologies Used](#4-technologies-used)
5. [Data Flow](#5-data-flow)
6. [Key Deliverables](#6-key-deliverables)
7. [What to Test](#7-what-to-test)
8. [Performance Metrics](#8-performance-metrics)

## Documentation
- [User Guide](docs/user_guide.md): Step-by-step instructions for running the project
- [Test Cases](docs/test_cases.md): Manual test plan and expected outcomes
- [System Architecture](docs/system_architecture.png): Visual representation of the system components and data flow
- [PostgreSQL Setup](postgres/postgres_setup.sql): Database schema and table creation scripts
- [PostgreSQL Connection Details](postgres/postgres_connection_details.txt): Database connection configuration

---

## 1. Introduction

This project implements a real-time ETL data pipeline designed to ingest and process user activity from a simulated e-commerce platform. The system captures events such as product views and purchases, processes them using Spark Structured Streaming, and ingests the processed data into a PostgreSQL database for further analysis and insights. The Spark application can be run using `spark-submit` for deployment and monitoring of performance metrics. Running the script within a PySpark Jupyter Notebook is also an optional method for development and debugging.

---

## 2. Project Goals

The primary goals of this project are to:

* Simulate a continuous stream of e-commerce user activity data.
* Utilize Apache Spark Structured Streaming to consume and transform this data in real time.
* Store the processed data reliably and efficiently in a PostgreSQL database.
* Demonstrate the architecture and functionality of a real-time data ingestion pipeline.
* Measure and evaluate the performance characteristics of the system using Spark's monitoring capabilities.

---

## 3. System Architecture

The system follows a three-stage architecture:

1.  **Data Generation:** A Python script (`data_generator.py`) simulates e-commerce events (product views and purchases) and writes them to CSV files in a designated directory (`data/csv_data`). New files are generated periodically (every 20 seconds) to mimic a continuous data stream.

2.  **Real-Time Data Processing:** Spark Structured Streaming, running within a Dockerized environment (including a master and worker node), monitors the directory where the CSV files are generated. The `spark_streaming_to_postgres.py` script reads these new files as they appear, applies necessary transformations (e.g., data type conversion, extracting information from text fields), and processes the data in micro-batches. This script can be executed using `spark-submit` or optionally within a PySpark Jupyter Notebook.

3.  **Data Ingestion:** The processed data from Spark Structured Streaming is then written to a PostgreSQL database. The database schema includes a table (`user_events`) designed to store the user ID, user name, event status, product details (name, description, price), and the timestamp of each event.

A visual representation of this architecture is provided in the ![System Architecture](docs/system_architecture.png).

---

## 4. Technologies Used

* **Apache Spark Structured Streaming:** For real-time data processing and stream ingestion.
* **PostgreSQL:** As the relational database for storage of processed data.
* **Python:** For simulating the e-commerce event data.
* **SQL:** For setting up the PostgreSQL database schema.
* **Docker and Docker Compose:** For containerizing the Spark and PostgreSQL environments, ensuring portability and reproducibility.
* **Jupyter Notebook:** An optional environment for running and developing the Spark streaming application.
* **Spark UI (localhost:4040):** For monitoring the Spark application and performance metrics when run with `spark-submit`.

---

## 5. Data Flow

1.  The `data_generator.py` script continuously generates e-commerce event data and saves it as new CSV files in the `data/csv_data` directory.
2.  The Spark Structured Streaming application (`spark_streaming_to_postgres.py`) monitors this directory.
3.  As new CSV files appear, Spark reads them, applies transformations to the data, and processes it in micro-batches.
4.  The processed micro-batches of data are then written to the `user_events` table in the PostgreSQL database.
5.  When run with `spark-submit`, the Spark application's performance and metrics can be monitored via the Spark UI at `localhost:4040`.
6. **Optional**: You can run the script in Jupyter notebook also

---

## 6. Key Deliverables

This project includes the following deliverables:

* `data_generator.py`: Python script to generate CSV event data.
* `spark_streaming_to_postgres.py`: Spark Structured Streaming job to process and write data.
* `postgres_setup.sql`: SQL script to create the database and table.
* `postgres_connection_details.txt`: Text file with database connection information.
* `project_overview.md`: This document, providing a high-level overview of the system.
* `user_guide.md`: Step-by-step instructions on how to run the project.
* `test_cases.md`: Manual test plan with expected vs. actual outcomes.
* `performance_metrics.md`: Report with system performance data (latency, throughput, etc.).
* `system_architecture.png`: Diagram showing data flow and components.

---

## 7. What to Test

The system will be tested to ensure:

* The `data_generator.py` script generates CSV files with the correct format and data.
* Spark Structured Streaming correctly detects and processes new CSV files as they arrive.
* The data transformations applied by Spark are accurate.
* Data is written to the `user_events` table in PostgreSQL without errors when run with both `spark-submit` and (optionally) Jupyter Notebook.
* The performance of the system (e.g., processing speed, latency, throughput) is within acceptable limits when monitored via the Spark UI.

---

## 8. Performance Metrics

The performance of the real-time data pipeline will be evaluated based on metrics such as:

* **Latency:** The time delay between an event being generated and it being written to the PostgreSQL database (measured via Spark UI when run with `spark-submit`).
* **Throughput:** The number of events processed per unit of time (measured via Spark UI when run with `spark-submit`).
* **Resource Utilization:** CPU and memory usage of the Spark cluster and PostgreSQL database (monitored via Spark UI and Docker stats).
* **Spark Application Duration:** The total time the Spark streaming application runs.

---

## 9. Future Improvements (Automatation). 
* In the next update, I will configure the Docker environment to automatically execute the data generation script (data_generator.py) and submit the Spark streaming job (spark_streaming_to_postgres.py) upon startup using docker-compose up. This will streamline the deployment process and eliminate the need for manual execution of these scripts.  
The planned approach involves modifying the docker-compose.yml file to include these commands in the service definition for the Spark driver container.

* Data Deduplication: To enhance data integrity and prevent duplicate entries in the PostgreSQL database, I will implement a deduplication mechanism. This will ensure that each event is written to the database only once, even if the streaming source provides the same event multiple times.  The implementation will likely involve checking for the existence of a record based on a unique key (e.g., user_id, event_time) before performing an insert operation.  
This could be achieved either within the Spark streaming job itself (using techniques like windowing and filtering) or by utilizing PostgreSQL's features, such as unique constraints or the ON CONFLICT DO NOTHING clause.