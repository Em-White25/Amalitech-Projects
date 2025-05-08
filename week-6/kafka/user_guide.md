# Heartbeat Monitoring System - Usage Guide

This guide will walk you through setting up and running the real-time heartbeat monitoring system using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning the repository)

## Step 1: Set Up Environment

1. Create a `.env` file in the project root (optional, as environment variables are now set in docker-compose.yml):
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_TOPIC=heartbeat-data

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=heartbeat_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## Step 2: Start the System

1. Build and start all services using Docker Compose:
```bash
docker-compose up -d
```

2. Verify all services are running:
```bash
docker-compose ps
```

You should see six services running:
- zookeeper
- kafka
- postgres
- generator (runs heartbeat_data_generator.py)
- producer
- consumer

3. Check service logs:
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f generator
docker-compose logs -f producer
docker-compose logs -f consumer
```

## Step 3: Monitor the System

1. Check Kafka topics:
```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list
```

2. View messages in the Kafka topic:
```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic heartbeat-data --from-beginning
```

3. Query the PostgreSQL database:
```bash
docker exec -it postgres psql -U postgres -d heartbeat_db
```

Useful PostgreSQL queries:
```sql
-- View all records
SELECT * FROM heartbeat_records;


-- Get average heart rate by customer
SELECT customer_id, AVG(heart_rate) as avg_heart_rate 
FROM heartbeat_records 
GROUP BY customer_id;

-- Get recent records
SELECT * FROM heartbeat_records 
ORDER BY timestamp DESC 
LIMIT 10;
```

## Step 4: Stop the System

Stop all services:
```bash
docker-compose down
```

To completely clean up (including volumes):
```bash
docker-compose down -v
```

## Troubleshooting

1. If services fail to start:
```bash
docker-compose logs
```

2. If database connection fails:
```bash
docker-compose restart postgres
```

3. If Kafka connection fails:
```bash
docker-compose restart kafka
```

4. If Python services fail:
```bash
# Restart specific service
docker-compose restart generator
docker-compose restart producer
docker-compose restart consumer

# Rebuild and restart all Python services
docker-compose up -d --build generator producer consumer
```

5. If you need to reset everything:
```bash
docker-compose down -v
docker-compose up -d
```

## Monitoring Tips

1. Watch for anomalies in the consumer logs:
```bash
docker-compose logs -f consumer
```

2. Monitor the database size:
```sql
SELECT pg_size_pretty(pg_database_size('heartbeat_db'));
```

3. Check Kafka topic statistics:
```bash
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic heartbeat-data
```

4. Monitor container resource usage:
```bash
docker stats
```

## Cleanup

When you're done testing:
```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove any remaining containers
docker rm -f $(docker ps -aq)

# Remove any remaining volumes
docker volume prune

# Remove the built images
docker rmi $(docker images -q heartbeat-monitoring_*)
```

## Development

If you need to modify the Python code:

1. Make your changes to the Python files
2. Rebuild the affected services:
```bash
docker-compose up -d --build generator producer consumer
```

To run a single service for testing:
```bash
docker-compose up generator
``` 