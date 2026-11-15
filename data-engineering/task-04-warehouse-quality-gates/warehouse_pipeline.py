
import os
import mysql.connector
from dotenv import load_dotenv
from quality_checks import run_quality_checks

load_dotenv(
    r"D:\TestSpace\data-engineering\task-01-extract-load\.env"
)


def run_pipeline():
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )

        cursor = connection.cursor()

        print("Starting warehouse quality pipeline...")

        # Step 1: Run quality checks before publishing
        run_quality_checks(cursor)

        # Step 2: Publish only after all checks pass
        connection.commit()

        print("\nPipeline completed successfully!")
        print("Warehouse data passed all quality gates.")

    except Exception as error:
        if connection:
            connection.rollback()

        print("\nPIPELINE FAILED!")
        print("Reason:", error)
        raise

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    run_pipeline()
