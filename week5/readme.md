# Real-Time Spark Streaming Data Ingestion Project

This project demonstrates a real-time data pipeline for ingesting and processing e-commerce user activity data using Apache Spark Structured Streaming and PostgreSQL.

## Overview

The system simulates a stream of user events (product views and purchases), processes them in real time using Spark, and stores the processed data in a PostgreSQL database for analysis.

For a detailed overview of the project, its goals, architecture, technologies used, and data flow, please refer to the [Project Overview](docs/project_overview.md) document in the `docs` directory.

## Folder Structure

./
├── data/
│   └── csv_data/         # Directory where simulated e-commerce event CSV files are generated.
├── docs/
│   ├── project_overview.md     # High-level overview of the project.
│   ├── user_guide.md           # Step-by-step instructions on how to run the project.
│   ├── test_cases.md         # Manual test plan and results.
│   ├── performance_metrics.md  # Report on system performance (to be implemented).
│   ├── postgres_connection_details.txt # Details for connecting to the PostgreSQL database.
│   └── system_architecture.png # Diagram illustrating the system architecture (optional).
├── postgres/             # Contains PostgreSQL related configurations and data volume.
├── src/                  # (contains scripts for data generation and streaming to postgres)
├── .gitignore            # Specifies intentionally untracked files that Git should ignore.
├── Docker-compose.yaml   # Docker Compose configuration file for running multi-container Docker applications.
├── Dockerfile.pyspark    # Dockerfile for building the PySpark notebook image.
└── README.md             # This file, providing a brief overview of the project.


## Getting Started

Refer to the [User Guide](docs/user_guide.md) in the `docs` directory for detailed instructions on how to set up and run the project.

## Documentation

All project-related documentation can be found in the [`docs`](docs/) directory.
