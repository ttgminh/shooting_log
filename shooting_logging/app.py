import streamlit as st
import mysql.connector
import datetime
import pandas as pd

# Connect to AWS RDS Database
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],  # AWS RDS endpoint
        user=st.secrets["DB_USERNAME"],  # Database username
        password=st.secrets["DB_PASSWORD"],  # Database password
        database=st.secrets["DB_NAME"]  # Database name
    )

# Verify the password to make edits
password = st.secrets["EDIT_PASSWORD"]
# Function to verify the password
def verify_password(input_password):
    return input_password == password

# Helper functions
def insert_or_get_gun(category, manufacturer, model, caliber, ownership_type, gun_notes):
    """Insert a gun if it doesn't exist, otherwise return its gun_id."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check if gun exists
    query = """
        SELECT gun_id FROM gun
        WHERE manufacturer = %s AND model = %s AND caliber = %s
    """
    cursor.execute(query, (manufacturer, model, caliber))
    result = cursor.fetchone()
    if result:
        gun_id = result[0]
    else:
        # Insert new gun
        query = """
            INSERT INTO gun (name, category, manufacturer, model, caliber, ownership_type, gun_notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, category, manufacturer, model, caliber, ownership_type, gun_notes))
        conn.commit()
        gun_id = cursor.lastrowid
    conn.close()
    return gun_id

def insert_or_get_ammo(manufacturer, ammo_type, caliber, cost_per_round, ammo_notes):
    """Insert ammo if it doesn't exist, otherwise return its ammo_id."""
    conn = get_connection()
    cursor = conn.cursor()
    # Check if ammo exists
    query = """
        SELECT ammo_id FROM ammo
        WHERE manufacturer = %s AND type = %s AND caliber = %s
    """
    cursor.execute(query, (manufacturer, ammo_type, caliber))
    result = cursor.fetchone()
    if result:
        ammo_id = result[0]
    else:
        # Insert new ammo
        query = """
            INSERT INTO ammo (manufacturer, type, caliber, cost_per_round, ammo_notes)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (manufacturer, ammo_type, caliber, cost_per_round, ammo_notes))
        conn.commit()
        ammo_id = cursor.lastrowid
    conn.close()
    return ammo_id

def insert_session_and_details(date, time, target_type, duration_minutes, gun_id, ammo_id, rounds_fired):
    """Insert a session and link it to the session_details table."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if a session for the same date already exists
    query_check = """
        SELECT session_id FROM session WHERE date = %s
    """
    cursor.execute(query_check, (date,))
    result = cursor.fetchone()

    if result:
        # If a session exists, reuse its session_id
        session_id = result[0]
    else:
        # Otherwise, create a new session
        query_insert = """
            INSERT INTO session (date, time, target_type, duration_minutes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_insert, (date, time, target_type, duration_minutes))
        session_id = cursor.lastrowid  # Get the newly created session_id

    # Insert session details
    query_details = """
        INSERT INTO session_details (session_id, gun_id, ammo_id, rounds_fired)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query_details, (session_id, gun_id, ammo_id, rounds_fired))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    return session_id


def delete_most_recent_session():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Find the most recent session
    query_find = """
        SELECT session_id FROM session
        ORDER BY date DESC, time DESC
        LIMIT 1
    """
    cursor.execute(query_find)
    result = cursor.fetchone()
    
    if result:
        session_id = result[0]
        
        # Delete session details
        query_delete_details = """
            DELETE FROM session_details WHERE session_id = %s
        """
        cursor.execute(query_delete_details, (session_id,))
        
        # Delete session
        query_delete_session = """
            DELETE FROM session WHERE session_id = %s
        """
        cursor.execute(query_delete_session, (session_id,))
        
        conn.commit()
        conn.close()
        return session_id
    else:
        conn.close()
        return None
    
def fetch_existing_guns():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT gun_id, name, category, manufacturer, model, caliber, ownership_type, gun_notes
        FROM gun
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_existing_ammo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT ammo_id, manufacturer, type, caliber, cost_per_round, ammo_notes
        FROM ammo
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

# Function to fetch the 5 most recent sessions
def fetch_recent_sessions():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier data handling
    query = """
        SELECT 
            s.session_id,
            s.date,
            s.duration_minutes,
            s.target_type,
            g.name AS gun_name,
            a.manufacturer AS ammo_manufacturer,
            a.type AS ammo_type,
            a.caliber AS ammo_caliber,
            sd.rounds_fired
        FROM 
            session s
        JOIN 
            session_details sd ON s.session_id = sd.session_id
        JOIN 
            gun g ON sd.gun_id = g.gun_id
        JOIN 
            ammo a ON sd.ammo_id = a.ammo_id
        ORDER BY 
            s.date ASC, s.time ASC;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

# Streamlit Form
st.title("Shooting Log")

#Filter for existing guns and ammo first, if not present, add new gun and ammo
    # Guns Check
existing_guns_df = pd.DataFrame(fetch_existing_guns())
existing_guns_df = existing_guns_df.sort_values(by='manufacturer')
existing_guns_df['display'] = existing_guns_df.apply(
    lambda row: f"{row['name']} - {row['ownership_type']} ({row['caliber']})", axis=1
)
existing_guns = existing_guns_df['display'].tolist()
existing_guns = existing_guns + ["Add New Gun"]

selected_gun_display = st.selectbox("Select Gun", existing_guns)

if selected_gun_display == "Add New Gun":
    selected_gun = "Add New Gun"
else:
    selected_gun = existing_guns_df.loc[existing_guns_df['display'] == selected_gun_display, 'name'].values[0]

    # Ammo Check
existing_ammo_df = pd.DataFrame(fetch_existing_ammo())
existing_ammo_df = existing_ammo_df.sort_values(by='manufacturer')
if selected_gun != "Add New Gun":
    existing_ammo_df = existing_ammo_df[existing_ammo_df['caliber'] == existing_guns_df.loc[existing_guns_df['name'] == selected_gun, 'caliber'].values[0]]
existing_ammo_df['display'] = existing_ammo_df.apply(
    lambda row: f"{row['manufacturer']} - {row['type']} ({row['caliber']})", axis=1
)
existing_ammo = existing_ammo_df['display'].tolist()
existing_ammo = existing_ammo + ["Add New Ammo"]

selected_gun_display = st.selectbox("Select Ammo", existing_ammo)

if selected_gun_display == "Add New Ammo":
    selected_ammo = "Add New Ammo"
else:
    selected_ammo = existing_ammo_df.loc[existing_ammo_df['display'] == selected_gun_display, 'manufacturer'].values[0]

with st.form("unified_form"):
    # Session Details
    st.subheader("Session Details")
    date = st.date_input("Date")
    default_time = datetime.time(8, 0)
    time = st.time_input("Time", value=default_time)
    target_type = st.selectbox("Target Type", ["Steel", "Paper"])
    target_type = target_type.lower()
    duration_minutes = st.number_input("Duration (Minutes)", min_value=1)

    # Gun Details
    if selected_gun == "Add New Gun":
        st.subheader("Gun Details")
        category_options=["Pistol", "Rifle", "Shotgun", "Revolver"]
        category = st.selectbox("Category", category_options)
        category = category.lower()
        manufacturer = st.text_input("Manufacturer")
        model = st.text_input("Model")
        caliber_options = ["9mm", ".22 LR", ".45 ACP", ".38 Special", ".223 Rem", ".308 Win", "12 Gauge"]
        caliber = st.selectbox("Caliber", caliber_options)
        caliber = caliber.lower()
        ownership_options = ["Personal", "Rental"]
        ownership_type = st.selectbox("Ownership Type", ownership_options)
        ownership_type = ownership_type.lower()
        gun_notes = st.text_area("Notes (optional)")
        name = f"{manufacturer} {model}"
    else:
        #enter existing gun information
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
        cost_per_round = st.number_input("Cost Per Round", min_value=0.01, step=0.01)
        ammo_notes = st.text_area("Ammo Notes (optional)")
    else:
        #enter existing ammo information
        selected_ammo_id = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'ammo_id'].values[0]
        ammo_manufacturer = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'manufacturer'].values[0]
        ammo_type = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'type'].values[0]
        ammo_caliber = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'caliber'].values[0]
        cost_per_round = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'cost_per_round'].values[0]
        ammo_notes = existing_ammo_df.loc[existing_ammo_df['manufacturer'] == selected_ammo, 'ammo_notes'].values[0]

    # Rounds Fired
    st.subheader("Session Details - Rounds Fired")
    rounds_fired = st.number_input("Rounds Fired", min_value=1)

    # Password Field
    password = st.text_input("Enter Password to Add Data", type="password")

    # Submit Button
    submitted = st.form_submit_button("Add All Data")

    if submitted:
        #verify password
        if password == st.secrets["EDIT_PASSWORD"]:
            try:
                # Insert gun and ammo
                gun_id = insert_or_get_gun(category, manufacturer, model, caliber, ownership_type, gun_notes)
                ammo_id = insert_or_get_ammo(ammo_manufacturer, ammo_type, ammo_caliber, cost_per_round, ammo_notes)

            # Insert session and link details
                session_id = insert_session_and_details(date, time, target_type, duration_minutes, gun_id, ammo_id, rounds_fired)

                st.success(f"Session, Gun, and Ammo added successfully! Session ID: {session_id}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Incorrect password. Please try again.")

# Password Field for Deletion
delete_password = st.text_input("Enter Password to Delete Data", type="password")
# Delete Button
delete_button = st.button("Delete Most Recent Session")
if delete_button:
    #verify password
    if delete_password == st.secrets["EDIT_PASSWORD"]:
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