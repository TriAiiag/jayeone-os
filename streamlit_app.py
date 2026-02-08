import streamlit as st
import pandas as pd

# --- 1. SETUP ---
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. DATA FETCHING ---
try:
    # Get the clean base URL from Secrets
    raw_url = st.secrets["spreadsheet_url"].strip()
    # Remove any accidental trailing slashes or /edit tags
    base_url = raw_url.split('/edit')[0].rstrip('/')
    
    @st.cache_data(ttl=60)
    def fetch_data(gid_code):
        # The exact format Google expects for a clean CSV export
        export_url = f"{base_url}/export?format=csv&gid={gid_code}"
        return pd.read_csv(export_url)

    # --- 3. NAVIGATION ---
    st.sidebar.title("🚜 Farm Manager")
    page = st.sidebar.radio("View Dashboard:", ["Orders", "Catalogue", "Stock"])

    st.title(f"🌱 {FARM_NAME} OS")

    # Map the pages to your actual Sheet GIDs
    if page == "Orders":
        st.subheader("📦 Real-Time Orders")
        df = fetch_data("0") # Usually the first tab
        st.dataframe(df, width="stretch")

    elif page == "Catalogue":
        st.subheader("🥗 Product Catalogue")
        df = fetch_data("1277793309") # Your Catalogue GID
        st.dataframe(df, width="stretch")

    elif page == "Stock":
        st.subheader("📉 Inventory Status")
        df = fetch_data("1374567283") # Your Stock GID
        st.dataframe(df, width="stretch")

except Exception as e:
    st.error(f"Handshake Error: {e}")
    st.info("Try removing '/edit?usp=sharing' from the URL in your Secrets tab.")
