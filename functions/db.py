import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USERNAME"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

def verify_password(input_password):
    return input_password == st.secrets["EDIT_PASSWORD"]

def insert_or_get_gun(category, manufacturer, model, caliber, ownership_type, gun_notes):
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
        cursor.execute(query, (f"{manufacturer} {model}", category, manufacturer, model, caliber, ownership_type, gun_notes))
        conn.commit()
        gun_id = cursor.lastrowid
    conn.close()
    return gun_id

def insert_or_get_ammo(manufacturer, ammo_type, caliber, ammo_notes):
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
            INSERT INTO ammo (manufacturer, type, caliber, ammo_notes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (manufacturer, ammo_type, caliber, ammo_notes))
        conn.commit()
        ammo_id = cursor.lastrowid
    conn.close()
    return ammo_id

def insert_session_and_details(date, time, target_type, duration_minutes, gun_id, ammo_id, rounds_fired, ammo_cost_total):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if a session for the same date already exists
    query_check = """
        SELECT session_id FROM session WHERE date = %s
    """
    cursor.execute(query_check, (date,))
    result = cursor.fetchone()

    if result:
        session_id = result[0]
    else:
        # Otherwise, create a new session
        query_insert = """
            INSERT INTO session (date, time, target_type, duration_minutes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_insert, (date, time, target_type, duration_minutes))
        session_id = cursor.lastrowid

    # Insert session details
    query_details = """
        INSERT INTO session_details (session_id, gun_id, ammo_id, rounds_fired, ammo_cost_total)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query_details, (session_id, gun_id, ammo_id, rounds_fired, ammo_cost_total))

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
        SELECT ammo_id, manufacturer, type, caliber, ammo_notes
        FROM ammo
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_recent_sessions():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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

def fetch_data(query):
    """
    Fetch data from the database using a raw SQL query.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

def fetch_all_data():
    """
    Fetch all session-related data from the database.
    """
    query = """
        SELECT 
            s.session_id,
            s.date,
            s.duration_minutes,
            sd.rounds_fired,
            sd.ammo_cost_total,
            (sd.ammo_cost_total / sd.rounds_fired) AS cost_per_round,
            g.name AS gun_name,
            g.manufacturer AS gun_manufacturer,
            a.type AS ammo_type,
            a.caliber AS ammo_caliber,
            a.manufacturer AS ammo_manufacturer
        FROM 
            session s
        JOIN 
            session_details sd ON s.session_id = sd.session_id
        JOIN 
            gun g ON sd.gun_id = g.gun_id
        JOIN 
            ammo a ON sd.ammo_id = a.ammo_id;
    """
    return fetch_data(query)
