
from safety import validate_sql_query

test_queries = [
    "SELECT * FROM customers",

    "DELETE FROM customers",

    "UPDATE products SET price = 100",

    "DROP TABLE orders",

    "SELECT * FROM customers; DROP TABLE orders"
]

for query in test_queries:

    print("\nTesting:", query)

    try:
        result = validate_sql_query(query)
        print("ALLOWED:", result)

    except ValueError as e:
        print("BLOCKED:", e)
