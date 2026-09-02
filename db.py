import os
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            os.getenv("postgresql://stockflow_user:jntDwxnhtEfkRsPUlG4zGnFDYZaiNaru@dpg-dabriu2fngtc73f2nh3g-a/stockflow_dhu1")
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None