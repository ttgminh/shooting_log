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

# Query 3: Most popular guns
def most_popular_guns():
    query = """
        SELECT g.name AS gun_name, COUNT(sd.gun_id) AS usage_count
        FROM session_details sd
        JOIN gun g ON sd.gun_id = g.gun_id
        GROUP BY sd.gun_id
        ORDER BY usage_count DESC
        LIMIT 1;
    """
    return fetch_data(query)

# Query 4: Ammo usage
def ammo_usage():
    query = """
        SELECT a.manufacturer, a.type, SUM(sd.rounds_fired) AS total_shots
        FROM session_details sd
        JOIN ammo a ON sd.ammo_id = a.ammo_id
        GROUP BY a.ammo_id
        ORDER BY total_shots DESC;
    """
    return fetch_data(query)

# Query 5: Sessions over time
def sessions_over_time():
    query = """
        SELECT DATE(date) AS session_date, COUNT(session_id) AS session_count
        FROM session
        GROUP BY DATE(date)
        ORDER BY session_date;
    """
    return fetch_data(query)

# Streamlit App
st.title("Shooting Log - Gun Statistics and Progress")

# Display total time at the range
st.header("Total Time Spent at the Range")
total_time = total_time_at_range()
st.metric("Total Time (Minutes)", total_time)

# Display total shots fired
st.header("Total Shots Fired")
total_shots = total_shots_fired()
st.metric("Total Shots", total_shots)

# Display most popular guns
st.header("Most Popular Guns")
popular_guns = most_popular_guns()
st.table(popular_guns)

# Display ammo usage
st.header("Ammo Usage")
ammo_data = ammo_usage()
st.table(ammo_data)

# Display sessions over time as a chart
st.header("Sessions Over Time")
session_data = sessions_over_time()
if not session_data.empty:
    fig, ax = plt.subplots()
    ax.plot(session_data["session_date"], session_data["session_count"], marker="o")
    ax.set_title("Sessions Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Sessions")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("No session data available to display.")

# Additional analysis can go here...
