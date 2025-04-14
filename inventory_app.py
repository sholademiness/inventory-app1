import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Set your app password here
PASSWORD = "Whogoes1@"

st.set_page_config(page_title="Inventory App", layout="centered")

# --- Simple login ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    pw = st.text_input("Enter Password", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
        st.experimental_rerun()
    elif pw:
        st.error("Wrong password. Try again.")
    st.stop()

# --- App Title ---
st.title("📦 Simple Inventory System")
st.markdown("Add, view, and download your inventory (Excel format).")

# --- Initialize inventory from saved file ---
inventory_file = "inventory_data.xlsx"

if os.path.exists(inventory_file):
    df_inventory = pd.read_excel(inventory_file)
else:
    df_inventory = pd.DataFrame(columns=["Name", "Quantity", "Location"])

# --- Add New Inventory ---
with st.form("Add New Item"):
    col1, col2 = st.columns(2)
    name = col1.text_input("Product Name")
    quantity = col1.number_input("Quantity", min_value=0, step=1)
    location = col2.text_input("Location")
    submit = st.form_submit_button("Add Item")

    if submit and name and location:
        new_row = pd.DataFrame([{
            "Name": name,
            "Quantity": quantity,
            "Location": location
        }])
        df_inventory = pd.concat([df_inventory, new_row], ignore_index=True)
        df_inventory.to_excel(inventory_file, index=False)
        st.success(f"{name} added successfully!")

# --- Display Inventory ---
st.subheader("📋 Current Inventory")
if not df_inventory.empty:
    st.dataframe(df_inventory, use_container_width=True)

    # --- Download Excel ---
    def to_excel(df):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()

    st.download_button(
        "📥 Download Inventory as Excel",
        data=to_excel(df_inventory),
        file_name="inventory_download.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No inventory items yet. Add some above.")
