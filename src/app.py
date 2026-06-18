import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Business Dashboard", layout="wide")
st.title("📊 Small Biz Analytics & Tracker")

# --- 1. CONNECT TO GOOGLE SHEETS ---
try:
    gc = gspread.service_account_from_dict(dict(st.secrets["connections"]["gsheets"]))
    sh = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    
    # Load all sheets
    ws_orders = sh.worksheet("Orders")
    ws_products = sh.worksheet("Products")
    # Clean product data for automatic pricing
    if not df_products.empty:
        # 1. Create the exact dropdown label: "Product Name (Weight)"
        df_products["Display_Name"] = df_products["Product_Name"].astype(str) + " (" + df_products["Weight"].astype(str) + ")"
        
        # 2. Strip '₹' and spaces, convert to a mathable float
        df_products["Clean_Price"] = df_products["Price"].replace(r'[₹,\s]', '', regex=True).astype(float)
        
        # 3. Create a dictionary map -> {"Product (150g)": 100.0}
        price_dict = dict(zip(df_products["Display_Name"], df_products["Clean_Price"]))
    else:
        price_dict = {"No Products Found": 0.0}
    ws_expenses = sh.worksheet("Expenses")
    ws_payments = sh.worksheet("Payments")
    
    # Convert to DataFrames
    df_orders = pd.DataFrame(ws_orders.get_all_records())
    df_products = pd.DataFrame(ws_products.get_all_records())
    df_expenses = pd.DataFrame(ws_expenses.get_all_records())
    df_payments = pd.DataFrame(ws_payments.get_all_records())

except Exception as e:
    st.error("❌ Database Connection Failed. Check your Sheet tabs and secrets.")
    st.stop()

# Clean data (ensure numeric columns are actually numbers)
for df, col in [(df_orders, 'Order_Total'), (df_orders, 'Quantity'), 
                (df_expenses, 'Amount'), (df_payments, 'Amount')]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- 2. LAYOUT: TABS ---
tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "➕ Data Entry", "🗄️ Database"])

# ==========================================
# TAB 1: DASHBOARD & CHARTS
# ==========================================
with tab1:
    # Calculate Core Metrics
    total_revenue = df_payments["Amount"].sum() if not df_payments.empty else 0.0
    total_expenses = df_expenses["Amount"].sum() if not df_expenses.empty else 0.0
    net_profit = total_revenue - total_expenses
    
    # Display Top Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Cash Received", f"₹{total_revenue:,.2f}")
    col2.metric("💸 Total Expenses", f"₹{total_expenses:,.2f}")
    col3.metric("🏦 Net Profit / Loss", f"₹{net_profit:,.2f}", 
                delta=f"₹{net_profit:,.2f}", delta_color="normal" if net_profit >= 0 else "inverse")
    
    st.markdown("---")
    
    # Charts Row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Expenses by Category")
        if not df_expenses.empty and "Category" in df_expenses.columns:
            fig_pie = px.pie(df_expenses, values="Amount", names="Category", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Not enough expense data to generate chart.")
            
    with chart_col2:
        st.subheader("Sales Volume by Product")
        if not df_orders.empty and "Product" in df_orders.columns:
            # Group by product to see what sells the most
            sales_data = df_orders.groupby("Product")["Quantity"].sum().reset_index()
            fig_bar = px.bar(sales_data, x="Product", y="Quantity", text_auto=True, color="Product")
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Not enough order data to generate chart.")

# ==========================================
# TAB 2: DATA ENTRY FORMS
# ==========================================
with tab2:
    entry_type = st.radio("What are you logging today?", ["🛒 New Order", "💳 Payment Received", "🧾 Business Expense"], horizontal=True)
    
    # Extract product list for dropdowns
    product_list = df_products["Product_Name"].astype(str) + " (" + df_products["Weight"].astype(str) + ")" if not df_products.empty else ["No Products Found"]
    
    if entry_type == "🛒 New Order":
        st.subheader("Log a New Order")
        
        # Notice we are NOT using 'with st.form()' here so the screen can update live
        col1, col2 = st.columns(2)
        client = col1.text_input("Client Name")
        product = col2.selectbox("Product", list(price_dict.keys()))
        qty = col1.number_input("Quantity", min_value=1, step=1)
        address = st.text_area("Delivery Address")
        status = st.selectbox("Status", ["Pending", "Shipped", "Delivered"])
        
        # --- THE AUTOMATIC CALCULATION ---
        unit_price = price_dict.get(product, 0.0)
        auto_total = unit_price * qty
        
        # Display the live total to the user beautifully
        st.info(f"**Total Order Value:** ₹{auto_total:,.2f}  *(₹{unit_price:,.2f} x {qty})*")
        
        # Use a standard button instead of form_submit_button
        if st.button("Save Order", type="primary"):
            if not client or not address:
                st.error("Please fill in the Client Name and Address.")
            else:
                new_id = f"ORD-{len(df_orders)+100}"
                new_row = [new_id, datetime.now().strftime("%Y-%m-%d"), client, address, product, qty, auto_total, status]
                ws_orders.append_row(new_row)
                st.success(f"Order {new_id} saved!")
                st.rerun()

    elif entry_type == "💳 Payment Received":
        with st.form("payment_form", clear_on_submit=True):
            st.subheader("Log a Payment")
            order_ref = st.text_input("Order ID (e.g., ORD-100)")
            amt = st.number_input("Amount Received (₹)", min_value=0.0, step=10.0)
            source = st.selectbox("Payment Source", ["UPI", "Cash", "Bank Transfer"])
            
            if st.form_submit_button("Save Payment"):
                new_id = f"PAY-{len(df_payments)+100}"
                new_row = [new_id, datetime.now().strftime("%Y-%m-%d"), order_ref, amt, source]
                ws_payments.append_row(new_row)
                st.success("Payment saved!")
                st.rerun()

    elif entry_type == "🧾 Business Expense":
        with st.form("expense_form", clear_on_submit=True):
            st.subheader("Log an Expense")
            cat = st.selectbox("Category", ["Raw Materials", "Packaging", "Shipping/Delivery", "Marketing", "Other"])
            item = st.text_input("Item Description (e.g., Curry Leaves, Jars)")
            amt = st.number_input("Amount Spent (₹)", min_value=0.0, step=10.0)
            
            if st.form_submit_button("Save Expense"):
                new_id = f"EXP-{len(df_expenses)+100}"
                new_row = [new_id, datetime.now().strftime("%Y-%m-%d"), cat, item, amt]
                ws_expenses.append_row(new_row)
                st.success("Expense saved!")
                st.rerun()

# ==========================================
# TAB 3: RAW DATABASE
# ==========================================
with tab3:
    st.subheader("Raw Database Explorer")
    view_table = st.selectbox("Select Table to View", ["Orders", "Payments", "Expenses", "Products"])
    
    if view_table == "Orders":
        st.dataframe(df_orders, use_container_width=True)
    elif view_table == "Payments":
        st.dataframe(df_payments, use_container_width=True)
    elif view_table == "Expenses":
        st.dataframe(df_expenses, use_container_width=True)
    else:
        st.dataframe(df_products, use_container_width=True)