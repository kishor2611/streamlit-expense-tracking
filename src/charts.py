import typing
"""
Charts module for the Business Dashboard.
Builds all Plotly visualizations with a consistent dark theme.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CHART_COLORS, CHART_TEMPLATE


# ─── Helper ──────────────────────────────────────────────────────────


def _apply_common_style(fig: go.Figure, title: typing.Optional[str] = None) -> go.Figure:
    """Apply the shared light-theme layout to every chart."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#4D2B12"),
        margin=dict(l=20, r=20, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#4D2B12"),
        ),
    )
    if title:
        fig.update_layout(
            title=dict(
                text=f"<b>{title}</b>",
                font=dict(family="Playfair Display, serif", size=16, color="#4D2B12")
            )
        )
    fig.update_xaxes(title_font=dict(color="#4D2B12"), tickfont=dict(color="#4D2B12"), gridcolor="rgba(0,0,0,0.05)")
    fig.update_yaxes(title_font=dict(color="#4D2B12"), tickfont=dict(color="#4D2B12"), gridcolor="rgba(0,0,0,0.05)")
    return fig


def _is_valid(df: pd.DataFrame, required_cols: typing.Optional[typing.List[str]] = None) -> bool:
    """Return True when *df* is a non-empty DataFrame with all required columns."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return False
    if required_cols:
        return all(col in df.columns for col in required_cols)
    return True


# ─── 1. Expenses Donut Chart ────────────────────────────────────────


def build_expense_pie(df_expenses: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Donut chart of expenses grouped by Category.

    Uses columns: ``Category``, ``Amount``.
    """
    if not _is_valid(df_expenses, ["Category", "Amount"]):
        return None

    grouped = (
        df_expenses.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig = px.pie(
        grouped,
        names="Category",
        values="Amount",
        hole=0.45,
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )

    fig.update_layout(showlegend=True, legend_title_text="")
    _apply_common_style(fig, title="Expenses by Category")
    return fig


# ─── 2. Sales Volume Bar Chart ──────────────────────────────────────


def build_sales_bar(df_orders: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Horizontal bar chart of sales volume by Product.

    Groups by ``Product``, sums ``Quantity``.
    """
    if not _is_valid(df_orders, ["Product", "Quantity"]):
        return None

    grouped = (
        df_orders.groupby("Product", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=True)  # ascending for horizontal layout
    )

    fig = px.bar(
        grouped,
        x="Quantity",
        y="Product",
        orientation="h",
        text_auto=True,
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_traces(
        marker=dict(cornerradius=6),
        textposition="outside",
    )

    fig.update_layout(
        xaxis_title="Units Sold",
        yaxis_title="",
    )

    _apply_common_style(fig, title="Sales Volume by Product")
    return fig


# ─── 3. Revenue vs Expenses Trend ───────────────────────────────────


def build_revenue_expense_trend(
    df_payments: pd.DataFrame,
    df_expenses: pd.DataFrame,
) -> typing.Optional[go.Figure]:
    """Line chart showing monthly revenue vs expenses.

    Parses the ``Date`` column in both DataFrames and groups by year-month.
    """
    if not _is_valid(df_payments, ["Date", "Amount"]):
        return None
    if not _is_valid(df_expenses, ["Date", "Amount"]):
        return None

    # --- revenue ---
    rev = df_payments.copy()
    rev["Date"] = pd.to_datetime(rev["Date"], dayfirst=True, errors="coerce")
    rev = rev.dropna(subset=["Date"])
    rev["Month"] = rev["Date"].dt.to_period("M").astype(str)
    rev_monthly = rev.groupby("Month", as_index=False)["Amount"].sum()
    rev_monthly.rename(columns={"Amount": "Revenue"}, inplace=True)

    # --- expenses ---
    exp = df_expenses.copy()
    exp["Date"] = pd.to_datetime(exp["Date"], dayfirst=True, errors="coerce")
    exp = exp.dropna(subset=["Date"])
    exp["Month"] = exp["Date"].dt.to_period("M").astype(str)
    exp_monthly = exp.groupby("Month", as_index=False)["Amount"].sum()
    exp_monthly.rename(columns={"Amount": "Expenses"}, inplace=True)

    # --- merge ---
    merged = pd.merge(rev_monthly, exp_monthly, on="Month", how="outer").fillna(0)
    merged.sort_values("Month", inplace=True)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=merged["Month"],
            y=merged["Revenue"],
            name="Revenue",
            mode="lines+markers",
            line=dict(color="#22C55E", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.10)",
            marker=dict(size=7),
            hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=merged["Month"],
            y=merged["Expenses"],
            name="Expenses",
            mode="lines+markers",
            line=dict(color="#F43F5E", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(244,63,94,0.10)",
            marker=dict(size=7),
            hovertemplate="Expenses: ₹%{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        hovermode="x unified",
    )

    _apply_common_style(fig, title="Revenue vs Expenses Trend")

    # Override margin and legend positions specifically for this chart to prevent overlap
    fig.update_layout(
        title=dict(
            text="<b>Revenue vs Expenses Trend</b>",
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=120, b=60, l=60, r=60)
    )
    return fig


# ─── 4. Payment Source Breakdown ─────────────────────────────────────


def build_payment_source_pie(df_payments: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Donut chart of payment sources.

    Groups by ``Source``, sums ``Amount``.
    """
    if not _is_valid(df_payments, ["Source", "Amount"]):
        return None

    grouped = (
        df_payments.groupby("Source", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig = px.pie(
        grouped,
        names="Source",
        values="Amount",
        hole=0.4,
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )

    fig.update_layout(showlegend=True, legend_title_text="")
    _apply_common_style(fig, title="Payment Sources")
    return fig


# ─── 5. Order Status Funnel ─────────────────────────────────────────

# Canonical funnel order + colour map
_FUNNEL_ORDER = ["Pending", "Shipped", "Delivered", "Cancelled"]
_FUNNEL_COLORS = {
    "Pending": "#F59E0B",
    "Shipped": "#3B82F6",
    "Delivered": "#22C55E",
    "Cancelled": "#EF4444",
}


def build_order_pipeline(df_orders: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Funnel chart showing order-status distribution.

    Uses column: ``Status``.
    """
    if not _is_valid(df_orders, ["Status"]):
        return None

    counts = df_orders["Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]

    # Enforce canonical order; keep only statuses present in the data
    ordered = [s for s in _FUNNEL_ORDER if s in counts["Status"].values]
    counts = counts.set_index("Status").loc[ordered].reset_index()
    colors = [_FUNNEL_COLORS.get(s, CHART_COLORS[0]) for s in counts["Status"]]

    fig = go.Figure(
        go.Funnel(
            y=counts["Status"],
            x=counts["Count"],
            marker=dict(color=colors),
            textinfo="value+percent initial",
            hovertemplate="<b>%{y}</b><br>Orders: %{x}<br>%{percentInitial:.1%} of total<extra></extra>",
        )
    )

    _apply_common_style(fig, title="Order Pipeline")
    return fig


# ─── 6. Monthly P&L Bar Chart ───────────────────────────────────────


def build_monthly_pnl_chart(df_pnl: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Grouped bar chart for monthly P&L with a Net Profit line overlay.

    Expected columns: ``Month``, ``Revenue``, ``Expenses``, ``Net_Profit``.
    """
    if not _is_valid(df_pnl, ["Month", "Revenue", "Expenses", "Net_Profit"]):
        return None

    fig = go.Figure()

    # Revenue bars
    fig.add_trace(
        go.Bar(
            x=df_pnl["Month"],
            y=df_pnl["Revenue"],
            name="Revenue",
            marker_color="#22C55E",
            marker=dict(cornerradius=4),
            hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # Expense bars
    fig.add_trace(
        go.Bar(
            x=df_pnl["Month"],
            y=df_pnl["Expenses"],
            name="Expenses",
            marker_color="#F43F5E",
            marker=dict(cornerradius=4),
            hovertemplate="Expenses: ₹%{y:,.0f}<extra></extra>",
        )
    )

    # Net Profit line
    fig.add_trace(
        go.Scatter(
            x=df_pnl["Month"],
            y=df_pnl["Net_Profit"],
            name="Net Profit",
            mode="lines+markers",
            line=dict(color="#6366F1", width=3, dash="dot"),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="Net Profit: ₹%{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        hovermode="x unified",
    )

    _apply_common_style(fig, title="Monthly Profit & Loss")

    # Override margin and legend positions specifically for this chart to prevent overlap
    fig.update_layout(
        title=dict(
            text="<b>Monthly Profit & Loss</b>",
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=120, b=60, l=60, r=60)
    )
    return fig


# ─── 7. Product Performance Chart ───────────────────────────────────


def build_product_performance(df_product_perf: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Combined bar + line chart with dual y-axes.

    Bars represent ``Units_Sold`` (left axis) and a line shows ``Revenue``
    (right axis).

    Expected columns: ``Product``, ``Units_Sold``, ``Revenue``.
    """
    if not _is_valid(df_product_perf, ["Product", "Units_Sold", "Revenue"]):
        return None

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bars – Units Sold (primary y-axis)
    fig.add_trace(
        go.Bar(
            x=df_product_perf["Product"],
            y=df_product_perf["Units_Sold"],
            name="Units Sold",
            marker_color="#8B5CF6",
            marker=dict(cornerradius=4),
            hovertemplate="Units: %{y}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Line – Revenue (secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=df_product_perf["Product"],
            y=df_product_perf["Revenue"],
            name="Revenue",
            mode="lines+markers",
            line=dict(color="#22C55E", width=3),
            marker=dict(size=8),
            hovertemplate="Revenue: ₹%{y:,.0f}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="Units Sold", secondary_y=False)
    fig.update_yaxes(title_text="Revenue (₹)", secondary_y=True)
    fig.update_layout(hovermode="x unified")

    _apply_common_style(fig, title="Product Performance")

    # Override margin and legend positions specifically for this chart to prevent rotated labels overlapping the legend
    fig.update_layout(
        title=dict(
            text="<b>Product Performance</b>",
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=120, b=120, l=60, r=60)
    )
    return fig


# ─── 8. Expense Breakdown Trend ───────────────────────────────────────

def build_expense_trend(df_expenses: pd.DataFrame) -> typing.Optional[go.Figure]:
    """Stacked bar chart showing monthly expense breakdown by Category.

    Expected columns: ``Date``, ``Category``, ``Amount``.
    """
    if not _is_valid(df_expenses, ["Date", "Category", "Amount"]):
        return None

    exp = df_expenses.copy()
    exp["Date"] = pd.to_datetime(exp["Date"], dayfirst=True, errors="coerce")
    exp = exp.dropna(subset=["Date"])
    exp["Month"] = exp["Date"].dt.to_period("M").astype(str)

    grouped = exp.groupby(["Month", "Category"], as_index=False)["Amount"].sum()
    grouped.sort_values("Month", inplace=True)

    fig = px.bar(
        grouped,
        x="Month",
        y="Amount",
        color="Category",
        barmode="stack",
        color_discrete_sequence=CHART_COLORS,
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
        hovermode="x unified",
    )

    _apply_common_style(fig, title="Monthly Expense Breakdown")

    # Override margin and legend positions specifically for this chart to prevent overlap
    fig.update_layout(
        title=dict(
            text="<b>Monthly Expense Breakdown</b>",
            y=0.98,
            x=0.5,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=120, b=60, l=60, r=60)
    )
    return fig

