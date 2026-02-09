import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gspread_pandas import Spread, Client

# --- 1. SETTINGS & CONFIG ---
st.set_page_config(page_title="Jayeone Farms OS", layout="wide")

# Your Sheet ID
SHEET_ID = "1Wr7fZYZoMKLyTbpohUzYYqDPPWXH8IZVw-08PVEb5YQ"

# --- 2. THE CLEANING ENGINE ---
def get_clean_df(spread, sheet_name):
    """Fetches data by sheet name and sanitizes headers"""
    try:
        raw_df = spread.sheet_to_df(index=None, sheet=sheet_name)
        raw_df.columns = [str(c).strip() for c in raw_df.columns]
        return raw_df.loc[:, ~raw_df.columns.duplicated()].copy()
    except Exception as e:
        st.error(f"Error loading sheet '{sheet_name}': {e}")
        return pd.DataFrame()

# --- 3. CONNECTION ---
def get_spread():
    creds_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scope)
    return Spread(SHEET_ID, creds=creds)

# --- 4. MAIN APP LOGIC ---
try:
    spread = get_spread()
    
    # DEFINE 'page' FIRST HERE
    st.sidebar.title("🌿 Jayeone Farms")
    page = st.sidebar.radio("Navigate", ["Orders Dashboard", "Inventory/Stock"])

    if page == "Orders Dashboard":
        # Make sure these names "Orders" and "STOCK" match your Google Sheet tabs EXACTLY
        orders_df = get_clean_df(spread, "Orders")
        stock_df = get_clean_df(spread, "STOCK")

        if not orders_df.empty:
            # --- 5. REVENUE RESTORER ---
            if 'Total' in orders_df.columns:
                clean_rev = pd.to_numeric(orders_df['Total'].astype(str).str.replace('[\₹,]', '', regex=True), errors='coerce').fillna(0)
                total_revenue = clean_rev.sum()
            else:
                total_revenue = 0

            # --- 6. DASHBOARD METRICS ---
            st.title("📦 Orders Management")
            m1, m2, m3 = st.columns(3)
            m1.metric("Live Orders", len(orders_df))
            m2.metric("Est. Revenue", f"₹{total_revenue:,.2f}")
            m3.metric("Stock Varieties", len(stock_df) if not stock_df.empty else 0)
            
            st.divider()

            # --- 7. SEARCHABLE INVENTORY LINK ---
            veggie_options = stock_df['Item_Name'].unique().tolist() if not stock_df.empty and 'Item_Name' in stock_df.columns else []

            # --- 8. PROFESSIONAL VIEW ---
            cols_to_show = ['Order_ID', 'Customer', 'Items', 'City', 'Total', 'Packed/Dispatched']
            display_df = orders_df[[c for c in cols_to_show if c in orders_df.columns]]

            st.subheader("Current Order Queue")
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "Items": st.column_config.SelectboxColumn(
                        "Select Item",
                        options=veggie_options,
                        help="Search from farm harvest list"
                    ),
                    "Packed/Dispatched": st.column_config.CheckboxColumn("Packed?"),
                    "Total": st.column_config.NumberColumn("Amount (₹)", format="₹%d")
                },
                hide_index=True,
                use_container_width=True,
                key="order_editor"
            )

            if st.button("🚀 Sync to Digital Fortress"):
                with st.spinner("Updating Farm Records..."):
                    # This replaces the data in the "Orders" sheet
                    spread.df_to_sheet(edited_df, index=False, sheet="Orders", replace=False)
                    st.success("Synchronized! Google Sheets is now updated.")
        else:
            st.warning("No data found in the 'Orders' sheet.")

    elif page == "Inventory/Stock":
        st.title("🚜 Farm Stock")
        stock_df = get_clean_df(spread, "STOCK")
        if not stock_df.empty:
            st.dataframe(stock_df, use_container_width=True)
        else:
            st.warning("No data found in the 'STOCK' sheet.")

except Exception as e:
    st.error(f"System Connection Error: {e}")
