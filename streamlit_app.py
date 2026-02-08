import streamlit as st
import pandas as pd

# --- 1. SETUP ---
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. THE ENGINE (HIGH-SPEED & CLEAN) ---
@st.cache_data(ttl=600)
def fetch_data(sid, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    # CLEANING: This removes any row where the first column is empty or says 'None'
    df = df.dropna(how='all') # Removes completely empty rows
    df = df[df.iloc[:, 0].notna()] # Removes rows where the ID/Name is missing
    return df

try:
    sid = st.secrets["SHEET_ID"].strip()
    
    # --- 3. NAVIGATION SIDEBAR ---
    st.sidebar.title("🚜 Farm Manager")
    
    if st.sidebar.button("🔄 Sync New Data"):
        st.cache_data.clear()
        st.rerun()

    page = st.sidebar.radio("View Dashboard:", ["Orders", "Catalogue", "Stock Status"])

    st.title(f"🌱 {FARM_NAME} OS")

    # --- 4. DISPLAY LOGIC ---
    if page == "Orders":
        st.subheader("📦 Incoming Orders")
        df = fetch_data(sid, "0")
        # Shows only rows with actual order data
        st.dataframe(df, width="stretch")

    elif page == "Catalogue":
        st.subheader("🥗 Product List & Pricing")
        df = fetch_data(sid, "1608295230")
        st.dataframe(df, width="stretch")

    elif page == "Stock Status":
        st.subheader("📉 Inventory Status")
        df = fetch_data(sid, "1277793309")
        st.dataframe(df, width="stretch")

except Exception as e:
    st.error(f"System Error: {e}")
