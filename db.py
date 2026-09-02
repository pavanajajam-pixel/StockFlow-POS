import os
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL")
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None
