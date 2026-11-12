
# safety.py

import sqlglot
from sqlglot import exp


MAX_ROWS = 100


def validate_sql_query(sql_query):
    """Validate generated SQL before execution."""

    if not sql_query or not sql_query.strip():
        raise ValueError("SQL query cannot be empty.")

    try:
        # Parse SQL using MySQL dialect
        statements = sqlglot.parse(
            sql_query,
            read="mysql"
        )

        # Reject multiple SQL statements
        if len(statements) != 1 or statements[0] is None:
            raise ValueError(
                "Multiple SQL statements are not allowed."
            )

        query = statements[0]

        # Allow only SELECT statements
        if not isinstance(query, exp.Select):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        # Reject SELECT INTO operations
        if query.find(exp.Into):
            raise ValueError(
                "SELECT INTO operations are not allowed."
            )

        # Add a row limit if one is not provided
        if query.args.get("limit") is None:
            query = query.limit(MAX_ROWS)

        # Convert back into MySQL SQL
        safe_query = query.sql(dialect="mysql")

        print("SQL Validation: PASSED")

        return safe_query

    except ValueError:
        raise

    except Exception as e:
        raise ValueError(
            f"Invalid SQL query: {e}"
        )


# Test SQL validation
if __name__ == "__main__":

    test_query = """
    SELECT * FROM customers
    """

    try:
        validated_query = validate_sql_query(test_query)

        print("\nValidated SQL:")
        print(validated_query)

    except ValueError as e:
        print(f"\nValidation Failed: {e}")
