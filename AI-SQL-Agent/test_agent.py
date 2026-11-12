from sql_generator import generate_sql
from query_executor import execute_sql_query

question = "Show me the top 5 customers by total spending."

print("\nUser Question:")
print(question)

# Generate SQL
sql_query = generate_sql(question)

print("\nGenerated SQL:")
print(sql_query)

# Execute SQL
results = execute_sql_query(sql_query)

print("\nDatabase Results:")

for row in results:
    print(row)