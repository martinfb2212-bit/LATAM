import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Export Operations Suite",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Force light theme via config ─────────────────────────────────────────────
# Inject into .streamlit/config.toml equivalent via query params trick
components.html("""
<script>
// Force the page body and all Streamlit wrappers to light background
const style = document.createElement('style');
style.textContent = `
  body, #root, .main, .block-container,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stMain"],
  [data-testid="stMainBlockContainer"] {
    background-color: #F5F2ED !important;
    color: #1A1A1A !important;
  }
`;
document.head.appendChild(style);
</script>
""", height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap');

/* ── Force light mode on every Streamlit container ── */
html,
body,
.main,
.block-container,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[class*="css"],
.element-container,
div[data-stale="false"] {
  background-color: #F5F2ED !important;
  color: #1A1A1A !important;
  font-family: 'Jost', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div {
  background-color: #5C1F1F !important;
}
section[data-testid="stSidebar"] * {
  color: #F5EDE8 !important;
}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSelectbox label {
  color: #D4B8B0 !important;
  font-size: .72rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
  border: 1px dashed rgba(212,176,168,.45) !important;
  border-radius: 0 !important;
  background: rgba(255,255,255,.05) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
  color: #D4B8B0 !important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  color: #F5EDE8 !important;
  font-size: .84rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="popover"] {
  background-color: #3D1010 !important;
  border-color: rgba(212,176,168,.3) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
  background: #FFFFFF !important;
  border: 1px solid #DDD8D0 !important;
  border-top: 3px solid #8C3D3D !important;
  border-radius: 0 !important;
  padding: 20px 24px !important;
}
[data-testid="metric-container"] label {
  font-family: 'Jost', sans-serif !important;
  font-size: .65rem !important;
  letter-spacing: .18em !important;
  text-transform: uppercase !important;
  color: #7A7A7A !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2.2rem !important;
  font-weight: 500 !important;
  color: #1A1A1A !important;
  line-height: 1.15 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-family: 'Jost', sans-serif !important;
  font-size: .78rem !important;
  font-weight: 500 !important;
  color: #1A1A1A !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid #DDD8D0 !important;
  border-radius: 0 !important;
}
[data-testid="stDataFrame"] * {
  color: #1A1A1A !important;
  background-color: #FFFFFF !important;
}

/* ── Buttons ── */
.stButton > button {
  background-color: #8C3D3D !important;
  color: #FFF5F0 !important;
  border: none !important;
  font-family: 'Jost', sans-serif !important;
  font-size: .72rem !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 10px 28px !important;
}
.stButton > button:hover { background-color: #5C1F1F !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
  background-color: #FFFFFF !important;
  color: #8C3D3D !important;
  border: 1px solid #8C3D3D !important;
  font-family: 'Jost', sans-serif !important;
  font-size: .70rem !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 8px 22px !important;
}
[data-testid="stDownloadButton"] button:hover {
  background-color: #8C3D3D !important;
  color: #FFFFFF !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #F5F2ED !important;
  border-bottom: 1px solid #DDD8D0 !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Jost', sans-serif !important;
  font-size: .68rem !important;
  letter-spacing: .13em !important;
  text-transform: uppercase !important;
  color: #7A7A7A !important;
  padding: 12px 22px !important;
  border-bottom: 2px solid transparent !important;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #8C3D3D !important;
  border-bottom: 2px solid #8C3D3D !important;
  font-weight: 500 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background-color: #F5F2ED !important;
  padding-top: 20px !important;
}

/* ── Expander ── */
details,
[data-testid="stExpander"] {
  border: 1px solid #DDD8D0 !important;
  border-radius: 0 !important;
  margin-bottom: 6px !important;
  background: #FFFFFF !important;
}
[data-testid="stExpander"] summary,
details summary {
  font-family: 'Jost', sans-serif !important;
  font-size: .78rem !important;
  letter-spacing: .06em !important;
  color: #1A1A1A !important;
  background: #FFFFFF !important;
  padding: 12px 16px !important;
}
[data-testid="stExpander"][open] summary,
details[open] summary { color: #8C3D3D !important; }
[data-testid="stExpander"] > div > div {
  background: #FFFFFF !important;
  padding: 0 16px 12px !important;
}

/* ── Multiselect ── */
.stMultiSelect [data-baseweb="tag"] {
  background-color: #F0EAE2 !important;
  color: #5C1F1F !important;
  border-radius: 0 !important;
}
[data-baseweb="select"] > div {
  background-color: #FFFFFF !important;
  border-color: #DDD8D0 !important;
  color: #1A1A1A !important;
}

/* ── Input/select text ── */
input, textarea, [data-baseweb="input"] * {
  background-color: #FFFFFF !important;
  color: #1A1A1A !important;
}

/* ── Radio ── */
[data-testid="stRadio"] > label {
  color: #1A1A1A !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
  color: #1A1A1A !important;
}

/* ── Alerts ── */
.stAlert {
  border-radius: 0 !important;
  background-color: #FFF8F5 !important;
  color: #1A1A1A !important;
}

/* ── Headers & text ── */
h1, h2, h3, h4, h5, h6, p, span, div, label {
  color: #1A1A1A !important;
}

/* ── Plotly chart bg ── */
.js-plotly-plot, .plotly, .plot-container {
  background: transparent !important;
}
</style>
"""
components.html(CSS, height=0)

# ── IATA → Country ────────────────────────────────────────────────────────────
IATA_COUNTRY = {
    "JFK":"United States","MIA":"United States","LAX":"United States","ORD":"United States",
    "ATL":"United States","BOS":"United States","DFW":"United States","SFO":"United States",
    "EWR":"United States","IAD":"United States","SEA":"United States","PHL":"United States",
    "DTW":"United States","MSP":"United States","CLT":"United States","LGA":"United States",
    "MDW":"United States","BWI":"United States","DEN":"United States","MCO":"United States",
    "YYZ":"Canada","YVR":"Canada","YUL":"Canada","YYC":"Canada","YEG":"Canada",
    "MEX":"Mexico","GDL":"Mexico","MTY":"Mexico","CUN":"Mexico",
    "PTY":"Panama","SJO":"Costa Rica","GUA":"Guatemala","SAL":"El Salvador",
    "MBJ":"Jamaica","KIN":"Jamaica","NAS":"Bahamas","PUJ":"Dominican Republic",
    "SDQ":"Dominican Republic","SJU":"Puerto Rico","HAV":"Cuba",
    "GRU":"Brazil","GIG":"Brazil","VCP":"Brazil","BSB":"Brazil","SSA":"Brazil",
    "BOG":"Colombia","MDE":"Colombia","CTG":"Colombia","CLO":"Colombia","BAQ":"Colombia",
    "UIO":"Ecuador","GYE":"Ecuador","LIM":"Peru","CUZ":"Peru",
    "SCL":"Chile","EZE":"Argentina","AEP":"Argentina","MVD":"Uruguay","ASU":"Paraguay",
    "LPB":"Bolivia","CCS":"Venezuela",
    "AMS":"Netherlands","LHR":"United Kingdom","LGW":"United Kingdom","MAN":"United Kingdom",
    "CDG":"France","ORY":"France","NCE":"France",
    "FRA":"Germany","MUC":"Germany","DUS":"Germany","HAM":"Germany","BER":"Germany",
    "MAD":"Spain","BCN":"Spain","VLC":"Spain",
    "FCO":"Italy","MXP":"Italy","VCE":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland","VIE":"Austria","BRU":"Belgium",
    "CPH":"Denmark","ARN":"Sweden","OSL":"Norway","HEL":"Finland",
    "LIS":"Portugal","ATH":"Greece","WAW":"Poland","PRG":"Czech Republic",
    "BUD":"Hungary","ZAG":"Croatia","SOF":"Bulgaria","OTP":"Romania",
    "IST":"Turkey","SAW":"Turkey",
    "DXB":"United Arab Emirates","AUH":"United Arab Emirates","SHJ":"United Arab Emirates",
    "DOH":"Qatar","BAH":"Bahrain","KWI":"Kuwait","MCT":"Oman",
    "TLV":"Israel","RUH":"Saudi Arabia","JED":"Saudi Arabia",
    "CAI":"Egypt","NBO":"Kenya","JNB":"South Africa","CPT":"South Africa",
    "ADD":"Ethiopia","KGL":"Rwanda","LOS":"Nigeria","ACC":"Ghana","CMN":"Morocco",
    "HKG":"Hong Kong","SIN":"Singapore","KUL":"Malaysia",
    "NRT":"Japan","HND":"Japan","KIX":"Japan",
    "ICN":"South Korea","PEK":"China","PVG":"China","CAN":"China",
    "TPE":"Taiwan","BKK":"Thailand","CGK":"Indonesia","DPS":"Indonesia",
    "MNL":"Philippines","SGN":"Vietnam","HAN":"Vietnam",
    "BOM":"India","DEL":"India","BLR":"India",
    "SYD":"Australia","MEL":"Australia","BNE":"Australia","AKL":"New Zealand",
}
COUNTRY_FLAG = {
    "United States":"🇺🇸","Canada":"🇨🇦","Mexico":"🇲🇽","Brazil":"🇧🇷","Colombia":"🇨🇴",
    "Ecuador":"🇪🇨","Peru":"🇵🇪","Chile":"🇨🇱","Argentina":"🇦🇷","Uruguay":"🇺🇾",
    "Paraguay":"🇵🇾","Bolivia":"🇧🇴","Venezuela":"🇻🇪","Panama":"🇵🇦","Costa Rica":"🇨🇷",
    "Guatemala":"🇬🇹","El Salvador":"🇸🇻","Honduras":"🇭🇳","Nicaragua":"🇳🇮",
    "Jamaica":"🇯🇲","Dominican Republic":"🇩🇴","Puerto Rico":"🇵🇷","Cuba":"🇨🇺","Bahamas":"🇧🇸",
    "Netherlands":"🇳🇱","United Kingdom":"🇬🇧","France":"🇫🇷","Germany":"🇩🇪","Spain":"🇪🇸",
    "Italy":"🇮🇹","Switzerland":"🇨🇭","Austria":"🇦🇹","Belgium":"🇧🇪","Denmark":"🇩🇰",
    "Sweden":"🇸🇪","Norway":"🇳🇴","Finland":"🇫🇮","Portugal":"🇵🇹","Greece":"🇬🇷",
    "Poland":"🇵🇱","Czech Republic":"🇨🇿","Hungary":"🇭🇺","Romania":"🇷🇴","Bulgaria":"🇧🇬",
    "Croatia":"🇭🇷","Turkey":"🇹🇷","Ukraine":"🇺🇦",
    "United Arab Emirates":"🇦🇪","Qatar":"🇶🇦","Saudi Arabia":"🇸🇦","Kuwait":"🇰🇼",
    "Bahrain":"🇧🇭","Oman":"🇴🇲","Israel":"🇮🇱",
    "Egypt":"🇪🇬","Kenya":"🇰🇪","South Africa":"🇿🇦","Ethiopia":"🇪🇹","Nigeria":"🇳🇬",
    "Ghana":"🇬🇭","Morocco":"🇲🇦","Rwanda":"🇷🇼",
    "Japan":"🇯🇵","South Korea":"🇰🇷","China":"🇨🇳","Hong Kong":"🇭🇰","Taiwan":"🇹🇼",
    "Singapore":"🇸🇬","Thailand":"🇹🇭","Malaysia":"🇲🇾","Indonesia":"🇮🇩","Philippines":"🇵🇭",
    "Vietnam":"🇻🇳","India":"🇮🇳","Australia":"🇦🇺","New Zealand":"🇳🇿",
}

REQUIRED_COLS = ["delivery_year","delivery_week","customer_name",
                 "supply_source_name","destination","total_quantity","total_price"]
SHIPMENT_KEYS = ["customer_name","delivery_year","delivery_week","supply_source_name","iata_code"]

# Plotly palette — all high-contrast on white background
PALETTE = ["#8C3D3D","#2D4A3E","#B8924A","#4A6080","#6B4080","#2D6B5A","#80502D"]

# ── Utility helpers ───────────────────────────────────────────────────────────
def flag(c): return COUNTRY_FLAG.get(c, "🌍")

def safe_int(v):
    try:
        f = float(v)
        return 0 if (np.isnan(f) or np.isinf(f)) else int(f)
    except Exception:
        return 0

def safe_float(v):
    try:
        f = float(v)
        return 0.0 if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return 0.0

def pct_change(cur, prev):
    c, p = safe_float(cur), safe_float(prev)
    if p == 0: return None
    return (c - p) / p * 100

def status_badge(chg, cur_fob):
    cf = safe_float(cur_fob)
    if chg is None:  return "🆕 New"
    if cf == 0:      return "⛔ Lost"
    if chg >= 15:    return "🚀 Strong growth"
    if chg >= 3:     return "🟢 Growing"
    if chg >= -5:    return "🟡 Stable"
    if chg >= -20:   return "🔻 Declining"
    return "🔴 At risk"

def safe_pivot_val(pivot_df, key_col, key_val, year_col):
    row = pivot_df[pivot_df[key_col] == key_val]
    if row.empty or year_col not in row.columns:
        return 0.0
    return safe_float(row[year_col].values[0])

# ── UI components ─────────────────────────────────────────────────────────────
def divider():
    st.markdown('<div style="border-top:1px solid #DDD8D0;margin:32px 0;"></div>', unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding:40px 0 28px 0;border-bottom:1px solid #DDD8D0;margin-bottom:32px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;
                  color:#1A1A1A;letter-spacing:.015em;line-height:1.15;">{title}</div>
      {"<div style='font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#7A7A7A;margin-top:10px;'>" + subtitle + "</div>" if subtitle else ""}
    </div>""", unsafe_allow_html=True)

def section_label(text, accent="#8C3D3D"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin:28px 0 12px 0;">
      <div style="width:28px;height:1px;background:{accent};"></div>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:500;
                   color:#1A1A1A;letter-spacing:.03em;">{text}</span>
      <div style="flex:1;height:1px;background:#EDE9E3;"></div>
    </div>""", unsafe_allow_html=True)

def info_strip(msg, accent="#2D4A3E"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border-left:3px solid {accent};
                padding:14px 20px;margin:10px 0 20px 0;
                font-family:'Jost',sans-serif;font-size:.83rem;
                color:#1A1A1A;line-height:1.8;
                box-shadow:0 1px 6px rgba(26,26,26,.05);">{msg}</div>""",
    unsafe_allow_html=True)

def country_strip(country, n_ship, fob, accent="#8C3D3D"):
    fl = flag(country)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;
                padding:13px 20px;background:#FFFFFF;
                border-top:2px solid {accent};border-bottom:1px solid #EDE9E3;
                margin:20px 0 4px 0;box-shadow:0 2px 8px rgba(26,26,26,.04);">
      <span style="font-size:1.2rem;">{fl}</span>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;
                   font-weight:500;color:#1A1A1A;">{country}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.68rem;letter-spacing:.12em;
                   text-transform:uppercase;color:#7A7A7A;margin-left:6px;">
        {n_ship} shipment{"s" if n_ship!=1 else ""}
      </span>
      <span style="margin-left:auto;font-family:'Cormorant Garamond',serif;
                   font-size:1.1rem;color:{accent};font-weight:500;">
        $ {fob:,.0f}
      </span>
    </div>""", unsafe_allow_html=True)

def shipment_row(customer, origin, n_lines, units, fob, accent):
    st.markdown(f"""
    <div style="background:#FAFAF8;border-bottom:1px solid #EDE9E3;
                padding:10px 18px;display:flex;flex-wrap:wrap;align-items:center;gap:10px;">
      <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;
                   font-weight:500;color:{accent};">📦 {customer}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.72rem;
                   color:#7A7A7A;letter-spacing:.04em;">from {origin}</span>
      <span style="margin-left:auto;font-family:'Jost',sans-serif;
                   font-size:.72rem;color:#4A4A4A;letter-spacing:.03em;">
        {n_lines} line{"s" if n_lines!=1 else ""} &nbsp;·&nbsp;
        {units:,} units &nbsp;·&nbsp; $ {fob:,.2f}
      </span>
    </div>""", unsafe_allow_html=True)

def metric_delta_str(cur, prev):
    ch = pct_change(cur, prev)
    return f"{ch:+.1f}%" if ch is not None else None

# ── Plotly layout base ────────────────────────────────────────────────────────
def plotly_layout(fig, height=None):
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Jost",
        font_color="#1A1A1A",
        font_size=12,
        margin=dict(l=4, r=4, t=16, b=4),
        legend=dict(
            orientation="h", y=1.1, x=0,
            font=dict(size=11, color="#1A1A1A"),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#EDE9E3", linecolor="#DDD8D0", tickcolor="#DDD8D0",
                     tickfont=dict(color="#4A4A4A", size=11))
    fig.update_yaxes(gridcolor="#EDE9E3", linecolor="#DDD8D0", tickcolor="#DDD8D0",
                     zeroline=False, tickfont=dict(color="#4A4A4A", size=11))
    if height:
        fig.update_layout(height=height)
    return fig

# ── Data loading ──────────────────────────────────────────────────────────────
def extract_iata(series):
    s = series.astype(str).str.upper().str.strip()
    extracted = s.str.extract(r'\b([A-Z]{3})\b', expand=False)
    return extracted.fillna(s.str[:3])

def load_and_validate(uploaded):
    try:
        df = pd.read_excel(uploaded, engine="openpyxl")
    except Exception as e:
        return None, f"Could not read file: {e}"
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return None, f"Missing required columns: **{', '.join(missing)}**"
    for opt in ["secondary_customer_name","crop_name","variety_name","order_type","product"]:
        if opt not in df.columns:
            df[opt] = ""
    df["delivery_year"]  = pd.to_numeric(df["delivery_year"],  errors="coerce")
    df["delivery_week"]  = pd.to_numeric(df["delivery_week"],  errors="coerce")
    df["total_quantity"] = pd.to_numeric(df["total_quantity"], errors="coerce").fillna(0)
    df["total_price"]    = pd.to_numeric(df["total_price"],    errors="coerce").fillna(0)
    df["iata_code"]      = extract_iata(df["destination"])
    df["country"]        = df["iata_code"].map(IATA_COUNTRY).fillna("Unknown")
    df["shipment_id"]    = (
        df["customer_name"].astype(str) + "|" +
        df["delivery_year"].astype(str) + "-W" +
        df["delivery_week"].astype(str).str.zfill(2) + "|" +
        df["supply_source_name"].astype(str) + "→" +
        df["iata_code"].astype(str)
    )
    return df, ""

def filter_week(df, year, week):
    return df[(df["delivery_year"]==year) & (df["delivery_week"]==week)]

def add_weeks(year, week, delta):
    import datetime as dt
    d = date.fromisocalendar(year, week, 1) + dt.timedelta(weeks=delta)
    iso = d.isocalendar()
    return iso[0], iso[1]

def week_label(y, w):
    try:
        d = date.fromisocalendar(y, w, 1)
        return d.strftime(f"Week {w}  ·  %b %d, {y}")
    except Exception:
        return f"Week {w} / {y}"

def apply_filters(df, origins, customers):
    if origins:   df = df[df["supply_source_name"].isin(origins)]
    if customers: df = df[df["customer_name"].isin(customers)]
    return df

def n_shipments(df):
    if df.empty: return 0
    return df.groupby(SHIPMENT_KEYS)["shipment_id"].nunique().sum()

# ════════════════════════════════════════════════════════════════════════════
# COMMERCIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    years_avail   = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(df["country"].dropna().unique())

    page_header("Commercial Intelligence",
                "Year-over-Year Performance  ·  Growth Analysis  ·  Market Focus")

    # ── Scope ──────────────────────────────────────────────────────────────
    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]

    col_scope, col_note = st.columns([1, 2])
    with col_scope:
        scope = st.radio("Comparison scope", [
            "📅  Year-to-Date",
            "📆  Full Year"
        ], key="ci_scope")
    with col_note:
        use_ytd = "Year-to-Date" in scope
        if use_ytd:
            info_strip(
                f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. "
                f"Prior years are capped at week {current_week} for a fair, apples-to-apples comparison.",
                "#2D4A3E")
        else:
            info_strip(
                "Comparing <strong>all weeks present in the system</strong> per year — "
                "including future confirmed orders. Useful for full-year forecasting.",
                "#B8924A")

    divider()

    # ── Filters ──────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    default_years = years_avail[-3:] if len(years_avail) >= 3 else years_avail
    sel_years     = fc1.multiselect("Years", years_avail, default=default_years, key="ci_years")
    sel_customers = fc2.multiselect("Customers", all_customers, default=[], key="ci_customers", placeholder="All customers")
    sel_countries = fc3.multiselect("Destination countries", all_countries, default=[], key="ci_countries", placeholder="All countries")

    if not sel_years:
        st.warning("Select at least one year.")
        return

    dff = df[df["delivery_year"].isin(sel_years)].copy()
    if sel_customers: dff = dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff = dff[dff["country"].isin(sel_countries)]
    if use_ytd:       dff = dff[dff["delivery_week"] <= current_week]

    if dff.empty:
        st.info("No data matches the selected filters.")
        return

    cur_year   = max(sel_years)
    prev_year  = cur_year - 1
    prev2_year = cur_year - 2
    cy, py, p2y = str(cur_year), str(prev_year), str(prev2_year)
    scope_lbl = f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df   = dff[dff["delivery_year"]==cur_year]
    prev_df  = dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df = dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    section_label(f"Summary  ·  {scope_lbl}  ·  {cur_year} vs {prev_year}")

    cur_ship  = n_shipments(cur_df)
    prev_ship = n_shipments(prev_df)
    cur_fob   = safe_float(cur_df["total_price"].sum())
    prev_fob  = safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
    cur_units = safe_float(cur_df["total_quantity"].sum())
    prev_units= safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Shipments",        f"{cur_ship:,}",        delta=metric_delta_str(cur_ship,  prev_ship))
    k2.metric("FOB Value",        f"$ {cur_fob:,.0f}",    delta=metric_delta_str(cur_fob,   prev_fob))
    k3.metric("Units Shipped",    f"{int(cur_units):,}",  delta=metric_delta_str(cur_units, prev_units))
    k4.metric("Active Customers", f"{cur_df['customer_name'].nunique():,}")

    divider()

    # ── Weekly FOB trend ─────────────────────────────────────────────────────
    section_label(f"Weekly FOB Trend  ·  {scope_lbl}")

    weekly = (
        dff.groupby(["delivery_year","delivery_week"])
        .agg(fob=("total_price","sum"))
        .reset_index()
    )
    weekly["Year"] = weekly["delivery_year"].astype(str)

    fig_trend = px.line(
        weekly, x="delivery_week", y="fob", color="Year",
        labels={"delivery_week":"ISO Week","fob":"FOB (USD)","Year":"Year"},
        color_discrete_sequence=PALETTE, markers=True,
    )
    fig_trend.update_traces(line_width=2.5, marker_size=5)
    fig_trend.update_yaxes(tickprefix="$ ")
    plotly_layout(fig_trend, height=340)
    st.plotly_chart(fig_trend, use_container_width=True)

    divider()

    # ── FOB by Country ────────────────────────────────────────────────────────
    section_label(f"FOB by Destination Country  ·  Last 3 Years  ·  {scope_lbl}")

    cy_grp = (
        dff.groupby(["country","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"))
        .reset_index()
    )
    cy_grp["Year"]  = cy_grp["delivery_year"].astype(str)
    cy_grp["label"] = cy_grp["country"].apply(lambda c: f"{flag(c)} {c}")

    order = (cy_grp[cy_grp["Year"]==cy].sort_values("fob", ascending=False)["country"].tolist())
    others = [c for c in cy_grp["country"].unique() if c not in order]
    full_order = order + others
    cy_grp["sort_key"] = cy_grp["country"].apply(lambda c: full_order.index(c) if c in full_order else 999)
    cy_grp = cy_grp.sort_values("sort_key")

    fig_cntry = px.bar(
        cy_grp, x="label", y="fob", color="Year", barmode="group",
        labels={"label":"Country","fob":"FOB (USD)","Year":"Year"},
        color_discrete_sequence=PALETTE,
    )
    fig_cntry.update_yaxes(tickprefix="$ ")
    fig_cntry.update_xaxes(tickangle=-35)
    plotly_layout(fig_cntry, height=380)
    st.plotly_chart(fig_cntry, use_container_width=True)

    divider()

    # ── Country status table ──────────────────────────────────────────────────
    section_label(f"Country Status Table  ·  {scope_lbl}")

    piv_fob = cy_grp.pivot_table(index="country", columns="Year", values="fob",   aggfunc="sum").reset_index()
    piv_shp = cy_grp.pivot_table(index="country", columns="Year", values="ships", aggfunc="sum").reset_index()

    country_rows = []
    for c in piv_fob["country"].unique():
        c_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, cy))
        p_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, py))
        p2_fob = safe_float(safe_pivot_val(piv_fob, "country", c, p2y))
        c_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, cy))
        p_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, py))
        p2_shp = safe_int(safe_pivot_val(piv_shp, "country", c, p2y))
        chg_py = pct_change(c_fob, p_fob)
        chg_p2 = pct_change(c_fob, p2_fob)
        badge  = status_badge(chg_py, c_fob)
        country_rows.append({
            "Country":       f"{flag(c)} {c}",
            f"Ships {cy}":   c_shp,
            f"Ships {py}":   p_shp  or "—",
            f"Ships {p2y}":  p2_shp or "—",
            f"FOB {cy}":     f"$ {c_fob:,.0f}",
            f"FOB {py}":     f"$ {p_fob:,.0f}"  if p_fob  else "—",
            f"FOB {p2y}":    f"$ {p2_fob:,.0f}" if p2_fob else "—",
            f"vs {py}":      f"{chg_py:+.1f}%"  if chg_py is not None else "—",
            f"vs {p2y}":     f"{chg_p2:+.1f}%"  if chg_p2 is not None else "—",
            "Status":        badge,
        })

    country_rows.sort(
        key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","").strip()),
        reverse=True
    )
    st.dataframe(pd.DataFrame(country_rows), use_container_width=True, hide_index=True)

    divider()

    # ── Customer × Country ────────────────────────────────────────────────────
    section_label(f"Customer Performance by Country  ·  {scope_lbl}")
    info_strip(
        "Each country panel shows every customer active in any selected year. "
        "Status reflects current-year FOB vs prior year. "
        "Use this to identify where commercial focus is needed.",
        "#8C3D3D")

    ccy = (
        dff.groupby(["country","customer_name","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"), units=("total_quantity","sum"))
        .reset_index()
    )

    top_cntry = (
        ccy[ccy["delivery_year"]==cur_year]
        .groupby("country")["fob"].sum()
        .sort_values(ascending=False).index.tolist()
    )
    other_c = [c for c in ccy["country"].unique() if c not in top_cntry]
    for country in (top_cntry + other_c):
        cdf_c = ccy[ccy["country"]==country]
        if cdf_c.empty: continue

        tot_fob = safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
        tot_shp = safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())

        with st.expander(
            f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f}  ({scope_lbl} {cur_year})",
            expanded=False
        ):
            piv_c_fob  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="fob",   aggfunc="sum").reset_index()
            piv_c_shp  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="ships", aggfunc="sum").reset_index()
            piv_c_unit = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="units", aggfunc="sum").reset_index()

            cust_rows = []
            for _, r in piv_c_fob.iterrows():
                cname = r["customer_name"]
                cf    = safe_float(r.get(cur_year,   0))
                pf    = safe_float(r.get(prev_year,  0))
                p2f   = safe_float(r.get(prev2_year, 0))
                cs    = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, cur_year))
                ps    = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, prev_year))
                cu    = safe_int(safe_pivot_val(piv_c_unit, "customer_name", cname, cur_year))
                chg   = pct_change(cf, pf)
                chg2  = pct_change(cf, p2f)
                cbadge = status_badge(chg, cf)
                cust_rows.append({
                    "Customer":     cname,
                    f"FOB {cy}":    f"$ {cf:,.0f}",
                    f"FOB {py}":    f"$ {pf:,.0f}"  if pf  else "—",
                    f"FOB {p2y}":   f"$ {p2f:,.0f}" if p2f else "—",
                    f"vs {py}":     f"{chg:+.1f}%"   if chg  is not None else "—",
                    f"vs {p2y}":    f"{chg2:+.1f}%"  if chg2 is not None else "—",
                    f"Ships {cy}":  cs,
                    f"Ships {py}":  ps or "—",
                    f"Units {cy}":  f"{cu:,}",
                    "Status":       cbadge,
                })

            cust_rows.sort(
                key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","").strip()),
                reverse=True
            )

            if cust_rows:
                st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)

                cdf_cur = cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob", ascending=False).head(12)
                if not cdf_cur.empty:
                    fig_mini = px.bar(
                        cdf_cur, x="customer_name", y="fob",
                        labels={"customer_name":"","fob":"FOB (USD)"},
                        color_discrete_sequence=["#8C3D3D"],
                    )
                    fig_mini.update_yaxes(tickprefix="$ ")
                    fig_mini.update_xaxes(tickangle=-30)
                    plotly_layout(fig_mini, height=200)
                    st.plotly_chart(fig_mini, use_container_width=True)

    divider()

    # ── Growth focus ──────────────────────────────────────────────────────────
    section_label("Growth Opportunity Focus")

    decline = [r for r in country_rows if any(k in r["Status"] for k in ["Declining","At risk","Lost"])]
    growing = [r for r in country_rows if any(k in r["Status"] for k in ["Growing","Strong"])]
    new_mkt = [r for r in country_rows if "New" in r["Status"]]

    g1, g2, g3 = st.columns(3)

    def focus_col(col, title, color, items):
        col.markdown(
            f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;'
            f'text-transform:uppercase;color:{color};margin-bottom:10px;'
            f'padding-bottom:8px;border-bottom:2px solid {color};">{title}</div>',
            unsafe_allow_html=True)
        if not items:
            col.markdown('<div style="font-family:Jost,sans-serif;font-size:.82rem;color:#7A7A7A;padding:6px 0;">None</div>', unsafe_allow_html=True)
        for r in items:
            chg = r.get(f"vs {py}","—")
            col.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:7px 0;border-bottom:1px solid #EDE9E3;">'
                f'<span style="font-family:Jost,sans-serif;font-size:.82rem;color:#1A1A1A;">{r["Country"]}</span>'
                f'<span style="font-family:Jost,sans-serif;font-size:.75rem;font-weight:500;color:{color};">{chg}</span>'
                f'</div>',
                unsafe_allow_html=True)

    focus_col(g1, "Needs attention",  "#8C3D3D", decline)
    focus_col(g2, "Growing markets",  "#2D4A3E", growing)
    focus_col(g3, "New markets",      "#B8924A", new_mkt)


# ════════════════════════════════════════════════════════════════════════════
# LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
def render_by_destination(df, accent, dl_key):
    if df.empty:
        st.info("No shipments found for this period.")
        return

    for country in sorted(df["country"].unique()):
        cdf  = df[df["country"]==country]
        n_s  = n_shipments(cdf)
        fob_t= safe_float(cdf["total_price"].sum())
        country_strip(country, n_s, fob_t, accent)

        for airport in sorted(cdf["iata_code"].dropna().unique()):
            adf    = cdf[cdf["iata_code"]==airport]
            n_sa   = n_shipments(adf)
            n_prod = len(adf)
            units  = safe_int(adf["total_quantity"].sum())
            fob_a  = safe_float(adf["total_price"].sum())

            with st.expander(
                f"✈  {airport}   {n_sa} shipment{'s' if n_sa!=1 else ''}  ·  "
                f"{n_prod} product line{'s' if n_prod!=1 else ''}  ·  "
                f"{units:,} units  ·  $ {fob_a:,.0f}",
                expanded=(n_s==1)
            ):
                for sid, sdf in adf.groupby("shipment_id", sort=False):
                    customer = sdf["customer_name"].iloc[0]
                    origin   = sdf["supply_source_name"].iloc[0]
                    shipment_row(customer, origin, len(sdf),
                                 safe_int(sdf["total_quantity"].sum()),
                                 safe_float(sdf["total_price"].sum()), accent)
                    line_cols = [c for c in ["crop_name","variety_name","product",
                                             "total_quantity","total_price","order_type"]
                                 if c in sdf.columns]
                    ldf = sdf[line_cols].copy()
                    ldf.columns = [c.replace("_"," ").title() for c in ldf.columns]
                    if "Total Price"    in ldf.columns: ldf["Total Price"]    = ldf["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                    if "Total Quantity" in ldf.columns: ldf["Total Quantity"] = ldf["Total Quantity"].apply(lambda x: f"{int(x):,}")
                    st.dataframe(ldf, use_container_width=True, hide_index=True)

    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇  Export to Excel", data=buf.getvalue(),
        file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{dl_key}")


def render_logistics(df_all):
    today    = date.today()
    iso      = today.isocalendar()
    cur_year, cur_week = iso[0], iso[1]

    VIEWS = [
        (-1,"Past Week",    "Quality Follow-up",   "#8C3D3D",
         "The logistics team must contact the customer to confirm receipt and quality. "
         "If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
        ( 0,"Current Week", "Arrival Monitoring",  "#2D4A3E",
         "Confirm material has arrived at destination. "
         "Send all final documents including the <strong>final commercial invoice</strong>."),
        ( 1,"Week +1",      "Dispatch Closure",    "#B8924A",
         "Coordinate dispatch closure with customs agents. "
         "<em>If documentation is incomplete, shipments may be delayed with prior <strong>Sales Manager approval</strong>.</em>"),
        ( 2,"Week +2",      "Document Review",     "#4A6080",
         "Review draft documents with customs agents: AWB, phytosanitary certificate, "
         "commercial invoice, packing list, and certificate of origin."),
        ( 3,"Week +3",      "Advance Preview",     "#6B4080",
         "Verify special requirements: Colombia → certificate of origin; "
         "Brazil &amp; Costa Rica → import permit. Ask customers about last-minute additions."),
    ]

    week_dfs = [filter_week(df_all, *add_weeks(cur_year, cur_week, d)) for d,*_ in VIEWS]

    page_header(
        "Logistics Dashboard",
        f"ISO Week {cur_week}  ·  {today.strftime('%B %d, %Y')}  ·  Air Freight Operations"
    )

    tab_labels = ["Overview"] + [v[1] for v in VIEWS]
    all_tabs   = st.tabs(tab_labels)

    # ── Overview ──────────────────────────────────────────────────────────────
    with all_tabs[0]:
        all_5w = pd.concat(week_dfs, ignore_index=True) if any(not d.empty for d in week_dfs) else pd.DataFrame()

        section_label("Five-Week Rolling Summary")
        n_s = n_shipments(all_5w) if not all_5w.empty else 0
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Shipments",     f"{n_s:,}")
        c2.metric("Product Lines", f"{len(all_5w):,}")
        c3.metric("Total Units",   f"{safe_int(all_5w['total_quantity'].sum() if not all_5w.empty else 0):,}")
        c4.metric("FOB Value",     f"$ {safe_float(all_5w['total_price'].sum() if not all_5w.empty else 0):,.0f}")
        c5.metric("Destinations",  f"{all_5w['country'].nunique() if not all_5w.empty else 0:,}")

        divider()
        section_label("Weekly Breakdown")
        ov_rows = []
        for i,(delta,wt,vt,accent,_) in enumerate(VIEWS):
            vy,vw = add_weeks(cur_year,cur_week,delta)
            wdf   = week_dfs[i]
            lbl   = "Past" if delta==-1 else ("Current" if delta==0 else f"+{delta}w")
            ov_rows.append({
                "Period":    f"{lbl}  ·  {week_label(vy,vw)}",
                "Stage":     vt,
                "Shipments": n_shipments(wdf) if not wdf.empty else 0,
                "Lines":     len(wdf),
                "Units":     f"{safe_int(wdf['total_quantity'].sum()):,}",
                "FOB":       f"$ {safe_float(wdf['total_price'].sum()):,.0f}",
                "Countries": wdf["country"].nunique() if not wdf.empty else 0,
            })
        st.dataframe(pd.DataFrame(ov_rows), use_container_width=True, hide_index=True)

        if not all_5w.empty:
            divider()
            section_label("Destination Breakdown  ·  All Active Weeks")
            dest = (
                all_5w.groupby(["country","iata_code"])
                .agg(ships=("shipment_id","nunique"), lines=("total_quantity","count"),
                     units=("total_quantity","sum"), fob=("total_price","sum"))
                .reset_index().sort_values(["country","fob"], ascending=[True,False])
            )
            dest["Country"] = dest["country"].apply(lambda c: f"{flag(c)}  {c}")
            dest = dest.rename(columns={"iata_code":"Airport","ships":"Shipments",
                                        "lines":"Lines","units":"Units","fob":"FOB (USD)"})
            dest["FOB (USD)"] = dest["FOB (USD)"].apply(lambda x: f"$ {x:,.0f}")
            dest["Units"]     = dest["Units"].apply(lambda x: f"{int(x):,}")
            st.dataframe(dest[["Country","Airport","Shipments","Lines","Units","FOB (USD)"]],
                         use_container_width=True, hide_index=True)

    # ── Week tabs ─────────────────────────────────────────────────────────────
    for tab,(delta,wt,vt,accent,msg),wdf in zip(all_tabs[1:],VIEWS,week_dfs):
        with tab:
            vy,vw = add_weeks(cur_year,cur_week,delta)
            n_s   = n_shipments(wdf) if not wdf.empty else 0

            section_label(f"{wt}  —  {vt}", accent)
            st.markdown(
                f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;'
                f'text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">'
                f'{week_label(vy,vw)}</div>', unsafe_allow_html=True)
            info_strip(msg, accent)

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Shipments",     f"{n_s:,}")
            c2.metric("Product Lines", f"{len(wdf):,}")
            c3.metric("Total Units",   f"{safe_int(wdf['total_quantity'].sum()):,}")
            c4.metric("FOB Value",     f"$ {safe_float(wdf['total_price'].sum()):,.0f}")
            c5.metric("Destinations",  f"{wdf['country'].nunique() if not wdf.empty else 0:,}")

            divider()
            section_label("Shipments by Destination", accent)
            render_by_destination(wdf, accent, dl_key=f"{delta}_{vw}_{vy}")


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:32px 0 6px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:400;
                  color:#F5EDE8;letter-spacing:.04em;line-height:1.2;">✦ Export Ops</div>
      <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                  text-transform:uppercase;color:#C4A090;margin-top:4px;">Management Suite</div>
    </div>
    <div style="border-top:1px solid rgba(212,176,168,.25);margin:16px 0 20px 0;"></div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Navigation</p>', unsafe_allow_html=True)
    page = st.radio("page_nav", ["📦  Logistics", "📈  Commercial Intelligence"],
                    label_visibility="collapsed", key="page_selector")

    st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:20px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Data Source</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"], label_visibility="collapsed")

    if "df" in st.session_state and st.session_state.df is not None:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.07);border:1px solid rgba(212,176,168,.2);
                    padding:12px 14px;margin-top:10px;font-family:Jost,sans-serif;
                    font-size:.74rem;line-height:2;">
          <span style="color:#D4B070;">●</span>
          <span style="color:#F5EDE8;margin-left:6px;">{st.session_state.filename}</span><br>
          <span style="color:#C4A090;">Updated&nbsp;&nbsp;</span>
          <span style="color:#F5EDE8;">{st.session_state.loaded_at}</span><br>
          <span style="color:#C4A090;">Records&nbsp;&nbsp;&nbsp;</span>
          <span style="color:#F5EDE8;">{len(st.session_state.df):,}</span>
        </div>""", unsafe_allow_html=True)

        if page == "📦  Logistics":
            st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:20px 0;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Filters</p>', unsafe_allow_html=True)
            origins   = st.multiselect("Origin",   sorted(st.session_state.df["supply_source_name"].dropna().unique()), placeholder="All origins",   key="log_origins")
            customers = st.multiselect("Customer", sorted(st.session_state.df["customer_name"].dropna().unique()),       placeholder="All customers", key="log_customers")
            st.session_state.origins   = origins
            st.session_state.customers = customers


# ── File processing ───────────────────────────────────────────────────────────
if uploaded is not None:
    df_new, err = load_and_validate(uploaded)
    if err:
        st.error(f"⚠️ {err}")
        st.stop()
    st.session_state.df        = df_new
    st.session_state.filename  = uploaded.name
    st.session_state.loaded_at = datetime.now().strftime("%b %d, %Y  %H:%M")
    if "origins"   not in st.session_state: st.session_state.origins   = []
    if "customers" not in st.session_state: st.session_state.customers = []


# ── Welcome screen ────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state.df is None:
    st.markdown("""
    <div style="max-width:640px;margin:100px auto 0 auto;padding:0 24px;">

      <div style="font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:300;
                  color:#1A1A1A;letter-spacing:.01em;line-height:1.15;text-align:center;
                  margin-bottom:6px;">
        Export Operations Suite
      </div>

      <div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.22em;
                  text-transform:uppercase;color:#7A7A7A;text-align:center;margin-bottom:48px;">
        Fresh Flowers &amp; Vegetables &nbsp;·&nbsp; Air Freight
      </div>

      <div style="border-top:1px solid #DDD8D0;border-bottom:1px solid #DDD8D0;
                  padding:36px 0;margin-bottom:36px;text-align:center;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-style:italic;
                    color:#7A7A7A;margin-bottom:16px;">
          Upload your weekly Excel file to begin
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;
                    line-height:1.9;">
          Use the <strong style="color:#8C3D3D;">sidebar uploader</strong> on the left.<br>
          Switch between <strong>Logistics</strong> and <strong>Commercial Intelligence</strong> using the navigation menu.
        </div>
      </div>

      <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;
                  padding:28px 32px;">
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                    text-transform:uppercase;color:#8C3D3D;margin-bottom:14px;">
          Required columns
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;line-height:2.1;">
          delivery_year &nbsp;·&nbsp; delivery_week &nbsp;·&nbsp; customer_name<br>
          supply_source_name &nbsp;·&nbsp; destination &nbsp;·&nbsp; total_quantity &nbsp;·&nbsp; total_price
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                    text-transform:uppercase;color:#7A7A7A;margin:20px 0 10px 0;">
          Optional columns
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#7A7A7A;line-height:2.1;">
          secondary_customer_name &nbsp;·&nbsp; crop_name &nbsp;·&nbsp; variety_name<br>
          order_type &nbsp;·&nbsp; product
        </div>
      </div>

    </div>""", unsafe_allow_html=True)
    st.stop()


# ── Routing ───────────────────────────────────────────────────────────────────
if page == "📈  Commercial Intelligence":
    render_commercial(st.session_state.df.copy())
else:
    df_log = apply_filters(
        st.session_state.df.copy(),
        st.session_state.get("origins", []),
        st.session_state.get("customers", [])
    )
    render_logistics(df_log)
