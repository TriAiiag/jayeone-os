import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
import urllib.parse

# --- 1. CONFIGURATION ---
FARM_NAME = "Jayeone Farms"
SECRET_KEY = "123890SKJNRREDDY"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mnWUg74jdlwDT2w7nd05N7hOhXuOj0TlCYAsfUOgLvc/edit?usp=sharing"

st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- 2. PROFESSIONAL UI STYLING ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; font-weight: bold; height: 3em; }}
    .product-card {{ background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; border: 1px solid #eee; }}
    .price-tag {{ color: #2e7d32; font-weight: bold; font-size: 1.3rem; }}
    .market-tag {{ color: #999; text-decoration: line-through; font-size: 0.9rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA CONNECTION ---
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Using the direct URL for connection
        cat = conn.read(spreadsheet=SHEET_URL, worksheet="CATALOGUE")
        settings = conn.read(spreadsheet=SHEET_URL, worksheet="SETTINGS")
        return cat, settings
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None, None

df_cat, df_settings = load_data()

# --- 4. THE GHOST SIDEBAR (Admin Access) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2153/2153067.png", width=100)
    st.title("Admin Access")
    admin_key = st.text_input("Enter Secret Key", type="password")
    
    if admin_key == SECRET_KEY:
        st.success("Welcome, Founder")
        st.subheader("System Health")
        st.write("✅ Database Linked")
        st.write("✅ WhatsApp Bridge Active")
    else:
        st.info("Quality Organic Produce | Anantapur")

# --- 5. MAIN CUSTOMER INTERFACE ---
st.title(f"🌱 {FARM_NAME}")
st.markdown("#### *Natural. Fresh. Fair. Direct from our farm to you.*")

if df_cat is not None:
    # Creating a 3-column grid for products
    cols = st.columns(3)
    cart = {}

    for idx, row in df_cat.iterrows():
        # Using exact column names from your sheet
        item_name = row['Item_Name']
        price = row['Price']
        mkt_price = row['Market_Retail_Price']
        unit = row['Unit']
        img = row.get('Image_URL', 'https://via.placeholder.com/150?text=Farm+Fresh')

        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{img}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                <h3>{item_name}</h3>
                <p class="market-tag">Market: ₹{mkt_price}</p>
                <p class="price-tag">Farm: ₹{price} / {unit}</p>
            </div>
            """, unsafe_allow_html=True)
            
            qty = st.number_input(f"Qty for {item_name}", min_value=0, step=1, key=f"prod_{idx}")
            if qty > 0:
                cart[item_name] = {"qty": qty, "price": price, "unit": unit}

    # --- 6. CHECKOUT & WHATSAPP LOGIC ---
    if cart:
        st.divider()
        st.subheader("🛒 Your Basket")
        total_bill = 0
        summary_text = f"*New Order from {FARM_NAME}*\n---\n"
        
        for item, details in cart.items():
            line_total = details['qty'] * details['price']
            total_bill += line_total
            summary_text += f"• {item}: {details['qty']} {details['unit']} = ₹{line_total}\n"
        
        summary_text += f"\n*Grand Total: ₹{total_bill}*\n---\n_Thank you for supporting local farmers!_"
        
        st.write(f"### Total Amount: ₹{total_bill}")
        
        # Pulling Phone from SETTINGS Row 1, Column 2
        wa_phone = df_settings.iloc[0, 1] if df_settings is not None else "91XXXXXXXXXX"
        
        encoded_msg = urllib.parse.quote(summary_text)
        wa_link = f"https://wa.me/{wa_phone}?text={encoded_msg}"

        if st.button("🚀 Confirm Order on WhatsApp"):
            st.balloons()
            st.markdown(f'''
                <a href="{wa_link}" target="_blank" style="text-decoration:none;">
                    <div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;font-size:1.1rem;">
                        CLICK HERE TO SEND ORDER
                    </div>
                </a>
            ''', unsafe_allow_html=True)
else:
    st.warning("Connecting to the farm database... please wait.")

st.divider()
st.caption("Powered by Triaiiag OS | Transparency in Agriculture")
