import psycopg2
import os
import logging
from dotenv import load_dotenv

load_dotenv()
DB_CONNECT_PARAMS = {}
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME") 

if INSTANCE_CONNECTION_NAME:
    # Cloud Run Environment
    DB_CONNECT_PARAMS = {
        "host": f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
        "user": os.getenv("DBUSER"),
        "password": os.getenv("PASSWORD"),
        "dbname": os.getenv("DBNAME")
    }
else:
    # Local Environment for backend testing
    DB_CONNECT_PARAMS = {
        "host": os.getenv("HOST"),
        "port": os.getenv("PORT"),
        "user": os.getenv("DBUSER"),
        "password": os.getenv("PASSWORD"),
        "dbname": os.getenv("DBNAME")
    }

def fetch_subscribers():
    query = "SELECT name, email FROM subscribers;"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        logging.error(f"Error fetching subscribers: {e}")
        return []