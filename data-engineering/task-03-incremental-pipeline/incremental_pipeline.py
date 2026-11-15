
import os
import json
import logging
from pathlib import Path

import mysql.connector
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

from logger import start_log, finish_log

# Load environment variables from Task 1 folder
load_dotenv(
    Path(__file__).parents[1]
    / "task-01-extract-load"
    / ".env"
)

PIPELINE_NAME = "testspace_incremental_pipeline"

mongo_client = None
mysql_conn = None
run_id = None
records_processed = 0

logging.basicConfig(
    filename=Path(__file__).with_name("pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    # Connect to MongoDB
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    mongo_db = mongo_client[os.getenv("MONGO_DB_NAME")]
    collection = mongo_db[os.getenv("MONGO_COLLECTION")]

    # Connect to MySQL
    mysql_conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = mysql_conn.cursor()

    # Start execution log
    run_id, start_time = start_log(cursor, PIPELINE_NAME)
    mysql_conn.commit()

    # Read the last processed MongoDB ObjectId
    cursor.execute(
        """
        SELECT last_processed_id
        FROM pipeline_checkpoint
        WHERE pipeline_name = %s
        """,
        (PIPELINE_NAME,)
    )

    checkpoint = cursor.fetchone()

    last_id = checkpoint[0] if checkpoint else None

    # Fetch only new MongoDB records
    query = {}

    if last_id:
        query["_id"] = {"$gt": ObjectId(last_id)}

    documents = list(
        collection.find(query).sort("_id", 1)
    )

    logging.info("Fetched %s new records", len(documents))

    # Insert new records into MySQL
    insert_query = """
        INSERT INTO exam_submissions_raw (
            mongo_id, workspace_id, workspace_name,
            student_id, student_name, dno, email,
            answers, score, obtained_marks, total_marks,
            time_taken, submitted_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            workspace_id = VALUES(workspace_id),
            workspace_name = VALUES(workspace_name),
            student_id = VALUES(student_id),
            student_name = VALUES(student_name),
            dno = VALUES(dno),
            email = VALUES(email),
            answers = VALUES(answers),
            score = VALUES(score),
            obtained_marks = VALUES(obtained_marks),
            total_marks = VALUES(total_marks),
            time_taken = VALUES(time_taken),
            submitted_at = VALUES(submitted_at)
    """

    for doc in documents:
        submitted_at = doc.get("submittedAt")

        if submitted_at is not None and submitted_at.tzinfo is not None:
            submitted_at = submitted_at.replace(tzinfo=None)

        values = (
            str(doc["_id"]),
            doc.get("workspaceId"),
            doc.get("workspaceName"),
            doc.get("studentId"),
            doc.get("studentName"),
            doc.get("dno"),
            doc.get("email"),
            json.dumps(doc.get("answers", {})),
            doc.get("score"),
            doc.get("obtainedMarks"),
            doc.get("totalMarks"),
            doc.get("time"),
            submitted_at
        )

        cursor.execute(insert_query, values)
        records_processed += 1

    # Update checkpoint only after successful loading
    if documents:
        latest_id = str(documents[-1]["_id"])

        cursor.execute(
            """
            INSERT INTO pipeline_checkpoint (
                pipeline_name, last_processed_id, last_run_at
            )
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                last_processed_id = VALUES(last_processed_id),
                last_run_at = NOW()
            """,
            (PIPELINE_NAME, latest_id)
        )

    # Mark execution successful
    finish_log(
        cursor,
        run_id,
        records_processed,
        "SUCCESS"
    )

    mysql_conn.commit()

    logging.info(
        "Pipeline completed successfully. Records: %s",
        records_processed
    )

    print("Pipeline completed successfully!")
    print(f"New records processed: {records_processed}")

except Exception as error:
    if mysql_conn and mysql_conn.is_connected():
        mysql_conn.rollback()

        if run_id is not None:
            try:
                finish_log(
                    cursor,
                    run_id,
                    records_processed,
                    "FAILED",
                    str(error)
                )
                mysql_conn.commit()
            except Exception:
                mysql_conn.rollback()

    logging.exception("Pipeline failed")
    print("Pipeline failed:", error)

finally:
    if mysql_conn and mysql_conn.is_connected():
        cursor.close()
        mysql_conn.close()

    if mongo_client:
        mongo_client.close()
