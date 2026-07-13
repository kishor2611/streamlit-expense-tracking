"""
Configuration constants for the Business Dashboard application.
Centralizes all app-wide settings, categories, and styling.
"""

# ─── Page Configuration ───────────────────────────────────────────
PAGE_TITLE = "House of Ishira — Business Tracker"
PAGE_ICON = "🍛"
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

# Supported Payment Sources
PAYMENT_SOURCES = ["UPI", "Cash", "Bank Transfer", "Cheque", "Other"]

# ─── ID Prefixes ─────────────────────────────────────────────────
ORDER_ID_PREFIX = "ORD"
EXPENSE_ID_PREFIX = "EXP"
PAYMENT_ID_PREFIX = "PAY"

# ─── Cache TTL (seconds) ─────────────────────────────────────────
DATA_CACHE_TTL = 60

# ─── Chart Color Palette ─────────────────────────────────────────
# A modern, harmonious palette matching the Gold and Green Ishira theme
CHART_COLORS = [
    "#B58926",  # Gold
    "#1C3322",  # Forest Green
    "#D4C2AD",  # Warm Cream/Brown
    "#4D2B12",  # Dark Bronze
    "#6366F1",  # Indigo
    "#EC4899",  # Pink
    "#F97316",  # Orange
    "#EAB308",  # Yellow
    "#22C55E",  # Green
    "#06B6D4",  # Cyan
]

CHART_TEMPLATE = "plotly_dark"

# ─── Status Colors (for badges) ──────────────────────────────────
STATUS_COLORS = {
    "Pending": "#B58926",    # Gold
    "Shipped": "#3B82F6",    # Blue
    "Delivered": "#1C3322",  # Forest Green
    "Cancelled": "#EF4444",  # Red
}

# ─── CSS Styles ───────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
    /* ── Global fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FCFAF7;
    }
    
    h1, h2, h3, h4, h5, h6, .section-header {
        font-family: 'Playfair Display', serif !important;
        color: #4D2B12 !important;
    }

    .main {
        background-color: #FCFAF7;
    }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(181,137,38,0.06) 0%, rgba(28,51,34,0.06) 100%);
        border: 1px solid rgba(181,137,38,0.2);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        min-height: 140px !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(181,137,38,0.15);
    }
    div[data-testid="stMetric"] label {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.03em;
        color: #4D2B12 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        color: #B58926 !important;
    }

    /* ── Tabs styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 4px;
        background: rgba(181,137,38,0.05);
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        color: #4D2B12 !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #B58926, #8F6612) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(181,137,38,0.3);
    }

    /* ── Buttons ── */
    /* Generic / Default Button styling */
    /* Generic / Default Button styling (excludes any primary/submit buttons) */
    .stButton button:not([data-testid="stBaseButton-primary"]),
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stDownloadButton"] a {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(181,137,38,0.4) !important;
        border-radius: 8px !important;
        transition: all 0.15s ease-in-out !important;
        font-weight: 600 !important;
        padding: 8px 12px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stColumn"] .stButton button:not([data-testid="stBaseButton-primary"]),
    div[data-testid="stColumn"] div[data-testid="stDownloadButton"] button,
    div[data-testid="stColumn"] div[data-testid="stDownloadButton"] a {
        width: 100% !important;
    }
    .stButton button:not([data-testid="stBaseButton-primary"]),
    .stButton button:not([data-testid="stBaseButton-primary"]) *,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stDownloadButton"] button *,
    div[data-testid="stDownloadButton"] a,
    div[data-testid="stDownloadButton"] a * {
        color: #B58926 !important;
        white-space: nowrap !important;
        font-size: 0.85rem !important;
        text-decoration: none !important;
    }
    .stButton button:not([data-testid="stBaseButton-primary"]):hover,
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stDownloadButton"] a:hover {
        background-color: #B58926 !important;
        border-color: #B58926 !important;
        box-shadow: 0 4px 12px rgba(181,137,38,0.2) !important;
        transform: scale(1.03) translateY(-1px) !important;
    }
    .stButton button:not([data-testid="stBaseButton-primary"]):hover *,
    div[data-testid="stDownloadButton"] button:hover *,
    div[data-testid="stDownloadButton"] a:hover * {
        color: #FFFFFF !important;
    }
    .stButton button:not([data-testid="stBaseButton-primary"]):focus,
    div[data-testid="stDownloadButton"] button:focus,
    div[data-testid="stDownloadButton"] a:focus {
        border-color: #B58926 !important;
        box-shadow: 0 0 0 3px rgba(181,137,38,0.3) !important;
        outline: none !important;
        transform: scale(1.03) !important;
    }
    .stButton button:not([data-testid="stBaseButton-primary"]):active,
    div[data-testid="stDownloadButton"] button:active,
    div[data-testid="stDownloadButton"] a:active {
        transform: scale(0.97) translateY(1px) !important;
        box-shadow: 0 2px 6px rgba(181,137,38,0.1) !important;
    }

    /* Primary Gold Button styling (handles type="primary" st.button and all st.form_submit_button submit buttons) */
    .stButton button[kind="primary"],
    .stButton button[data-testid="stBaseButton-primary"],
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #B58926, #8F6612) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 16px rgba(181,137,38,0.25) !important;
        height: auto !important;
        width: auto !important;
        white-space: normal !important;
        font-size: 1rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton button[kind="primary"],
    .stButton button[kind="primary"] *,
    .stButton button[data-testid="stBaseButton-primary"],
    .stButton button[data-testid="stBaseButton-primary"] *,
    div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stFormSubmitButton"] button * {
        color: #FCFAF7 !important;
    }
    .stButton button[kind="primary"]:hover,
    .stButton button[data-testid="stBaseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px) scale(1.03) !important;
        box-shadow: 0 6px 24px rgba(181,137,38,0.35) !important;
    }
    .stButton button[kind="primary"]:hover *,
    .stButton button[data-testid="stBaseButton-primary"]:hover *,
    div[data-testid="stFormSubmitButton"] button:hover * {
        color: #FFFFFF !important;
    }
    .stButton button[data-testid="stBaseButton-primary"]:focus,
    div[data-testid="stFormSubmitButton"] button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(181,137,38,0.4) !important;
        transform: scale(1.03) !important;
    }
    .stButton button[data-testid="stBaseButton-primary"]:active,
    div[data-testid="stFormSubmitButton"] button:active {
        transform: translateY(1px) scale(0.97) !important;
        box-shadow: 0 3px 10px rgba(181,137,38,0.15) !important;
    }

    /* ── Danger button (delete) ── */
    .danger-btn > button {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(239,68,68,0.25) !important;
        height: auto !important;
        width: auto !important;
        white-space: normal !important;
    }
    .danger-btn > button:hover {
        box-shadow: 0 6px 24px rgba(239,68,68,0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Form Inputs & Labels (light theme forcing) ── */
    /* Widget labels */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    label,
    label p,
    span[data-testid="stWidgetLabel"] p {
        color: #4D2B12 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Inputs (text input, number, text area) */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        color: #4D2B12 !important;
        border: 1px solid rgba(181,137,38,0.3) !important;
        border-radius: 8px !important;
    }

    /* Date inputs container */
    div[data-testid="stDateInput"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(181,137,38,0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Date inputs child elements reset */
    div[data-testid="stDateInput"] div,
    div[data-testid="stDateInput"] input {
        background-color: transparent !important;
        color: #4D2B12 !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stDateInput"] * {
        color: #4D2B12 !important;
    }

    /* Select boxes */
    div[data-baseweb="select"] {
        border: 1px solid rgba(181,137,38,0.3) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div {
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="select"] * {
        color: #4D2B12 !important;
    }
    
    /* Multiselect tags styling */
    [data-baseweb="tag"] {
        background-color: rgba(181, 137, 38, 0.15) !important;
        border: 1px solid rgba(181, 137, 38, 0.3) !important;
        border-radius: 6px !important;
    }
    [data-baseweb="tag"] * {
        background-color: transparent !important;
        color: #4D2B12 !important;
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
        color: #4D2B12 !important;
        background-color: #FFFFFF !important;
        border: 1px solid rgba(181,137,38,0.2) !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid rgba(181,137,38,0.15) !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
    }
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] span,
    .main [data-testid="stMarkdownContainer"] li,
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] li {
        color: #4D2B12 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Override primary button text styles to stay off-white/white (prevent markdown color pollution) */
    .main .stButton button[kind="primary"] *,
    .main .stButton button[data-testid="stBaseButton-primary"] *,
    .main .stButton button[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] *,
    .main .stButton button[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] span,
    .main div[data-testid="stFormSubmitButton"] button *,
    .main div[data-testid="stFormSubmitButton"] button [data-testid="stMarkdownContainer"] *,
    .main div[data-testid="stFormSubmitButton"] button [data-testid="stMarkdownContainer"] span {
        color: #FCFAF7 !important;
    }
    .main .stButton button[kind="primary"]:hover *,
    .main .stButton button[data-testid="stBaseButton-primary"]:hover *,
    .main .stButton button[data-testid="stBaseButton-primary"]:hover [data-testid="stMarkdownContainer"] *,
    .main .stButton button[data-testid="stBaseButton-primary"]:hover [data-testid="stMarkdownContainer"] span,
    .main div[data-testid="stFormSubmitButton"] button:hover *,
    .main div[data-testid="stFormSubmitButton"] button:hover [data-testid="stMarkdownContainer"] *,
    .main div[data-testid="stFormSubmitButton"] button:hover [data-testid="stMarkdownContainer"] span {
        color: #FFFFFF !important;
    }

    /* ── Info / Success / Error boxes ── */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(181,137,38,0.2) !important;
    }
    .stAlert p,
    .stAlert span,
    .stAlert li,
    .stAlert div,
    .stAlert strong,
    .stAlert em,
    .stAlert svg {
        color: #1A202C !important;
        fill: #1A202C !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1C3322 0%, #0F1E14 100%) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #FCFAF7 !important;
        font-family: 'Playfair Display', serif !important;
    }
    /* Force sidebar metric text to be visible on dark green bg */
    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
    }
    section[data-testid="stSidebar"] [data-testid="stMetric"] label {
        color: #D4C2AD !important;
        font-family: 'Inter', sans-serif !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FCFAF7 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #D4C2AD !important;
    }

    /* Sidebar buttons text color override */
    section[data-testid="stSidebar"] .stButton > button,
    section[data-testid="stSidebar"] .stButton > button * {
        color: #B58926 !important;
        font-family: 'Inter', sans-serif !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] .stButton > button:hover * {
        color: #FFFFFF !important;
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
    .status-pending { background: rgba(181,137,38,0.15); color: #B58926; }
    .status-shipped { background: rgba(59,130,246,0.15); color: #3B82F6; }
    .status-delivered { background: rgba(28,51,34,0.15); color: #1C3322; }
    .status-cancelled { background: rgba(239,68,68,0.15); color: #EF4444; }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #B58926;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(181,137,38,0.2);
    }

    /* ── KPI delta colors ── */
    [data-testid="stMetricDelta"] svg {
        width: 14px;
        height: 14px;
    }

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

    /* ── Hide Streamlit default menu/footer ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
