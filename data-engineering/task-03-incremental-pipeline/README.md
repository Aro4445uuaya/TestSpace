# Task 3: Incremental Data Pipeline

## Overview
This project implements an incremental data pipeline that extracts new exam submission records from MongoDB and loads them into a MySQL data warehouse.

The pipeline is designed to be safe to execute repeatedly without unnecessarily processing previously loaded records.

## Key Features
- **Incremental Loading:** Fetches only records with MongoDB ObjectIds greater than the last processed checkpoint.
- **Duplicate Prevention:** Uses MySQL upsert logic to prevent duplicate records.
- **Checkpoint Management:** Stores the last successfully processed record ID in MySQL.
- **Run Logging:** Records execution status, start time, end time, processed record count, and errors.
- **Failure Handling:** Uses database transactions to roll back failed data loads and checkpoint updates.
- **Scheduler Ready:** Can be configured with Windows Task Scheduler or another scheduling tool for automatic execution.

## Technologies Used
- Python
- MongoDB Atlas
- MySQL
- PyMongo
- MySQL Connector/Python
- python-dotenv
- Python Logging

## Project Structure
```text
task-03-incremental-pipeline/
│
├── incremental_pipeline.py
├── logger.py
├── README.md
└── pipeline.log
```

## How to Run

1. Install the required Python packages:
```bash
pip install pymongo mysql-connector-python python-dotenv
```

2. Configure the environment variables using the `.env` file from Task 1.

3. Run the pipeline:
```bash
python incremental_pipeline.py
```

## Database Tables
- `exam_submissions_raw` – Stores extracted records.
- `pipeline_checkpoint` – Tracks the last processed MongoDB ObjectId.
- `pipeline_run_logs` – Stores pipeline execution details.

## Validation
The pipeline was tested with two consecutive executions:

## 1st run
PS D:\TestSpace\data-engineering\task-01-extract-load> D:\TestSpace\venv\Scripts\python.exe D:\TestSpace\data-engineering\task-03-incremental-pipeline\incremental_pipeline.py

Pipeline completed successfully!
New records processed: 8

## 2nd run
PS D:\TestSpace\data-engineering\task-01-extract-load> D:\TestSpace\venv\Scripts\python.exe D:\TestSpace\data-engineering\task-03-incremental-pipeline\incremental_pipeline.py
Pipeline completed successfully!
New records processed: 0

| Execution | Records Processed | Status |
|---|---:|---|
| First Run  | 8 | SUCCESS |
| Second Run | 0 | SUCCESS |

The second execution did not reprocess the existing records.

## Scheduling
The pipeline is scheduler-ready and can be configured to run automatically using Windows Task Scheduler or another scheduling service. Scheduling configuration is not included in this implementation.

## Author
Arokia Benedict Ebenezar