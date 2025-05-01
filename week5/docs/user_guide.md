# User Guide: Real-Time Spark Structured Streaming (ETL - Data Ingestion)

This guide provides step-by-step instructions on how to set up and run the real-time e-commerce data ingestion project.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Docker:** You need Docker installed to containerize and run the Spark and PostgreSQL services. You can find installation instructions for your operating system on the official Docker website: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
* **Docker Compose:** Docker Compose is used to manage the multi-container Docker application defined in the `docker-compose.yml` file. It is usually installed along with Docker Desktop. If you need to install it separately, follow the instructions here: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
* **Python 3:** While the Docker containers handle the execution of the Python scripts, you might need Python 3 installed on your host machine if you want to examine or modify the scripts. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/)

## 2. Project Setup

1.  **Clone the Repository:** If you have the project files in a repository (e.g., Git), clone it to your local machine:
    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```
    
2.  **Environment Configuration:**
    * Create a file named `.env` in the root of your project directory.
    * Add the following environment variables to the `.env` file, replacing the placeholder values with your desired PostgreSQL credentials and port:
        ```
        POSTGRES_USER=your_postgres_user
        POSTGRES_PASSWORD=your_postgres_password
        POSTGRES_DB=ecommerce_db
        POSTGRES_PORT=5432
        ```
       
## 3. Running the Project

1.  **Start the Docker Containers:** Navigate to the root of your project directory (where the `docker-compose.yml` file is located) in your terminal and run the following command:
    ```bash
    docker compose up --build -d
    ```
    This command will build the Docker images (if necessary) and start the PostgreSQL, Spark Master, Spark Worker, and PySpark Notebook containers in detached mode (running in the background).

2.  **Set up the PostgreSQL Database:**
    * Once the containers are running, you need to execute the SQL script to create the `ecommerce_db` database and the `user_events` table. You can do this by executing the `postgres_setup.sql` script inside the `postgres` container. First, copy the SQL file into the container (if it's not already mounted):
        ```bash
        docker cp postgres_setup.sql postgres:/docker-entrypoint-initdb.d/
        ```
        (Docker will usually run scripts in this directory on initialization. If it doesn't, you might need to connect to the container and run it manually using `psql`). Alternatively, you can connect to the PostgreSQL container using `psql` from your host:
        ```bash
        psql -h localhost -p <host_postgres_port> -U ${POSTGRES_USER} -d postgres -f postgres_setup.sql
        ```
        (Replace `<host_postgres_port>` with the port you mapped in `docker-compose.yml`, e.g., 5432).

3.  **Run the Data Generator:**
    * Open a terminal and navigate to the directory containing the `data_generator.py` script.
    * Run the script:
        ```bash
        python data_generator.py
        ```
    * This script will start generating CSV files in the `data/csv_data` directory. Keep this script running in the background.

4.  4.  **Run the Spark Streaming Job in Jupyter Notebook:**
    * Open your web browser and navigate to the Jupyter Notebook interface, usually accessible at `http://localhost:8888`.
    * Navigate to the `/app` directory within the notebook (this is where your project files are mounted).
    * Open or create a new Python notebook.
    * In a notebook cell, you can run your `spark_streaming_to_postgres.py` script using the `%run` magic command:
        ```python
        %run spark_streaming_to_postgres.py
        ```
    * This will execute your Spark Structured Streaming job within the Jupyter Notebook environment. You should see the Spark application logs and any print statements in the notebook output.


## 4. Verifying the Data Ingestion

1.  **Monitor Jupyter Notebook Output:** Observe the output of the cell where you ran the `spark_streaming_to_postgres.py` script. It should indicate that the Spark streaming job has started and is processing data. You might see logs related to reading the CSV files and writing to PostgreSQL.
2.  **Query PostgreSQL:** Connect to the `ecommerce_db` database using a PostgreSQL client (e.g., `psql`, pgAdmin) and query the `user_events` table to see if the data is being written:
    ```sql
    SELECT COUNT(*) FROM user_events;
    SELECT * FROM user_events LIMIT 10;
    ```
    (Use the credentials you defined in your `.env` file to connect).

## 5. Stopping the Project

To stop the project and the Docker containers, navigate to your project directory in the terminal and run:

```bash
docker compose down