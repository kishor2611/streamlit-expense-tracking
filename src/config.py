"""
Configuration constants for the Business Dashboard application.
Centralizes all app-wide settings, categories, and styling.
"""

# ─── Page Configuration ───────────────────────────────────────────
PAGE_TITLE = "📊 Small Biz Analytics & Tracker"
PAGE_ICON = "📊"
LAYOUT = "wide"

# ─── Google Sheets Worksheet Names ────────────────────────────────
WS_ORDERS = "Orders"
WS_PRODUCTS = "Products"
WS_EXPENSES = "Expenses"
WS_PAYMENTS = "Payments"

# ─── Column Definitions ──────────────────────────────────────────
# Orders columns (in sheet order)
ORDER_COLS = ["Order_ID", "Date", "Client_Name", "Address", "Product", "Quantity", "Order_Total", "Status"]

# Products columns
PRODUCT_COLS = ["Product_Name", "Weight", "Price"]

# Expenses columns
EXPENSE_COLS = ["Expense_ID", "Date", "Category", "Item", "Amount"]

# Payments columns
PAYMENT_COLS = ["Payment_ID", "Date", "Order_ID", "Amount", "Source"]

# ─── Business Logic Constants ────────────────────────────────────
ORDER_STATUSES = ["Pending", "Shipped", "Delivered", "Cancelled"]

EXPENSE_CATEGORIES = [
    "Raw Materials",
    "Packaging",
    "Shipping/Delivery",
    "Marketing",
    "Utilities",
    "Rent",
    "Salary",
    "Equipment",
    "Other",
]

PAYMENT_SOURCES = ["UPI", "Cash", "Bank Transfer", "Cheque", "Other"]

# ─── ID Prefixes ─────────────────────────────────────────────────
ORDER_ID_PREFIX = "ORD"
EXPENSE_ID_PREFIX = "EXP"
PAYMENT_ID_PREFIX = "PAY"

# ─── Cache TTL (seconds) ─────────────────────────────────────────
DATA_CACHE_TTL = 60

# ─── Chart Color Palette ─────────────────────────────────────────
# A modern, harmonious palette for Plotly charts
CHART_COLORS = [
    "#6366F1",  # Indigo
    "#8B5CF6",  # Violet
    "#EC4899",  # Pink
    "#F43F5E",  # Rose
    "#F97316",  # Orange
    "#EAB308",  # Yellow
    "#22C55E",  # Green
    "#06B6D4",  # Cyan
    "#3B82F6",  # Blue
    "#A855F7",  # Purple
]

CHART_TEMPLATE = "plotly_dark"

# ─── Status Colors (for badges) ──────────────────────────────────
STATUS_COLORS = {
    "Pending": "#F59E0B",    # Amber
    "Shipped": "#3B82F6",    # Blue
    "Delivered": "#22C55E",  # Green
    "Cancelled": "#EF4444",  # Red
}

# ─── CSS Styles ───────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
    /* ── Global font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(99,102,241,0.15);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }

    /* ── Tabs styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 4px;
        background: rgba(99,102,241,0.04);
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.3);
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        border: none;
        border-radius: 10px;
        padding: 10px 28px;
        font-weight: 600;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 16px rgba(99,102,241,0.25);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(99,102,241,0.35);
    }

    /* ── Danger button (delete) ── */
    .danger-btn > button {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.25);
    }
    .danger-btn > button:hover {
        box-shadow: 0 6px 24px rgba(239,68,68,0.35) !important;
        transform: translateY(-1px);
    }

    /* ── Data frames ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        font-weight: 600;
        border-radius: 10px;
    }

    /* ── Info / Success / Error boxes ── */
    .stAlert {
        border-radius: 12px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #E2E8F0;
    }

    /* ── Status badges ── */
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .status-pending { background: rgba(245,158,11,0.15); color: #F59E0B; }
    .status-shipped { background: rgba(59,130,246,0.15); color: #3B82F6; }
    .status-delivered { background: rgba(34,197,94,0.15); color: #22C55E; }
    .status-cancelled { background: rgba(239,68,68,0.15); color: #EF4444; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #6366F1;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(99,102,241,0.2);
    }

    /* ── KPI delta colors ── */
    [data-testid="stMetricDelta"] svg {
        width: 14px;
        height: 14px;
    }

    /* ── Hide Streamlit default menu/footer ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Pipeline progress ── */
    .pipeline-stage {
        text-align: center;
        padding: 16px 12px;
        border-radius: 12px;
        font-weight: 600;
    }
    .pipeline-count {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .pipeline-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.8;
    }
</style>
"""
