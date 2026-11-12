import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL

# Load environment variables
load_dotenv()

# Read database configuration
db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME")
)

# Create database engine
engine = create_engine(
    db_url,
    pool_pre_ping=True
)

def test_connection():
    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT DATABASE()")
            )

            database_name = result.scalar()

            print("MySQL connection successful!")
            print(f"Connected Database: {database_name}")

            # Display available tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            print("\nAvailable Tables:")
            for table in tables:
                print(f"- {table}")

    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_connection()
