import streamlit as st
# CRITICAL: The internal name is streamlit_gsheets, not st_gsheets_connection
from streamlit_gsheets import GSheetsConnection

# 1. SECURE CONFIG
FARM_NAME = "Jayeone Farms"

st.set_page_config(page_title=FARM_NAME, page_icon="🌱")

# 2. THE CONNECTION
try:
    # This pulls from your Secrets vault
    SECRET_KEY = st.secrets["SECRET_KEY"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_cat = conn.read(worksheet="CATALOGUE")
    st.success("Digital Fortress Live!")
except Exception as e:
    st.error(f"Handshake Error: {e}")
    st.info("Ensure Secrets has SECRET_KEY and [connections.gsheets] block.")
    df_cat = None

# 3. UI
st.title(f"🌱 {FARM_NAME} OS")
if df_cat is not None:
    st.dataframe(df_cat)
