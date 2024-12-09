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

# Streamlit App
st.title("Shooting Log - Gun Statistics and Progress")

# Display total time at the range
st.header("Total Time Spent at the Range")
total_time = total_time_at_range()
if total_time is None or not isinstance(total_time, (int, float)):
    total_time = 0  # Default value if total_time is invalid
st.metric("Total Time (Minutes)", total_time)

# Display total shots fired
st.header("Total Shots Fired")
total_shots = total_shots_fired()
if total_shots is None or not isinstance(total_shots, (int, float)):
    total_shots = 0  # Default value if total_shots is invalid
st.metric("Total Shots", total_shots)
