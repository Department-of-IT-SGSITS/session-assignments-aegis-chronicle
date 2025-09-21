import psycopg2
import os
import logging
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# Cloud Run Logs - Streamlit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

# Database connection parameters
DB_CONNECT_PARAMS = {}
if INSTANCE_CONNECTION_NAME:
    # Production env - Unix socket
    logging.info(f"Connecting via Unix socket!")
    DB_CONNECT_PARAMS = {
        "host": f"/cloudsql/{INSTANCE_CONNECTION_NAME}",
        "dbname": os.getenv("DBNAME"),
        "user": os.getenv("DBUSER"),
        "password": os.getenv("PASSWORD")
    }
else:
    # Local dev - TCP socket
    logging.info(f"Connecting via TCP socket!")
    DB_CONNECT_PARAMS = {
        "host": os.getenv("HOST"),
        "dbname": os.getenv("DBNAME"),
        "user": os.getenv("DBUSER"),
        "password": os.getenv("PASSWORD"),
        "port": os.getenv("PORT")
    }

# DB Initialization
def init_db():
    create_table_command = """
    CREATE TABLE IF NOT EXISTS subscribers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_command)
            conn.commit()
        logging.info("Database initialized successfully.")
    except psycopg2.OperationalError as e:
        logging.error(f"DATABASE CONNECTION FAILED: {e}")
        st.error("Failed to connect to the database. Service is temporarily unavailable.")
        st.stop()
    except Exception as e:
        logging.exception("Unexpected error during DB initialization.")
        st.error("An unexpected error occurred during database setup.")
        st.stop()

# Email check
def email_exists(email: str) -> bool:
    query = "SELECT 1 FROM subscribers WHERE email = %s LIMIT 1;"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                return cur.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking email: {e}")
        st.error(f"Error checking email: {e}")
        return False

# Add subscriber
def add_subscriber(name: str, email: str) -> bool:
    query = "INSERT INTO subscribers (name, email) VALUES (%s, %s);"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, email))
            conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        st.warning("This email address is already subscribed.")
        return False
    except Exception as e:
        logging.error(f"Database error on adding subscriber: {e}")
        st.error(f"Database error on adding subscriber: {e}")
        return False
    
# Fetch all subscribers
def fetch_subscribers():
    query = "SELECT name, email FROM subscribers;"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        logging.error(f"Error fetching subscribers: {e}")
        st.error(f"Error fetching subscribers: {e}")
        return []