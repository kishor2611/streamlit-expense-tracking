"""
📊 Small Biz Analytics & Tracker
Main application file — orchestrates the entire dashboard.
"""

import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime, date

# Ensure `src/` is on the import path so modules resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, CUSTOM_CSS,
    ORDER_STATUSES, EXPENSE_CATEGORIES, PAYMENT_SOURCES,
    ORDER_ID_PREFIX, EXPENSE_ID_PREFIX, PAYMENT_ID_PREFIX,
    STATUS_COLORS,
)
from database import (
    get_worksheets, load_all_data, build_price_dict, clear_cache,
    generate_id, add_order, update_order, delete_row,
    add_payment, add_expense,
    get_outstanding_payments, get_monthly_pnl,
    get_client_summary, get_product_performance,
)
from charts import (
    build_expense_pie, build_sales_bar,
    build_revenue_expense_trend, build_payment_source_pie,
    build_order_pipeline, build_monthly_pnl_chart,
    build_product_performance,
)
from components import (
    render_sidebar, render_pipeline, render_top_clients,
    render_date_filter, filter_by_date,
    render_search_filter, render_export_buttons,
    section_header, calculate_period_delta, status_badge,
)

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG & STYLING
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# DATA CONNECTION
# ═══════════════════════════════════════════════════════════════════════
try:
    worksheets = get_worksheets()
    df_orders, df_products, df_expenses, df_payments = load_all_data(worksheets)
    price_dict = build_price_dict(df_products)
    if not price_dict:
        price_dict = {"No Products Found": 0.0}
except Exception as e:
    st.error("❌ Database Connection Failed. Here is the exact reason:")
    st.exception(e)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
refresh_clicked = render_sidebar(df_orders, df_payments, df_expenses)
if refresh_clicked:
    clear_cache()
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Dashboard",
    "➕ Data Entry",
    "🗄️ Database",
    "📊 Reports & Insights",
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════════
with tab1:
    # ── Date Filter ──
    section_header("Date Range Filter", "📅")
    start_date, end_date = render_date_filter(key_prefix="dash")

    # Filter all dataframes
    filt_orders = filter_by_date(df_orders, "Date", start_date, end_date)
    filt_expenses = filter_by_date(df_expenses, "Date", start_date, end_date)
    filt_payments = filter_by_date(df_payments, "Date", start_date, end_date)

    st.markdown("---")

    # ── KPI Metrics ──
    section_header("Key Performance Indicators", "🎯")

    total_revenue = filt_payments["Amount"].sum() if not filt_payments.empty else 0.0
    total_expenses = filt_expenses["Amount"].sum() if not filt_expenses.empty else 0.0
    net_profit = total_revenue - total_expenses
    total_orders = len(filt_orders) if not filt_orders.empty else 0

    # Deltas vs previous period
    _, rev_delta, rev_pct = calculate_period_delta(df_payments, "Amount", "Date", start_date, end_date)
    _, exp_delta, exp_pct = calculate_period_delta(df_expenses, "Amount", "Date", start_date, end_date)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Cash Received", f"₹{total_revenue:,.2f}", delta=f"₹{rev_delta:,.0f} ({rev_pct})")
    kpi2.metric("💸 Total Expenses", f"₹{total_expenses:,.2f}", delta=f"₹{exp_delta:,.0f} ({exp_pct})", delta_color="inverse")
    kpi3.metric("🏦 Net Profit / Loss", f"₹{net_profit:,.2f}",
                delta=f"₹{net_profit:,.0f}",
                delta_color="normal" if net_profit >= 0 else "inverse")
    kpi4.metric("📦 Total Orders", f"{total_orders:,}")

    st.markdown("---")

    # ── Order Pipeline ──
    section_header("Order Status Pipeline", "🚚")
    render_pipeline(filt_orders)

    st.markdown("---")

    # ── Charts (2 × 2 Grid) ──
    section_header("Analytics Charts", "📊")

    chart_r1_c1, chart_r1_c2 = st.columns(2)

    with chart_r1_c1:
        fig = build_revenue_expense_trend(filt_payments, filt_expenses)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for Revenue vs Expenses trend.")

    with chart_r1_c2:
        fig = build_expense_pie(filt_expenses)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough expense data for chart.")

    chart_r2_c1, chart_r2_c2 = st.columns(2)

    with chart_r2_c1:
        fig = build_sales_bar(filt_orders)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough order data for chart.")

    with chart_r2_c2:
        fig = build_payment_source_pie(filt_payments)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough payment data for chart.")

    st.markdown("---")

    # ── Top Clients ──
    section_header("Top Clients", "👥")
    render_top_clients(filt_orders, n=5)


# ══════════════════════════════════════════════════════════════════════
# TAB 2: DATA ENTRY
# ══════════════════════════════════════════════════════════════════════
with tab2:
    entry_type = st.radio(
        "What are you logging today?",
        [
            "🛒 New Order",
            "✏️ Update Order",
            "🗑️ Delete Record",
            "💳 Payment Received",
            "🧾 Business Expense",
        ],
        horizontal=True,
    )

    # ─────────────────────────── New Order ────────────────────────────
    if entry_type == "🛒 New Order":
        st.subheader("Log a New Order")

        col1, col2 = st.columns(2)

        # Auto-suggest client names from existing orders
        known_clients = sorted(df_orders["Client_Name"].dropna().unique().tolist()) if not df_orders.empty and "Client_Name" in df_orders.columns else []
        client = col1.selectbox(
            "Client Name",
            options=[""] + known_clients,
            format_func=lambda x: "Type or select a client…" if x == "" else x,
            key="new_order_client_select",
        )
        # Allow typing a new client name if not in the list
        if client == "":
            client = col1.text_input("Or enter a new client name", key="new_order_client_new")

        product = col2.selectbox("Product", list(price_dict.keys()), key="new_order_product")
        qty = col1.number_input("Quantity", min_value=1, step=1, key="new_order_qty")
        order_date = col2.date_input("Order Date", value=date.today(), key="new_order_date")
        address = st.text_area("Delivery Address", key="new_order_address")
        remarks_col, status_col = st.columns(2)
        notes = remarks_col.text_input("Notes / Remarks (optional)", key="new_order_notes")
        status = status_col.selectbox("Status", ORDER_STATUSES, key="new_order_status")

        unit_price = price_dict.get(product, 0.0)
        auto_total = unit_price * qty

        st.info(f"**Total Order Value:** ₹{auto_total:,.2f}  *(₹{unit_price:,.2f} × {qty})*")

        if st.button("💾 Save Order", type="primary", key="save_new_order"):
            if not client or not address:
                st.error("⚠️ Please fill in the Client Name and Address.")
            else:
                with st.spinner("Saving order…"):
                    new_id = generate_id(ORDER_ID_PREFIX, df_orders)
                    date_str = order_date.strftime("%Y-%m-%d")
                    add_order(worksheets["orders"], new_id, date_str, client, address, product, qty, auto_total, status)
                    clear_cache()
                st.toast(f"✅ Order {new_id} saved successfully!", icon="🎉")
                st.rerun()

    # ─────────────────────────── Update Order ────────────────────────
    elif entry_type == "✏️ Update Order":
        st.subheader("Update an Existing Order")

        if df_orders.empty:
            st.info("No orders available to update yet.")
        else:
            order_ids = df_orders["Order_ID"].tolist()
            order_ids.reverse()
            selected_id = st.selectbox("Select Order to Update", order_ids, key="update_order_select")

            current_data = df_orders[df_orders["Order_ID"] == selected_id].iloc[0]
            sheet_row_index = df_orders[df_orders["Order_ID"] == selected_id].index[0] + 2

            col1, col2 = st.columns(2)
            client = col1.text_input("Client Name", value=str(current_data["Client_Name"]), key="update_client")

            prod_list = list(price_dict.keys())
            current_prod = str(current_data["Product"])
            default_prod_idx = prod_list.index(current_prod) if current_prod in prod_list else 0
            product = col2.selectbox("Product", prod_list, index=default_prod_idx, key="update_product")

            qty = col1.number_input("Quantity", min_value=1, step=1, value=int(current_data["Quantity"]), key="update_qty")
            address = st.text_area("Delivery Address", value=str(current_data["Address"]), key="update_address")

            default_status_idx = ORDER_STATUSES.index(str(current_data["Status"])) if str(current_data["Status"]) in ORDER_STATUSES else 0
            status = st.selectbox("Status", ORDER_STATUSES, index=default_status_idx, key="update_status")

            unit_price = price_dict.get(product, 0.0)
            auto_total = unit_price * qty
            st.info(f"**Updated Order Value:** ₹{auto_total:,.2f}  *(₹{unit_price:,.2f} × {qty})*")

            if st.button("💾 Save Changes", type="primary", key="save_update_order"):
                if not client or not address:
                    st.error("⚠️ Please fill in the Client Name and Address.")
                else:
                    with st.spinner("Updating order…"):
                        update_order(
                            worksheets["orders"], sheet_row_index,
                            selected_id, str(current_data["Date"]),
                            client, address, product, qty, auto_total, status,
                        )
                        clear_cache()
                    st.toast(f"✅ Order {selected_id} updated!", icon="✏️")
                    st.rerun()

    # ─────────────────────────── Delete Record ───────────────────────
    elif entry_type == "🗑️ Delete Record":
        st.subheader("Delete a Record")

        delete_target = st.selectbox(
            "What do you want to delete?",
            ["Order", "Payment", "Expense"],
            key="delete_target",
        )

        if delete_target == "Order":
            if df_orders.empty:
                st.info("No orders to delete.")
            else:
                # Build descriptive labels: "ORD-100 | Client Name | Product"
                order_labels = []
                for _, row in df_orders.iterrows():
                    label = f"{row['Order_ID']} | {row['Client_Name']} | {row['Product']}"
                    order_labels.append(label)
                order_labels.reverse()
                sel_label = st.selectbox("Select Order", order_labels, key="del_order_select")
                sel_id = sel_label.split(" | ")[0]  # Extract the Order_ID

                row_data = df_orders[df_orders["Order_ID"] == sel_id].iloc[0]
                sheet_row = df_orders[df_orders["Order_ID"] == sel_id].index[0] + 2

                with st.expander("📋 Order Details", expanded=True):
                    det_c1, det_c2, det_c3 = st.columns(3)
                    det_c1.write(f"**Client:** {row_data['Client_Name']}")
                    det_c2.write(f"**Product:** {row_data['Product']}")
                    det_c3.write(f"**Total:** ₹{row_data['Order_Total']:,.2f}")
                    st.write(f"**Date:** {row_data['Date']} | **Status:** {row_data['Status']}")

                st.warning("⚠️ This action is **permanent** and cannot be undone.")
                if st.button("🗑️ Confirm Delete Order", key="confirm_del_order"):
                    with st.spinner("Deleting…"):
                        delete_row(worksheets["orders"], sheet_row)
                        clear_cache()
                    st.toast(f"🗑️ Order {sel_id} deleted.", icon="🗑️")
                    st.rerun()

        elif delete_target == "Payment":
            if df_payments.empty:
                st.info("No payments to delete.")
            else:
                pay_labels = []
                for _, row in df_payments.iterrows():
                    pay_id = row["Payment_ID"]
                    order_id = row.get("Order_ID", row.get("Order_Ref", "N/A"))
                    client_name = "Unknown Client"
                    product = "Unknown Product"
                    if not df_orders.empty and order_id != "N/A":
                        match = df_orders[df_orders["Order_ID"] == order_id]
                        if not match.empty:
                            client_name = match.iloc[0].get("Client_Name", "Unknown Client")
                            product = match.iloc[0].get("Product", "Unknown Product")
                    label = f"{pay_id} | {order_id} | {client_name} | {product}"
                    pay_labels.append(label)
                pay_labels.reverse()
                sel_label = st.selectbox("Select Payment", pay_labels, key="del_pay_select")
                sel_id = sel_label.split(" | ")[0]
                row_data = df_payments[df_payments["Payment_ID"] == sel_id].iloc[0]
                sheet_row = df_payments[df_payments["Payment_ID"] == sel_id].index[0] + 2

                with st.expander("📋 Payment Details", expanded=True):
                    det_c1, det_c2, det_c3 = st.columns(3)
                    det_c1.write(f"**Order Ref:** {row_data.get('Order_ID', row_data.get('Order_Ref', 'N/A'))}")
                    det_c2.write(f"**Amount:** ₹{row_data.get('Amount', 0):,.2f}")
                    det_c3.write(f"**Source:** {row_data.get('Source', row_data.get('Payment_Source', row_data.get('Mode', 'N/A')))}")

                st.warning("⚠️ This action is **permanent** and cannot be undone.")
                if st.button("🗑️ Confirm Delete Payment", key="confirm_del_pay"):
                    with st.spinner("Deleting…"):
                        delete_row(worksheets["payments"], sheet_row)
                        clear_cache()
                    st.toast(f"🗑️ Payment {sel_id} deleted.", icon="🗑️")
                    st.rerun()

        elif delete_target == "Expense":
            if df_expenses.empty:
                st.info("No expenses to delete.")
            else:
                exp_labels = []
                for _, row in df_expenses.iterrows():
                    exp_id = row["Expense_ID"]
                    cat = row.get("Category", "N/A")
                    item = row.get("Item", "N/A")
                    amt = row.get("Amount", 0.0)
                    label = f"{exp_id} | {cat} | {item} | ₹{amt:,.2f}"
                    exp_labels.append(label)
                exp_labels.reverse()
                sel_label = st.selectbox("Select Expense", exp_labels, key="del_exp_select")
                sel_id = sel_label.split(" | ")[0]
                row_data = df_expenses[df_expenses["Expense_ID"] == sel_id].iloc[0]
                sheet_row = df_expenses[df_expenses["Expense_ID"] == sel_id].index[0] + 2

                with st.expander("📋 Expense Details", expanded=True):
                    det_c1, det_c2, det_c3 = st.columns(3)
                    det_c1.write(f"**Category:** {row_data.get('Category', 'N/A')}")
                    det_c2.write(f"**Item:** {row_data.get('Item', 'N/A')}")
                    det_c3.write(f"**Amount:** ₹{row_data.get('Amount', 0.0):,.2f}")

                st.warning("⚠️ This action is **permanent** and cannot be undone.")
                if st.button("🗑️ Confirm Delete Expense", key="confirm_del_exp"):
                    with st.spinner("Deleting…"):
                        delete_row(worksheets["expenses"], sheet_row)
                        clear_cache()
                    st.toast(f"🗑️ Expense {sel_id} deleted.", icon="🗑️")
                    st.rerun()

    # ─────────────────────────── Payment ─────────────────────────────
    elif entry_type == "💳 Payment Received":
        with st.form("payment_form", clear_on_submit=True):
            st.subheader("Log a Payment")

            p_col1, p_col2 = st.columns(2)

            # Dropdown of existing orders instead of free text
            if not df_orders.empty:
                order_options = df_orders["Order_ID"].tolist()
                order_options.reverse()
                order_ref = p_col1.selectbox("Order ID", order_options)

                # Show remaining balance for selected order
                selected_order = df_orders[df_orders["Order_ID"] == order_ref].iloc[0]
                order_total = float(selected_order["Order_Total"])
                paid_so_far = df_payments[df_payments["Order_ID"] == order_ref]["Amount"].sum() if not df_payments.empty else 0.0
                remaining = order_total - paid_so_far
                st.info(f"**Order Total:** ₹{order_total:,.2f} | **Paid so far:** ₹{paid_so_far:,.2f} | **Remaining:** ₹{remaining:,.2f}")
            else:
                order_ref = p_col1.text_input("Order ID (e.g., ORD-100)")
                remaining = float("inf")

            amt = p_col2.number_input("Amount Received (₹)", min_value=0.0, step=10.0)
            pay_date = p_col1.date_input("Payment Date", value=date.today())
            source = p_col2.selectbox("Payment Source", PAYMENT_SOURCES)

            submitted = st.form_submit_button("💾 Save Payment", type="primary")
            if submitted:
                if amt <= 0:
                    st.error("⚠️ Please enter a valid amount.")
                elif amt > remaining and remaining != float("inf"):
                    st.warning(f"⚠️ Payment (₹{amt:,.2f}) exceeds the remaining balance (₹{remaining:,.2f}). Are you sure?")
                    # Still save it — it's a warning, not a block
                    new_id = generate_id(PAYMENT_ID_PREFIX, df_payments)
                    add_payment(worksheets["payments"], new_id, pay_date.strftime("%Y-%m-%d"), order_ref, amt, source)
                    clear_cache()
                    st.toast("✅ Payment saved!", icon="💳")
                    st.rerun()
                else:
                    new_id = generate_id(PAYMENT_ID_PREFIX, df_payments)
                    add_payment(worksheets["payments"], new_id, pay_date.strftime("%Y-%m-%d"), order_ref, amt, source)
                    clear_cache()
                    st.toast("✅ Payment saved!", icon="💳")
                    st.rerun()

    # ─────────────────────────── Expense ──────────────────────────────
    elif entry_type == "🧾 Business Expense":
        with st.form("expense_form", clear_on_submit=True):
            st.subheader("Log an Expense")

            e_col1, e_col2 = st.columns(2)
            cat = e_col1.selectbox("Category", EXPENSE_CATEGORIES)
            item = e_col2.text_input("Item Description (e.g., Curry Leaves, Jars)")
            amt = e_col1.number_input("Amount Spent (₹)", min_value=0.0, step=10.0)
            exp_date = e_col2.date_input("Expense Date", value=date.today())

            submitted = st.form_submit_button("💾 Save Expense", type="primary")
            if submitted:
                if not item:
                    st.error("⚠️ Please enter an item description.")
                elif amt <= 0:
                    st.error("⚠️ Please enter a valid amount.")
                else:
                    new_id = generate_id(EXPENSE_ID_PREFIX, df_expenses)
                    add_expense(worksheets["expenses"], new_id, exp_date.strftime("%Y-%m-%d"), cat, item, amt)
                    clear_cache()
                    st.toast("✅ Expense saved!", icon="🧾")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════
# TAB 3: DATABASE EXPLORER
# ══════════════════════════════════════════════════════════════════════
with tab3:
    section_header("Database Explorer", "🗄️")

    view_table = st.selectbox(
        "Select Table to View",
        ["Orders", "Payments", "Expenses", "Products"],
        key="db_table_select",
    )

    table_map = {
        "Orders": df_orders,
        "Payments": df_payments,
        "Expenses": df_expenses,
        "Products": df_products,
    }
    raw_df = table_map[view_table]

    # Search & Filter
    filtered_df = render_search_filter(raw_df, view_table, key_prefix=f"db_{view_table.lower()}")

    if filtered_df is not None and not filtered_df.empty:
        # Summary stats
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        summary_col1.metric("📋 Total Records", f"{len(filtered_df):,}")

        if "Amount" in filtered_df.columns:
            summary_col2.metric("💰 Total Amount", f"₹{filtered_df['Amount'].sum():,.2f}")
        elif "Order_Total" in filtered_df.columns:
            summary_col2.metric("💰 Total Value", f"₹{filtered_df['Order_Total'].sum():,.2f}")

        if "Quantity" in filtered_df.columns:
            summary_col3.metric("📦 Total Quantity", f"{filtered_df['Quantity'].sum():,.0f}")

        st.markdown("")

        # Interactive data editor
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        # Export
        render_export_buttons(filtered_df, view_table)
    else:
        st.info(f"No data found in {view_table}.")


# ══════════════════════════════════════════════════════════════════════
# TAB 4: REPORTS & INSIGHTS
# ══════════════════════════════════════════════════════════════════════
with tab4:
    report_type = st.selectbox(
        "Select Report",
        [
            "📈 Monthly P&L Statement",
            "📦 Product Performance",
            "👤 Client Report",
            "⏳ Outstanding Payments",
        ],
        key="report_select",
    )

    # ─────────────── Monthly P&L ─────────────────────────────────────
    if report_type == "📈 Monthly P&L Statement":
        section_header("Monthly Profit & Loss Statement", "📈")

        df_pnl = get_monthly_pnl(df_payments, df_expenses)

        if df_pnl.empty:
            st.info("Not enough data to generate P&L statement.")
        else:
            # Chart
            fig = build_monthly_pnl_chart(df_pnl)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Table
            section_header("P&L Data Table", "📋")

            # Add formatting
            display_pnl = df_pnl.copy()
            display_pnl["Revenue"] = display_pnl["Revenue"].apply(lambda x: f"₹{x:,.2f}")
            display_pnl["Expenses"] = display_pnl["Expenses"].apply(lambda x: f"₹{x:,.2f}")
            display_pnl["Net_Profit"] = display_pnl["Net_Profit"].apply(lambda x: f"₹{x:,.2f}")

            st.dataframe(display_pnl, use_container_width=True, hide_index=True)

            # Totals
            totals_c1, totals_c2, totals_c3 = st.columns(3)
            totals_c1.metric("Total Revenue", f"₹{df_pnl['Revenue'].sum():,.2f}")
            totals_c2.metric("Total Expenses", f"₹{df_pnl['Expenses'].sum():,.2f}")
            totals_c3.metric("Total Net Profit", f"₹{df_pnl['Net_Profit'].sum():,.2f}")

            render_export_buttons(df_pnl, "Monthly_PnL")

    # ─────────────── Product Performance ─────────────────────────────
    elif report_type == "📦 Product Performance":
        section_header("Product Performance Report", "📦")

        df_prod_perf = get_product_performance(df_orders)

        if df_prod_perf.empty:
            st.info("Not enough data for product performance report.")
        else:
            # Chart
            fig = build_product_performance(df_prod_perf)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Table
            section_header("Product Data Table", "📋")
            display_prod = df_prod_perf.copy()
            display_prod["Revenue"] = display_prod["Revenue"].apply(lambda x: f"₹{x:,.2f}")
            display_prod["Avg_Order_Value"] = display_prod["Avg_Order_Value"].apply(lambda x: f"₹{x:,.2f}")

            st.dataframe(display_prod, use_container_width=True, hide_index=True)

            # Summary
            best = df_prod_perf.sort_values("Revenue", ascending=False).iloc[0]
            st.success(f"🏆 **Best Seller:** {best['Product']} — {best['Units_Sold']:.0f} units sold, ₹{best['Revenue']:,.2f} revenue")

            render_export_buttons(df_prod_perf, "Product_Performance")

    # ─────────────── Client Report ───────────────────────────────────
    elif report_type == "👤 Client Report":
        section_header("Client Report", "👤")

        df_client = get_client_summary(df_orders, df_payments)

        if df_client.empty:
            st.info("Not enough data for client report.")
        else:
            # Summary metrics
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("👤 Total Clients", f"{len(df_client):,}")
            mc2.metric("💰 Total Order Value", f"₹{df_client['Total_Order_Value'].sum():,.2f}")
            mc3.metric("⚠️ Total Outstanding", f"₹{df_client['Balance'].sum():,.2f}")

            st.markdown("---")

            # Table
            st.dataframe(
                df_client.sort_values("Total_Order_Value", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Client_Name": st.column_config.TextColumn("Client"),
                    "Total_Orders": st.column_config.NumberColumn("Orders"),
                    "Total_Order_Value": st.column_config.NumberColumn("Order Value", format="₹%,.2f"),
                    "Total_Paid": st.column_config.NumberColumn("Paid", format="₹%,.2f"),
                    "Balance": st.column_config.NumberColumn("Balance Due", format="₹%,.2f"),
                },
            )

            render_export_buttons(df_client, "Client_Report")

    # ─────────────── Outstanding Payments ────────────────────────────
    elif report_type == "⏳ Outstanding Payments":
        section_header("Outstanding Payments", "⏳")

        df_outstanding = get_outstanding_payments(df_orders, df_payments)

        if df_outstanding.empty:
            st.success("🎉 All orders are fully paid! No outstanding balances.")
        else:
            # Summary
            oc1, oc2 = st.columns(2)
            oc1.metric("📋 Orders with Balance", f"{len(df_outstanding):,}")
            oc2.metric("💰 Total Outstanding", f"₹{df_outstanding['Balance'].sum():,.2f}")

            st.markdown("---")

            # Table
            st.dataframe(
                df_outstanding.sort_values("Balance", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Order_ID": st.column_config.TextColumn("Order"),
                    "Client_Name": st.column_config.TextColumn("Client"),
                    "Product": st.column_config.TextColumn("Product"),
                    "Order_Total": st.column_config.NumberColumn("Order Total", format="₹%,.2f"),
                    "Paid": st.column_config.NumberColumn("Paid", format="₹%,.2f"),
                    "Balance": st.column_config.NumberColumn("Balance Due", format="₹%,.2f"),
                },
            )

            render_export_buttons(df_outstanding, "Outstanding_Payments")