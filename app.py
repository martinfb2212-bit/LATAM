import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import streamlit.components.v1 as components

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Dashboard · Export Operations",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Jost:wght@300;400;500;600&display=swap');
:root{--ivory:#FAF7F2;--burgundy:#9C4A52;--sage:#8A9E85;--gold:#B8974A;--charcoal:#2C2825;--cream:#EDE8E0;--white:#FFFFFF;}
html,body,[class*="css"]{font-family:'Jost',sans-serif!important;background-color:var(--ivory)!important;color:var(--charcoal)!important;}
section[data-testid="stSidebar"]{background-color:var(--charcoal)!important;}
section[data-testid="stSidebar"] *{color:var(--ivory)!important;}
section[data-testid="stSidebar"] label{color:var(--cream)!important;font-family:'Jost',sans-serif!important;font-size:.78rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;}
[data-testid="metric-container"]{background:var(--white)!important;border:1px solid var(--cream)!important;border-left:3px solid var(--burgundy)!important;border-radius:6px!important;padding:16px 20px!important;}
[data-testid="metric-container"] label{font-family:'Jost',sans-serif!important;font-size:.72rem!important;letter-spacing:.1em!important;text-transform:uppercase!important;color:var(--burgundy)!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{font-family:'Cormorant Garamond',serif!important;font-size:2rem!important;font-weight:600!important;color:var(--charcoal)!important;}
[data-testid="stDataFrame"]{border:1px solid var(--cream)!important;border-radius:6px!important;}
.stButton>button{background-color:var(--burgundy)!important;color:var(--ivory)!important;border:none!important;font-family:'Jost',sans-serif!important;letter-spacing:.08em!important;border-radius:4px!important;}
.stButton>button:hover{background-color:var(--gold)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--white)!important;border-bottom:2px solid var(--cream)!important;}
.stTabs [data-baseweb="tab"]{font-family:'Jost',sans-serif!important;font-size:.75rem!important;letter-spacing:.07em!important;text-transform:uppercase!important;color:var(--charcoal)!important;}
.stTabs [aria-selected="true"]{border-bottom:2px solid var(--burgundy)!important;color:var(--burgundy)!important;}
[data-testid="stFileUploader"]{border:1px dashed var(--burgundy)!important;border-radius:6px!important;padding:8px!important;}
</style>
"""
components.html(CSS, height=0)

# ── IATA → Country ────────────────────────────────────────────────────────────
IATA_COUNTRY = {
    "JFK":"United States","MIA":"United States","LAX":"United States","ORD":"United States",
    "ATL":"United States","BOS":"United States","DFW":"United States","SFO":"United States",
    "EWR":"United States","IAD":"United States","SEA":"United States","PHL":"United States",
    "DTW":"United States","MSP":"United States","CLT":"United States","LGA":"United States",
    "MDW":"United States","BWI":"United States","SLC":"United States","DEN":"United States",
    "PDX":"United States","HOU":"United States","TPA":"United States","MCO":"United States",
    "YYZ":"Canada","YVR":"Canada","YUL":"Canada","YYC":"Canada","YEG":"Canada","YOW":"Canada",
    "MEX":"Mexico","GDL":"Mexico","MTY":"Mexico","CUN":"Mexico","TIJ":"Mexico",
    "PTY":"Panama","SJO":"Costa Rica","GUA":"Guatemala","SAL":"El Salvador",
    "BZE":"Belize","MGA":"Nicaragua","TGU":"Honduras",
    "MBJ":"Jamaica","KIN":"Jamaica","NAS":"Bahamas","PUJ":"Dominican Republic",
    "SDQ":"Dominican Republic","SJU":"Puerto Rico","HAV":"Cuba",
    "GRU":"Brazil","GIG":"Brazil","VCP":"Brazil","BSB":"Brazil","SSA":"Brazil","REC":"Brazil",
    "BOG":"Colombia","MDE":"Colombia","CTG":"Colombia","CLO":"Colombia","BAQ":"Colombia",
    "UIO":"Ecuador","GYE":"Ecuador",
    "LIM":"Peru","CUZ":"Peru","SCL":"Chile","PMC":"Chile",
    "EZE":"Argentina","AEP":"Argentina","COR":"Argentina",
    "MVD":"Uruguay","ASU":"Paraguay","LPB":"Bolivia","VVI":"Bolivia",
    "CCS":"Venezuela","MAR":"Venezuela",
    "AMS":"Netherlands","EIN":"Netherlands",
    "LHR":"United Kingdom","LGW":"United Kingdom","MAN":"United Kingdom","EDI":"United Kingdom",
    "CDG":"France","ORY":"France","NCE":"France","LYS":"France",
    "FRA":"Germany","MUC":"Germany","DUS":"Germany","HAM":"Germany","TXL":"Germany","BER":"Germany",
    "MAD":"Spain","BCN":"Spain","VLC":"Spain","AGP":"Spain","PMI":"Spain",
    "FCO":"Italy","MXP":"Italy","LIN":"Italy","NAP":"Italy","VCE":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland","BSL":"Switzerland",
    "VIE":"Austria","SZG":"Austria","BRU":"Belgium","LGG":"Belgium",
    "CPH":"Denmark","ARN":"Sweden","OSL":"Norway","HEL":"Finland",
    "LIS":"Portugal","OPO":"Portugal","ATH":"Greece","SKG":"Greece",
    "WAW":"Poland","KRK":"Poland","PRG":"Czech Republic","BUD":"Hungary",
    "ZAG":"Croatia","SOF":"Bulgaria","OTP":"Romania",
    "IST":"Turkey","SAW":"Turkey","KBP":"Ukraine",
    "DXB":"United Arab Emirates","AUH":"United Arab Emirates","SHJ":"United Arab Emirates",
    "DOH":"Qatar","BAH":"Bahrain","KWI":"Kuwait","MCT":"Oman","AMM":"Jordan",
    "TLV":"Israel","RUH":"Saudi Arabia","JED":"Saudi Arabia","DMM":"Saudi Arabia",
    "CAI":"Egypt","NBO":"Kenya","JNB":"South Africa","CPT":"South Africa",
    "ADD":"Ethiopia","KGL":"Rwanda","LOS":"Nigeria","ACC":"Ghana","CMN":"Morocco",
    "HKG":"Hong Kong","SIN":"Singapore","KUL":"Malaysia",
    "NRT":"Japan","HND":"Japan","KIX":"Japan",
    "ICN":"South Korea","PEK":"China","PVG":"China","CAN":"China",
    "TPE":"Taiwan","BKK":"Thailand","CGK":"Indonesia","DPS":"Indonesia",
    "MNL":"Philippines","SGN":"Vietnam","HAN":"Vietnam",
    "BOM":"India","DEL":"India","BLR":"India","MAA":"India",
    "SYD":"Australia","MEL":"Australia","BNE":"Australia",
    "AKL":"New Zealand",
}

COUNTRY_FLAG = {
    "United States":"🇺🇸","Canada":"🇨🇦","Mexico":"🇲🇽","Brazil":"🇧🇷","Colombia":"🇨🇴",
    "Ecuador":"🇪🇨","Peru":"🇵🇪","Chile":"🇨🇱","Argentina":"🇦🇷","Uruguay":"🇺🇾",
    "Paraguay":"🇵🇾","Bolivia":"🇧🇴","Venezuela":"🇻🇪","Panama":"🇵🇦","Costa Rica":"🇨🇷",
    "Guatemala":"🇬🇹","El Salvador":"🇸🇻","Honduras":"🇭🇳","Nicaragua":"🇳🇮","Belize":"🇧🇿",
    "Jamaica":"🇯🇲","Dominican Republic":"🇩🇴","Puerto Rico":"🇵🇷","Cuba":"🇨🇺","Bahamas":"🇧🇸",
    "Netherlands":"🇳🇱","United Kingdom":"🇬🇧","France":"🇫🇷","Germany":"🇩🇪","Spain":"🇪🇸",
    "Italy":"🇮🇹","Switzerland":"🇨🇭","Austria":"🇦🇹","Belgium":"🇧🇪","Denmark":"🇩🇰",
    "Sweden":"🇸🇪","Norway":"🇳🇴","Finland":"🇫🇮","Portugal":"🇵🇹","Greece":"🇬🇷",
    "Poland":"🇵🇱","Czech Republic":"🇨🇿","Hungary":"🇭🇺","Romania":"🇷🇴","Bulgaria":"🇧🇬",
    "Croatia":"🇭🇷","Turkey":"🇹🇷","Ukraine":"🇺🇦",
    "United Arab Emirates":"🇦🇪","Qatar":"🇶🇦","Saudi Arabia":"🇸🇦","Kuwait":"🇰🇼",
    "Bahrain":"🇧🇭","Oman":"🇴🇲","Jordan":"🇯🇴","Israel":"🇮🇱",
    "Egypt":"🇪🇬","Kenya":"🇰🇪","South Africa":"🇿🇦","Ethiopia":"🇪🇹","Nigeria":"🇳🇬",
    "Ghana":"🇬🇭","Morocco":"🇲🇦","Rwanda":"🇷🇼",
    "Japan":"🇯🇵","South Korea":"🇰🇷","China":"🇨🇳","Hong Kong":"🇭🇰","Taiwan":"🇹🇼",
    "Singapore":"🇸🇬","Thailand":"🇹🇭","Malaysia":"🇲🇾","Indonesia":"🇮🇩","Philippines":"🇵🇭",
    "Vietnam":"🇻🇳","India":"🇮🇳","Australia":"🇦🇺","New Zealand":"🇳🇿",
}

REQUIRED_COLS = [
    "delivery_year","delivery_week","customer_name",
    "supply_source_name","destination","total_quantity","total_price"
]
SHIPMENT_KEYS = ["customer_name","delivery_year","delivery_week","supply_source_name","iata_code"]

# ── Utilities ─────────────────────────────────────────────────────────────────
def flag(c): return COUNTRY_FLAG.get(c,"🌍")

def ornament():
    st.markdown('<div style="text-align:center;color:#B8974A;letter-spacing:.4em;margin:18px 0;font-size:.85rem;">✦ ─────── ✦ ─────── ✦</div>', unsafe_allow_html=True)

def hero(title, subtitle, color="#9C4A52"):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color} 0%,#2C2825 100%);
                border-radius:8px;padding:32px 36px;margin-bottom:24px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;font-weight:600;color:#FAF7F2;letter-spacing:.04em;">{title}</div>
      <div style="font-family:'Jost',sans-serif;font-size:.85rem;color:#EDE8E0;letter-spacing:.12em;text-transform:uppercase;margin-top:6px;">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

def section_hdr(label, accent="#9C4A52"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid {accent};
                border-radius:6px;padding:12px 20px;margin:16px 0 6px 0;">
      <span style="font-family:'Jost',sans-serif;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:{accent};">{label}</span>
    </div>""", unsafe_allow_html=True)

def alert_card(msg, accent="#8A9E85"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid {accent};
                border-radius:6px;padding:14px 20px;margin:8px 0 16px 0;
                font-family:'Jost',sans-serif;font-size:.84rem;color:#2C2825;line-height:1.7;">{msg}</div>""",
    unsafe_allow_html=True)

def delta_chip(val, suffix=""):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<span style="color:#8A9E85;font-size:.75rem;">— no prior data</span>'
    color = "#2d7a4f" if val >= 0 else "#9C4A52"
    arrow = "▲" if val >= 0 else "▼"
    return f'<span style="color:{color};font-size:.75rem;font-weight:500;">{arrow} {abs(val):.1f}%{suffix}</span>'

def kpi_row(shipments, products, qty, fob, destinations):
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Shipments",    f"{shipments:,}")
    c2.metric("Product Lines",f"{products:,}")
    c3.metric("Total Units",  f"{int(qty):,}")
    c4.metric("FOB Value",    f"$ {fob:,.0f}")
    c5.metric("Destinations", f"{destinations:,}")

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

def pct_change(curr, prev):
    if prev and prev != 0:
        return (curr - prev) / prev * 100
    return None

# ── Render shipments by destination ──────────────────────────────────────────
def render_by_destination(df, accent, dl_key):
    if df.empty:
        st.info("No shipments found for this period.")
        return
    for country in sorted(df["country"].unique()):
        cdf = df[df["country"]==country]
        airports = sorted(cdf["iata_code"].dropna().unique())
        n_ship = cdf.groupby(SHIPMENT_KEYS).ngroups
        fob_total = cdf["total_price"].sum()
        fl = flag(country)
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:4px solid {accent};
                    border-radius:6px;padding:10px 18px;margin:14px 0 4px 0;">
          <span style="font-size:1.3rem;">{fl}</span>
          <span style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;color:{accent};margin-left:8px;">{country}</span>
          <span style="font-family:'Jost',sans-serif;font-size:.72rem;color:#8A9E85;letter-spacing:.08em;text-transform:uppercase;margin-left:12px;">
            {n_ship} shipment{'s' if n_ship!=1 else ''} · $ {fob_total:,.0f} FOB
          </span>
        </div>""", unsafe_allow_html=True)
        for airport in airports:
            adf = cdf[cdf["iata_code"]==airport]
            n_ship_a = adf.groupby(SHIPMENT_KEYS).ngroups
            n_prods  = len(adf)
            units    = int(adf["total_quantity"].sum())
            fob      = adf["total_price"].sum()
            label = f"✈  {airport}  —  {n_ship_a} shipment{'s' if n_ship_a!=1 else ''}  ·  {n_prods} line{'s' if n_prods!=1 else ''}  ·  {units:,} units  ·  $ {fob:,.0f}"
            with st.expander(label, expanded=(n_ship==1)):
                for sid, sdf in adf.groupby("shipment_id", sort=False):
                    customer = sdf["customer_name"].iloc[0]
                    origin   = sdf["supply_source_name"].iloc[0]
                    s_units  = int(sdf["total_quantity"].sum())
                    s_fob    = sdf["total_price"].sum()
                    n_lines  = len(sdf)
                    st.markdown(f"""
                    <div style="background:#FAF7F2;border:1px solid #EDE8E0;border-radius:6px;padding:10px 16px;margin:8px 0 4px 0;">
                      <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:600;color:{accent};">📦 {customer}</span>
                      <span style="font-family:'Jost',sans-serif;font-size:.75rem;color:#8A9E85;margin-left:10px;">from {origin}</span>
                      <span style="font-family:'Jost',sans-serif;font-size:.72rem;color:#2C2825;margin-left:16px;letter-spacing:.05em;">
                        {n_lines} line{'s' if n_lines!=1 else ''} · {s_units:,} units · $ {s_fob:,.2f} FOB
                      </span>
                    </div>""", unsafe_allow_html=True)
                    line_cols = [c for c in ["crop_name","variety_name","product","total_quantity","total_price","order_type"] if c in sdf.columns]
                    line_df = sdf[line_cols].copy()
                    line_df.columns = [c.replace("_"," ").title() for c in line_df.columns]
                    if "Total Price"    in line_df.columns: line_df["Total Price"]    = line_df["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                    if "Total Quantity" in line_df.columns: line_df["Total Quantity"] = line_df["Total Quantity"].apply(lambda x: f"{int(x):,}")
                    st.dataframe(line_df, use_container_width=True, hide_index=True)
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇  Export full period to Excel", data=buf.getvalue(),
        file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{dl_key}")

# ════════════════════════════════════════════════════════════════════════════
# COMMERCIAL INTELLIGENCE PAGE
# ════════════════════════════════════════════════════════════════════════════
def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_COLORS = ["#9C4A52","#8A9E85","#B8974A","#2C2825","#C47A5A","#5A7A8A","#A8845A"]

    hero("Commercial Intelligence", "Year-over-Year Performance · Growth Analysis", color="#2C2825")

    years = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(df["country"].dropna().unique())

    # ── Filters ──────────────────────────────────────────────────────────────
    with st.expander("🔍  Filter data", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        sel_years     = fc1.multiselect("Years", years, default=years, key="ci_years")
        sel_customers = fc2.multiselect("Customers", all_customers, default=[], key="ci_customers", placeholder="All customers")
        sel_countries = fc3.multiselect("Destination countries", all_countries, default=[], key="ci_countries", placeholder="All countries")

    if not sel_years:
        st.warning("Select at least one year to continue.")
        return

    dff = df[df["delivery_year"].isin(sel_years)].copy()
    if sel_customers: dff = dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff = dff[dff["country"].isin(sel_countries)]

    if dff.empty:
        st.info("No data matches the selected filters.")
        return

    cur_year  = max(sel_years)
    prev_year = cur_year - 1

    # ── YTD vs Full-Year toggle ───────────────────────────────────────────────
    today_iso   = date.today().isocalendar()
    current_week = today_iso[1]

    ornament()
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;
                color:#2C2825;margin-bottom:6px;">Comparison Scope</div>""", unsafe_allow_html=True)

    scope_col1, scope_col2 = st.columns([2,3])
    with scope_col1:
        scope = st.radio(
            "scope", ["📅  Year-to-Date (fair comparison)", "📆  Full Year (all data in system)"],
            label_visibility="collapsed", key="ci_scope"
        )
    with scope_col2:
        if "YTD" in scope or "Year-to-Date" in scope:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid #8A9E85;
                        border-radius:6px;padding:10px 16px;font-family:'Jost',sans-serif;
                        font-size:.82rem;color:#2C2825;line-height:1.7;">
              Comparing <strong>Week 1 – Week {current_week}</strong> across all selected years.<br>
              Prior years are capped at the same week so the comparison is apples-to-apples.
            </div>""", unsafe_allow_html=True)
        else:
            max_week_cur  = int(dff[dff["delivery_year"]==cur_year]["delivery_week"].max()) if not dff[dff["delivery_year"]==cur_year].empty else current_week
            max_week_prev = int(dff[dff["delivery_year"]==prev_year]["delivery_week"].max()) if prev_year in dff["delivery_year"].values else 0
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:3px solid #B8974A;
                        border-radius:6px;padding:10px 16px;font-family:'Jost',sans-serif;
                        font-size:.82rem;color:#2C2825;line-height:1.7;">
              Comparing <strong>all weeks in the system</strong> per year.<br>
              {cur_year}: up to week {max_week_cur} &nbsp;·&nbsp;
              {prev_year}: up to week {max_week_prev if max_week_prev else "—"}
            </div>""", unsafe_allow_html=True)

    ornament()

    # Apply YTD cap if selected
    use_ytd = "YTD" in scope or "Year-to-Date" in scope
    if use_ytd:
        dff = dff[dff["delivery_week"] <= current_week]

    def shipments_in(d): return d.groupby(SHIPMENT_KEYS)["shipment_id"].nunique().sum() if not d.empty else 0

    cur_df  = dff[dff["delivery_year"]==cur_year]
    prev_df = dff[dff["delivery_year"]==prev_year] if prev_year in dff["delivery_year"].values else pd.DataFrame()

    cur_ship  = shipments_in(cur_df)
    prev_ship = shipments_in(prev_df)
    cur_fob   = cur_df["total_price"].sum()
    prev_fob  = prev_df["total_price"].sum() if not prev_df.empty else 0
    cur_units = cur_df["total_quantity"].sum()
    prev_units= prev_df["total_quantity"].sum() if not prev_df.empty else 0

    # ── YoY KPIs ──────────────────────────────────────────────────────────────
    scope_label = f"YTD W1–W{current_week}" if use_ytd else "Full Year"
    section_hdr(f"{scope_label} Summary  ·  {cur_year} vs {prev_year}", "#9C4A52")

    k1,k2,k3,k4 = st.columns(4)
    def delta_metric(col, label, cur, prev):
        delta = pct_change(cur, prev)
        delta_str = f"{delta:+.1f}%" if delta is not None else None
        col.metric(label, f"{cur:,.0f}", delta=delta_str)

    delta_metric(k1, "Shipments",    cur_ship,  prev_ship)
    delta_metric(k2, "FOB Value (USD)", cur_fob,   prev_fob)
    delta_metric(k3, "Units Shipped", cur_units, prev_units)
    k4.metric("Active Customers", cur_df["customer_name"].nunique())

    ornament()

    # ── Weekly FOB trend by year ──────────────────────────────────────────────
    section_hdr(f"Weekly FOB · Year-over-Year Trend  ({scope_label})", "#B8974A")

    weekly = (
        dff.groupby(["delivery_year","delivery_week"])
        .agg(fob=("total_price","sum"), shipments=("shipment_id","nunique"))
        .reset_index()
    )
    weekly["delivery_year"] = weekly["delivery_year"].astype(str)

    fig_trend = px.line(
        weekly, x="delivery_week", y="fob",
        color="delivery_year",
        labels={"delivery_week":"ISO Week","fob":"FOB (USD)","delivery_year":"Year"},
        color_discrete_sequence=PLOTLY_COLORS,
        markers=True,
    )
    fig_trend.update_layout(
        plot_bgcolor="#FAF7F2", paper_bgcolor="#FAF7F2",
        font_family="Jost", font_color="#2C2825",
        legend_title_text="Year",
        hovermode="x unified",
        margin=dict(l=0,r=0,t=10,b=0),
        yaxis=dict(tickprefix="$ ", gridcolor="#EDE8E0"),
        xaxis=dict(gridcolor="#EDE8E0"),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    ornament()

    # ── FOB by Country · YoY comparison ──────────────────────────────────────
    section_hdr("FOB by Destination Country · Year Comparison", "#9C4A52")

    country_year = (
        dff.groupby(["country","delivery_year"])
        .agg(fob=("total_price","sum"), shipments=("shipment_id","nunique"))
        .reset_index()
    )
    country_year["delivery_year"] = country_year["delivery_year"].astype(str)
    country_year["flag_country"]  = country_year["country"].apply(lambda c: f"{flag(c)} {c}")

    # sort countries by current year FOB descending
    top_order = (
        country_year[country_year["delivery_year"]==str(cur_year)]
        .sort_values("fob", ascending=False)["country"].tolist()
    )
    other = [c for c in country_year["country"].unique() if c not in top_order]
    order = top_order + other

    country_year["sort_key"] = country_year["country"].apply(lambda c: order.index(c) if c in order else 999)
    country_year = country_year.sort_values("sort_key")

    fig_country = px.bar(
        country_year, x="flag_country", y="fob",
        color="delivery_year", barmode="group",
        labels={"flag_country":"Country","fob":"FOB (USD)","delivery_year":"Year"},
        color_discrete_sequence=PLOTLY_COLORS,
    )
    fig_country.update_layout(
        plot_bgcolor="#FAF7F2", paper_bgcolor="#FAF7F2",
        font_family="Jost", font_color="#2C2825",
        legend_title_text="Year",
        margin=dict(l=0,r=0,t=10,b=0),
        yaxis=dict(tickprefix="$ ", gridcolor="#EDE8E0"),
        xaxis=dict(gridcolor="#EDE8E0", tickangle=-30),
    )
    st.plotly_chart(fig_country, use_container_width=True)

    ornament()

    # ── YoY comparison table by country ──────────────────────────────────────
    section_hdr("Country Performance Table · Growth Status", "#8A9E85")

    pivot_fob = country_year.pivot_table(
        index="country", columns="delivery_year", values="fob", aggfunc="sum"
    ).reset_index()
    pivot_ship = country_year.pivot_table(
        index="country", columns="delivery_year", values="shipments", aggfunc="sum"
    ).reset_index()

    cy, py = str(cur_year), str(prev_year)
    rows = []
    for _, r in pivot_fob.iterrows():
        c_fob  = r.get(cy, 0) or 0
        p_fob  = r.get(py, 0) or 0
        c_ship_row = pivot_ship[pivot_ship["country"]==r["country"]]
        c_ship = c_ship_row[cy].values[0] if (not c_ship_row.empty and cy in c_ship_row.columns) else 0
        p_ship = c_ship_row[py].values[0] if (not c_ship_row.empty and py in c_ship_row.columns) else 0

        fob_chg  = pct_change(c_fob, p_fob)
        ship_chg = pct_change(c_ship, p_ship)

        if fob_chg is None:
            status = "🆕 New"
        elif c_fob == 0:
            status = "🔴 Lost"
        elif fob_chg >= 10:
            status = "🟢 Growing"
        elif fob_chg >= -5:
            status = "🟡 Stable"
        else:
            status = "🔴 Declining"

        rows.append({
            "Country":                  f"{flag(r['country'])} {r['country']}",
            f"Shipments {cy}":          int(c_ship),
            f"Shipments {py}":          int(p_ship) if p_ship else "—",
            f"FOB {cy}":                f"$ {c_fob:,.0f}",
            f"FOB {py}":                f"$ {p_fob:,.0f}" if p_fob else "—",
            "FOB Change":               f"{fob_chg:+.1f}%" if fob_chg is not None else "—",
            "Status":                   status,
        })

    rows.sort(key=lambda x: float(x[f"FOB {cy}"].replace("$","").replace(",","")) if isinstance(x[f"FOB {cy}"], str) else 0, reverse=True)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    ornament()

    # ── Customer-level analysis ───────────────────────────────────────────────
    section_hdr("Customer Performance · Year-over-Year", "#B8974A")

    cust_year = (
        dff.groupby(["customer_name","delivery_year"])
        .agg(fob=("total_price","sum"), shipments=("shipment_id","nunique"), units=("total_quantity","sum"))
        .reset_index()
    )
    cust_year["delivery_year"] = cust_year["delivery_year"].astype(str)

    piv_cust_fob  = cust_year.pivot_table(index="customer_name", columns="delivery_year", values="fob",       aggfunc="sum").reset_index()
    piv_cust_ship = cust_year.pivot_table(index="customer_name", columns="delivery_year", values="shipments", aggfunc="sum").reset_index()
    piv_cust_unit = cust_year.pivot_table(index="customer_name", columns="delivery_year", values="units",     aggfunc="sum").reset_index()

    cust_rows = []
    for _, r in piv_cust_fob.iterrows():
        c_fob   = r.get(cy, 0) or 0
        p_fob   = r.get(py, 0) or 0
        ship_r  = piv_cust_ship[piv_cust_ship["customer_name"]==r["customer_name"]]
        unit_r  = piv_cust_unit[piv_cust_unit["customer_name"]==r["customer_name"]]
        c_ship  = ship_r[cy].values[0] if (not ship_r.empty and cy in ship_r.columns) else 0
        p_ship  = ship_r[py].values[0] if (not ship_r.empty and py in ship_r.columns) else 0
        c_units = unit_r[cy].values[0] if (not unit_r.empty and cy in unit_r.columns) else 0

        fob_chg = pct_change(c_fob, p_fob)

        # Countries served this year
        countries_cur = cur_df[cur_df["customer_name"]==r["customer_name"]]["country"].unique()
        cntry_str = ", ".join(sorted([f"{flag(c)} {c}" for c in countries_cur]))

        if fob_chg is None: status = "🆕 New"
        elif c_fob == 0:    status = "🔴 Lost"
        elif fob_chg >= 10: status = "🟢 Growing"
        elif fob_chg >= -5: status = "🟡 Stable"
        else:               status = "🔴 Declining"

        cust_rows.append({
            "Customer":           r["customer_name"],
            f"FOB {cy}":          f"$ {c_fob:,.0f}",
            f"FOB {py}":          f"$ {p_fob:,.0f}" if p_fob else "—",
            "FOB Δ":              f"{fob_chg:+.1f}%" if fob_chg is not None else "—",
            f"Ships {cy}":        int(c_ship),
            f"Ships {py}":        int(p_ship) if p_ship else "—",
            f"Units {cy}":        f"{int(c_units):,}",
            "Destinations":       cntry_str,
            "Status":             status,
        })

    cust_rows.sort(key=lambda x: float(x[f"FOB {cy}"].replace("$","").replace(",","").strip()) if isinstance(x[f"FOB {cy}"],str) else 0, reverse=True)
    st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)

    ornament()

    # ── Week-by-week heatmap: FOB per customer per week ──────────────────────
    section_hdr(f"Weekly FOB Heatmap · {cur_year} ({scope_label}) · by Customer", "#9C4A52")

    heat_df = (
        cur_df.groupby(["customer_name","delivery_week"])
        .agg(fob=("total_price","sum"))
        .reset_index()
    )
    if not heat_df.empty:
        heat_pivot = heat_df.pivot_table(index="customer_name", columns="delivery_week", values="fob", aggfunc="sum").fillna(0)
        # Top 20 customers by FOB
        top20 = heat_pivot.sum(axis=1).nlargest(20).index
        heat_pivot = heat_pivot.loc[top20]

        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_pivot.values,
            x=[f"W{int(w)}" for w in heat_pivot.columns],
            y=heat_pivot.index.tolist(),
            colorscale=[[0,"#FAF7F2"],[0.5,"#B8974A"],[1,"#9C4A52"]],
            hoverongaps=False,
            hovertemplate="Customer: %{y}<br>Week: %{x}<br>FOB: $ %{z:,.0f}<extra></extra>",
        ))
        fig_heat.update_layout(
            plot_bgcolor="#FAF7F2", paper_bgcolor="#FAF7F2",
            font_family="Jost", font_color="#2C2825",
            margin=dict(l=0,r=0,t=10,b=0),
            height=max(300, len(top20)*28),
            xaxis=dict(side="top"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    ornament()

    # ── Focus: where to grow ──────────────────────────────────────────────────
    section_hdr("Growth Opportunity Focus", "#8A9E85")
    alert_card(
        "Countries and customers marked <strong>🔴 Declining</strong> or <strong>🔴 Lost</strong> "
        "represent recovery opportunities. Those marked <strong>🆕 New</strong> indicate recent market entries to nurture. "
        "Prioritize <strong>🟡 Stable</strong> accounts with high FOB for growth activation — "
        "they have established relationships but untapped volume potential.",
        "#8A9E85"
    )

    # Declining + lost countries
    decline = [r for r in rows if "Declining" in r["Status"] or "Lost" in r["Status"]]
    growing = [r for r in rows if "Growing"   in r["Status"]]
    new_mkt = [r for r in rows if "New"       in r["Status"]]

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div style="font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#9C4A52;margin-bottom:6px;">⚠ Needs attention</div>', unsafe_allow_html=True)
        for r in decline:
            st.markdown(f'<div style="font-size:.84rem;padding:4px 0;border-bottom:1px solid #EDE8E0;">{r["Country"]} &nbsp; <span style="color:#9C4A52;">{r["FOB Change"]}</span></div>', unsafe_allow_html=True)
        if not decline: st.caption("None — great!")
    with c2:
        st.markdown('<div style="font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#2d7a4f;margin-bottom:6px;">✅ Growing markets</div>', unsafe_allow_html=True)
        for r in growing:
            st.markdown(f'<div style="font-size:.84rem;padding:4px 0;border-bottom:1px solid #EDE8E0;">{r["Country"]} &nbsp; <span style="color:#2d7a4f;">{r["FOB Change"]}</span></div>', unsafe_allow_html=True)
        if not growing: st.caption("None yet")
    with c3:
        st.markdown('<div style="font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#B8974A;margin-bottom:6px;">🆕 New markets</div>', unsafe_allow_html=True)
        for r in new_mkt:
            st.markdown(f'<div style="font-size:.84rem;padding:4px 0;border-bottom:1px solid #EDE8E0;">{r["Country"]}</div>', unsafe_allow_html=True)
        if not new_mkt: st.caption("None")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:600;
                color:#FAF7F2;padding:10px 0 2px 0;letter-spacing:.04em;">✦ Export Ops</div>
    <div style="font-family:'Jost',sans-serif;font-size:.7rem;letter-spacing:.14em;
                text-transform:uppercase;color:#8A9E85;margin-bottom:18px;">Management Suite</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # ── Page selector ─────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#B8974A;">Navigation</p>', unsafe_allow_html=True)
    page = st.radio(
        "page", ["📦  Logistics",  "📈  Commercial Intelligence"],
        label_visibility="collapsed",
        key="page_selector"
    )

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

        if page == "📦  Logistics":
            st.markdown("---")
            st.markdown('<p style="font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#B8974A;">Filters</p>', unsafe_allow_html=True)
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
    hero("Export Operations Suite", "Logistics · Commercial Intelligence · Air Freight")
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-radius:8px;
                padding:36px 42px;max-width:700px;margin:0 auto;text-align:center;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;color:#9C4A52;margin-bottom:10px;">
        Upload your data file to begin</div>
      <div style="font-family:'Jost',sans-serif;font-size:.84rem;color:#2C2825;line-height:1.9;margin-bottom:22px;">
        Use the <strong>sidebar uploader</strong> to load your weekly Excel export.<br>
        Navigate between <strong>Logistics</strong> and <strong>Commercial Intelligence</strong> using the sidebar menu.
      </div>
      <div style="background:#FAF7F2;border-radius:6px;padding:16px 22px;font-family:'Jost',sans-serif;
                  font-size:.78rem;color:#2C2825;text-align:left;line-height:2;">
        <strong style="color:#B8974A;">Required columns</strong><br>
        delivery_year · delivery_week · customer_name · supply_source_name · destination · total_quantity · total_price<br><br>
        <strong style="color:#8A9E85;">Optional columns</strong><br>
        secondary_customer_name · crop_name · variety_name · order_type · product
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ════════════════════════════════════════════════════════════════════════════

# ── COMMERCIAL INTELLIGENCE ───────────────────────────────────────────────────
if page == "📈  Commercial Intelligence":
    render_commercial(st.session_state.df.copy())
    st.stop()

# ── LOGISTICS PAGE ────────────────────────────────────────────────────────────
df_all = apply_filters(
    st.session_state.df.copy(),
    st.session_state.get("origins",[]),
    st.session_state.get("customers",[])
)
today    = date.today()
iso      = today.isocalendar()
cur_year, cur_week = iso[0], iso[1]

VIEWS = [
    (-1,"Past Week",    "Quality Follow-up",     "#9C4A52",
     "The logistics team must contact the customer to confirm receipt and material quality. "
     "If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
    ( 0,"Current Week", "Arrival Monitoring",    "#8A9E85",
     "Confirm with the customer that material has arrived at destination. "
     "Send all final documents including the <strong>final commercial invoice</strong>."),
    ( 1,"Week +1",      "Dispatch Closure",      "#B8974A",
     "Coordinate dispatch closure with customs agents. "
     "<em>If documentation has not been fully reviewed, shipments may be delayed one week "
     "with prior <strong>Sales Manager approval</strong>.</em>"),
    ( 2,"Week +2",      "Document Review",       "#9C4A52",
     "Review draft documents with customs agents: AWB, phytosanitary certificate, "
     "commercial invoice, packing list, and certificate of origin."),
    ( 3,"Week +3",      "Advance Order Preview", "#8A9E85",
     "Verify special requirements by origin: Colombia → certificate of origin; "
     "Brazil &amp; Costa Rica → import permit. "
     "Ask the customer if they wish to add a last-minute order based on availability per origin."),
]

week_dfs = [filter_week(df_all, *add_weeks(cur_year, cur_week, d)) for d,*_ in VIEWS]

hero("Export Logistics Dashboard",
     f"ISO Week {cur_week} · {today.strftime('%B %d, %Y')} · Air Freight Operations")

tab_labels = ["📊  Overview"] + [f"{v[1]}  ·  {v[2]}" for v in VIEWS]
all_tabs   = st.tabs(tab_labels)

# ── Overview tab ──────────────────────────────────────────────────────────────
with all_tabs[0]:
    ornament()
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:600;
                color:#9C4A52;margin-bottom:4px;">Global Operations Overview</div>
    <div style="font-family:'Jost',sans-serif;font-size:.74rem;letter-spacing:.12em;
                text-transform:uppercase;color:#8A9E85;margin-bottom:16px;">
      Five-week rolling window · Weeks −1 through +3</div>""", unsafe_allow_html=True)

    all_5w = pd.concat(week_dfs, ignore_index=True) if any(not d.empty for d in week_dfs) else pd.DataFrame()
    section_hdr("Rolling 5-Week Summary", "#9C4A52")
    n_ship = all_5w.groupby(SHIPMENT_KEYS).ngroups if not all_5w.empty else 0
    kpi_row(n_ship, len(all_5w),
            all_5w["total_quantity"].sum() if not all_5w.empty else 0,
            all_5w["total_price"].sum()    if not all_5w.empty else 0,
            all_5w["country"].nunique()    if not all_5w.empty else 0)
    ornament()
    section_hdr("Weekly Breakdown by Shipment", "#B8974A")
    rows = []
    for i,(delta,week_title,view_title,accent,_) in enumerate(VIEWS):
        vy,vw = add_weeks(cur_year,cur_week,delta)
        wdf   = week_dfs[i]
        label = "← Past" if delta==-1 else ("▶ Current" if delta==0 else f"+{delta}w")
        n_s   = wdf.groupby(SHIPMENT_KEYS).ngroups if not wdf.empty else 0
        rows.append({
            "Period":        f"{label}  {week_label(vy,vw)}",
            "Stage":         view_title,
            "Shipments":     n_s,
            "Product Lines": len(wdf),
            "Units":         f"{int(wdf['total_quantity'].sum()):,}",
            "FOB (USD)":     f"$ {wdf['total_price'].sum():,.0f}",
            "Destinations":  wdf["country"].nunique() if not wdf.empty else 0,
            "Countries":     ", ".join(sorted(wdf["country"].unique())) if not wdf.empty else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    ornament()
    section_hdr("Destination Breakdown · All Active Weeks", "#8A9E85")
    if not all_5w.empty:
        dest = (
            all_5w.groupby(["country","iata_code"])
            .agg(shipments=("shipment_id","nunique"), product_lines=("total_quantity","count"),
                 units=("total_quantity","sum"), fob=("total_price","sum"))
            .reset_index().sort_values(["country","fob"], ascending=[True,False])
        )
        dest["Flag + Country"] = dest["country"].map(lambda c: f"{flag(c)}  {c}")
        dest = dest.rename(columns={"iata_code":"Airport","shipments":"Shipments",
                                    "product_lines":"Product Lines","units":"Units","fob":"FOB (USD)"})
        dest["FOB (USD)"] = dest["FOB (USD)"].apply(lambda x: f"$ {x:,.0f}")
        dest["Units"]     = dest["Units"].apply(lambda x: f"{int(x):,}")
        st.dataframe(dest[["Flag + Country","Airport","Shipments","Product Lines","Units","FOB (USD)"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No data for the five-week window.")

# ── Logistics view tabs ───────────────────────────────────────────────────────
for tab,(delta,week_title,view_title,accent,msg),wdf in zip(all_tabs[1:],VIEWS,week_dfs):
    with tab:
        vy,vw  = add_weeks(cur_year,cur_week,delta)
        n_ship = wdf.groupby(SHIPMENT_KEYS).ngroups if not wdf.empty else 0
        ornament()
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:600;
                    color:{accent};margin-bottom:2px;">{week_title} — {view_title}</div>
        <div style="font-family:'Jost',sans-serif;font-size:.74rem;letter-spacing:.12em;
                    text-transform:uppercase;color:#8A9E85;margin-bottom:12px;">{week_label(vy,vw)}</div>
        """, unsafe_allow_html=True)
        alert_card(msg, accent)
        kpi_row(n_ship, len(wdf), wdf["total_quantity"].sum(), wdf["total_price"].sum(),
                wdf["country"].nunique() if not wdf.empty else 0)
        ornament()
        section_hdr("Shipments by Destination Country & Airport", accent)
        render_by_destination(wdf, accent, dl_key=f"{delta}_{vw}_{vy}")
