import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Business Tracker", layout="wide")
st.title("📈 Small Biz Order & Profit Tracker")

# 1. Connect to your Google Sheet
# (Requires setting up a service account or making sheet accessible via link)
conn = st.connection("gsheets", type=GSheetsConnection)

# Load existing data
orders_df = conn.read(worksheet="Orders", ttl=0)
expenses_df = conn.read(worksheet="Expenses", ttl=0)

# --- SIDEBAR: INPUT NEW DATA ---
st.sidebar.header("➕ Add New Record")
entry_type = st.sidebar.radio("Type", ["Order", "Expense"])

if entry_type == "Order":
    with st.sidebar.form("order_form", clear_on_submit=True):
        prod = st.text_input("Product Name")
        rev = st.number_input("Revenue (INR)", min_value=0.0, step=50.0)
        status = st.selectbox("Status", ["Paid", "Pending"])
        submit = st.form_submit_button("Log Order")
        if submit:
            new_order = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Order_ID": len(orders_df)+1, "Product": prod, "Revenue": rev, "Status": status}])
            updated_orders = pd.concat([orders_df, new_order], ignore_index=True)
            conn.update(worksheet="Orders", data=updated_orders)
            st.sidebar.success("Order Logged!")
            st.rerun()

else:
    with st.sidebar.form("expense_form", clear_on_submit=True):
        cat = st.selectbox("Category", ["Raw Materials", "Shipping", "Marketing", "Other"])
        amt = st.number_input("Amount (INR)", min_value=0.0, step=10.0)
        submit = st.form_submit_button("Log Expense")
        if submit:
            new_expense = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Expense_ID": len(expenses_df)+1, "Category": cat, "Amount": amt}])
            updated_expenses = pd.concat([expenses_df, new_expense], ignore_index=True)
            conn.update(worksheet="Expenses", data=updated_expenses)
            st.sidebar.success("Expense Logged!")
            st.rerun()

# --- MAIN DASHBOARD: METRICS & PROFITS ---
total_rev = orders_df["Revenue"].sum() if not orders_df.empty else 0.0
total_exp = expenses_df["Amount"].sum() if not expenses_df.empty else 0.0
net_profit = total_rev - total_exp

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{total_rev:,.2f}")
col2.metric("Total Expenses", f"₹{total_exp:,.2f}")
col3.metric("Net Profit", f"₹{net_profit:,.2f}", delta=f"₹{net_profit:,.2f}")

# --- DATA TABLES ---
st.subheader("📦 Recent Orders")
st.dataframe(orders_df.tail(10), use_container_width=True)

st.subheader("💸 Recent Expenses")
st.dataframe(expenses_df.tail(10), use_container_width=True)