import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP ---
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. THE ENGINE ---
def get_gspread_client():
    creds_dict = st.secrets["gspread_credentials"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def fetch_data(sid, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    return pd.read_csv(url).dropna(how='all')

try:
    sid = st.secrets["SHEET_ID"].strip()
    
    st.sidebar.title("🚜 Farm Manager")
    page = st.sidebar.radio("View Dashboard:", ["Orders", "Catalogue", "Stock Status"])

    st.title(f"🌱 {FARM_NAME} OS")

    if page == "Orders":
        st.subheader("📦 Incoming Orders")
        raw_df = fetch_data(sid, "0")
        
        # --- THE HIDE ENGINE: This removes the redundant column from view ---
        # It looks for any variation of the name
        display_df = raw_df.copy()
        for col in ["Packed/Dispatched", "Status", "packed/dispatched"]:
            if col in display_df.columns:
                display_df = display_df.drop(columns=[col])

        # Interactive Editor
        edited_df = st.data_editor(display_df, width="stretch", hide_index=True)

        if st.button("💾 Save Changes to Digital Fortress"):
            with st.spinner("Writing to Jayeone Cloud..."):
                client = get_gspread_client()
                sh = client.open_by_key(sid)
                # Opening the specific tab named 'ORDERS'
                worksheet = sh.worksheet("ORDERS") 
                
                # Syncing data back
                worksheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success("✅ Records Synced Successfully!")
                st.cache_data.clear()

    elif page == "Catalogue":
        st.dataframe(fetch_data(sid, "1608295230"), width="stretch", hide_index=True)

    elif page == "Stock Status":
        st.dataframe(fetch_data(sid, "1277793309"), width="stretch", hide_index=True)

except Exception as e:
    st.error(f"System Error: {e}")
