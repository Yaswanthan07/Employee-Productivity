from database.connection import init_postgres_schema


if __name__ == "__main__":
    init_postgres_schema()
    print("PostgreSQL schema initialized successfully.")
