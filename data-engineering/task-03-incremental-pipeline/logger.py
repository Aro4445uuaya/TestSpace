
from datetime import datetime


def start_log(cursor, pipeline_name):
    start_time = datetime.now()

    cursor.execute(
        """
        INSERT INTO pipeline_run_logs (
            pipeline_name, start_time, status
        )
        VALUES (%s, %s, %s)
        """,
        (pipeline_name, start_time, "RUNNING")
    )

    return cursor.lastrowid, start_time


def finish_log(
    cursor,
    run_id,
    records_processed,
    status,
    error_message=None
):
    end_time = datetime.now()

    cursor.execute(
        """
        UPDATE pipeline_run_logs
        SET end_time = %s,
            records_processed = %s,
            status = %s,
            error_message = %s
        WHERE run_id = %s
        """,
        (
            end_time,
            records_processed,
            status,
            error_message,
            run_id
        )
    )
