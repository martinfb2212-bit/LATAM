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
    "LIM":"Peru","CUZ":"Peru",
    "SCL":"Chile","PMC":"Chile",
    "EZE":"Argentina","AEP":"Argentina","COR":"Argentina",
    "MVD":"Uruguay","ASU":"Paraguay",
    "LPB":"Bolivia","VVI":"Bolivia",
    "CCS":"Venezuela","MAR":"Venezuela",
    "AMS":"Netherlands","EIN":"Netherlands",
    "LHR":"United Kingdom","LGW":"United Kingdom","MAN":"United Kingdom","EDI":"United Kingdom",
    "CDG":"France","ORY":"France","NCE":"France","LYS":"France",
    "FRA":"Germany","MUC":"Germany","DUS":"Germany","HAM":"Germany","TXL":"Germany","BER":"Germany",
    "MAD":"Spain","BCN":"Spain","VLC":"Spain","AGP":"Spain","PMI":"Spain",
    "FCO":"Italy","MXP":"Italy","LIN":"Italy","NAP":"Italy","VCE":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland","BSL":"Switzerland",
    "VIE":"Austria","SZG":"Austria",
    "BRU":"Belgium","LGG":"Belgium",
    "CPH":"Denmark","ARN":"Sweden","OSL":"Norway","HEL":"Finland","RKV":"Iceland",
    "LIS":"Portugal","OPO":"Portugal",
    "ATH":"Greece","SKG":"Greece",
    "WAW":"Poland","KRK":"Poland",
    "PRG":"Czech Republic","BRQ":"Czech Republic",
    "BUD":"Hungary","ZAG":"Croatia","SOF":"Bulgaria","OTP":"Romania",
    "VNO":"Lithuania","RIX":"Latvia","TLL":"Estonia",
    "IST":"Turkey","SAW":"Turkey","ADB":"Turkey","ESB":"Turkey",
    "KBP":"Ukraine","SVO":"Russia","LED":"Russia","DME":"Russia",
    "DXB":"United Arab Emirates","AUH":"United Arab Emirates","SHJ":"United Arab Emirates",
    "DOH":"Qatar","BAH":"Bahrain","KWI":"Kuwait","MCT":"Oman","AMM":"Jordan",
    "TLV":"Israel","BEY":"Lebanon","RUH":"Saudi Arabia","JED":"Saudi Arabia","DMM":"Saudi Arabia",
    "CAI":"Egypt","HRG":"Egypt","SSH":"Egypt",
    "NBO":"Kenya","MBA":"Kenya",
    "JNB":"South Africa","CPT":"South Africa","DUR":"South Africa",
    "ADD":"Ethiopia","DAR":"Tanzania","EBB":"Uganda","KGL":"Rwanda",
    "LOS":"Nigeria","ABV":"Nigeria","ACC":"Ghana","DKR":"Senegal",
    "CMN":"Morocco","RAK":"Morocco","TUN":"Tunisia","ALG":"Algeria",
    "HKG":"Hong Kong","MFM":"Macau",
    "SIN":"Singapore","KUL":"Malaysia","BKI":"Malaysia",
    "NRT":"Japan","HND":"Japan","KIX":"Japan","NGO":"Japan","CTS":"Japan",
    "ICN":"South Korea","GMP":"South Korea","PUS":"South Korea",
    "PEK":"China","PKX":"China","PVG":"China","CAN":"China","SZX":"China",
    "TPE":"Taiwan","KHH":"Taiwan",
    "BKK":"Thailand","DMK":"Thailand","HKT":"Thailand",
    "CGK":"Indonesia","DPS":"Indonesia","SUB":"Indonesia",
    "MNL":"Philippines","CEB":"Philippines",
    "SGN":"Vietnam","HAN":"Vietnam","DAD":"Vietnam",
    "BOM":"India","DEL":"India","BLR":"India","MAA":"India","CCU":"India","HYD":"India",
    "CMB":"Sri Lanka","DAC":"Bangladesh","KTM":"Nepal",
    "SYD":"Australia","MEL":"Australia","BNE":"Australia","PER":"Australia","ADL":"Australia",
    "AKL":"New Zealand","CHC":"New Zealand","WLG":"New Zealand",
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
    "Croatia":"🇭🇷","Serbia":"🇷🇸","Turkey":"🇹🇷","Ukraine":"🇺🇦","Russia":"🇷🇺",
    "United Arab Emirates":"🇦🇪","Qatar":"🇶🇦","Saudi Arabia":"🇸🇦","Kuwait":"🇰🇼",
    "Bahrain":"🇧🇭","Oman":"🇴🇲","Jordan":"🇯🇴","Israel":"🇮🇱","Lebanon":"🇱🇧",
    "Egypt":"🇪🇬","Kenya":"🇰🇪","South Africa":"🇿🇦","Ethiopia":"🇪🇹","Nigeria":"🇳🇬",
    "Ghana":"🇬🇭","Morocco":"🇲🇦","Tunisia":"🇹🇳","Rwanda":"🇷🇼","Uganda":"🇺🇬",
    "Japan":"🇯🇵","South Korea":"🇰🇷","China":"🇨🇳","Hong Kong":"🇭🇰","Taiwan":"🇹🇼",
    "Singapore":"🇸🇬","Thailand":"🇹🇭","Malaysia":"🇲🇾","Indonesia":"🇮🇩","Philippines":"🇵🇭",
    "Vietnam":"🇻🇳","India":"🇮🇳","Pakistan":"🇵🇰","Australia":"🇦🇺","New Zealand":"🇳🇿",
}

REQUIRED_COLS = [
    "delivery_year","delivery_week","customer_name",
    "supply_source_name","destination","total_quantity","total_price"
]

# Keys that define ONE unique shipment
SHIPMENT_KEYS = ["customer_name","delivery_year","delivery_week","supply_source_name","iata_code"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def flag(country): return COUNTRY_FLAG.get(country, "🌍")

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

def kpi_row(shipments, products, qty, fob, destinations):
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Shipments",    f"{shipments:,}")
    c2.metric("Product Lines",f"{products:,}")
    c3.metric("Total Units",  f"{int(qty):,}")
    c4.metric("FOB Value",    f"$ {fob:,.0f}")
    c5.metric("Destinations", f"{destinations:,}")

def extract_iata(series):
    """Robustly extract 3-letter IATA code from messy cell values."""
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

    # ── Assign shipment ID ────────────────────────────────────────────────────
    # A shipment is uniquely identified by: customer + year + week + origin + destination
    df["shipment_id"] = (
        df["customer_name"].astype(str) + " | " +
        df["delivery_year"].astype(str) + "-W" +
        df["delivery_week"].astype(str).str.zfill(2) + " | " +
        df["supply_source_name"].astype(str) + " → " +
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

# ── Build shipment summary table (one row per shipment) ───────────────────────
def build_shipment_summary(df):
    """Collapse product rows into one row per shipment."""
    if df.empty:
        return pd.DataFrame()

    agg = (
        df.groupby(SHIPMENT_KEYS + ["country"], as_index=False)
        .agg(
            product_lines  =("total_quantity", "count"),
            total_units    =("total_quantity", "sum"),
            total_fob      =("total_price",    "sum"),
            crops          =("crop_name",      lambda x: ", ".join(sorted(x.dropna().astype(str).unique()))),
            varieties      =("variety_name",   lambda x: ", ".join(sorted(x.dropna().astype(str).unique()))),
            order_types    =("order_type",     lambda x: ", ".join(sorted(x.dropna().astype(str).unique()))),
            secondary_cust =("secondary_customer_name", lambda x: ", ".join(sorted(set(str(v) for v in x if str(v).strip())))),
        )
        .rename(columns={
            "customer_name":      "Customer",
            "supply_source_name": "Origin",
            "iata_code":          "Airport",
            "country":            "Country",
            "product_lines":      "Product Lines",
            "total_units":        "Units",
            "total_fob":          "FOB (USD)",
            "crops":              "Crops",
            "varieties":          "Varieties",
            "order_types":        "Order Type",
            "secondary_cust":     "Secondary Customer",
            "delivery_year":      "Year",
            "delivery_week":      "Week",
        })
    )
    agg["FOB (USD)"] = agg["FOB (USD)"].apply(lambda x: f"$ {x:,.2f}")
    agg["Units"]     = agg["Units"].apply(lambda x: f"{int(x):,}")

    display_cols = [c for c in [
        "Customer","Secondary Customer","Origin","Airport","Country",
        "Crops","Varieties","Product Lines","Units","FOB (USD)","Order Type"
    ] if c in agg.columns]

    return agg[display_cols]

# ── Render shipments grouped by country → airport ─────────────────────────────
def render_by_destination(df, accent, dl_key):
    if df.empty:
        st.info("No shipments found for this period with the current filters.")
        return

    countries = sorted(df["country"].unique())

    for country in countries:
        cdf = df[df["country"] == country]
        airports = sorted(cdf["iata_code"].dropna().unique())
        n_shipments = cdf.groupby(SHIPMENT_KEYS).ngroups
        fob_total   = cdf["total_price"].sum()
        fl = flag(country)

        # Country header
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-left:4px solid {accent};
                    border-radius:6px;padding:10px 18px;margin:14px 0 4px 0;">
          <span style="font-size:1.3rem;">{fl}</span>
          <span style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;
                       color:{accent};margin-left:8px;">{country}</span>
          <span style="font-family:'Jost',sans-serif;font-size:.72rem;color:#8A9E85;
                       letter-spacing:.08em;text-transform:uppercase;margin-left:12px;">
            {n_shipments} shipment{'s' if n_shipments!=1 else ''} · $ {fob_total:,.0f} FOB
          </span>
        </div>""", unsafe_allow_html=True)

        for airport in airports:
            adf = cdf[cdf["iata_code"] == airport]

            # Count distinct shipments (not rows) for this airport
            n_ship  = adf.groupby(SHIPMENT_KEYS).ngroups
            n_prods = len(adf)
            units   = int(adf["total_quantity"].sum())
            fob     = adf["total_price"].sum()

            label = (
                f"✈  {airport}  —  "
                f"{n_ship} shipment{'s' if n_ship!=1 else ''}  ·  "
                f"{n_prods} product line{'s' if n_prods!=1 else ''}  ·  "
                f"{units:,} units  ·  $ {fob:,.0f}"
            )

            with st.expander(label, expanded=(n_shipments == 1)):
                # Group by shipment_id and show each shipment as a collapsible card
                shipment_groups = adf.groupby("shipment_id", sort=False)
                for sid, sdf in shipment_groups:
                    customer   = sdf["customer_name"].iloc[0]
                    origin     = sdf["supply_source_name"].iloc[0]
                    s_units    = int(sdf["total_quantity"].sum())
                    s_fob      = sdf["total_price"].sum()
                    n_lines    = len(sdf)

                    st.markdown(f"""
                    <div style="background:#FAF7F2;border:1px solid #EDE8E0;border-radius:6px;
                                padding:10px 16px;margin:8px 0 4px 0;">
                      <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;
                                   font-weight:600;color:{accent};">📦 {customer}</span>
                      <span style="font-family:'Jost',sans-serif;font-size:.75rem;color:#8A9E85;
                                   margin-left:10px;">from {origin}</span>
                      <span style="font-family:'Jost',sans-serif;font-size:.72rem;color:#2C2825;
                                   margin-left:16px;letter-spacing:.05em;">
                        {n_lines} line{'s' if n_lines!=1 else ''} · {s_units:,} units · $ {s_fob:,.2f} FOB
                      </span>
                    </div>""", unsafe_allow_html=True)

                    # Product lines table
                    line_cols = [c for c in [
                        "crop_name","variety_name","product","total_quantity","total_price","order_type"
                    ] if c in sdf.columns]
                    line_df = sdf[line_cols].copy()
                    line_df.columns = [c.replace("_"," ").title() for c in line_df.columns]
                    if "Total Price" in line_df.columns:
                        line_df["Total Price"] = line_df["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                    if "Total Quantity" in line_df.columns:
                        line_df["Total Quantity"] = line_df["Total Quantity"].apply(lambda x: f"{int(x):,}")
                    st.dataframe(line_df, use_container_width=True, hide_index=True)

    # Download
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button(
        label="⬇  Export full period to Excel",
        data=buf.getvalue(),
        file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{dl_key}",
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:600;
                color:#FAF7F2;padding:10px 0 2px 0;letter-spacing:.04em;">✦ Export Ops</div>
    <div style="font-family:'Jost',sans-serif;font-size:.7rem;letter-spacing:.14em;
                text-transform:uppercase;color:#8A9E85;margin-bottom:18px;">Logistics Dashboard</div>
    """, unsafe_allow_html=True)
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
    hero("Export Logistics Dashboard", "Fresh Flowers & Vegetables · Air Freight Operations")
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #EDE8E0;border-radius:8px;
                padding:36px 42px;max-width:700px;margin:0 auto;text-align:center;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;color:#9C4A52;margin-bottom:10px;">
        Upload your data file to begin</div>
      <div style="font-family:'Jost',sans-serif;font-size:.84rem;color:#2C2825;line-height:1.9;margin-bottom:22px;">
        Use the <strong>sidebar uploader</strong> to load your weekly Excel export.</div>
      <div style="background:#FAF7F2;border-radius:6px;padding:16px 22px;font-family:'Jost',sans-serif;
                  font-size:.78rem;color:#2C2825;text-align:left;line-height:2;">
        <strong style="color:#B8974A;">Required columns</strong><br>
        delivery_year · delivery_week · customer_name · supply_source_name · destination · total_quantity · total_price<br><br>
        <strong style="color:#8A9E85;">Optional columns</strong><br>
        secondary_customer_name · crop_name · variety_name · order_type · product · Total_Unit_Price
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Main setup ────────────────────────────────────────────────────────────────
df_all   = apply_filters(st.session_state.df.copy(),
                         st.session_state.get("origins",[]),
                         st.session_state.get("customers",[]))
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

week_dfs = []
for delta, *_ in VIEWS:
    vy, vw = add_weeks(cur_year, cur_week, delta)
    week_dfs.append(filter_week(df_all, vy, vw))

hero("Export Logistics Dashboard",
     f"ISO Week {cur_week} · {today.strftime('%B %d, %Y')} · Air Freight Operations")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_labels = ["📊  Overview"] + [f"{v[1]}  ·  {v[2]}" for v in VIEWS]
all_tabs   = st.tabs(tab_labels)

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW TAB
# ════════════════════════════════════════════════════════════════════════════
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
    if not all_5w.empty:
        n_ship = all_5w.groupby(SHIPMENT_KEYS).ngroups
        kpi_row(n_ship, len(all_5w),
                all_5w["total_quantity"].sum(),
                all_5w["total_price"].sum(),
                all_5w["country"].nunique())
    else:
        kpi_row(0,0,0,0,0)

    ornament()
    section_hdr("Weekly Breakdown by Shipment", "#B8974A")
    rows = []
    for i,(delta,week_title,view_title,accent,_) in enumerate(VIEWS):
        vy, vw = add_weeks(cur_year, cur_week, delta)
        wdf    = week_dfs[i]
        label  = "← Past" if delta==-1 else ("▶ Current" if delta==0 else f"+{delta}w")
        n_ship = wdf.groupby(SHIPMENT_KEYS).ngroups if not wdf.empty else 0
        rows.append({
            "Period":        f"{label}  {week_label(vy,vw)}",
            "Stage":         view_title,
            "Shipments":     n_ship,
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
            .agg(
                shipments    =("shipment_id",    "nunique"),
                product_lines=("total_quantity", "count"),
                units        =("total_quantity", "sum"),
                fob          =("total_price",    "sum"),
            )
            .reset_index()
            .sort_values(["country","fob"], ascending=[True,False])
        )
        dest["Flag + Country"] = dest["country"].map(lambda c: f"{flag(c)}  {c}")
        dest = dest.rename(columns={"iata_code":"Airport","shipments":"Shipments",
                                    "product_lines":"Product Lines","units":"Units","fob":"FOB (USD)"})
        dest["FOB (USD)"] = dest["FOB (USD)"].apply(lambda x: f"$ {x:,.0f}")
        dest["Units"]     = dest["Units"].apply(lambda x: f"{int(x):,}")
        st.dataframe(dest[["Flag + Country","Airport","Shipments","Product Lines","Units","FOB (USD)"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the five-week window.")

# ════════════════════════════════════════════════════════════════════════════
# LOGISTICS VIEWS TABS
# ════════════════════════════════════════════════════════════════════════════
for tab,(delta,week_title,view_title,accent,msg),wdf in zip(all_tabs[1:], VIEWS, week_dfs):
    with tab:
        vy, vw  = add_weeks(cur_year, cur_week, delta)
        n_ship  = wdf.groupby(SHIPMENT_KEYS).ngroups if not wdf.empty else 0
        ornament()
        st.markdown(f"""
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:600;
                    color:{accent};margin-bottom:2px;">{week_title} — {view_title}</div>
        <div style="font-family:'Jost',sans-serif;font-size:.74rem;letter-spacing:.12em;
                    text-transform:uppercase;color:#8A9E85;margin-bottom:12px;">{week_label(vy,vw)}</div>
        """, unsafe_allow_html=True)

        alert_card(msg, accent)
        kpi_row(n_ship, len(wdf),
                wdf["total_quantity"].sum(),
                wdf["total_price"].sum(),
                wdf["country"].nunique() if not wdf.empty else 0)

        ornament()
        section_hdr("Shipments by Destination Country & Airport", accent)
        render_by_destination(wdf, accent, dl_key=f"{delta}_{vw}_{vy}")
