import psycopg2
import os
import logging
import streamlit as st
from dotenv import load_dotenv

# --- Connection Setup ---
# Load environment variables from .env file
load_dotenv()
host = os.getenv("HOST")
dname = os.getenv("DBNAME")
user = os.getenv("DBUSER")
pwd = os.getenv("PASSWORD")
port = os.getenv("PORT")
print("\n\n",pwd,"\n\n")
if not host:
    st.error("HOST environment variable is not set. Please check your .env file.")
    st.stop()
if not dname:
    st.error("DBNAME environment variable is not set. Please check your .env file.")
    st.stop()
if not user:
    st.error("DBUSER environment variable is not set. Please check your .env file.")
    st.stop()
if not pwd:
    st.error("PWD environment variable is not set. Please check your .env file.")
    st.stop()
if not port:
    st.error("PORT environment variable is not set. Please check your .env file.")
    st.stop()

# Centralized connection details
DB_CONNECT_PARAMS = {
    "host": host,
    "dbname": dname,
    "user": user,
    "password": pwd,
    "port": port
}

# --- Database Initialization ---
def init_db():
    """
    Initializes the database by creating the subscribers table if it doesn't exist.
    This is idempotent and safe to run on every app start.
    """
    # SQL command to create the table with the specified constraints
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
        logging.info("Database initialized successfully")
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection failed: {e}")
        st.error(f"Database connection failed: {e}")
        st.info("Please check your .env file and ensure the Cloud SQL instance is accessible.")
        st.stop()
    except Exception as e:
        logging.exception("Unexpected error during DB initialization")
        st.error(f"An error occurred during DB initialization: {e}")
        st.stop()

# --- Query Functions ---
def email_exists(email: str) -> bool:
    """
    Checks if an email already exists in the subscribers table.
    Optimized to be fast and efficient.
    """
    query = "SELECT 1 FROM subscribers WHERE email = %s LIMIT 1;"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email,))
                return cur.fetchone() is not None
    except Exception as e:
        st.error(f"Error checking email: {e}")
        return False # Fail safely

def add_subscriber(name: str, email: str) -> bool:
    """
    Adds a new subscriber to the database.
    Returns True on success, False on failure.
    """
    query = "INSERT INTO subscribers (name, email) VALUES (%s, %s);"
    try:
        with psycopg2.connect(**DB_CONNECT_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, email))
            conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        # This error is expected if the email already exists.
        # The UI should ideally prevent this, but this is a database-level safeguard.
        st.warning("This email address is already subscribed.")
        return False
    except Exception as e:
        st.error(f"Database error on adding subscriber: {e}")
        return False