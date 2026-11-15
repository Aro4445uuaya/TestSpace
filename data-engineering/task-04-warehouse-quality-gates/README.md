# Task 04 — Warehouse Pipeline with Quality Gates

## Project Overview

This project implements a dimensional data warehouse pipeline for the TestSpace examination platform.

The main objective is to prevent invalid data from passing through the warehouse quality validation process.

The pipeline validates warehouse records using automated data quality checks. If any validation fails, the pipeline raises an error and stops execution.

## Technologies Used

- Python
- MySQL
- MySQL Connector/Python
- python-dotenv
- Python unittest
- SQL

## Dimensional Data Model

This project follows a Star Schema dimensional modelling approach.

### Dimension Tables

**1. dim_student**
- student_key (Primary Key)
- student_id
- student_name
- email

**2. dim_workspace**
- workspace_key (Primary Key)
- workspace_id
- workspace_name

**3. dim_date**
- date_key (Primary Key)
- full_date
- day
- month
- month_name
- quarter
- year

### Fact Table

**fact_exam_submissions_dw**

- submission_key (Primary Key)
- mongo_id
- student_key (Foreign Key)
- workspace_key (Foreign Key)
- date_key (Foreign Key)
- score
- obtained_marks
- total_marks
- percentage
- time_taken

## Model Diagram

The dimensional model is represented using a Star Schema, with the exam submissions fact table connected to three dimension tables.

![TestSpace Star Schema](diagrams/star_schema.png)

## Data Quality Checks

The pipeline includes seven data quality checks:

1. Duplicate submission detection.
2. Missing required ID validation.
3. Invalid examination marks validation.
4. Invalid percentage validation.
5. Missing student reference validation.
6. Missing workspace reference validation.
7. Missing date reference validation.

## Quality Gate Behaviour

- If all quality checks pass, the pipeline completes successfully.
- If any quality check fails, the pipeline raises a ValueError.
- Invalid data prevents successful pipeline completion.

## Testing

Automated unit tests were implemented using Python's unittest framework.

Test scenarios:

- All quality checks passing.
- Invalid marks causing quality validation failure.

The pipeline was also tested against the MySQL warehouse using a temporary invalid record.

The invalid record was detected, and the pipeline stopped as expected. The temporary test record was subsequently removed.

## Project Structure

```text
task-04-warehouse-quality-gates/
│
├── diagrams/
│   └── star_schema.png
│
├── quality_checks.py
├── test_quality_checks.py
├── warehouse_pipeline.py
├── README.md
└── requirements.txt
```

## Installation

Install the required packages:

```bash
pip install mysql-connector-python python-dotenv
```

Configure the MySQL environment variables using the `.env` file from Task 1. Do not upload credentials to GitHub.

## Run the Pipeline

```bash
python warehouse_pipeline.py
```

## Run Unit Tests

```bash
python -m unittest -v test_quality_checks.py
```

## Expected Outcome

The pipeline validates warehouse data and prevents successful execution when data quality rules are violated.

## Author

Arokia Benedict Ebenezar