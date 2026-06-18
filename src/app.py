import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Business Tracker", layout="wide")
st.title("📈 Small Biz Order & Profit Tracker")

# Connect natively using Streamlit Secrets dictionary directly
try:
    gc = gspread.service_account_from_dict(st.secrets["connections"]["gsheets"])
    # Paste your actual spreadsheet URL or unique Sheet ID key here
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    
    orders_sheet = sh.worksheet("Orders")
    expenses_sheet = sh.worksheet("Expenses")
    
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    expenses_df = pd.DataFrame(expenses_sheet.get_all_records())
except Exception as e:
    st.error("Connection failed. Check your Secrets format.")
    st.exception(e)
    st.stop()

# --- Rest of your dashboard UI logic remains the same ---
st.subheader("📦 Recent Orders")
st.dataframe(orders_df)