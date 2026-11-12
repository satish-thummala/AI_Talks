
# query_executor.py

from sqlalchemy import text
from database import engine
from safety import validate_sql_query


def execute_sql_query(sql_query):
    """Validate and execute a SQL query."""

    # Step 1: Validate SQL
    safe_query = validate_sql_query(sql_query)

    # Step 2: Execute validated SQL
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text(safe_query)
            )

            rows = result.mappings().all()

            return [dict(row) for row in rows]

    except Exception as e:
        print(f"SQL Execution Error: {e}")
        raise


# Test query execution
if __name__ == "__main__":

    sample_query = """
    SELECT * FROM customers
    """

    try:
        results = execute_sql_query(sample_query)

        print("\nQuery Results:")

        if results:
            for row in results:
                print(row)
        else:
            print("No records found.")

    except Exception as e:
        print(f"Error: {e}")
