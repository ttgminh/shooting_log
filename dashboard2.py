import streamlit as st
import pandas as pd
import plotly.express as px
from functions.db import fetch_all_data

# Fetch all data from the database
df = pd.DataFrame(fetch_all_data())

#create tabs
tab1, tab2, tab3 = st.tabs(["Main Metrics","Ammo Details", "Gun Details"])

with tab1:
    # Display metrics in Streamlit
    st.title("Gun Range Statistics")

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)

    # Total time spent at the range
    total_time = df.drop_duplicates(subset='date')['duration_minutes'].sum()
    st.metric("Total Time Spent at Range", f"{total_time} mins")

    # Total number of shots fired
    total_shots = df['rounds_fired'].sum()
    st.metric("Total Shots Fired", total_shots)

    # Most popular gun name
    popular_gun = df['gun_name'].value_counts().idxmax()
    st.metric("Most Popular Gun", popular_gun)

    # Average session duration
    avg_duration = round(df['duration_minutes'].mean())
    st.metric("Average Session Duration", f"{avg_duration} mins")

    # Average rounds fired per session
    avg_rounds_fired = round(df['rounds_fired'].mean(), 1)
    st.metric("Average Rounds Fired per Session", avg_rounds_fired)

    # Total cost of ammo
    total_ammo_cost = df['ammo_cost_total'].sum()
    formatted_total_ammo_cost = "${:,.2f}".format(total_ammo_cost)
    st.metric("Total Ammo Cost", formatted_total_ammo_cost)

    

with tab2:
    # Display ammo section stats in columns
    col1, col2 = st.columns(2)

    # Display pie chart for ammo type distribution
    ammo_type_grouped = df.groupby('ammo_type')['rounds_fired'].sum().reset_index()
    fig = px.pie(ammo_type_grouped, names='ammo_type', values='rounds_fired', title='Ammo Type Distribution')
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    # Display bar chart for ammo manufacturer distribution
    ammo_manufacturer_grouped = df.groupby('ammo_manufacturer')['rounds_fired'].sum().reset_index()
    fig = px.bar(ammo_manufacturer_grouped, x='ammo_manufacturer', y='rounds_fired', title='Ammo Manufacturer Distribution')
    with col2:
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Display gun section in columns
    col1, col2 = st.columns(2)

    # Display gun rankings
    df['rounds_fired'] = pd.to_numeric(df['rounds_fired'])
    gun_ranking_grouped = df.groupby('gun_name').agg({'rounds_fired': 'sum'}).reset_index()
    gun_ranking_grouped = gun_ranking_grouped.rename(columns={'gun_name': 'Gun Name', 'rounds_fired': 'Total Rounds Fired'})
    gun_ranking_grouped = gun_ranking_grouped.sort_values(by='Total Rounds Fired', ascending=True)

    with col1:
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

    with col2:
        fig3 = px.bar(gun_manufacturer_grouped, x='Total Rounds Fired', y='Gun Manufacturer', orientation='h', title='Gun Manufacturer Distribution', text='Total Rounds Fired', color='Total Rounds Fired', color_continuous_scale='Inferno')
        fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig3.update_layout(showlegend=False, xaxis=dict(showgrid=False, showticklabels=False))
        fig3.update(layout_coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)