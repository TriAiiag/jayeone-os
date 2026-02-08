import streamlit as st
import pandas as pd

# --- 1. SETUP ---
FARM_NAME = "Jayeone Farms"
st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. ENGINE ---
@st.cache_data(ttl=600)
def fetch_data(sid, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df = df.dropna(how='all').reset_index(drop=True)
    df = df[df.iloc[:, 0].notna()]
    return df

try:
    sid = st.secrets["SHEET_ID"].strip()
    
    st.sidebar.title("🚜 Farm Manager")
    page = st.sidebar.radio("View Dashboard:", ["Orders", "Catalogue", "Stock Status"])
    
    if st.sidebar.button("🔄 Sync New Data"):
        st.cache_data.clear()
        st.rerun()

    st.title(f"🌱 {FARM_NAME} OS")

    if page == "Orders":
        st.subheader("📦 Incoming Orders")
        raw_df = fetch_data(sid, "0")
        
        # --- THE FIX: Create a real checkbox column from scratch ---
        # This prevents the "cannot be interpreted as boolean" error
        display_df = raw_df.copy()
        display_df.insert(0, "Packed?", False) # Inserts a False (Checkbox) column at the start

        st.data_editor(
            display_df,
            column_config={
                "Packed?": st.column_config.CheckboxColumn(
                    "Packed?",
                    help="Check this when the order is ready",
                    default=False,
                )
            },
            # We disable all other columns so the checkbox is the only thing you can click
            disabled=[col for col in display_df.columns if col != "Packed?"],
            width="stretch",
            hide_index=True
        )

    elif page == "Catalogue":
        st.subheader("🥗 Product List & Pricing")
        df = fetch_data(sid, "1608295230")
        st.dataframe(df, width="stretch", hide_index=True)

    elif page == "Stock Status":
        st.subheader("📉 Inventory Status")
        df = fetch_data(sid, "1277793309")
        st.dataframe(df, width="stretch", hide_index=True)

except Exception as e:
    st.error(f"System Error: {e}")
