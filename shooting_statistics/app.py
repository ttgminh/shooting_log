import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal

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
    total_time = df["total_time"].iloc[0]
    if isinstance(total_time, Decimal):
        total_time = int(total_time)
    return total_time

# Query 2: Total number of shots fired
def total_shots_fired():
    query = """
        SELECT SUM(rounds_fired) AS total_shots
        FROM session_details;
    """
    df = fetch_data(query)
    total_shots = df["total_shots"].iloc[0]
    if isinstance(total_shots, Decimal):
        total_shots = int(total_shots)
    return total_shots

# Query 3: Most popular gun name
def most_popular_gun():
    query = """
        select name, count(session_details.gun_id)
        from gun
        join session_details
        on session_details.gun_id = gun.gun_id
        group by name
        order by (session_details.gun_id)
        limit 1;
    """
    df = fetch_data(query)
    popular_gun = df["name"].iloc[0]
    return popular_gun

#query 4: Session details
def session_details():
    query = """
        SELECT 
            s.session_id as "Session Number",
            s.date as "Date",
            s.duration_minutes as "Duration (minutes)",
            s.target_type as "Target Type",
            g.name AS "Gun Name",
            a.manufacturer AS "Ammo Manufacturer",
            a.type AS "Ammo Type",
            a.caliber AS "Ammo Caliber",
            sd.rounds_fired as "Rounds Fired"
        FROM 
            session s
        JOIN 
            session_details sd ON s.session_id = sd.session_id
        JOIN 
            gun g ON sd.gun_id = g.gun_id
        JOIN 
            ammo a ON sd.ammo_id = a.ammo_id
        ORDER BY 
            s.date DESC, s.time DESC
        LIMIT 5;
    """
    df = fetch_data(query)
    return df

# Streamlit App

#Set page configuration to wide mode
st.set_page_config(layout="wide")

# Set page title
st.title("Shooting Log - Gun Statistics and Progress of Minh Tran")

# Display metrics in columns
col1, col2, col3 = st.columns(3)

# Display total time at the range
with col1:
    st.subheader("Total Minutes Spent at the Range")
    total_time = total_time_at_range()
    if total_time is None or not isinstance(total_time, (int, float)):
        total_time = 0  # Default value if total_time is invalid
    st.metric("", total_time)

# Display total number of shots fired
with col2:
    st.subheader("Total Shots Fired")
    total_shots = total_shots_fired()
    if total_shots is None or not isinstance(total_shots, int):
        total_shots = 0  # Default value if total_shots is invalid
    st.metric("", total_shots)

# Display most popular gun name
with col3:
    st.subheader("Most Popular Gun")
    popular_gun = most_popular_gun()
    if popular_gun is None or not isinstance(popular_gun, str):
        popular_gun = "N/A"  # Default value if popular_gun is invalid
    st.metric("", popular_gun)

# Display session details
st.subheader("Recent Sessions")
df = session_details()
st.write(df)
