import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP ---
FARM_NAME = "Jayeone Farms OS"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. THE ENGINE ---
def get_gspread_client():
    # Authenticates using fixed Secrets
    creds_dict = st.secrets["gspread_credentials"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def fetch_data(sid, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    # Loads and immediately removes rows that are entirely empty
    return pd.read_csv(url).dropna(how='all')

try:
    sid = st.secrets["SHEET_ID"].strip()
    page = st.sidebar.radio("Dashboard:", ["Orders", "Catalogue", "Stock Status"])
    st.title(f"🌱 {FARM_NAME}")

    if page == "Orders":
        st.subheader("📦 Incoming Orders")
        raw_df = fetch_data(sid, "0")
        
        # --- THE CLEANUP ENGINE ---
        # 1. Removes all rows where the first column (Order_ID) is empty
        display_df = raw_df[raw_df.iloc[:, 0].notna()].copy()
        
        # 2. Specifically drops columns you don't want visible
        cols_to_drop = ["Packed/Dispatched", "Status", "Timestamp", "packed/dispatched"]
        display_df = display_df.drop(columns=[c for c in cols_to_drop if c in display_df.columns], errors='ignore')

        # Interactive Table
        edited_df = st.data_editor(display_df, width="stretch", hide_index=True)

        if st.button("💾 Save Changes to Digital Fortress"):
            with st.spinner("Syncing with Jayeone Cloud..."):
                client = get_gspread_client()
                sh = client.open_by_key(sid)
                # Matches your exact tab 'ORDERS'
                worksheet = sh.worksheet("ORDERS") 
                # Overwrites only the active data area
                worksheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success("✅ Dashboard Updated!")
                st.cache_data.clear()

    elif page == "Catalogue":
        # Pulls from GID 1608295230
        st.dataframe(fetch_data(sid, "1608295230"), width="stretch", hide_index=True)

    elif page == "Stock Status":
        # Pulls from GID 1277793309
        st.dataframe(fetch_data(sid, "1277793309"), width="stretch", hide_index=True)

except Exception as e:
    st.error(f"System Error: {e}")
