"""
Reusable UI components for the Streamlit Business Dashboard.

Provides sidebar, status badges, pipeline visualization, top-client tables,
date filters, search/filter bars, export buttons, section headers, and
KPI delta calculations.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta


# ─── 1. Sidebar ──────────────────────────────────────────────────────

def render_sidebar(df_orders, df_payments, df_expenses):
    """Render the sidebar with branding and quick stats.

    Uses st.sidebar to render the app title, subtitle, key financial
    metrics (total orders, revenue, expenses, net profit), a refresh
    button, and the last-refreshed timestamp.

    Parameters
    ----------
    df_orders : pd.DataFrame
        Orders table (used for row count).
    df_payments : pd.DataFrame
        Payments table (``Amount`` column summed for revenue).
    df_expenses : pd.DataFrame
        Expenses table (``Amount`` column summed for expenses).

    Returns
    -------
    bool
        ``True`` if the *🔄 Refresh Data* button was clicked.
    """
    st.sidebar.markdown("# 📊 Biz Tracker")
    st.sidebar.markdown("*Small Business Analytics*")
    st.sidebar.markdown("---")

    # --- Quick Stats ---
    st.sidebar.markdown("### Quick Stats")

    total_orders = len(df_orders) if df_orders is not None and not df_orders.empty else 0
    total_revenue = (
        df_payments["Amount"].sum()
        if df_payments is not None and not df_payments.empty and "Amount" in df_payments.columns
        else 0.0
    )
    total_expenses = (
        df_expenses["Amount"].sum()
        if df_expenses is not None and not df_expenses.empty and "Amount" in df_expenses.columns
        else 0.0
    )
    net_profit = total_revenue - total_expenses

    st.sidebar.metric("Total Orders", f"{total_orders:,}")
    st.sidebar.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    st.sidebar.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    st.sidebar.metric("Net Profit", f"₹{net_profit:,.2f}")

    st.sidebar.markdown("---")

    # --- Refresh ---
    refresh = st.sidebar.button("🔄 Refresh Data")
    st.sidebar.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return refresh


# ─── 2. Status Badge ─────────────────────────────────────────────────

def status_badge(status):
    """Return an HTML string for a coloured status badge.

    The badge CSS classes (``status-pending``, ``status-shipped``, etc.)
    are defined in :pydata:`config.CUSTOM_CSS`.

    Parameters
    ----------
    status : str
        One of ``'Pending'``, ``'Shipped'``, ``'Delivered'``, or
        ``'Cancelled'``.

    Returns
    -------
    str
        An HTML ``<span>`` element, e.g.
        ``'<span class="status-badge status-pending">PENDING</span>'``.
    """
    css_map = {
        "Pending": "status-pending",
        "Shipped": "status-shipped",
        "Delivered": "status-delivered",
        "Cancelled": "status-cancelled",
    }
    css_class = css_map.get(status, "status-pending")
    label = status.upper() if status else "UNKNOWN"
    return f'<span class="status-badge {css_class}">{label}</span>'


# ─── 3. Order Pipeline ───────────────────────────────────────────────

def render_pipeline(df_orders):
    """Render the order-status pipeline as coloured metric columns.

    Displays 3–4 columns (Pending / Shipped / Delivered / Cancelled)
    with the count of orders in each status.  The Cancelled column is
    only shown when at least one cancelled order exists.

    Parameters
    ----------
    df_orders : pd.DataFrame
        Must contain a ``Status`` column.
    """
    if df_orders is None or df_orders.empty or "Status" not in df_orders.columns:
        st.info("No order data available for the pipeline view.")
        return

    status_counts = df_orders["Status"].value_counts()

    stages = [
        ("Pending", "#F59E0B"),
        ("Shipped", "#3B82F6"),
        ("Delivered", "#22C55E"),
    ]

    # Only add Cancelled column if any exist
    if status_counts.get("Cancelled", 0) > 0:
        stages.append(("Cancelled", "#EF4444"))

    cols = st.columns(len(stages))

    for col, (label, color) in zip(cols, stages):
        count = status_counts.get(label, 0)
        col.markdown(
            f"""
            <div style="text-align:center; padding:20px; border-radius:12px;
                        background:rgba({_hex_to_rgb(color)},0.12);">
                <div style="font-size:2.2rem; font-weight:800; color:{color};">
                    {count}
                </div>
                <div style="font-size:0.8rem; font-weight:600; text-transform:uppercase;
                            letter-spacing:0.06em; color:{color}; opacity:0.9;">
                    {label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _hex_to_rgb(hex_color):
    """Convert a hex colour like ``'#F59E0B'`` to an ``'r,g,b'`` string."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


# ─── 4. Top Clients Table ────────────────────────────────────────────

def render_top_clients(df_orders, n=5):
    """Show a styled table of the top *n* clients by total order value.

    Groups ``df_orders`` by ``Client_Name``, sums ``Order_Total``,
    counts orders, sorts descending, and displays the top *n* rows
    using :func:`st.dataframe` with ``column_config`` formatting.

    Parameters
    ----------
    df_orders : pd.DataFrame
        Must contain ``Client_Name`` and ``Order_Total`` columns.
    n : int, optional
        Number of top clients to show (default ``5``).
    """
    if (
        df_orders is None
        or df_orders.empty
        or "Client_Name" not in df_orders.columns
        or "Order_Total" not in df_orders.columns
    ):
        st.info("Not enough order data to show top clients.")
        return

    top = (
        df_orders.groupby("Client_Name")
        .agg(Total_Orders=("Order_Total", "count"), Total_Value=("Order_Total", "sum"))
        .sort_values("Total_Value", ascending=False)
        .head(n)
        .reset_index()
    )
    top.insert(0, "Rank", range(1, len(top) + 1))

    st.dataframe(
        top,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "Client_Name": st.column_config.TextColumn("Client Name"),
            "Total_Orders": st.column_config.NumberColumn("Total Orders"),
            "Total_Value": st.column_config.NumberColumn(
                "Total Value",
                format="₹%,.2f",
            ),
        },
    )


# ─── 5. Date Filter Bar ──────────────────────────────────────────────

def render_date_filter(key_prefix="dashboard"):
    """Render a date-range filter with quick-select buttons.

    The filter row contains four quick-select buttons (*This Month*,
    *Last 30 Days*, *This Year*, *All Time*) followed by explicit
    start / end date pickers.

    Session-state keys are namespaced with *key_prefix* to avoid
    conflicts when the component is reused on multiple tabs.

    Parameters
    ----------
    key_prefix : str, optional
        Prefix for ``st.session_state`` keys (default ``'dashboard'``).

    Returns
    -------
    tuple[datetime.date, datetime.date]
        ``(start_date, end_date)``
    """
    sk_start = f"{key_prefix}_start_date"
    sk_end = f"{key_prefix}_end_date"

    # Initialise session-state defaults (All Time)
    if sk_start not in st.session_state:
        st.session_state[sk_start] = date(2020, 1, 1)
    if sk_end not in st.session_state:
        st.session_state[sk_end] = date.today()

    btn_cols = st.columns([1, 1, 1, 1, 2, 2])

    with btn_cols[0]:
        if st.button("This Month", key=f"{key_prefix}_btn_month"):
            today = date.today()
            st.session_state[sk_start] = today.replace(day=1)
            st.session_state[sk_end] = today

    with btn_cols[1]:
        if st.button("Last 30 Days", key=f"{key_prefix}_btn_30d"):
            st.session_state[sk_start] = date.today() - timedelta(days=30)
            st.session_state[sk_end] = date.today()

    with btn_cols[2]:
        if st.button("This Year", key=f"{key_prefix}_btn_year"):
            st.session_state[sk_start] = date.today().replace(month=1, day=1)
            st.session_state[sk_end] = date.today()

    with btn_cols[3]:
        if st.button("All Time", key=f"{key_prefix}_btn_all"):
            st.session_state[sk_start] = date(2020, 1, 1)
            st.session_state[sk_end] = date.today()

    with btn_cols[4]:
        start_date = st.date_input(
            "Start Date",
            value=st.session_state[sk_start],
            key=f"{key_prefix}_date_start_input",
        )
    with btn_cols[5]:
        end_date = st.date_input(
            "End Date",
            value=st.session_state[sk_end],
            key=f"{key_prefix}_date_end_input",
        )

    # Persist manual picks back into session state
    st.session_state[sk_start] = start_date
    st.session_state[sk_end] = end_date

    return start_date, end_date


# ─── 6. Filter DataFrame by Date ─────────────────────────────────────

def filter_by_date(df, date_col, start_date, end_date):
    """Filter a DataFrame to rows within a date range (inclusive).

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    date_col : str
        Name of the column that contains date values.
    start_date : datetime.date
        Inclusive start date.
    end_date : datetime.date
        Inclusive end date.

    Returns
    -------
    pd.DataFrame
        Filtered copy; the original is returned unchanged if the
        date column is missing or cannot be parsed.
    """
    if df is None or df.empty or date_col not in df.columns:
        return df

    try:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        mask = (dates >= pd.Timestamp(start_date)) & (dates <= pd.Timestamp(end_date))
        return df.loc[mask].reset_index(drop=True)
    except Exception:
        return df


# ─── 7. Search and Filter Bar ────────────────────────────────────────

def render_search_filter(df, table_name, key_prefix):
    """Render a search box and column-aware filters for a table.

    Provides:
    * A text-search input that matches across **all** columns.
    * A ``Status`` multi-select (if the column exists).
    * A ``Category`` multi-select (if the column exists).
    * A date-range filter (if a ``Date`` column exists).

    Parameters
    ----------
    df : pd.DataFrame
        The table to filter.
    table_name : str
        Human-readable table name (used in widget labels).
    key_prefix : str
        Prefix for widget keys to avoid collisions.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    if df is None or df.empty:
        st.info(f"No data available in {table_name}.")
        return df if df is not None else pd.DataFrame()

    filtered = df.copy()

    # --- Text search ---
    search_term = st.text_input(
        f"🔍 Search {table_name}",
        key=f"{key_prefix}_search",
        placeholder="Type to search across all columns…",
    )
    if search_term:
        mask = filtered.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1,
        )
        filtered = filtered.loc[mask]

    filter_cols = st.columns(3)

    # --- Status filter ---
    if "Status" in filtered.columns:
        with filter_cols[0]:
            statuses = df["Status"].dropna().unique().tolist()
            selected = st.multiselect(
                "Filter by Status",
                options=statuses,
                default=statuses,
                key=f"{key_prefix}_status",
            )
            if selected:
                filtered = filtered[filtered["Status"].isin(selected)]

    # --- Category filter ---
    if "Category" in filtered.columns:
        with filter_cols[1]:
            categories = df["Category"].dropna().unique().tolist()
            selected_cats = st.multiselect(
                "Filter by Category",
                options=categories,
                default=categories,
                key=f"{key_prefix}_category",
            )
            if selected_cats:
                filtered = filtered[filtered["Category"].isin(selected_cats)]

    # --- Date filter ---
    if "Date" in filtered.columns:
        with filter_cols[2]:
            try:
                parsed_dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
                if not parsed_dates.empty:
                    min_date = parsed_dates.min().date()
                    max_date = parsed_dates.max().date()
                else:
                    min_date = date(2020, 1, 1)
                    max_date = date.today()
            except Exception:
                min_date = date(2020, 1, 1)
                max_date = date.today()

            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                key=f"{key_prefix}_date_range",
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                filtered = filter_by_date(filtered, "Date", date_range[0], date_range[1])

    return filtered.reset_index(drop=True)


# ─── 8. Export Buttons ────────────────────────────────────────────────

def render_export_buttons(df, table_name):
    """Render a CSV download button for a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Data to export.
    table_name : str
        Used in the button label and download filename.
    """
    if df is None or df.empty:
        st.info("No data to export.")
        return

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download {table_name} as CSV",
        data=csv_data,
        file_name=f"{table_name.lower()}_export.csv",
        mime="text/csv",
    )


# ─── 9. Section Header ───────────────────────────────────────────────

def section_header(title, icon=""):
    """Render a styled section header.

    Uses the ``section-header`` CSS class defined in
    :pydata:`config.CUSTOM_CSS`.

    Parameters
    ----------
    title : str
        Header text.
    icon : str, optional
        Emoji or icon string prepended to *title*.
    """
    display_text = f"{icon} {title}" if icon else title
    st.markdown(
        f'<div class="section-header">{display_text}</div>',
        unsafe_allow_html=True,
    )


# ─── 10. KPI Metric with Delta ───────────────────────────────────────

def calculate_period_delta(df, amount_col, date_col, start_date, end_date):
    """Calculate value and delta between the current and previous period.

    The *previous period* has the same duration as
    ``end_date - start_date`` and ends the day before *start_date*.

    Parameters
    ----------
    df : pd.DataFrame
        Source data.
    amount_col : str
        Column to sum (must be numeric).
    date_col : str
        Column containing date values.
    start_date : datetime.date
        Start of the current period (inclusive).
    end_date : datetime.date
        End of the current period (inclusive).

    Returns
    -------
    tuple[float, float, str]
        ``(current_sum, delta_value, delta_pct_str)``
        *delta_pct_str* is formatted like ``'+12.5%'`` or ``'-8.3%'``.
    """
    if (
        df is None
        or df.empty
        or amount_col not in df.columns
        or date_col not in df.columns
    ):
        return 0.0, 0.0, "+0.0%"

    try:
        dates = pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        return 0.0, 0.0, "+0.0%"

    # Current period
    current_mask = (dates >= pd.Timestamp(start_date)) & (dates <= pd.Timestamp(end_date))
    current_sum = pd.to_numeric(df.loc[current_mask, amount_col], errors="coerce").sum()

    # Previous period (same duration, ending right before start_date)
    period_length = (end_date - start_date).days
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_length)

    prev_mask = (dates >= pd.Timestamp(prev_start)) & (dates <= pd.Timestamp(prev_end))
    prev_sum = pd.to_numeric(df.loc[prev_mask, amount_col], errors="coerce").sum()

    delta_value = current_sum - prev_sum

    if prev_sum != 0:
        delta_pct = (delta_value / abs(prev_sum)) * 100
    else:
        delta_pct = 0.0 if delta_value == 0 else 100.0

    sign = "+" if delta_pct >= 0 else ""
    delta_pct_str = f"{sign}{delta_pct:.1f}%"

    return current_sum, delta_value, delta_pct_str
