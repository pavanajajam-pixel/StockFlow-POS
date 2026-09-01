import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="stockflow",        # ✅ make sure this database exists
            user="postgres",        # ✅ your PostgreSQL username
            password="password",  # 🔑 replace with your actual password
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None
