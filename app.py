import streamlit as st

#streamlit config
st.set_page_config(
    page_title="Minh's Shooting Progress Tracker",
    page_icon="🔫",
    layout="wide"
)

st.title("🎯🔫 Minh's Shooting Progress Tracker 🎯🔫")

#import pages
dashboard_page = st.Page("dashboard.py", title="Dashboard", icon="📊")
logging_page = st.Page("logging.py", title="Logging", icon="📝")


pg = st.navigation([dashboard_page, logging_page])
pg.run()

