
# agent.py

from sql_generator import generate_sql
from query_executor import execute_sql_query


def run_agent(question):
    """Run the complete AI SQL Agent workflow."""

    print("\nAI SQL Agent is processing your question...")

    try:
        # Step 1: Generate SQL query
        print("\n[1] Generating SQL Query...")

        sql_query = generate_sql(question)

        print("\nGenerated SQL:")
        print(sql_query)

        # Step 2: Execute SQL query
        print("\n[2] Executing SQL Query...")

        results = execute_sql_query(sql_query)

        # Step 3: Display results
        print("\n[3] Query Results:")

        if results:
            for index, row in enumerate(results, start=1):
                print(f"\nRecord {index}:")
                for key, value in row.items():
                    print(f"{key}: {value}")
        else:
            print("No records found.")

        return results

    except Exception as e:
        print(f"\nAgent Error: {e}")
        return None


# Run AI SQL Agent
if __name__ == "__main__":

    print("=" * 50)
    print("         AI SQL AGENT")
    print("=" * 50)

    question = input("\nAsk your database a question: ")

    run_agent(question)
