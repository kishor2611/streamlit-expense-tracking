"""
Database module for the Streamlit Business Dashboard.

Handles all Google Sheets interactions using gspread, including:
- Connection and worksheet management
- Data loading with Streamlit caching
- CRUD operations for Orders, Products, Expenses, and Payments
- Analytics helpers for financial reporting

Worksheet Column Structures:
    Orders:   Order_ID, Date, Client_Name, Address, Product, Quantity, Order_Total, Status
    Products: Product_Name, Weight, Price
    Expenses: Expense_ID, Date, Category, Item, Amount
    Payments: Payment_ID, Date, Order_ID, Amount, Source
"""

from __future__ import annotations
import streamlit as st
import gspread
import pandas as pd


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_worksheets():
    """Connect to Google Sheets and return a dict of worksheet objects.

    Uses service-account credentials stored in ``st.secrets['connections']['gsheets']``
    and opens the spreadsheet whose URL is at
    ``st.secrets['connections']['gsheets']['spreadsheet']``.

    Returns:
        dict: Mapping of lowercase worksheet names to ``gspread.Worksheet``
              objects with keys ``'orders'``, ``'products'``, ``'expenses'``,
              ``'payments'``.
    """
    creds = dict(st.secrets["connections"]["gsheets"])
    spreadsheet_url = creds.pop("spreadsheet")

    client = gspread.service_account_from_dict(creds)
    spreadsheet = client.open_by_url(spreadsheet_url)

    return {
        "orders": spreadsheet.worksheet("Orders"),
        "products": spreadsheet.worksheet("Products"),
        "expenses": spreadsheet.worksheet("Expenses"),
        "payments": spreadsheet.worksheet("Payments"),
    }


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def load_all_data(_worksheets):
    """Load all data from every worksheet into pandas DataFrames.

    The parameter is prefixed with ``_`` so that Streamlit does not attempt to
    hash the ``gspread.Worksheet`` objects.

    Numeric columns (``Order_Total``, ``Quantity``, ``Amount``) are coerced to
    numeric types; unparseable values become ``0``.

    Args:
        _worksheets (dict): Dict returned by :func:`get_worksheets`.

    Returns:
        tuple: ``(df_orders, df_products, df_expenses, df_payments)`` — four
        :class:`pandas.DataFrame` objects, one per worksheet.
    """
    # Helper to fetch records safely (returns empty DF when sheet has no rows)
    def _fetch(ws, columns):
        records = ws.get_all_records()
        if records:
            return pd.DataFrame(records)
        return pd.DataFrame(columns=columns)

    df_orders = _fetch(
        _worksheets["orders"],
        ["Order_ID", "Date", "Client_Name", "Address", "Product", "Quantity", "Order_Total", "Status"],
    )
    df_products = _fetch(
        _worksheets["products"],
        ["Product_Name", "Weight", "Price"],
    )
    df_expenses = _fetch(
        _worksheets["expenses"],
        ["Expense_ID", "Date", "Category", "Item", "Amount"],
    )
    df_payments = _fetch(
        _worksheets["payments"],
        ["Payment_ID", "Date", "Order_ID", "Amount", "Source"],
    )

    # Clean numeric columns
    for col in ("Order_Total", "Quantity"):
        if col in df_orders.columns:
            df_orders[col] = pd.to_numeric(df_orders[col], errors="coerce").fillna(0)

    if "Amount" in df_expenses.columns:
        df_expenses["Amount"] = pd.to_numeric(df_expenses["Amount"], errors="coerce").fillna(0)

    if "Amount" in df_payments.columns:
        df_payments["Amount"] = pd.to_numeric(df_payments["Amount"], errors="coerce").fillna(0)

    # Normalize payment column names (sheets may use different header names)
    payment_renames = {"Payment_Source": "Source", "Mode": "Source", "Payment_Mode": "Source"}
    for old_name, new_name in payment_renames.items():
        if old_name in df_payments.columns and new_name not in df_payments.columns:
            df_payments.rename(columns={old_name: new_name}, inplace=True)

    return df_orders, df_products, df_expenses, df_payments


def build_price_dict(df_products):
    """Build a price dictionary from the Products DataFrame.

    Display names are formatted as ``'Product Name (Weight)'``.  Price strings
    are cleaned by stripping the ``₹`` symbol and commas before conversion to
    ``float``.

    Args:
        df_products (pd.DataFrame): DataFrame with columns ``Product_Name``,
            ``Weight``, and ``Price``.

    Returns:
        dict: Mapping of display name (``str``) → price (``float``).
    """
    price_dict = {}

    if df_products.empty:
        return price_dict

    for _, row in df_products.iterrows():
        display_name = f"{row['Product_Name']} ({row['Weight']})"
        price_str = str(row["Price"]).replace("₹", "").replace(",", "").strip()
        try:
            price_dict[display_name] = float(price_str)
        except (ValueError, TypeError):
            price_dict[display_name] = 0.0

    return price_dict


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------

def generate_id(prefix, existing_df):
    """Generate the next sequential ID for a given prefix.

    IDs follow the pattern ``PREFIX-NNN`` (e.g. ``ORD-100``, ``ORD-101``).
    If *existing_df* is empty the sequence starts at ``100``.

    Args:
        prefix (str): The ID prefix (e.g. ``'ORD'``, ``'PAY'``, ``'EXP'``).
        existing_df (pd.DataFrame): DataFrame whose first column contains
            existing IDs in ``PREFIX-NNN`` format.

    Returns:
        str: The next ID string, e.g. ``'ORD-101'``.
    """
    if existing_df.empty:
        return f"{prefix}-100"

    id_col = existing_df.columns[0]
    max_num = 99  # Will result in starting at 100 when incremented

    for val in existing_df[id_col]:
        try:
            num = int(str(val).split("-")[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue

    return f"{prefix}-{max_num + 1}"


def add_order(ws, order_id, date_str, client, address, product, qty, total, status):
    """Append a new order row to the Orders worksheet.

    Args:
        ws (gspread.Worksheet): The Orders worksheet object.
        order_id (str): Unique order identifier (e.g. ``'ORD-100'``).
        date_str (str): Date string for the order.
        client (str): Client / customer name.
        address (str): Delivery or billing address.
        product (str): Product name (display name).
        qty (int | float): Quantity ordered.
        total (float): Order total amount.
        status (str): Order status (e.g. ``'Pending'``, ``'Delivered'``).
    """
    ws.append_row(
        [order_id, date_str, client, address, product, qty, total, status],
        value_input_option="USER_ENTERED",
    )


def update_order(ws, sheet_row_index, order_id, date_str, client, address, product, qty, total, status):
    """Update an existing order row in-place.

    Args:
        ws (gspread.Worksheet): The Orders worksheet object.
        sheet_row_index (int): 1-indexed row number in the sheet (includes
            header row, so data rows start at 2).
        order_id (str): Order identifier.
        date_str (str): Updated date string.
        client (str): Updated client name.
        address (str): Updated address.
        product (str): Updated product name.
        qty (int | float): Updated quantity.
        total (float): Updated order total.
        status (str): Updated status.
    """
    cell_range = f"A{sheet_row_index}:H{sheet_row_index}"
    ws.update(
        cell_range,
        [[order_id, date_str, client, address, product, qty, total, status]],
        value_input_option="USER_ENTERED",
    )


def delete_row(ws, sheet_row_index):
    """Delete a single row from a worksheet.

    Args:
        ws (gspread.Worksheet): Any worksheet object.
        sheet_row_index (int): 1-indexed row number to delete.
    """
    ws.delete_rows(int(sheet_row_index))


def add_product(ws, name, weight, price):
    """Append a new product row to the Products worksheet.

    Args:
        ws (gspread.Worksheet): The Products worksheet object.
        name (str): Product Name.
        weight (str): Weight (e.g. '100g', '500g').
        price (float): Price of the product.
    """
    ws.append_row(
        [name, weight, price],
        value_input_option="USER_ENTERED",
    )


def update_product(ws, sheet_row_index, name, weight, price):
    """Update an existing product row in-place.

    Args:
        ws (gspread.Worksheet): The Products worksheet object.
        sheet_row_index (int): 1-indexed row number to update.
        name (str): Updated product name.
        weight (str): Updated weight.
        price (float): Updated price.
    """
    cell_range = f"A{sheet_row_index}:C{sheet_row_index}"
    ws.update(
        cell_range,
        [[name, weight, price]],
        value_input_option="USER_ENTERED",
    )


def add_payment(ws, payment_id, date_str, order_ref, amount, source):
    """Append a new payment row to the Payments worksheet.

    Args:
        ws (gspread.Worksheet): The Payments worksheet object.
        payment_id (str): Unique payment identifier (e.g. ``'PAY-100'``).
        date_str (str): Date string for the payment.
        order_ref (str): Associated ``Order_ID``.
        amount (float): Payment amount.
        source (str): Payment source / method.
    """
    ws.append_row(
        [payment_id, date_str, order_ref, amount, source],
        value_input_option="USER_ENTERED",
    )


def add_expense(ws, expense_id, date_str, category, item, amount):
    """Append a new expense row to the Expenses worksheet.

    Args:
        ws (gspread.Worksheet): The Expenses worksheet object.
        expense_id (str): Unique expense identifier (e.g. ``'EXP-100'``).
        date_str (str): Date string for the expense.
        category (str): Expense category.
        item (str): Description of the expense item.
        amount (float): Expense amount.
    """
    ws.append_row(
        [expense_id, date_str, category, item, amount],
        value_input_option="USER_ENTERED",
    )


# ---------------------------------------------------------------------------
# Analytics Helpers
# ---------------------------------------------------------------------------

def get_outstanding_payments(df_orders, df_payments):
    """Identify orders where total payments are less than the order total.

    Groups payments by ``Order_ID`` and compares the sum against each order's
    ``Order_Total``.

    Args:
        df_orders (pd.DataFrame): Orders DataFrame.
        df_payments (pd.DataFrame): Payments DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns ``Order_ID``, ``Client_Name``,
        ``Product``, ``Order_Total``, ``Paid``, ``Balance``.
    """
    result_cols = ["Order_ID", "Client_Name", "Product", "Order_Total", "Paid", "Balance"]

    if df_orders.empty:
        return pd.DataFrame(columns=result_cols)

    # Aggregate payments per order
    if df_payments.empty:
        paid_map = pd.Series(dtype=float)
    else:
        paid_map = df_payments.groupby("Order_ID")["Amount"].sum()

    records = []
    for _, order in df_orders.iterrows():
        order_id = order["Order_ID"]
        order_total = float(order["Order_Total"])
        paid = float(paid_map.get(order_id, 0))
        balance = order_total - paid
        if balance > 0:
            records.append({
                "Order_ID": order_id,
                "Client_Name": order["Client_Name"],
                "Product": order["Product"],
                "Order_Total": order_total,
                "Paid": paid,
                "Balance": balance,
            })

    if not records:
        return pd.DataFrame(columns=result_cols)

    return pd.DataFrame(records, columns=result_cols)


def get_monthly_pnl(df_payments, df_expenses):
    """Calculate monthly Profit & Loss.

    Parses ``Date`` columns, groups revenue (payments) and expenses by
    year-month, and computes net profit.

    Args:
        df_payments (pd.DataFrame): Payments DataFrame.
        df_expenses (pd.DataFrame): Expenses DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns ``Month`` (``'YYYY-MM'``),
        ``Revenue``, ``Expenses``, ``Net_Profit``, sorted by month ascending.
    """
    result_cols = ["Month", "Revenue", "Expenses", "Net_Profit"]

    # Monthly revenue from payments
    if not df_payments.empty:
        pay = df_payments.copy()
        pay["Date"] = pd.to_datetime(pay["Date"], errors="coerce")
        pay = pay.dropna(subset=["Date"])
        pay["Month"] = pay["Date"].dt.to_period("M").astype(str)
        monthly_revenue = pay.groupby("Month")["Amount"].sum()
    else:
        monthly_revenue = pd.Series(dtype=float)

    # Monthly expenses
    if not df_expenses.empty:
        exp = df_expenses.copy()
        exp["Date"] = pd.to_datetime(exp["Date"], errors="coerce")
        exp = exp.dropna(subset=["Date"])
        exp["Month"] = exp["Date"].dt.to_period("M").astype(str)
        monthly_expenses = exp.groupby("Month")["Amount"].sum()
    else:
        monthly_expenses = pd.Series(dtype=float)

    # Combine all months
    all_months = sorted(set(monthly_revenue.index) | set(monthly_expenses.index))

    if not all_months:
        return pd.DataFrame(columns=result_cols)

    records = []
    for month in all_months:
        revenue = float(monthly_revenue.get(month, 0))
        expenses = float(monthly_expenses.get(month, 0))
        records.append({
            "Month": month,
            "Revenue": revenue,
            "Expenses": expenses,
            "Net_Profit": revenue - expenses,
        })

    return pd.DataFrame(records, columns=result_cols)


def get_client_summary(df_orders, df_payments):
    """Get a per-client summary of orders and payments.

    Args:
        df_orders (pd.DataFrame): Orders DataFrame.
        df_payments (pd.DataFrame): Payments DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns ``Client_Name``,
        ``Total_Orders``, ``Total_Order_Value``, ``Total_Paid``, ``Balance``.
    """
    result_cols = ["Client_Name", "Total_Orders", "Total_Order_Value", "Total_Paid", "Balance"]

    if df_orders.empty:
        return pd.DataFrame(columns=result_cols)

    # Aggregate orders per client
    client_orders = df_orders.groupby("Client_Name").agg(
        Total_Orders=("Order_ID", "count"),
        Total_Order_Value=("Order_Total", "sum"),
    ).reset_index()

    # Aggregate payments per order, then map to client
    if not df_payments.empty:
        paid_by_order = df_payments.groupby("Order_ID")["Amount"].sum()
        df_orders_copy = df_orders.copy()
        df_orders_copy["Paid"] = df_orders_copy["Order_ID"].map(paid_by_order).fillna(0)
        client_paid = df_orders_copy.groupby("Client_Name")["Paid"].sum().reset_index()
        client_paid.columns = ["Client_Name", "Total_Paid"]
    else:
        client_paid = pd.DataFrame({
            "Client_Name": client_orders["Client_Name"],
            "Total_Paid": 0.0,
        })

    summary = client_orders.merge(client_paid, on="Client_Name", how="left")
    summary["Total_Paid"] = summary["Total_Paid"].fillna(0)
    summary["Balance"] = summary["Total_Order_Value"] - summary["Total_Paid"]

    return summary[result_cols]


def get_product_performance(df_orders):
    """Get per-product performance metrics.

    Args:
        df_orders (pd.DataFrame): Orders DataFrame.

    Returns:
        pd.DataFrame: DataFrame with columns ``Product``, ``Units_Sold``,
        ``Revenue``, ``Avg_Order_Value``.
    """
    result_cols = ["Product", "Units_Sold", "Revenue", "Avg_Order_Value"]

    if df_orders.empty:
        return pd.DataFrame(columns=result_cols)

    summary = df_orders.groupby("Product").agg(
        Units_Sold=("Quantity", "sum"),
        Revenue=("Order_Total", "sum"),
        Avg_Order_Value=("Order_Total", "mean"),
    ).reset_index()

    return summary[result_cols]


# ---------------------------------------------------------------------------
# Cache Management
# ---------------------------------------------------------------------------

def clear_cache():
    """Clear the cached data to force a refresh on next load."""
    load_all_data.clear()
