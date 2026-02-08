import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
import urllib.parse

# --- CONFIGURATION ---
FARM_NAME = "Jayeone Farms"
SECRET_KEY = "123890SKJNRREDDY"

st.set_page_config(page_title=FARM_NAME, page_icon="🌱", layout="wide")

# --- UI STYLING ---
st.markdown(f"""
    <style>
    .stButton>button {{ width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; font-weight: bold; height: 3em; }}
    .product-card {{ background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; margin-bottom: 20px; border: 1px solid #eee; }}
    .price-tag {{ color: #2e7d32; font-weight: bold; font-size: 1.3rem; }}
    .market-tag {{ color: #999; text-decoration: line-through; font-size: 0.9rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE DATA CONNECTION ---
def load_data():
    try:
        # This now automatically looks for the URL in your 'Secrets'
        conn = st.connection("gsheets", type=GSheetsConnection)
        cat = conn.read(worksheet="CATALOGUE")
        settings = conn.read(worksheet="SETTINGS")
        return cat, settings
    except Exception as e:
        st.error(f"Waiting for Secret Handshake... {e}")
        return None, None

df_cat, df_settings = load_data()

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2153/2153067.png", width=100)
    st.title("Admin Access")
    admin_key = st.text_input("Security Key", type="password")
    
    if admin_key == SECRET_KEY:
        st.success("Access Granted, Founder")
    else:
        st.info("Quality Organic Produce")

# --- CUSTOMER UI ---
st.title(f"🌱 {FARM_NAME}")

if df_cat is not None:
    cols = st.columns(3)
    cart = {}

    for idx, row in df_cat.iterrows():
        # Mapping to your exact column names
        item = row['Item_Name']
        price = row['Price']
        mkt_price = row['Market_Retail_Price']
        unit = row['Unit']
        img = row.get('Image_URL', 'https://via.placeholder.com/150?text=Farm+Fresh')

        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{img}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                <h3>{item}</h3>
                <p class="market-tag">Market: ₹{mkt_price}</p>
                <p class="price-tag">Farm: ₹{price} / {unit}</p>
            </div>
            """, unsafe_allow_html=True)
            
            qty = st.number_input("Qty", min_value=0, step=1, key=f"p_{idx}")
            if qty > 0:
                cart[item] = {"qty": qty, "price": price, "unit": unit}

    if cart:
        st.divider()
        total_bill = 0
        summary = f"*New Order: {FARM_NAME}*\n---\n"
        
        for item, details in cart.items():
            line_total = details['qty'] * details['price']
            total_bill += line_total
            summary += f"• {item}: {details['qty']} {details['unit']} = ₹{line_total}\n"
        
        summary += f"\n*Total: ₹{total_bill}*"
        st.write(f"### Grand Total: ₹{total_bill}")
        
        # Get phone from SETTINGS tab (Row 1, Column 2)
        wa_phone = str(df_settings.iloc[0, 1]) if df_settings is not None else "91"
        
        encoded_msg = urllib.parse.quote(summary)
        wa_url = f"https://wa.me/{wa_phone}?text={encoded_msg}"

        if st.button("🚀 Order via WhatsApp"):
            st.balloons()
            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">CONFIRM ON WHATSAPP</div></a>', unsafe_allow_html=True)
else:
    st.info("Syncing with the Digital Fortress... please check your Streamlit Secrets.")
