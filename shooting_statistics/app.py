import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Connect to AWS RDS Database
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],  # AWS RDS endpoint
        user=st.secrets["DB_USERNAME"],  # Database username
        password=st.secrets["DB_PASSWORD"],  # Database password
        database=st.secrets["DB_NAME"]  # Database name
    )

# Fetch data from the database
def fetch_data(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# Query 1: Total time spent at the range
def total_time_at_range():
    query = """
        SELECT SUM(duration_minutes) AS total_time
        FROM session;
    """
    df = fetch_data(query)
    return df["total_time"].iloc[0]

# Query 2: Total shots fired
def total_shots_fired():
    query = """
        SELECT SUM(rounds_fired) AS total_shots
        FROM session_details;
    """
    df = fetch_data(query)
    return df["total_shots"].iloc[0]
