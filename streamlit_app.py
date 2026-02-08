import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. SETTINGS
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱")

# 2. SECURE CONNECTION
try:
    # We explicitly tell the connection where to find the URL
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # If the secret is failing, we use this as a backup
    target_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    df_cat = conn.read(spreadsheet=target_url, worksheet="CATALOGUE")
    st.success("✅ Digital Fortress: ONLINE")
except Exception as e:
    st.error(f"❌ Handshake Error: {e}")
    st.info("Check that your Secrets tab has the [connections.gsheets] section.")
    df_cat = None

# 3. DISPLAY
st.title(f"🌱 {FARM_NAME} OS")
if df_cat is not None:
    st.dataframe(df_cat)
