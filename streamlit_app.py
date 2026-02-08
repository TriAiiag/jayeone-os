import streamlit as st
import pandas as pd

# 1. THE FOUNDATION
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱")

# 2. THE FAST-TRACK CONNECTION
# This converts your Google Sheet link into a direct "Download CSV" link
RAW_URL = "https://docs.google.com/spreadsheets/d/1mnWUg74jdlwDT2w7nd05N7hOhXuOj0TlCYAsfUOgLvc/export?format=csv"

@st.cache_data(ttl=60) # Refreshes every minute
def fetch_data(url):
    try:
        # Direct read is 10x faster than the library handshake
        return pd.read_csv(url)
    except Exception as e:
        return None

# 3. UI & LOGIC
st.title(f"🌱 {FARM_NAME} OS")

data = fetch_data(RAW_URL)

if data is not None:
    st.success("✅ Connected to Farm Database")
    st.dataframe(data, use_container_width=True)
else:
    st.error("❌ Connection Timeout")
    st.info("Check if your Google Sheet is still set to 'Anyone with the link'.")
