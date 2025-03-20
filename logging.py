import streamlit as st
import datetime
import pandas as pd
from functions.db import (
    get_connection,
    verify_password,
    insert_or_get_gun,
    insert_or_get_ammo,
    insert_session_and_details,
    delete_most_recent_session,
    fetch_existing_guns,
    fetch_existing_ammo,
    fetch_recent_sessions,
)

# Streamlit Form
st.title("Shooting Log")

# Filter for existing guns and ammo first, if not present, add new gun and ammo
existing_guns_df = pd.DataFrame(fetch_existing_guns())
existing_guns_df = existing_guns_df.sort_values(by='manufacturer')
existing_guns_df['display'] = existing_guns_df.apply(
    lambda row: f"{row['name']} - {row['ownership_type']} ({row['caliber']})", axis=1
)
existing_guns = existing_guns_df['display'].tolist() + ["Add New Gun"]

selected_gun_display = st.selectbox("Select Gun", existing_guns)

if selected_gun_display == "Add New Gun":
    selected_gun = "Add New Gun"
else:
    selected_gun = existing_guns_df.loc[existing_guns_df['display'] == selected_gun_display, 'name'].values[0]

existing_ammo_df = pd.DataFrame(fetch_existing_ammo())
existing_ammo_df = existing_ammo_df.sort_values(by='manufacturer')
if selected_gun != "Add New Gun":
    existing_ammo_df = existing_ammo_df[
        existing_ammo_df['caliber'] == existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'caliber'].values[0]
    ]
existing_ammo_df['display'] = existing_ammo_df.apply(
    lambda row: f"{row['manufacturer']} - {row['type']} ({row['caliber']})", axis=1
)
existing_ammo = existing_ammo_df['display'].tolist() + ["Add New Ammo"]

selected_ammo_display = st.selectbox("Select Ammo", existing_ammo)

if selected_ammo_display == "Add New Ammo":
    selected_ammo = "Add New Ammo"
else:
    selected_ammo = existing_ammo_df.loc[existing_ammo_df['display'] == selected_ammo_display, 'manufacturer'].values[0]

with st.form("unified_form"):
    # Session Details
    st.subheader("Session Details")
    date = st.date_input("Date")
    default_time = datetime.time(8, 0)
    time = st.time_input("Time", value=default_time)
    target_type = st.selectbox("Target Type", ["Steel", "Paper"]).lower()
    duration_minutes = st.number_input("Duration (Minutes)", min_value=1)

    # Gun Details
    if selected_gun == "Add New Gun":
        st.subheader("Gun Details")
        category = st.selectbox("Category", ["Pistol", "Rifle", "Shotgun", "Revolver"]).lower()
        manufacturer = st.text_input("Manufacturer")
        model = st.text_input("Model")
        caliber = st.selectbox("Caliber", ["9mm", ".22 LR", ".45 ACP", ".38 Special", ".223 Rem", ".308 Win", "12 Gauge"]).lower()
        ownership_type = st.selectbox("Ownership Type", ["Personal", "Rental"]).lower()
        gun_notes = st.text_area("Notes (optional)")
        name = f"{manufacturer} {model}"
    else:
        selected_gun_id = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'gun_id'].values[0]
        category = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'category'].values[0]
        manufacturer = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'manufacturer'].values[0]
        model = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'model'].values[0]
        caliber = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'caliber'].values[0]
        ownership_type = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'ownership_type'].values[0]
        gun_notes = existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'gun_notes'].values[0]
        name = selected_gun

    # Ammo Details
    if selected_ammo == "Add New Ammo":
        st.subheader("Ammo Details")
        ammo_manufacturer = st.text_input("Ammo Manufacturer")
        ammo_type = st.text_input("Ammo Type (e.g., FMJ, HP)")
        ammo_caliber = st.text_input("Ammo Caliber (e.g., 9mm, .22 LR)")
        ammo_notes = st.text_area("Ammo Notes (optional)")
    else:
        selected_ammo_id = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'ammo_id'].values[0]
        ammo_manufacturer = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'manufacturer'].values[0]
        ammo_type = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'type'].values[0]
        ammo_caliber = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'caliber'].values[0]
        ammo_notes = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'ammo_notes'].values[0]

    # Rounds Fired
    st.subheader("Session Details - Rounds Fired and Ammo Cost")
    rounds_fired = st.number_input("Rounds Fired", min_value=50)
    ammo_cost_total = st.number_input("Ammo Cost Total", min_value=0.0)

    # Password Field
    password = st.text_input("Enter Password to Add Data", type="password")

    # Submit Button
    submitted = st.form_submit_button("Add All Data")

    if submitted:
        if verify_password(password):
            try:
                gun_id = insert_or_get_gun(category, manufacturer, model, caliber, ownership_type, gun_notes)
                ammo_id = insert_or_get_ammo(ammo_manufacturer, ammo_type, ammo_caliber, ammo_notes)
                session_id = insert_session_and_details(date, time, target_type, duration_minutes, gun_id, ammo_id, rounds_fired, ammo_cost_total)
                st.success(f"Session, Gun, and Ammo added successfully! Session ID: {session_id}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Incorrect password. Please try again.")

# Password Field for Deletion
delete_password = st.text_input("Enter Password to Delete Data", type="password")
delete_button = st.button("Delete Most Recent Session")
if delete_button:
    if verify_password(delete_password):
        try:
            session_id = delete_most_recent_session()
            if session_id:
                st.success(f"Session with ID {session_id} deleted successfully!")
            else:
                st.warning("No sessions found to delete.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Incorrect password. Please try again.")

# Display recent sessions
st.header("Recent Sessions")
recent_sessions = fetch_recent_sessions()
df = pd.DataFrame(recent_sessions)
st.write(df)