import streamlit as st
import pandas as pd
import urllib.parse
# We are moving the import inside a try-block to catch the EXACT error
try:
    from st_gsheets_connection import GSheetsConnection
except ImportError:
    st.error("SYSTEM ALERT: The GSheets library is NOT installed. Check requirements.txt")

# --- CONFIGURATION ---
FARM_NAME = "Jayeone Farms"
# We pull it from the hidden vault:
SECRET_KEY = st.secrets["SECRET_KEY"]

st.set_page_config(page_title=FARM_NAME, page_icon="🌱")

# --- MANUAL OVERRIDE CONNECTION ---
try:
    # This is the "Brute Force" way to connect
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_cat = conn.read(worksheet="CATALOGUE")
    df_settings = conn.read(worksheet="SETTINGS")
except Exception as e:
    st.error(f"CONNECTION ERROR: {e}")
    st.info("Check if your Secret URL is on ONE SINGLE LINE in the settings.")
    df_cat, df_settings = None, None

# --- UI (Simplified for Debugging) ---
st.title(f"🌱 {FARM_NAME} OS")

if df_cat is not None:
    st.success("Fortress Connected!")
    # Show a simple list to prove it works
    for idx, row in df_cat.iterrows():
        st.write(f"✅ {row['Item_Name']} - ₹{row['Price']}")
else:
    st.warning("Awaiting Data...")
