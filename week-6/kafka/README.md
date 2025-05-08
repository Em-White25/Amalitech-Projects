# Heartbeat Monitoring System

A real-time heartbeat monitoring system that uses Kafka for message streaming and PostgreSQL for data storage. This system simulates and processes heartbeat data from multiple customers, providing a robust platform for monitoring and analyzing heart rate data.

## System Architecture

The system consists of several components:
- **Data Generator**: Simulates heartbeat data for multiple customers
- **Kafka**: Message broker for real-time data streaming
- **Producer**: Publishes heartbeat data to Kafka
- **Consumer**: Processes and stores heartbeat data in PostgreSQL
- **PostgreSQL**: Database for persistent storage of heartbeat records

## Project Structure

```
.
├── images/                  # Project images and diagrams
├── user_guide.md           # Detailed usage instructions
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Python service container configuration
├── requirements.txt        # Python dependencies
├── db_schema.sql          # Database schema definition
├── heartbeat_data_generator.py  # Heartbeat data simulation
├── producer.py            # Kafka producer implementation
└── consumer.py            # Kafka consumer implementation
```

## Getting Started

1. Clone the repository
2. Follow the detailed setup instructions in the [User Guide](user_guide.md)
3. Use Docker Compose to start all services:
   ```bash
   docker-compose up -d
   ```

## Key Features

- Real-time heartbeat data simulation
- Distributed message processing with Kafka
- Persistent data storage in PostgreSQL
- Scalable microservices architecture
- Docker containerization for easy deployment

## Documentation

- [User Guide](user_guide.md) - Complete setup and usage instructions
- [Database Schema](db_schema.sql) - Database structure and queries
- [Docker Configuration](docker-compose.yml) - Service configuration details

## Requirements

- Docker and Docker Compose
- Git (optional, for cloning the repository)

