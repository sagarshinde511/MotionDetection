import streamlit as st
import pandas as pd
import mysql.connector

# Set up page configuration
st.set_page_config(
    page_title="Motion Detection Log Dashboard",
    page_icon="🎥",
    layout="wide"
)

# Database Configuration (Matching your credentials)
db_config = {
    'host': "82.180.143.66",
    'user': "u263681140_AttendanceInt",
    'password': "SagarAtten@12345",
    'database': "u263681140_Attendance"
}

def fetch_motion_data():
    """
    Fetches the motion detection logs from the MySQL database.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        # Fetch data in descending order of ID so the newest events appear first
        query = "SELECT id, start AS 'Motion Start', end AS 'Motion End' FROM MotionDetected ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame() # Return empty DataFrame on failure

# --- Dashboard UI Layout ---

st.title("🎥 Live Motion Detection Log Dashboard")
st.write("This application monitors and displays data captured from the MediaPipe tracking loop.")

# Sidebar Controls
st.sidebar.header("Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh (10s)", value=True)

# Main Dashboard Metric Counters
df_logs = fetch_motion_data()

if not df_logs.empty:
    total_detections = len(df_logs)
    
    # Check if currently active (latest row has no 'end' time stamp or is '0')
    latest_end = str(df_logs.iloc[0]['Motion End']).strip()
    is_active = latest_end == '0' or latest_end == '' or latest_end.lower() == 'none'
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Motion Events Logged", value=total_detections)
    with col2:
        if is_active:
            st.image("https://img.shields.io/badge/Status-Active%20Motion%20Detected-red?style=for-the-badge&logo=liveperson", use_container_width=False)
        else:
            st.image("https://img.shields.io/badge/Status-No%20Motion-green?style=for-the-badge", use_container_width=False)

    st.markdown("---")
    
    # Render the Interactive Data Table
    st.subheader("📋 Logged Activity History")
    st.dataframe(
        df_logs, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("Log ID", format="%d"),
            "Motion Start": st.column_config.TextColumn("Start Timestamp 🟢"),
            "Motion End": st.column_config.TextColumn("End Timestamp 🔴"),
        }
    )
else:
    st.info("No motion logs found in the database table yet. Start your Python tracking script to begin recording rows.")

# Auto-refresh mechanism
if auto_refresh:
    st.empty()
    import time
    time.sleep(10)
    st.rerun()
