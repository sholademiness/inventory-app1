import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ✅ FIRST Streamlit command
st.set_page_config(page_title="CBoy Inventory App", layout="wide")

# === LOGIN INFO ===
CORRECT_USERNAME = "Chekube"
CORRECT_PASSWORD = "Cmoney"

# === LOGIN FUNCTION ===
def login():
    st.title("🔐 CBoy Inventory Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()

        else:
            st.error("Invalid username or password")

# === SESSION CHECK ===
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# === LOGOUT BUTTON ===
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

# === FILE SETUP ===
if not os.path.exists("inventory.csv"):
    pd.DataFrame(columns=["Item", "Quantity"]).to_csv("inventory.csv", index=False)
if not os.path.exists("history.csv"):
    pd.DataFrame(columns=["Item", "Quantity Removed", "Date"]).to_csv("history.csv", index=False)
if not os.path.exists("added_items.csv"):
    pd.DataFrame(columns=["Item", "Quantity Added", "Date"]).to_csv("added_items.csv", index=False)

inventory_df = pd.read_csv("inventory.csv")
history_df = pd.read_csv("history.csv")
added_df = pd.read_csv("added_items.csv")

# === BACKUP ===
if not os.path.exists("backups"):
    os.makedirs("backups")

backup_filename = f"backups/cboy_backup_{date.today()}.xlsx"
if not os.path.exists(backup_filename):
    with pd.ExcelWriter(backup_filename, engine="xlsxwriter") as writer:
        inventory_df.to_excel(writer, sheet_name="Inventory", index=False)
        history_df.to_excel(writer, sheet_name="Removed", index=False)
        added_df.to_excel(writer, sheet_name="Added", index=False)

# === UI ===
st.title("📦 CBoy Inventory Management")
tab1, tab2, tab3 = st.tabs(["📋 Inventory", "➕ Add / ➖ Remove", "📊 History & Backup"])

# === TAB 1: INVENTORY ===
with tab1:
    st.subheader("📋 Current Inventory")
    st.dataframe(inventory_df, use_container_width=True)

# === TAB 2: ADD / REMOVE ===
with tab2:
    st.subheader("➕ Add Items")
    with st.form("add_form"):
        item = st.text_input("Item Name").strip()
        qty_add = st.number_input("Quantity to Add", min_value=1, step=1)
        if st.form_submit_button("Add Item"):
            if item:
                item = item.title()
                if item in inventory_df["Item"].values:
                    inventory_df.loc[inventory_df["Item"] == item, "Quantity"] += qty_add
                else:
                    inventory_df = pd.concat([inventory_df, pd.DataFrame({"Item": [item], "Quantity": [qty_add]})], ignore_index=True)
                added_df = pd.concat([added_df, pd.DataFrame({"Item": [item], "Quantity Added": [qty_add], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") ]})], ignore_index=True)
                st.success(f"Added {qty_add} {item}(s) to inventory.")
            else:
                st.error("Please enter an item name.")

    st.subheader("➖ Remove Items")
    with st.form("remove_form"):
        if inventory_df.empty:
            st.warning("Inventory is empty.")
        else:
            item_remove = st.selectbox("Select Item", inventory_df["Item"].unique())
            qty_remove = st.number_input("Quantity to Remove", min_value=1, step=1)
            if st.form_submit_button("Remove Item"):
                available = inventory_df.loc[inventory_df["Item"] == item_remove, "Quantity"].values[0]
                if qty_remove > available:
                    st.error(f"Cannot remove {qty_remove}. Only {available} available.")
                else:
                    inventory_df.loc[inventory_df["Item"] == item_remove, "Quantity"] -= qty_remove
                    history_df = pd.concat([history_df, pd.DataFrame({"Item": [item_remove], "Quantity Removed": [qty_remove], "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S") ]})], ignore_index=True)
                    st.success(f"Removed {qty_remove} {item_remove}(s) from inventory.")

# === TAB 3: HISTORY ===
with tab3:
    st.subheader("📈 Added Items")
    st.dataframe(added_df, use_container_width=True)

    st.subheader("📉 Removed Items")
    st.dataframe(history_df, use_container_width=True)

    st.subheader("⬇️ Download Excel Backup")
    with pd.ExcelWriter("cboy_temp_backup.xlsx", engine="xlsxwriter") as writer:
        inventory_df.to_excel(writer, sheet_name="Inventory", index=False)
        history_df.to_excel(writer, sheet_name="Removed", index=False)
        added_df.to_excel(writer, sheet_name="Added", index=False)
    with open("cboy_temp_backup.xlsx", "rb") as f:
        st.download_button("📥 Download Backup", f, file_name="cboy_inventory_backup.xlsx")

# === SAVE EVERYTHING ===
inventory_df.to_csv("inventory.csv", index=False)
history_df.to_csv("history.csv", index=False)
added_df.to_csv("added_items.csv", index=False)
