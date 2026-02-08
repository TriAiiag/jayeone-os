import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP ---
st.set_page_config(page_title="Jayeone Farms OS", page_icon="🌱", layout="wide")

# --- 2. ENGINE ---
def get_gspread_client():
    creds_dict = st.secrets["gspread_credentials"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def fetch_data(sid, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

try:
    sid = st.secrets["SHEET_ID"].strip()
    page = st.sidebar.radio("Dashboard:", ["Orders", "Catalogue", "Stock"])

    if page == "Orders":
        st.subheader("📦 Incoming Orders")
        raw_df = fetch_data(sid, "0")
        
        # --- THE CLEANUP LAYER ---
        # 1. Strip hidden spaces and drop unwanted columns
        raw_df.columns = raw_df.columns.str.strip()
        display_df = raw_df.drop(columns=["Packed/Dispatched", "Status", "Timestamp"], errors='ignore')
        
        # 2. Kill the 'None' rows (If first column is empty, hide the row)
        display_df = display_df[display_df.iloc[:, 0].notna()].copy()

        # THE INTERACTIVE EDITOR
        edited_df = st.data_editor(display_df, width="stretch", hide_index=True)

        if st.button("💾 Save to Google Sheet"):
            with st.spinner("Writing to Digital Fortress..."):
                client = get_gspread_client()
                sh = client.open_by_key(sid)
                worksheet = sh.worksheet("ORDERS") 
                # Updates the sheet with cleaned data
                worksheet.update([edited_df.columns.values.tolist()] + edited_df.values.tolist())
                st.success("✅ Changes Saved!")
                st.cache_data.clear()

    elif page == "Catalogue":
        st.dataframe(fetch_data(sid, "1608295230").dropna(how='all'), width="stretch", hide_index=True)

    elif page == "Stock":
        st.dataframe(fetch_data(sid, "1277793309").dropna(how='all'), width="stretch", hide_index=True)

except Exception as e:
    st.error(f"⚠️ {e}")
