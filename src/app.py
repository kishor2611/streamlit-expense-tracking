import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Business Tracker", layout="wide")
st.title("📈 Small Biz Order & Profit Tracker")

# 1. Establish Authentication and Connection
try:
    # Extract the credential block directly from st.secrets
    secret_dict = dict(st.secrets["connections"]["gsheets"])
    
    # Authenticate using the dictionary fields
    gc = gspread.service_account_from_dict(secret_dict)
    
    # Open the private sheet using the URL string inside that dictionary
    spreadsheet_url = secret_dict["spreadsheet"]
    sh = gc.open_by_url(spreadsheet_url)
    
    # Access individual tabs
    orders_sheet = sh.worksheet("Orders")
    expenses_sheet = sh.worksheet("Expenses")
    
    # Read records into memory
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    expenses_df = pd.DataFrame(expenses_sheet.get_all_records())
    
except KeyError as ke:
    st.error(f"❌ Missing expected key in Secrets manager: {ke}")
    st.stop()
except gspread.exceptions.SpreadsheetNotFound:
    st.error("❌ Google couldn't find the sheet. Ensure your service account email is added as an 'Editor' on the Google Sheet!")
    st.stop()
except Exception as e:
    st.error("❌ Connection failed unexpectedly:")
    st.exception(e)
    st.stop()

# --- 2. Dashboard Logic & UI Form Processing ---
st.sidebar.header("➕ Add New Record")
entry_type = st.sidebar.radio("Type", ["Order", "Expense"])

if entry_type == "Order":
    with st.sidebar.form("order_form", clear_on_submit=True):
        prod = st.text_input("Product Name")
        rev = st.number_input("Revenue", min_value=0.0, step=10.0)
        status = st.selectbox("Status", ["Paid", "Pending"])
        submit = st.form_submit_button("Log Order")
        if submit:
            new_row = [datetime.now().strftime("%Y-%m-%d"), len(orders_df)+1, prod, rev, status]
            orders_sheet.append_row(new_row)
            st.sidebar.success("Order Logged!")
            st.hybrid_fallback = True
            st.rerun()
else:
    with st.sidebar.form("expense_form", clear_on_submit=True):
        cat = st.selectbox("Category", ["Raw Materials", "Shipping", "Marketing", "Other"])
        amt = st.number_input("Amount", min_value=0.0, step=10.0)
        submit = st.form_submit_button("Log Expense")
        if submit:
            new_row = [datetime.now().strftime("%Y-%m-%d"), len(expenses_df)+1, cat, amt]
            expenses_sheet.append_row(new_row)
            st.sidebar.success("Expense Logged!")
            st.rerun()

# --- 3. Render Metrics & Data Frames ---
total_rev = orders_df["Revenue"].sum() if not orders_df.empty else 0.0
total_exp = expenses_df["Amount"].sum() if not expenses_df.empty else 0.0
net_profit = total_rev - total_exp

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{total_rev:,.2f}")
col2.metric("Total Expenses", f"₹{total_exp:,.2f}")
col3.metric("Net Profit", f"₹{net_profit:,.2f}")

st.subheader("📦 Recent Orders")
st.dataframe(orders_df.tail(10), use_container_width=True)

st.subheader("💸 Recent Expenses")
st.dataframe(expenses_df.tail(10), use_container_width=True)