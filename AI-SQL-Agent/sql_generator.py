
import os
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import inspect

from database import engine

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)


def get_database_schema():
    """Retrieve the MySQL database schema."""

    inspector = inspect(engine)
    schema = ""

    tables = inspector.get_table_names()

    for table in tables:
        schema += f"\nTable: {table}\n"

        columns = inspector.get_columns(table)

        for column in columns:
            schema += (
                f"- {column['name']}: "
                f"{column['type']}\n"
            )

        # Retrieve foreign key relationships
        foreign_keys = inspector.get_foreign_keys(table)

        for fk in foreign_keys:
            schema += (
                f"Foreign Key: "
                f"{fk['constrained_columns']} -> "
                f"{fk['referred_table']}."
                f"{fk['referred_columns']}\n"
            )

    return schema


def generate_sql(question):
    """Generate a MySQL query from a natural language question."""

    schema = get_database_schema()

    prompt = f"""
You are an expert MySQL SQL query generator.

Convert the user's natural language question
into a valid MySQL SELECT query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Generate a valid MySQL SELECT query.
2. Use only tables and columns in the schema.
3. Use correct JOIN conditions.
4. Use appropriate aggregate functions when needed.
5. Do not generate INSERT, UPDATE, DELETE,
   DROP, ALTER, or CREATE statements.
6. Return only the SQL query.
7. Do not include markdown or explanations.

SQL QUERY:
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql_query = response.choices[0].message.content.strip()

    # Remove markdown code fences if present
    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")

    return sql_query.strip()


# Test SQL generation
if __name__ == "__main__":

    question = "Show me the top 5 customers by total spending."

    sql = generate_sql(question)

    print("\nUser Question:")
    print(question)

    print("\nGenerated SQL:")
    print(sql)
