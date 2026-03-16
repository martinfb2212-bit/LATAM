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

# ── Global CSS ────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap');

:root {
  --ivory:    #FAFAF8;
  --white:    #FFFFFF;
  --burgundy: #8B3A3A;
  --burg-lt:  #C27070;
  --sage:     #7A9E8E;
  --gold:     #C4974A;
  --gold-lt:  #E8C98A;
  --charcoal: #1E1E1E;
  --mid:      #5A5A5A;
  --soft:     #9A9A9A;
  --cream:    #F0EDE8;
  --border:   #E8E4DC;
}

html, body, [class*="css"] {
  font-family: 'Jost', sans-serif !important;
  background-color: var(--ivory) !important;
  color: var(--charcoal) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color: var(--white) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--charcoal) !important; }
section[data-testid="stSidebar"] .stRadio label {
  font-family: 'Jost', sans-serif !important;
  font-size: .82rem !important;
  letter-spacing: .06em !important;
}

/* Metrics */
[data-testid="metric-container"] {
  background: var(--white) !important;
  border: 1px solid var(--border) !important;
  border-top: 2px solid var(--burgundy) !important;
  border-radius: 2px !important;
  padding: 18px 22px !important;
}
[data-testid="metric-container"] label {
  font-family: 'Jost', sans-serif !important;
  font-size: .68rem !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  color: var(--soft) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2.1rem !important;
  font-weight: 500 !important;
  color: var(--charcoal) !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-size: .78rem !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 2px !important;
}

/* Buttons */
.stButton > button {
  background-color: var(--charcoal) !important;
  color: var(--white) !important;
  border: none !important;
  font-family: 'Jost', sans-serif !important;
  font-size: .75rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
  border-radius: 2px !important;
  padding: 8px 22px !important;
}
.stButton > button:hover { background-color: var(--burgundy) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Jost', sans-serif !important;
  font-size: .72rem !important;
  letter-spacing: .1em !important;
  text-transform: uppercase !important;
  color: var(--soft) !important;
  padding: 10px 20px !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: var(--burgundy) !important;
  border-bottom: 2px solid var(--burgundy) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  border: 1px solid var(--border) !important;
  border-radius: 2px !important;
}

/* Expander */
details summary {
  font-family: 'Jost', sans-serif !important;
  font-size: .78rem !important;
  letter-spacing: .06em !important;
}

/* Radio */
.stRadio [data-testid="stMarkdownContainer"] p {
  font-size: .82rem !important;
}

/* Select */
.stMultiSelect [data-baseweb="tag"] {
  background-color: var(--cream) !important;
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
    "AMS":"Netherlands","EIN":"Netherlands",
    "LHR":"United Kingdom","LGW":"United Kingdom","MAN":"United Kingdom",
    "CDG":"France","ORY":"France","NCE":"France",
    "FRA":"Germany","MUC":"Germany","DUS":"Germany","HAM":"Germany","BER":"Germany",
    "MAD":"Spain","BCN":"Spain","VLC":"Spain",
    "FCO":"Italy","MXP":"Italy","VCE":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland",
    "VIE":"Austria","BRU":"Belgium",
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

# ── Helpers ───────────────────────────────────────────────────────────────────
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
    if chg is None:   return "🆕 New"
    if cf == 0:       return "⛔ Lost"
    if chg >= 15:     return "🚀 Strong growth"
    if chg >= 3:      return "🟢 Growing"
    if chg >= -5:     return "🟡 Stable"
    if chg >= -20:    return "🔻 Declining"
    return "🔴 At risk"

def div():
    st.markdown(
        '<div style="border-top:1px solid #E8E4DC;margin:28px 0;"></div>',
        unsafe_allow_html=True)

def page_title(title, sub=""):
    st.markdown(f"""
    <div style="padding:32px 0 20px 0;border-bottom:1px solid #E8E4DC;margin-bottom:28px;">
      <div style="font-family:\'Cormorant Garamond\',serif;font-size:2.6rem;font-weight:400;
                  color:#1E1E1E;letter-spacing:.01em;line-height:1.2;">{title}</div>
      {"<div style='font-family:Jost,sans-serif;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#9A9A9A;margin-top:8px;'>"+sub+"</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def section_title(t, accent="#8B3A3A"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:24px 0 10px 0;">
      <div style="width:3px;height:18px;background:{accent};border-radius:1px;flex-shrink:0;"></div>
      <span style="font-family:\'Cormorant Garamond\',serif;font-size:1.25rem;font-weight:500;
                   color:#1E1E1E;letter-spacing:.02em;">{t}</span>
    </div>""", unsafe_allow_html=True)

def note_box(msg, color="#7A9E8E"):
    st.markdown(f"""
    <div style="background:#FAFAF8;border:1px solid #E8E4DC;border-left:3px solid {color};
                padding:14px 20px;margin:10px 0 18px 0;font-family:Jost,sans-serif;
                font-size:.83rem;color:#1E1E1E;line-height:1.75;">{msg}</div>""",
    unsafe_allow_html=True)

def country_header(country, n_ship, fob, accent="#8B3A3A"):
    fl = flag(country)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:12px 18px;
                background:#FFFFFF;border:1px solid #E8E4DC;border-left:3px solid {accent};
                margin:16px 0 4px 0;">
      <span style="font-size:1.25rem;">{fl}</span>
      <span style="font-family:\'Cormorant Garamond\',serif;font-size:1.1rem;font-weight:500;
                   color:{accent};">{country}</span>
      <span style="font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.08em;
                   text-transform:uppercase;color:#9A9A9A;margin-left:4px;">
        {n_ship} shipment{"s" if n_ship!=1 else ""} &nbsp;·&nbsp; $ {fob:,.0f} FOB
      </span>
    </div>""", unsafe_allow_html=True)

def shipment_card(customer, origin, n_lines, units, fob, accent):
    st.markdown(f"""
    <div style="background:#FAFAF8;border:1px solid #E8E4DC;padding:10px 16px;
                margin:6px 0 3px 0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
      <span style="font-family:\'Cormorant Garamond\',serif;font-size:1rem;font-weight:500;
                   color:{accent};">📦 {customer}</span>
      <span style="font-family:Jost,sans-serif;font-size:.74rem;color:#9A9A9A;">from {origin}</span>
      <span style="font-family:Jost,sans-serif;font-size:.72rem;color:#5A5A5A;margin-left:auto;">
        {n_lines} line{"s" if n_lines!=1 else ""} &nbsp;·&nbsp; {units:,} units &nbsp;·&nbsp; $ {fob:,.2f}
      </span>
    </div>""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
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
        return d.strftime(f"Week {w} · %b %d, {y}")
    except Exception:
        return f"Week {w} / {y}"

def apply_filters(df, origins, customers):
    if origins:   df = df[df["supply_source_name"].isin(origins)]
    if customers: df = df[df["customer_name"].isin(customers)]
    return df

def n_shipments(df):
    if df.empty: return 0
    return df.groupby(SHIPMENT_KEYS)["shipment_id"].nunique().sum()

# ── Pivot helpers (safe) ──────────────────────────────────────────────────────
def safe_pivot_val(pivot_df, key_col, key_val, year_col):
    row = pivot_df[pivot_df[key_col] == key_val]
    if row.empty or year_col not in row.columns:
        return 0.0
    return safe_float(row[year_col].values[0])

# ════════════════════════════════════════════════════════════════════════════
# COMMERCIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    PALETTE = ["#8B3A3A","#7A9E8E","#C4974A","#4A6B8A","#6B4A8A","#4A8A6B","#8A6B4A"]

    years_avail = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(df["country"].dropna().unique())

    page_title("Commercial Intelligence", "Year-over-Year Performance & Growth Analysis")

    # ── Scope toggle ─────────────────────────────────────────────────────────
    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]
    current_year = today_iso[0]

    sc1, sc2 = st.columns([1, 2])
    with sc1:
        scope = st.radio("Comparison scope", [
            "📅  Year-to-Date",
            "📆  Full Year"
        ], key="ci_scope")
    with sc2:
        use_ytd = "Year-to-Date" in scope
        if use_ytd:
            note_box(
                f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. "
                f"Prior years are capped at the same week for a fair comparison.",
                "#7A9E8E")
        else:
            note_box(
                "Comparing <strong>all weeks present in the system</strong> per year — "
                "including future confirmed orders. Useful for full-year forecasting.",
                "#C4974A")

    div()

    # ── Filters ───────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    sel_years     = fc1.multiselect("Years", years_avail, default=years_avail[-3:] if len(years_avail)>=3 else years_avail, key="ci_years")
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

    cur_year  = max(sel_years)
    prev_year = cur_year - 1
    prev2_year= cur_year - 2
    cy, py, p2y = str(cur_year), str(prev_year), str(prev2_year)

    scope_lbl = f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df  = dff[dff["delivery_year"]==cur_year]
    prev_df = dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df= dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ── Top-level KPIs ────────────────────────────────────────────────────────
    div()
    section_title(f"Summary · {scope_lbl} · {cur_year} vs {prev_year}")

    cur_ship  = n_shipments(cur_df)
    prev_ship = n_shipments(prev_df)
    cur_fob   = safe_float(cur_df["total_price"].sum())
    prev_fob  = safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
    cur_units = safe_float(cur_df["total_quantity"].sum())
    prev_units= safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0

    def pct_str(c, p):
        ch = pct_change(c, p)
        return f"{ch:+.1f}%" if ch is not None else None

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Shipments",       f"{cur_ship:,}",           delta=pct_str(cur_ship, prev_ship))
    k2.metric("FOB Value",       f"$ {cur_fob:,.0f}",       delta=pct_str(cur_fob, prev_fob))
    k3.metric("Units Shipped",   f"{int(cur_units):,}",     delta=pct_str(cur_units, prev_units))
    k4.metric("Active Customers",f"{cur_df['customer_name'].nunique():,}")

    div()

    # ── Weekly FOB trend ──────────────────────────────────────────────────────
    section_title(f"Weekly FOB Trend · {scope_lbl}")

    weekly = (
        dff.groupby(["delivery_year","delivery_week"])
        .agg(fob=("total_price","sum"))
        .reset_index()
    )
    weekly["Year"] = weekly["delivery_year"].astype(str)

    fig_trend = px.line(
        weekly, x="delivery_week", y="fob", color="Year",
        labels={"delivery_week":"Week","fob":"FOB (USD)"},
        color_discrete_sequence=PALETTE,
        markers=True,
    )
    fig_trend.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        font_family="Jost", font_color="#1E1E1E",
        hovermode="x unified",
        margin=dict(l=0,r=0,t=10,b=0),
        yaxis=dict(tickprefix="$ ", gridcolor="#F0EDE8", zeroline=False),
        xaxis=dict(gridcolor="#F0EDE8", title="ISO Week"),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    fig_trend.update_traces(line_width=2, marker_size=4)
    st.plotly_chart(fig_trend, use_container_width=True)

    div()

    # ── Country performance: last 3 years ─────────────────────────────────────
    section_title(f"FOB by Destination Country · Last 3 Years ({scope_lbl})")

    cy_grp = (
        dff.groupby(["country","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"))
        .reset_index()
    )
    cy_grp["Year"] = cy_grp["delivery_year"].astype(str)
    cy_grp["label"] = cy_grp["country"].apply(lambda c: f"{flag(c)} {c}")

    order = (
        cy_grp[cy_grp["Year"]==cy]
        .sort_values("fob", ascending=False)["country"].tolist()
    )
    others = [c for c in cy_grp["country"].unique() if c not in order]
    full_order = order + others
    cy_grp["sort_key"] = cy_grp["country"].apply(lambda c: full_order.index(c) if c in full_order else 999)
    cy_grp = cy_grp.sort_values("sort_key")

    fig_cntry = px.bar(
        cy_grp, x="label", y="fob", color="Year", barmode="group",
        labels={"label":"Country","fob":"FOB (USD)","Year":"Year"},
        color_discrete_sequence=PALETTE,
    )
    fig_cntry.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        font_family="Jost", font_color="#1E1E1E",
        margin=dict(l=0,r=0,t=10,b=0),
        yaxis=dict(tickprefix="$ ", gridcolor="#F0EDE8", zeroline=False),
        xaxis=dict(gridcolor="#F0EDE8", tickangle=-30),
        legend=dict(orientation="h", y=1.08, x=0),
        bargap=0.25, bargroupgap=0.05,
    )
    st.plotly_chart(fig_cntry, use_container_width=True)

    div()

    # ── Country performance table ─────────────────────────────────────────────
    section_title(f"Country Status Table · {scope_lbl}")

    piv_fob = cy_grp.pivot_table(index="country", columns="Year", values="fob",  aggfunc="sum").reset_index()
    piv_shp = cy_grp.pivot_table(index="country", columns="Year", values="ships", aggfunc="sum").reset_index()

    country_rows = []
    all_ctry = piv_fob["country"].unique()
    for c in all_ctry:
        c_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, cy))
        p_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, py))
        p2_fob = safe_float(safe_pivot_val(piv_fob, "country", c, p2y))
        c_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, cy))
        p_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, py))
        p2_shp = safe_int(safe_pivot_val(piv_shp, "country", c, p2y))
        chg_py = pct_change(c_fob, p_fob)
        chg_p2 = pct_change(c_fob, p2_fob)
        st = status_badge(chg_py, c_fob)
        country_rows.append({
            "Country":              f"{flag(c)} {c}",
            f"Ships {cy}":          c_shp,
            f"Ships {py}":          p_shp or "—",
            f"Ships {p2y}":         p2_shp or "—",
            f"FOB {cy}":            f"$ {c_fob:,.0f}",
            f"FOB {py}":            f"$ {p_fob:,.0f}" if p_fob else "—",
            f"FOB {p2y}":           f"$ {p2_fob:,.0f}" if p2_fob else "—",
            f"vs {py}":             f"{chg_py:+.1f}%" if chg_py is not None else "—",
            f"vs {p2y}":            f"{chg_p2:+.1f}%" if chg_p2 is not None else "—",
            "Status":               st,
        })

    country_rows.sort(key=lambda x: safe_float(x[f"FOB {cy}"].replace("$","").replace(",","")) if isinstance(x[f"FOB {cy}"],str) else 0, reverse=True)
    st.dataframe(pd.DataFrame(country_rows), use_container_width=True, hide_index=True)

    div()

    # ── Customer × Country breakdown ──────────────────────────────────────────
    section_title(f"Customer Performance by Country · {scope_lbl}")
    note_box(
        "Each country shows all customers active in any of the selected years. "
        "Status compares current year FOB vs prior year. "
        "Use this to identify where commercial attention is needed.",
        "#8B3A3A")

    # Build customer × country × year aggregation
    ccy = (
        dff.groupby(["country","customer_name","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"), units=("total_quantity","sum"))
        .reset_index()
    )

    # Sort countries by current-year FOB
    top_cntry = (
        ccy[ccy["delivery_year"]==cur_year]
        .groupby("country")["fob"].sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    other_c = [c for c in ccy["country"].unique() if c not in top_cntry]
    ordered_countries = top_cntry + other_c

    for country in ordered_countries:
        cdf_c = ccy[ccy["country"]==country]
        if cdf_c.empty: continue

        tot_fob = safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
        tot_shp = safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())

        with st.expander(f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f} FOB  ({cy})", expanded=False):
            piv_c_fob  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="fob",   aggfunc="sum").reset_index()
            piv_c_shp  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="ships", aggfunc="sum").reset_index()
            piv_c_unit = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="units", aggfunc="sum").reset_index()

            cust_rows = []
            for _, r in piv_c_fob.iterrows():
                cname  = r["customer_name"]
                cf     = safe_float(r.get(cur_year, 0))
                pf     = safe_float(r.get(prev_year,  0))
                p2f    = safe_float(r.get(prev2_year, 0))
                cs     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, cur_year))
                ps     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, prev_year))
                cu     = safe_int(safe_pivot_val(piv_c_unit, "customer_name", cname, cur_year))
                chg    = pct_change(cf, pf)
                chg2   = pct_change(cf, p2f)
                sbadge = status_badge(chg, cf)

                cust_rows.append({
                    "Customer":       cname,
                    f"FOB {cy}":      f"$ {cf:,.0f}",
                    f"FOB {py}":      f"$ {pf:,.0f}" if pf else "—",
                    f"FOB {p2y}":     f"$ {p2f:,.0f}" if p2f else "—",
                    f"vs {py}":       f"{chg:+.1f}%"  if chg  is not None else "—",
                    f"vs {p2y}":      f"{chg2:+.1f}%" if chg2 is not None else "—",
                    f"Ships {cy}":    cs,
                    f"Ships {py}":    ps or "—",
                    f"Units {cy}":    f"{cu:,}",
                    "Status":         sbadge,
                })

            cust_rows.sort(key=lambda x: safe_float(x[f"FOB {cy}"].replace("$","").replace(",","").strip()) if isinstance(x[f"FOB {cy}"],str) else 0, reverse=True)

            if cust_rows:
                st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)

                # Mini bar chart: top customers this year
                cdf_cur = cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob", ascending=False).head(12)
                if not cdf_cur.empty:
                    fig_mini = px.bar(
                        cdf_cur, x="customer_name", y="fob",
                        labels={"customer_name":"","fob":"FOB (USD)"},
                        color_discrete_sequence=["#8B3A3A"],
                    )
                    fig_mini.update_layout(
                        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                        font_family="Jost", font_color="#1E1E1E",
                        margin=dict(l=0,r=0,t=6,b=0),
                        height=220,
                        yaxis=dict(tickprefix="$ ", gridcolor="#F0EDE8", zeroline=False),
                        xaxis=dict(gridcolor="#F0EDE8", tickangle=-25),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_mini, use_container_width=True)

    div()

    # ── Growth focus panel ────────────────────────────────────────────────────
    section_title("Growth Opportunity Focus")

    decline = [r for r in country_rows if "Declining" in r["Status"] or "At risk" in r["Status"] or "Lost" in r["Status"]]
    growing = [r for r in country_rows if "Growing"   in r["Status"] or "Strong"  in r["Status"]]
    new_mkt = [r for r in country_rows if "New"       in r["Status"]]

    g1, g2, g3 = st.columns(3)
    def focus_list(col, label, color, items, fob_key):
        col.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:{color};margin-bottom:8px;">{label}</div>', unsafe_allow_html=True)
        if not items:
            col.caption("None")
            return
        for r in items:
            chg = r.get(f"vs {py}", "—")
            col.markdown(f'<div style="font-size:.84rem;padding:5px 0;border-bottom:1px solid #F0EDE8;color:#1E1E1E;">{r["Country"]}<span style="float:right;color:{color};font-size:.78rem;">{chg}</span></div>', unsafe_allow_html=True)

    focus_list(g1, "⚠ Needs attention", "#8B3A3A", decline, f"FOB {cy}")
    focus_list(g2, "✓ Growing markets",  "#7A9E8E", growing, f"FOB {cy}")
    focus_list(g3, "✦ New markets",      "#C4974A", new_mkt, f"FOB {cy}")

# ════════════════════════════════════════════════════════════════════════════
# LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
def render_by_destination(df, accent, dl_key):
    if df.empty:
        st.info("No shipments found for this period.")
        return
    for country in sorted(df["country"].unique()):
        cdf = df[df["country"]==country]
        airports = sorted(cdf["iata_code"].dropna().unique())
        n_s  = n_shipments(cdf)
        fob_t= safe_float(cdf["total_price"].sum())
        country_header(country, n_s, fob_t, accent)
        for airport in airports:
            adf    = cdf[cdf["iata_code"]==airport]
            n_sa   = n_shipments(adf)
            n_prod = len(adf)
            units  = safe_int(adf["total_quantity"].sum())
            fob_a  = safe_float(adf["total_price"].sum())
            with st.expander(f"✈  {airport}  —  {n_sa} shipment{'s' if n_sa!=1 else ''}  ·  {n_prod} lines  ·  {units:,} units  ·  $ {fob_a:,.0f}", expanded=(n_s==1)):
                for sid, sdf in adf.groupby("shipment_id", sort=False):
                    customer = sdf["customer_name"].iloc[0]
                    origin   = sdf["supply_source_name"].iloc[0]
                    shipment_card(customer, origin, len(sdf), safe_int(sdf["total_quantity"].sum()), safe_float(sdf["total_price"].sum()), accent)
                    line_cols = [c for c in ["crop_name","variety_name","product","total_quantity","total_price","order_type"] if c in sdf.columns]
                    line_df = sdf[line_cols].copy()
                    line_df.columns = [c.replace("_"," ").title() for c in line_df.columns]
                    if "Total Price"    in line_df.columns: line_df["Total Price"]    = line_df["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                    if "Total Quantity" in line_df.columns: line_df["Total Quantity"] = line_df["Total Quantity"].apply(lambda x: f"{int(x):,}")
                    st.dataframe(line_df, use_container_width=True, hide_index=True)
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇  Export to Excel", data=buf.getvalue(),
        file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{dl_key}")

def render_logistics(df_all):
    import plotly.graph_objects as go
    today    = date.today()
    iso      = today.isocalendar()
    cur_year, cur_week = iso[0], iso[1]

    VIEWS = [
        (-1,"Past Week",    "Quality Follow-up",    "#8B3A3A",
         "The logistics team must contact the customer to confirm receipt and quality. "
         "If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
        ( 0,"Current Week", "Arrival Monitoring",   "#7A9E8E",
         "Confirm material has arrived at destination. "
         "Send all final documents including the <strong>final commercial invoice</strong>."),
        ( 1,"Week +1",      "Dispatch Closure",     "#C4974A",
         "Coordinate dispatch closure with customs agents. "
         "<em>If documentation is incomplete, shipments may be delayed with prior <strong>Sales Manager approval</strong>.</em>"),
        ( 2,"Week +2",      "Document Review",      "#4A6B8A",
         "Review draft documents with customs agents: AWB, phytosanitary certificate, "
         "commercial invoice, packing list, and certificate of origin."),
        ( 3,"Week +3",      "Advance Preview",      "#6B4A8A",
         "Verify special requirements: Colombia → certificate of origin; "
         "Brazil &amp; Costa Rica → import permit. Ask customers about last-minute additions."),
    ]

    week_dfs = [filter_week(df_all, *add_weeks(cur_year, cur_week, d)) for d,*_ in VIEWS]

    page_title(
        "Logistics Dashboard",
        f"ISO Week {cur_week}  ·  {today.strftime('%B %d, %Y')}  ·  Air Freight Operations"
    )

    tab_labels = ["Overview"] + [f"{v[1]}" for v in VIEWS]
    all_tabs   = st.tabs(tab_labels)

    # Overview
    with all_tabs[0]:
        all_5w = pd.concat(week_dfs, ignore_index=True) if any(not d.empty for d in week_dfs) else pd.DataFrame()

        section_title("Five-Week Rolling Summary")
        n_s = n_shipments(all_5w) if not all_5w.empty else 0
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Shipments",     f"{n_s:,}")
        c2.metric("Product Lines", f"{len(all_5w):,}")
        c3.metric("Total Units",   f"{safe_int(all_5w['total_quantity'].sum() if not all_5w.empty else 0):,}")
        c4.metric("FOB Value",     f"$ {safe_float(all_5w['total_price'].sum() if not all_5w.empty else 0):,.0f}")
        c5.metric("Destinations",  f"{all_5w['country'].nunique() if not all_5w.empty else 0:,}")

        div()
        section_title("Weekly Breakdown")
        rows = []
        for i,(delta,wt,vt,accent,_) in enumerate(VIEWS):
            vy,vw = add_weeks(cur_year,cur_week,delta)
            wdf   = week_dfs[i]
            lbl   = "Past" if delta==-1 else ("Current" if delta==0 else f"+{delta}w")
            rows.append({
                "Period":        f"{lbl} · {week_label(vy,vw)}",
                "Stage":         vt,
                "Shipments":     n_shipments(wdf) if not wdf.empty else 0,
                "Lines":         len(wdf),
                "Units":         f"{safe_int(wdf['total_quantity'].sum()):,}",
                "FOB (USD)":     f"$ {safe_float(wdf['total_price'].sum()):,.0f}",
                "Countries":     wdf["country"].nunique() if not wdf.empty else 0,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        if not all_5w.empty:
            div()
            section_title("Destination Breakdown")
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

    # Individual week tabs
    for tab,(delta,wt,vt,accent,msg),wdf in zip(all_tabs[1:],VIEWS,week_dfs):
        with tab:
            vy,vw = add_weeks(cur_year,cur_week,delta)
            n_s   = n_shipments(wdf) if not wdf.empty else 0

            section_title(f"{wt} — {vt}", accent)
            st.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#9A9A9A;margin-bottom:12px;">{week_label(vy,vw)}</div>', unsafe_allow_html=True)
            note_box(msg, accent)

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Shipments",     f"{n_s:,}")
            c2.metric("Product Lines", f"{len(wdf):,}")
            c3.metric("Total Units",   f"{safe_int(wdf['total_quantity'].sum()):,}")
            c4.metric("FOB Value",     f"$ {safe_float(wdf['total_price'].sum()):,.0f}")
            c5.metric("Destinations",  f"{wdf['country'].nunique() if not wdf.empty else 0:,}")

            div()
            section_title("Shipments by Destination", accent)
            render_by_destination(wdf, accent, dl_key=f"{delta}_{vw}_{vy}")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 0 8px 0;">
      <div style="font-family:\'Cormorant Garamond\',serif;font-size:1.5rem;font-weight:400;
                  color:#1E1E1E;letter-spacing:.02em;">✦ Export Ops</div>
      <div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;
                  text-transform:uppercase;color:#9A9A9A;margin-top:2px;">Management Suite</div>
    </div>
    <div style="border-top:1px solid #E8E4DC;margin:12px 0 16px 0;"></div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#9A9A9A;margin-bottom:6px;">Navigation</p>', unsafe_allow_html=True)
    page = st.radio("page", ["📦  Logistics", "📈  Commercial Intelligence"],
                    label_visibility="collapsed", key="page_selector")

    st.markdown('<div style="border-top:1px solid #E8E4DC;margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#9A9A9A;margin-bottom:6px;">Data Source</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"], label_visibility="collapsed")

    if "df" in st.session_state and st.session_state.df is not None:
        st.markdown(f"""
        <div style="background:#FAFAF8;border:1px solid #E8E4DC;padding:12px 14px;margin-top:8px;
                    font-family:Jost,sans-serif;font-size:.75rem;color:#5A5A5A;line-height:1.9;">
          <span style="color:#C4974A;">●</span> {st.session_state.filename}<br>
          <span style="color:#9A9A9A;">Updated</span>  {st.session_state.loaded_at}<br>
          <span style="color:#9A9A9A;">Records</span>  {len(st.session_state.df):,}
        </div>""", unsafe_allow_html=True)

        if page == "📦  Logistics":
            st.markdown('<div style="border-top:1px solid #E8E4DC;margin:16px 0;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#9A9A9A;margin-bottom:6px;">Filters</p>', unsafe_allow_html=True)
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

# ── Welcome ───────────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state.df is None:
    st.markdown("""
    <div style="max-width:680px;margin:80px auto;text-align:center;padding:0 20px;">
      <div style="font-family:\'Cormorant Garamond\',serif;font-size:3rem;font-weight:300;
                  color:#1E1E1E;letter-spacing:.02em;line-height:1.2;margin-bottom:8px;">
        Export Operations Suite
      </div>
      <div style="font-family:Jost,sans-serif;font-size:.75rem;letter-spacing:.18em;text-transform:uppercase;
                  color:#9A9A9A;margin-bottom:40px;">
        Fresh Flowers &amp; Vegetables · Air Freight
      </div>
      <div style="border-top:1px solid #E8E4DC;padding-top:32px;">
        <div style="font-family:Jost,sans-serif;font-size:.9rem;color:#5A5A5A;line-height:1.9;margin-bottom:28px;">
          Upload your weekly Excel file using the <strong>sidebar uploader</strong>.<br>
          Navigate between <strong>Logistics</strong> and <strong>Commercial Intelligence</strong>.
        </div>
        <div style="background:#FAFAF8;border:1px solid #E8E4DC;border-top:2px solid #8B3A3A;
                    padding:20px 28px;text-align:left;">
          <div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
                      color:#8B3A3A;margin-bottom:12px;">Required columns</div>
          <div style="font-family:Jost,sans-serif;font-size:.82rem;color:#5A5A5A;line-height:2;">
            delivery_year · delivery_week · customer_name<br>
            supply_source_name · destination · total_quantity · total_price
          </div>
          <div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
                      color:#9A9A9A;margin:16px 0 8px 0;">Optional columns</div>
          <div style="font-family:Jost,sans-serif;font-size:.82rem;color:#9A9A9A;line-height:2;">
            secondary_customer_name · crop_name · variety_name · order_type · product
          </div>
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
