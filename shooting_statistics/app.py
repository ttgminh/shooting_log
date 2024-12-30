import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from decimal import Decimal
import numpy as np
import plotly.express as px

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
@st.cache_data(ttl=60)
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
@st.cache_data(ttl=60)
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
@st.cache_data(ttl=60)
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

# Query 7: Average Session Duration
@st.cache_data(ttl=60)
def avg_session_duration():
    query = """
        SELECT AVG(duration_minutes) AS avg_duration
        FROM session;
    """
    df = fetch_data(query)
    avg_duration = df["avg_duration"].iloc[0]
    if isinstance(avg_duration, Decimal):
        avg_duration = int(avg_duration)
    return avg_duration

# Query 8: Average round fired per session
@st.cache_data(ttl=60)
def avg_rounds_fired():
    query = """
        SELECT AVG(rounds_fired) AS avg_rounds_fired
        FROM session_details;
    """
    df = fetch_data(query)
    avg_rounds_fired = df["avg_rounds_fired"].iloc[0]
    if isinstance(avg_rounds_fired, Decimal):
        avg_rounds_fired = int(avg_rounds_fired)
    return avg_rounds_fired

#query 4: Session details
@st.cache_data(ttl=60)
def session_details():
    query = """
        SELECT 
            s.session_id as "Session Number",
            s.date as "Date",
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

# Query 5: Type of ammo used, caliber and rounds fired
@st.cache_data(ttl=60)
def ammo_details():
    query = """
        SELECT 
            a.type as "Ammo Type",
            a.caliber as "Ammo Caliber",
            SUM(sd.rounds_fired) as "Total Rounds Fired"
        FROM 
            ammo a
        JOIN 
            session_details sd ON a.ammo_id = sd.ammo_id
        GROUP BY 
            a.type, a.caliber
        ORDER BY 
            SUM(sd.rounds_fired) DESC;
    """
    df = fetch_data(query)
    return df

# Query 6: Gun details
#get the gun name, manufacturer, type, caliber, and total rounds fired and ammo type
@st.cache_data(ttl=60)
def gun_details():
    query = """
         SELECT 
            g.name as "Gun Name",
            g.manufacturer as "Gun Manufacturer",
            g.category as "Gun Category",
            g.caliber as "Gun Caliber",
            SUM(sd.rounds_fired) as "Total Rounds Fired",
            a.type as "Ammo Type"
        FROM
            gun g
        JOIN
            session_details sd ON g.gun_id = sd.gun_id
        JOIN
            ammo a ON sd.ammo_id = a.ammo_id
        GROUP BY
            g.name, g.manufacturer, g.category, g.caliber, a.type
        ORDER BY
            SUM(sd.rounds_fired) DESC;
    """
    df = fetch_data(query)
    return df

# Streamlit App

# Set default colormap to inferno
plt.rcParams['image.cmap'] = 'inferno'

#Set page configuration to wide mode
st.set_page_config(layout="wide")

# Set page title
st.title("Gun Range Statistics Minh Tran")

# Display metrics in columns
col1, col2, col3 = st.columns(3)

# Display total time at the range
with col1:
    st.markdown("<h3 style='text-align: center;'>Total Minutes Spent at Range</h3>", unsafe_allow_html=True)
    total_time = total_time_at_range()
    if total_time is None or not isinstance(total_time, (int, float)):
        total_time = 0  # Default value if total_time is invalid
    st.markdown(f"<h1 style='text-align: center;'>{total_time}</h1>", unsafe_allow_html=True)

# Display total number of shots fired
with col2:
    st.markdown("<h3 style='text-align: center;'>Total Shots Fired</h3>", unsafe_allow_html=True)
    total_shots = total_shots_fired()
    if total_shots is None or not isinstance(total_shots, int):
        total_shots = 0  # Default value if total_shots is invalid
    st.markdown(f"<h1 style='text-align: center;'>{total_shots}</h1>", unsafe_allow_html=True)

# Display most popular gun name
with col3:
    st.markdown("<h3 style='text-align: center;'>Most Popular Gun</h3>", unsafe_allow_html=True)
    popular_gun = most_popular_gun()
    if popular_gun is None or not isinstance(popular_gun, str):
        popular_gun = "N/A"  # Default value if popular_gun is invalid
    st.markdown(f"<h1 style='text-align: center;'>{popular_gun}</h1>", unsafe_allow_html=True)

# Display metrics in columns
col1, col2 = st.columns(2)

# Display average session duration
with col1:
    st.markdown("<h3 style='text-align: center;'>Average Session Duration</h3>", unsafe_allow_html=True)
    avg_duration = avg_session_duration()
    if avg_duration is None or not isinstance(avg_duration, (int, float)):
        avg_duration = 0  # Default value if avg_duration is invalid
    st.markdown(f"<h1 style='text-align: center;'>{avg_duration}</h1>", unsafe_allow_html=True)

# Display average rounds fired per session
with col2:
    st.markdown("<h3 style='text-align: center;'>Average Rounds Fired per Session</h3>", unsafe_allow_html=True)
    avg_rounds = avg_rounds_fired()
    if avg_rounds is None or not isinstance(avg_rounds, int):
        avg_rounds = 0  # Default value if avg_rounds is invalid
    st.markdown(f"<h1 style='text-align: center;'>{avg_rounds}</h1>", unsafe_allow_html=True)


# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Ammo section title
st.markdown("<h2 style='text-align: center;'>Ammo Details</h2>", unsafe_allow_html=True)

#Display ammo section stats in columns
col4, col5 = st.columns(2)

#Get ammo details
ammo_df = ammo_details()

# Display pie chart for ammo type distribution
ammo_type_grouped = ammo_df.groupby('Ammo Type')['Total Rounds Fired'].sum().reset_index()
with col4:
    fig1 = px.pie(ammo_type_grouped, values='Total Rounds Fired', names='Ammo Type', color_discrete_sequence=px.colors.sequential.RdBu)
    fig1.update_layout(title={'text': 'Ammo Type Distribution', 'x': 0.45, 'xanchor': 'center'})
    st.plotly_chart(fig1)

# Display pie chart for ammo caliber distribution
ammo_caliber_grouped = ammo_df.groupby('Ammo Caliber')['Total Rounds Fired'].sum().reset_index()
with col5:
    fig2 = px.pie(ammo_caliber_grouped, values='Total Rounds Fired', names='Ammo Caliber', color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_layout(title={'text': 'Ammo Caliber Distribution', 'x': 0.45, 'xanchor': 'center'})
    st.plotly_chart(fig2)

# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Ammo section title
st.markdown("<h2 style='text-align: center;'>Gun Details</h2>", unsafe_allow_html=True)

# Fetch gun ranking data
gun_ranking_df = gun_details()

#Display gun section in columns
col6, col7 = st.columns(2)

#Display gun rankings
gun_ranking_df['Total Rounds Fired'] = pd.to_numeric(gun_ranking_df['Total Rounds Fired'])
gun_ranking_grouped = gun_ranking_df.groupby('Gun Name').agg({'Total Rounds Fired': 'sum'}).reset_index()
gun_ranking_grouped = gun_ranking_grouped.sort_values(by='Total Rounds Fired', ascending=True)

with col6:
    fig = px.bar(gun_ranking_grouped, x='Total Rounds Fired', y='Gun Name', orientation='h', title='Gun Rankings by Most Shots Fired', text='Total Rounds Fired', color='Total Rounds Fired', color_continuous_scale='Inferno')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(showlegend=False,xaxis=dict(showgrid=False, showticklabels=False))
    fig.update(layout_coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# Display gun manufacturer distribution
gun_manufacturer_grouped = gun_ranking_df.groupby('Gun Manufacturer')['Total Rounds Fired'].sum().reset_index()
gun_manufacturer_grouped['Gun Manufacturer'] = gun_manufacturer_grouped['Gun Manufacturer'].str.capitalize()
gun_manufacturer_grouped = gun_manufacturer_grouped.sort_values(by='Total Rounds Fired', ascending=True)

with col7:
    fig3 = px.bar(
        gun_manufacturer_grouped,   
        x='Total Rounds Fired', 
        y='Gun Manufacturer', 
        orientation='h', 
        title='Gun Manufacturer Distribution', 
        text='Total Rounds Fired', 
        color='Total Rounds Fired', 
        color_continuous_scale='Inferno'
    )
    fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig3.update_layout(showlegend=False, xaxis=dict(showgrid=False, showticklabels=False))
    fig3.update(layout_coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Ammo section title
st.markdown("<h2 style='text-align: center;'>Session Details</h2>", unsafe_allow_html=True)

# Display session details
st.subheader("Recent Sessions")
df = session_details()
st.write(df)

# Display the date distribution of the sessions with bar chart
session_date_grouped = df.groupby('Date').size().reset_index(name='Count')
session_date_grouped['Date'] = pd.to_datetime(session_date_grouped['Date'])

# Group by week
session_date_grouped['Week'] = session_date_grouped['Date'].dt.to_period('W').apply(lambda r: r.start_time)
weekly_grouped = session_date_grouped.groupby('Week')['Count'].sum().reset_index()

fig4 = px.bar(weekly_grouped, x='Week', y='Count', title='Weekly Session Date Distribution')
fig4.update_xaxes(title_text='Week')
fig4.update_yaxes(title_text='Count')
st.plotly_chart(fig4)
