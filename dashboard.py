import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from functions.db import fetch_all_data

# Fetch all data from the database
df = pd.DataFrame(fetch_all_data())

# Total time spent at the range
total_time = df.drop_duplicates(subset='date')['duration_minutes'].sum()

# Total number of shots fired
total_shots = df['rounds_fired'].sum()

# Most popular gun name
popular_gun = df['gun_name'].value_counts().idxmax()

# Average session duration
avg_duration = round(df['duration_minutes'].mean())

# Average rounds fired per session
avg_rounds_fired = round(df['rounds_fired'].mean(), 1)

# Total cost of ammo
total_ammo_cost = df['ammo_cost_total'].sum()

# Set default colormap to inferno
plt.rcParams['image.cmap'] = 'inferno'

# Display metrics in Streamlit
st.title("Gun Range Statistics")

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Time Spent at Range", f"{total_time} mins")
    st.metric("Total Shots Fired", total_shots)

with col2:
    st.metric("Most Popular Gun", popular_gun)
    st.metric("Average Session Duration", f"{avg_duration} mins")

with col3:
    formatted_total_ammo_cost = "${:,.2f}".format(total_ammo_cost)
    st.metric("Average Rounds Fired per Session", avg_rounds_fired)
    st.metric("Total Ammo Cost", formatted_total_ammo_cost)

# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Ammo section title
st.markdown("<h2 style='text-align: center;'>Ammo Details</h2>", unsafe_allow_html=True)

# Display ammo section stats in columns
col4, col5 = st.columns(2)

# Display pie chart for ammo type distribution
ammo_type_grouped = df.groupby('ammo_type')['rounds_fired'].sum().reset_index()
ammo_type_grouped = ammo_type_grouped.rename(columns={'rounds_fired': 'Rounds Fired', 'ammo_type': 'Ammo Type'})
with col4:
    fig1 = px.pie(ammo_type_grouped, values='Rounds Fired', names='Ammo Type', color_discrete_sequence=px.colors.sequential.RdBu)
    fig1.update_layout(title={'text': 'Ammo Type Distribution', 'x': 0.45, 'xanchor': 'center'})
    st.plotly_chart(fig1)

# Display pie chart for ammo caliber distribution
ammo_caliber_grouped = df.groupby('ammo_caliber')['rounds_fired'].sum().reset_index()
ammo_caliber_grouped = ammo_caliber_grouped.rename(columns={'rounds_fired': 'Total Rounds Fired', 'ammo_caliber': 'Ammo Caliber'})
with col5:
    fig2 = px.pie(ammo_caliber_grouped, values='Total Rounds Fired', names='Ammo Caliber', color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_layout(title={'text': 'Ammo Caliber Distribution', 'x': 0.45, 'xanchor': 'center'})
    st.plotly_chart(fig2)

# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Gun section title
st.markdown("<h2 style='text-align: center;'>Gun Details</h2>", unsafe_allow_html=True)

# Display gun section in columns
col6, col7 = st.columns(2)

# Display gun rankings
df['rounds_fired'] = pd.to_numeric(df['rounds_fired'])
gun_ranking_grouped = df.groupby('gun_name').agg({'rounds_fired': 'sum'}).reset_index()
gun_ranking_grouped = gun_ranking_grouped.rename(columns={'gun_name': 'Gun Name', 'rounds_fired': 'Total Rounds Fired'})
gun_ranking_grouped = gun_ranking_grouped.sort_values(by='Total Rounds Fired', ascending=True)

with col6:
    fig = px.bar(gun_ranking_grouped, x='Total Rounds Fired', y='Gun Name', orientation='h', title='Gun Rankings by Most Shots Fired', text='Total Rounds Fired', color='Total Rounds Fired', color_continuous_scale='Inferno')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, showticklabels=False))
    fig.update(layout_coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# Display gun manufacturer distribution
df['gun_manufacturer'] = df['gun_manufacturer'].str.capitalize()
gun_manufacturer_grouped = df.groupby('gun_manufacturer')['rounds_fired'].sum().reset_index()
gun_manufacturer_grouped = gun_manufacturer_grouped.rename(columns={'gun_manufacturer': 'Gun Manufacturer', 'rounds_fired': 'Total Rounds Fired'})
gun_manufacturer_grouped = gun_manufacturer_grouped.sort_values(by='Total Rounds Fired', ascending=True)

with col7:
    fig3 = px.bar(gun_manufacturer_grouped, x='Total Rounds Fired', y='Gun Manufacturer', orientation='h', title='Gun Manufacturer Distribution', text='Total Rounds Fired', color='Total Rounds Fired', color_continuous_scale='Inferno')
    fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig3.update_layout(showlegend=False, xaxis=dict(showgrid=False, showticklabels=False))
    fig3.update(layout_coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

# Add a horizontal divider
st.markdown("<hr>", unsafe_allow_html=True)

# Display Session Details section title
st.markdown("<h2 style='text-align: center;'>Session Details</h2>", unsafe_allow_html=True)

# Display session details
st.subheader("Sessions Raw Data")
st.write(df)

# Display the date distribution of the sessions with bar chart
session_date_grouped = df.groupby('date').size().reset_index(name='Count')
session_date_grouped['date'] = pd.to_datetime(session_date_grouped['date'])

# Group by week
session_date_grouped['Week'] = session_date_grouped['date'].dt.to_period('W').apply(lambda r: r.start_time)
weekly_grouped = session_date_grouped.groupby('Week')['Count'].sum().reset_index()

fig4 = px.bar(weekly_grouped, x='Week', y='Count', title='Weekly Session Date Distribution')
fig4.update_xaxes(title_text='Week')
fig4.update_yaxes(title_text='Count')
st.plotly_chart(fig4)