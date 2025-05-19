# Flight Price Analysis Pipeline - Project Overview

## Project Description
An automated data pipeline that processes flight price data from Bangladesh, performing ETL operations and generating analytical insights. The project uses Apache Airflow for workflow orchestration, with data flowing through multiple stages from raw data ingestion to final analytics.

## Technical Stack
- **Orchestration**: Apache Airflow
- **Databases**: MySQL (staging), PostgreSQL (analytics)
- **Languages**: Python
- **Data Processing**: Pandas, SQL
- **Storage**: Local file system, Database systems

--- 

## Pipeline Architecture

### 1. Data Flow
```
Kaggle Dataset → Local Storage → MySQL → Validation → Transformation → PostgreSQL
```

### 2. Key Components
- **Data Ingestion**: Automated download and extraction
- **Data Storage**: MySQL & PostgreSQL
- **Data Processing**: Python-based data transformation
- **Quality Control**: Automated validation checks
- **Analytics**: KPI computation and storage

---

## DAG Structure

### Main Pipeline (`flight_price_analysis_pipeline`)
1. **Data Extraction**
   - Downloads dataset from Kaggle
   - Handles API interactions
   - Manages file extraction

2. **Data Storage**
   - Creates necessary databases
   - Manages data loading
   - Handles data type mapping

3. **Data Quality**
   - Validates data integrity
   - Checks for anomalies
   - Ensures data consistency

4. **Data Transformation**
   - Processes raw data
   - Computes KPIs
   - Generates analytics

5. **Analytics Storage**
   - Loads processed data
   - Stores KPIs
   - Maintains data consistency

---

## Challenges and Solutions

### 1. Database Connection Issues
**Challenge**: Initial connection failures to both MySQL and PostgreSQL databases. I designed the project to orchestrate using astro's runtime image, but back and forth with errors and configuration, i reverted to apache airflow's docker image.

**Solution**:
- Implemented robust connection handling with retry mechanisms
- Added proper error handling and logging
- Verified database credentials and connection parameters
- Ensured proper database user permissions

### 2. Column Name Mapping
**Challenge**: Mismatched column names between MySQL and PostgreSQL tables, mainly in the `flight_data` table.

**Solution**:
- Created a comprehensive column mapping dictionary
- Implemented dynamic column selection in SQL queries
- Added validation to ensure all required columns are present

### 3. Data Type Compatibility
**Challenge**: Incompatible data types between MySQL and PostgreSQL, mainly with:
- `DATETIME` vs `TIMESTAMP`
- `TEXT` vs `VARCHAR`
- `INT` vs `BIGINT`

**Solution**:
- Implemented proper data type casting in SQL queries
- Added explicit type conversions where needed
- Used PostgreSQL-compatible data types in table creation

### 4. Memory Management
**Challenge**: The dataset only had 57000 rows of data. The processing of this data could be handled by my machine at one go.
But as an "advocate" for loading batch data in chunks to improve memory efficiency and optimization, I decided to implement this technique during the data processing.
I also thought, why run the task (loading to PostgreSQL) sequentially when we can parallelize.

**Solution**:
- Implemented chunked data loading (10,000 rows per chunk)
- Added proper connection cleanup between chunks
- Implemented parallel processing with 2 workers
- Added progress tracking for long-running operations

### 5. Performance Optimization
**Challenge**: Proactively anticipating performance issues. I implemented techniques to combat this in the future.

**Solution**:
- Implemented parallel processing for multiple tables
- Added chunked data loading
- Optimized SQL queries with proper indexing
- Added progress tracking and logging

### 6. Error Handling
**Challenge**: I've been faulted twice for not implementing proper logging in my projects. I implemented a few techniques in this project.
I improved my error handling skills.

**Solution**:
- Implemented comprehensive error handling
- Added retry mechanisms for failed operations
- Improved logging for better debugging
- Added transaction management

### 7. Data Integrity
**Challenge**: Ensuring data consistency during transfer.

**Solution**:
- Implemented row count verification
- Added data validation checks
- Added logging for data transfer verification

---

## Best Practices Implemented

1. **Connection Management**
   - Proper connection pooling
   - Automatic connection cleanup
   - Retry mechanisms for failed connections

2. **Error Handling**
   - Comprehensive exception handling
   - Detailed error logging
   - Graceful failure recovery

3. **Performance**
   - Chunked data processing
   - Parallel processing
   - Optimized SQL queries

4. **Monitoring**
   - Progress tracking
   - Detailed logging
   - Performance metrics
---
## Key Features
- Automated data pipeline
- Comprehensive error handling
- Data quality validation
- Performance optimization
- Scalable architecture

## Business Value
- Automated flight price analysis
- Market trend identification
- Pricing strategy insights
- Operational efficiency

## Maintenance & Monitoring
- Error logging and tracking
- Data quality checks
- Automated retries
- Resource optimization

## Future Improvements

1. Add more detailed progress reporting
2. Add performance metrics collection
3. Implement automated testing
4. Add data consistency checks

