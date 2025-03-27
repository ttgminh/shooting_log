import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import datetime
from functions.db import fetch_all_data
from functions.dash import display_metric

alt.themes.enable("dark")

# Fetch all data from the database
df = pd.DataFrame(fetch_all_data())

#create tabs
tab1, tab2, tab3 = st.tabs(["Main Metrics","Ammo Details", "Gun Details"])

with tab1:
    # Display metrics in Streamlit
    st.title("Gun Range Statistics")

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        # Total time spent at the range
        total_time = df.drop_duplicates(subset='date')['duration_minutes'].sum()
        display_metric(col1, "Total Time Spent at Range", f"{total_time} mins")

        # Total number of shots fired
        total_shots = df['rounds_fired'].sum()
        display_metric(col1, "Total Shots Fired", total_shots)

    with col2:
        # Most popular gun name
        popular_gun = df['gun_name'].value_counts().idxmax()
        display_metric(col2, "Most Popular Gun", popular_gun)

        # Average session duration
        avg_duration = round(df['duration_minutes'].mean())
        display_metric(col2, "Average Session Duration", f"{avg_duration} mins")

    with col3:
        # Average rounds fired per session
        avg_rounds_fired = round(df['rounds_fired'].mean(), 1)
        display_metric(col3, "Average Rounds Fired per Session", avg_rounds_fired)

        # Total cost of ammo
        total_ammo_cost = df['ammo_cost_total'].sum()
        formatted_total_ammo_cost = "${:,.2f}".format(total_ammo_cost)
        display_metric(col3, "Total Ammo Cost", formatted_total_ammo_cost)

    # Session raw data ordered by date descending
    st.title("Session Data")
    df_sorted = df.sort_values(by='date', ascending=False)
    st.write(df_sorted)

with tab2:
    # Metrics for ammo details
    st.title("Ammo Details")

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Number of unique ammos
        unique_ammo_count = df['ammo_type'].nunique()
        display_metric(col1, "Unique Ammo Types", unique_ammo_count)

    with col2:
        # Total rounds fired
        total_rounds_fired = df['rounds_fired'].sum()
        display_metric(col2, "Total Rounds Fired", total_rounds_fired)

    with col3:
        # Average rounds fired per session
        avg_rounds_fired = df['rounds_fired'].mean()
        display_metric(col3, "Avg Rounds/Session", round(avg_rounds_fired, 1))

    with col4:
        # Average cost per round
        avg_cost_per_round = df['ammo_cost_total'].sum() / df['rounds_fired'].sum()
        display_metric(col4, "Avg Cost/Round", f"${avg_cost_per_round:.2f}")

    # Display ammo section stats in columns
    col5, col6 = st.columns([1,3])
    
    # Display pie chart for ammo type distribution
    ammo_type_grouped = df.groupby('ammo_type')['rounds_fired'].sum().reset_index()
    fig = px.pie(ammo_type_grouped, names='ammo_type', values='rounds_fired', title='Ammo Type Distribution',color_discrete_sequence=px.colors.sequential.Inferno)
    with col5:
        st.plotly_chart(fig, use_container_width=True)

    # Display bar chart for ammo manufacturer distribution
    ammo_manufacturer_grouped = df.groupby('ammo_manufacturer')['rounds_fired'].sum().reset_index()
    ammo_manufacturer_grouped = ammo_manufacturer_grouped.sort_values(by='rounds_fired', ascending=False)
    fig = px.bar(ammo_manufacturer_grouped, x='ammo_manufacturer', y='rounds_fired', title='Ammo Manufacturer Distribution', color_discrete_sequence=["#FF0000"])
    fig.update_layout(
        yaxis=dict(showticklabels=False, showgrid=False),
        xaxis_title='Ammo Manufacturer',
        yaxis_title='Total Rounds Fired'
    )
    fig.update_traces(
        text=ammo_manufacturer_grouped['rounds_fired'],
        textposition='outside'
    )
    with col6:
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Display Gun section title
    st.title("Gun Details")

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Number of unique guns
        unique_gun_count = df['gun_name'].nunique()
        display_metric(col1, "Unique Guns", unique_gun_count)

    with col2:
        # Most popular gun name
        popular_gun = df['gun_name'].value_counts().idxmax()
        display_metric(col2, "Most Popular Gun", popular_gun)

    with col3:
        # Most Recent Gun Used
        most_recent_gun = df['gun_name'].iloc[-1]
        display_metric(col3, "Most Recent Gun Used", most_recent_gun)

    with col4:
        # Gun with the highest average rounds per session
        avg_rounds_per_gun = df.groupby('gun_name')['rounds_fired'].mean().idxmax()
        display_metric(col4, "Highest Avg Rounds/Session Gun", avg_rounds_per_gun)
    
    # Display gun section in columns
    col5, col6 = st.columns(2)

    # Display gun rankings
    df['rounds_fired'] = pd.to_numeric(df['rounds_fired'])
    gun_ranking_grouped = df.groupby('gun_name').agg({'rounds_fired': 'sum'}).reset_index()
    gun_ranking_grouped = gun_ranking_grouped.rename(columns={'gun_name': 'Gun Name', 'rounds_fired': 'Total Rounds Fired'})
    gun_ranking_grouped = gun_ranking_grouped.sort_values(by='Total Rounds Fired', ascending=True)

    with col5:
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

    with col6:
        fig3 = px.bar(gun_manufacturer_grouped, x='Total Rounds Fired', y='Gun Manufacturer', orientation='h', title='Gun Manufacturer Distribution', text='Total Rounds Fired', color='Total Rounds Fired', color_continuous_scale='Inferno')
        fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig3.update_layout(showlegend=False, xaxis=dict(showgrid=False, showticklabels=False))
        fig3.update(layout_coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)