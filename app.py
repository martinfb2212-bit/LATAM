import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Dashboard · Export Operations",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS via components (avoids markdown rendering bug) ─────────────────
import streamlit.components.v1 as components

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Jost:wght@300;400;500;600&display=swap');

:root {
  --ivory:    #FAF7F2;
  --burgundy: #9C4A52;
  --sage:     #8A9E85;
  --gold:     #B8974A;
  --charcoal: #2C2825;
  --cream:    #EDE8E0;
  --white:    #FFFFFF;
}

html, body, [class*="css"] {
  font-family: 'Jost', sans-serif !important;
  background-color: var(--ivory) !important;
  color: var(--charcoal) !important;
}

section[data-testid="stSidebar"] {
  background-color: var(--charcoal) !important;
}
section[data-testid="stSidebar"] * {
  color: var(--ivory) !important;
}
section[data-testid="stSidebar"] label {
  color: var(--cream) !important;
  font-family: 'Jost', sans-serif !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

[data-testid="metric-container"] {
  background: var(--white) !important;
  border: 1px solid var(--cream) !important;
  border-left: 3px solid var(--burgundy) !important;
  border-radius: 6px !important;
  padding: 16px 20px !important;
}
[data-testid="metric-container"] label {
  font-family: 'Jost', sans-serif !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--burgundy) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2rem !important;
  font-weight: 600 !important;
  color: var(--charcoal) !important;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--cream) !important;
  border-radius: 6px !important;
}

.stButton > button {
  background-color: var(--burgundy) !important;
  color: var(--ivory) !important;
  border: none !important;
  font-family: 'Jost', sans-serif !important;
  letter-spacing: 0.08em !important;
  border-radius: 4px !important;
}
.stButton > button:hover {
  background-color: var(--gold) !important;
}

.stAlert {
  border-left: 3px solid var(--sage) !important;
  background: var(--white) !important;
  font-family: 'Jost', sans-serif !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: var(--white) !important;
  border-bottom: 2px solid var(--cream) !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Jost', sans-serif !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  color: var(--charcoal) !important;
}
.stTabs [aria-selected="true"] {
  border-bottom: 2px solid var(--burgundy) !important;
  color: var(--burgundy) !important;
}

[data-testid="stFileUploader"] {
  border: 1px dashed var(--burgundy) !important;
  border-radius: 6px !important;
  padding: 8px !important;
}
</style>
"""

# Inject via a zero-height iframe — always renders, never shows as text
components.html(CSS, height=0)

# ── IATA → Country ────────────────────────────────────────────────────────────
IATA_COUNTRY = {
    "JFK":"United States","MIA":"United States","LAX":"United States","ORD":"United States",
    "ATL":"United States","BOS":"United States","DFW":"United States","SFO":"United States",
    "EWR":"United States","IAD":"United States","SEA":"United States","PHL":"United States",
    "YYZ":"Canada","YVR":"Canada","YUL":"Canada","YYC":"Canada",
    "MEX":"Mexico","GDL":"Mexico","MTY":"Mexico",
    "AMS":"Netherlands","LHR":"United Kingdom","CDG":"France","FRA":"Germany",
    "MUC":"Germany","MAD":"Spain","BCN":"Spain","FCO":"Italy","MXP":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland","VIE":"Austria","BRU":"Belgium",
    "CPH":"Denmark","ARN":"Sweden","OSL":"Norway","HEL":"Finland",
    "LIS":"Portugal","ATH":"Greece","WAW":"Poland","PRG":"Czech Republic",
    "BUD":"Hungary","ZAG":"Croatia","SOF":"Bulgaria","OTP":"Romania",
    "DXB":"United Arab Emirates","AUH":"United Arab Emirates","DOH":"Qatar",
    "KWI":"Kuwait","BAH":"Bahrain","CAI":"Egypt","NBO":"Kenya","JNB":"South Africa",
    "ADD":"Ethiopia","LOS":"Nigeria","CMN":"Morocco","TUN":"Tunisia",
    "HKG":"Hong Kong","SIN":"Singapore","NRT":"Japan","KIX":"Japan","ICN":"South Korea",
    "PEK":"China","PVG":"China","CAN":"China","BKK":"Thailand","KUL":"Malaysia",
    "CGK":"Indonesia","MNL":"Philippines","SYD":"Australia","MEL":"Australia",
    "AKL":"New Zealand","BOM":"India","DEL":"India",
    "GRU":"Brazil","GIG":"Brazil","BOG":"Colombia","MDE":"Colombia","UIO":"Ecuador",
    "GYE":"Ecuador","LIM":"Peru","SCL":"Chile","EZE":"Argentina","MVD":"Uruguay",
    "ASU":"Paraguay","VCP":"Brazil","CTG":"Colombia",
    "MBJ":"Jamaica","NAS":"Bahamas","PUJ":"Dominican Republic","SDQ":"Dominican Republic",
    "SJU":"Puerto Rico","HAV":"Cuba","BZE":"Belize","PTY":"Panama",
}

REQUIRED_COLS = [
    "delivery_year","delivery_week","customer_name",
    "supply_source_name","destination","total_quantity","total_price"
]

DISPLAY_COLS_MAP = {
    "customer_name":           "Customer",
    "secondary_customer_name": "Secondary Customer",
    "supply_source_name":      "Origin",
    "destination":             "Dest. Airport",
    "country":                 "Country",
    "crop_name":               "Crop",
    "variety_name":            "Variety",
    "total_quantity":          "Qty",
    "total_price":             "FOB Total (USD)",
    "order_type":              "Order Type",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def ornament():
    st.markdown(
        '<div style="text-align:center;color:#B8974A;letter-spacing:.4em;'
        'margin:18px 0;font-size:.85rem;">✦ ─────── ✦ ─────── ✦</div>',
        unsafe_allow_html=True,
    )

def hero(title, subtitle, color="#9C4A52"):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color} 0%,#2C2825 100%);
                border-radius:8px;padding:32px 36px;margin-bottom:24px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;
                  font-weight:600;color:#FAF7F2;letter-spacing:.04em;">{title}</div>
      <div style="font-family:'Jost',sans-serif;font-size:.85rem;color:#EDE8E0;
                  letter-spacing:.12em;text-transform:uppercase;margin-top:6px;">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

def section_card(label, accent="#9C4A52"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid {accent};
                border-radius:6px;padding:14px 20px;margin:12px 0 4px 0;">
      <span style="font-family:'Jost',sans-serif;font-size:.72rem;letter-spacing:.12em;
                   text-transform:uppercase;color:{accent};">{label}</span>
    </div>""", unsafe_allow_html=True)

def alert_card(msg, accent="#8A9E85"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid {accent};
                border-radius:6px;padding:14px 20px;margin:8px 0 16px 0;
                font-family:'Jost',sans-serif;font-size:.84rem;color:#2C2825;line-height:1.7;">
      {msg}
    </div>""", unsafe_allow_html=True)

def metrics_row(orders, qty, fob):
    c1, c2, c3 = st.columns(3)
    c1.metric("Orders", f"{orders:,}")
    c2.metric("Total Qty", f"{int(qty):,}")
    c3.metric("FOB Value", f"$ {fob:,.2f}")

def build_display_df(df):
    cols = [c for c in DISPLAY_COLS_MAP if c in df.columns]
    out = df[cols].copy()
    out.rename(columns={c: DISPLAY_COLS_MAP[c] for c in cols}, inplace=True)
    if "FOB Total (USD)" in out.columns:
        out["FOB Total (USD)"] = out["FOB Total (USD)"].apply(lambda x: f"$ {x:,.2f}")
    return out

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
    df["country"]        = df["destination"].str.upper().map(IATA_COUNTRY).fillna("Unknown")
    return df, ""

def filter_week(df, year, week):
    return df[(df["delivery_year"] == year) & (df["delivery_week"] == week)]

def week_label(y, w):
    try:
        d = date.fromisocalendar(y, w, 1)
        return d.strftime(f"Week {w} · %b %d, {y}")
    except Exception:
        return f"Week {w} / {y}"

def apply_filters(df, origins, customers):
    if origins:
        df = df[df["supply_source_name"].isin(origins)]
    if customers:
        df = df[df["customer_name"].isin(customers)]
    return df

def add_weeks(year, week, delta):
    import datetime as dt
    d = date.fromisocalendar(year, week, 1) + dt.timedelta(weeks=delta)
    iso = d.isocalendar()
    return iso[0], iso[1]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;
                font-weight:600;color:#FAF7F2;padding:10px 0 2px 0;letter-spacing:.04em;">
      ✦ Export Ops
    </div>
    <div style="font-family:'Jost',sans-serif;font-size:.7rem;letter-spacing:.14em;
                text-transform:uppercase;color:#8A9E85;margin-bottom:18px;">
      Logistics Dashboard
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#B8974A;">📂 Data Source</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"], label_visibility="collapsed")

    if "df" in st.session_state and st.session_state.df is not None:
        st.markdown(f"""
        <div style="background:#3a3330;border-radius:6px;padding:12px 14px;margin-top:8px;
                    font-family:'Jost',sans-serif;font-size:.75rem;color:#EDE8E0;line-height:1.8;">
          <span style="color:#B8974A;">📄</span> {st.session_state.filename}<br>
          <span style="color:#8A9E85;">Updated:</span> {st.session_state.loaded_at}<br>
          <span style="color:#8A9E85;">Records:</span> {len(st.session_state.df):,}
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#B8974A;">Filters</p>', unsafe_allow_html=True)
        origins   = st.multiselect("Origin",   sorted(st.session_state.df["supply_source_name"].dropna().unique()), placeholder="All origins")
        customers = st.multiselect("Customer", sorted(st.session_state.df["customer_name"].dropna().unique()),       placeholder="All customers")
        st.session_state.origins   = origins
        st.session_state.customers = customers

# ── Process upload ────────────────────────────────────────────────────────────
if uploaded is not None:
    df_new, err = load_and_validate(uploaded)
    if err:
        st.error(f"⚠️ {err}")
        st.stop()
    else:
        st.session_state.df        = df_new
        st.session_state.filename  = uploaded.name
        st.session_state.loaded_at = datetime.now().strftime("%b %d, %Y  %H:%M")
        if "origins"   not in st.session_state: st.session_state.origins   = []
        if "customers" not in st.session_state: st.session_state.customers = []

# ── Welcome screen ────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state.df is None:
    hero("Export Logistics Dashboard", "Fresh Flowers & Vegetables · Air Freight Operations")
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-radius:8px;
                padding:36px 42px;max-width:700px;margin:0 auto;text-align:center;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;
                  color:#9C4A52;margin-bottom:10px;">Upload your data file to begin</div>
      <div style="font-family:'Jost',sans-serif;font-size:.84rem;color:#2C2825;
                  line-height:1.9;margin-bottom:22px;">
        Use the <strong>sidebar uploader</strong> to load your weekly Excel export.<br>
        The dashboard refreshes automatically each time you upload a new file.
      </div>
      <div style="background:#FAF7F2;border-radius:6px;padding:16px 22px;
                  font-family:'Jost',sans-serif;font-size:.78rem;color:#2C2825;
                  text-align:left;line-height:2;">
        <strong style="color:#B8974A;">Required columns</strong><br>
        delivery_year · delivery_week · customer_name · supply_source_name<br>
        destination · total_quantity · total_price<br><br>
        <strong style="color:#8A9E85;">Optional columns</strong><br>
        secondary_customer_name · crop_name · variety_name · order_type · product · Total_Unit_Price
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Main dashboard ────────────────────────────────────────────────────────────
df     = st.session_state.df.copy()
df     = apply_filters(df, st.session_state.get("origins",[]), st.session_state.get("customers",[]))
today  = date.today()
iso    = today.isocalendar()
cur_year, cur_week = iso[0], iso[1]

hero(
    "Export Logistics Dashboard",
    f"ISO Week {cur_week} · {today.strftime('%B %d, %Y')} · Air Freight Operations",
)

VIEWS = [
    (-1, "Past Week",    "Quality Follow-up",       "#9C4A52",
     "The logistics team must contact the customer to confirm receipt and material quality. "
     "If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
    ( 0, "Current Week", "Arrival Monitoring",      "#8A9E85",
     "Confirm with the customer that material has arrived at destination. "
     "Send all final documents including the <strong>final commercial invoice</strong>."),
    ( 1, "Week +1",      "Dispatch Closure",        "#B8974A",
     "Coordinate dispatch closure with customs agents. "
     "<em>Note: if documentation has not been fully reviewed between client and origin, "
     "shipments may be delayed one week with prior <strong>Sales Manager approval</strong>.</em>"),
    ( 2, "Week +2",      "Document Review",         "#9C4A52",
     "Review draft documents with customs agents: AWB, phytosanitary certificate, "
     "commercial invoice, packing list, and certificate of origin."),
    ( 3, "Week +3",      "Advance Order Preview",   "#8A9E85",
     "Verify special requirements by origin: Colombia → certificate of origin; "
     "Brazil &amp; Costa Rica → import permit. "
     "Ask the customer if they wish to add a last-minute order based on availability per origin."),
]

tabs = st.tabs([f"{v[1]}  ·  {v[2]}" for v in VIEWS])

for tab, (delta, week_title, view_title, accent, msg) in zip(tabs, VIEWS):
    with tab:
        vy, vw = add_weeks(cur_year, cur_week, delta)
        wdf    = filter_week(df, vy, vw)

        ornament()
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;
                    font-weight:600;color:{accent};margin-bottom:2px;">
          {week_title} — {view_title}
        </div>
        <div style="font-family:'Jost',sans-serif;font-size:.74rem;letter-spacing:.12em;
                    text-transform:uppercase;color:#8A9E85;margin-bottom:12px;">
          {week_label(vy, vw)}
        </div>""", unsafe_allow_html=True)

        alert_card(msg, accent)
        metrics_row(len(wdf), wdf["total_quantity"].sum(), wdf["total_price"].sum())
        ornament()
        section_card("Order Detail", accent)

        if wdf.empty:
            st.info("No orders found for this period with the current filters.")
        else:
            st.dataframe(build_display_df(wdf), use_container_width=True, hide_index=True)

            buf = io.BytesIO()
            wdf.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                label=f"⬇  Export {week_title} to Excel",
                data=buf.getvalue(),
                file_name=f"logistics_{week_title.lower().replace(' ','_')}_w{vw}_{vy}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_{delta}",
            )
