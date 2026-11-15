
def run_quality_checks(cursor):
    """
    Runs data quality checks on the dimensional warehouse.
    Raises an error if any check fails.
    """

    checks = {
        "Duplicate submissions": """
            SELECT COUNT(*)
            FROM (
                SELECT mongo_id
                FROM fact_exam_submissions_dw
                GROUP BY mongo_id
                HAVING COUNT(*) > 1
            ) AS duplicates
        """,

        "Missing required IDs": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw
            WHERE mongo_id IS NULL
               OR student_key IS NULL
               OR workspace_key IS NULL
               OR date_key IS NULL
        """,

        "Invalid marks": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw
            WHERE obtained_marks < 0
               OR total_marks <= 0
               OR obtained_marks > total_marks
        """,

        "Invalid percentage": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw
            WHERE percentage < 0
               OR percentage > 100
        """,

        "Missing student references": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw f
            LEFT JOIN dim_student s
                ON f.student_key = s.student_key
            WHERE s.student_key IS NULL
        """,

        "Missing workspace references": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw f
            LEFT JOIN dim_workspace w
                ON f.workspace_key = w.workspace_key
            WHERE w.workspace_key IS NULL
        """,

        "Missing date references": """
            SELECT COUNT(*)
            FROM fact_exam_submissions_dw f
            LEFT JOIN dim_date d
                ON f.date_key = d.date_key
            WHERE d.date_key IS NULL
        """
    }

    failed_checks = []

    for check_name, query in checks.items():
        cursor.execute(query)
        failed_records = cursor.fetchone()[0]

        if failed_records > 0:
            print(f"FAIL: {check_name} - {failed_records} invalid records")
            failed_checks.append(check_name)
        else:
            print(f"PASS: {check_name}")

    if failed_checks:
        raise ValueError(
            "Data quality validation failed: "
            + ", ".join(failed_checks)
        )

    print("\nAll data quality checks passed!")

    return True