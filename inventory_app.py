import streamlit as st
import pandas as pd
import os

DATA_FILE = "inventory.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Item", "Quantity"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def add_item(df, name, quantity):
    if name in df["Item"].values:
        st.warning("Item already exists. Use 'Update Item' instead.")
    else:
        new_row = {"Item": name, "Quantity": quantity}
        df.loc[len(df)] = new_row
        save_data(df)
        st.success(f"Added {name} with {quantity} units.")

def update_item(df, name, quantity):
    if name in df["Item"].values:
        df.loc[df["Item"] == name, "Quantity"] = quantity
        save_data(df)
        st.success(f"Updated {name} to {quantity} units.")
    else:
        st.warning("Item not found. Use 'Add Item' to add new items.")

st.set_page_config(page_title="CBoy Inventory App", page_icon="📦")
st.title("📦 CBoy Inventory App")

menu = st.sidebar.radio("Menu", ["View Inventory", "Add Item", "Update Item"])

df = load_data()

if menu == "View Inventory":
    st.subheader("📋 Current Inventory")
    if df.empty:
        st.info("No items in inventory.")
    else:
        low_stock = df[df["Quantity"] < 5]
        if not low_stock.empty:
            st.warning("⚠️ Low Stock Items")
            st.table(low_stock)
        st.dataframe(df)

elif menu == "Add Item":
    st.subheader("➕ Add New Item")
    name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    if st.button("Add"):
        add_item(df, name, quantity)

elif menu == "Update Item":
    st.subheader("✏️ Update Item Quantity")
    if df.empty:
        st.info("No items available to update.")
    else:
        name = st.selectbox("Select Item", df["Item"].tolist())
        quantity = st.number_input("New Quantity", min_value=0, step=1)
        if st.button("Update"):
            update_item(df, name, quantity)
