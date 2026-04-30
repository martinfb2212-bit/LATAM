import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import json
import pathlib
import bcrypt
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Export Operations Suite",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Force light theme ─────────────────────────────────────────────────────────
components.html("""
<script>
const s = document.createElement('style');
s.textContent = `
  body, #root, .main, .block-container,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stMain"],
  [data-testid="stMainBlockContainer"] {
    background-color: #F5F2ED !important;
    color: #1A1A1A !important;
  }
`;
document.head.appendChild(s);
</script>""", height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap');

html,body,.main,.block-container,
[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],[class*="css"],.element-container {
  background-color:#F5F2ED!important;color:#1A1A1A!important;
  font-family:'Jost',sans-serif!important;
}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div,
section[data-testid="stSidebar"]>div>div { background-color:#5C1F1F!important; }
section[data-testid="stSidebar"] * { color:#F5EDE8!important; }
section[data-testid="stSidebar"] label {
  color:#D4B8B0!important;font-size:.72rem!important;
  letter-spacing:.12em!important;text-transform:uppercase!important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
  border:1px dashed rgba(212,176,168,.45)!important;border-radius:0!important;
  background:rgba(255,255,255,.05)!important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  color:#F5EDE8!important;font-size:.84rem!important;
}
[data-testid="metric-container"] {
  background:#FFFFFF!important;border:1px solid #DDD8D0!important;
  border-top:3px solid #8C3D3D!important;border-radius:0!important;padding:20px 24px!important;
}
[data-testid="metric-container"] label {
  font-family:'Jost',sans-serif!important;font-size:.65rem!important;
  letter-spacing:.18em!important;text-transform:uppercase!important;color:#7A7A7A!important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family:'Cormorant Garamond',serif!important;font-size:2.2rem!important;
  font-weight:500!important;color:#1A1A1A!important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] svg{display:none!important;}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-family:'Jost',sans-serif!important;font-size:.78rem!important;color:#1A1A1A!important;
}
[data-testid="stDataFrame"]{border:1px solid #DDD8D0!important;border-radius:0!important;}
[data-testid="stDataFrame"] *{color:#1A1A1A!important;background-color:#FFFFFF!important;}
.stButton>button {
  background-color:#8C3D3D!important;color:#FFF5F0!important;border:none!important;
  font-family:'Jost',sans-serif!important;font-size:.72rem!important;
  letter-spacing:.14em!important;text-transform:uppercase!important;
  border-radius:0!important;padding:10px 28px!important;
}
.stButton>button:hover{background-color:#5C1F1F!important;}
[data-testid="stDownloadButton"] button {
  background-color:#FFFFFF!important;color:#8C3D3D!important;
  border:1px solid #8C3D3D!important;font-family:'Jost',sans-serif!important;
  font-size:.70rem!important;letter-spacing:.14em!important;
  text-transform:uppercase!important;border-radius:0!important;padding:8px 22px!important;
}
[data-testid="stDownloadButton"] button:hover{background-color:#8C3D3D!important;color:#FFFFFF!important;}
.stTabs [data-baseweb="tab-list"]{background:#F5F2ED!important;border-bottom:1px solid #DDD8D0!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{
  font-family:'Jost',sans-serif!important;font-size:.68rem!important;
  letter-spacing:.13em!important;text-transform:uppercase!important;
  color:#7A7A7A!important;padding:12px 22px!important;
  border-bottom:2px solid transparent!important;background:transparent!important;
}
.stTabs [aria-selected="true"]{color:#8C3D3D!important;border-bottom:2px solid #8C3D3D!important;font-weight:500!important;}
.stTabs [data-baseweb="tab-panel"]{background-color:#F5F2ED!important;padding-top:20px!important;}
details,[data-testid="stExpander"]{border:1px solid #DDD8D0!important;border-radius:0!important;margin-bottom:6px!important;background:#FFFFFF!important;}
[data-testid="stExpander"] summary,details summary{
  font-family:'Jost',sans-serif!important;font-size:.78rem!important;
  color:#1A1A1A!important;background:#FFFFFF!important;padding:12px 16px!important;
}
[data-testid="stExpander"][open] summary,details[open] summary{color:#8C3D3D!important;}
[data-testid="stExpander"]>div>div{background:#FFFFFF!important;padding:0 16px 12px!important;}
.stMultiSelect [data-baseweb="tag"]{background-color:#F0EAE2!important;color:#5C1F1F!important;border-radius:0!important;}
[data-baseweb="select"]>div{background-color:#FFFFFF!important;border-color:#DDD8D0!important;color:#1A1A1A!important;}
input,textarea,[data-baseweb="input"]*{background-color:#FFFFFF!important;color:#1A1A1A!important;}
[data-testid="stRadio"]>label,[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p{color:#1A1A1A!important;}
.stAlert{border-radius:0!important;background-color:#FFF8F5!important;color:#1A1A1A!important;}
</style>
"""
components.html(CSS, height=0)

# ── Constants ─────────────────────────────────────────────────────────────────
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

REQUIRED_COLS  = ["delivery_year","delivery_week","customer_name",
                  "supply_source_name","destination","total_quantity","total_price"]
SHIPMENT_KEYS  = ["customer_name","delivery_year","delivery_week","supply_source_name","iata_code"]
EXCLUDED_COUNTRIES = {"Netherlands","Kenya","Canada"}
PALETTE = ["#8C3D3D","#2D4A3E","#B8924A","#4A6080","#6B4080","#2D6B5A","#80502D"]

DEFAULT_TARGETS_2026 = {
    "Brazil":        20.0,
    "Mexico":        25.0,
    "Costa Rica":     8.0,
    "Chile":         20.0,
    "Guatemala":     25.0,
    "Peru":          45.0,
    "United States": 20.0,
}

# ── Utility helpers ───────────────────────────────────────────────────────────
def flag(c): return COUNTRY_FLAG.get(c,"🌍")

def safe_int(v):
    try:
        f = float(v)
        return 0 if (np.isnan(f) or np.isinf(f)) else int(f)
    except: return 0

def safe_float(v):
    try:
        f = float(v)
        return 0.0 if (np.isnan(f) or np.isinf(f)) else f
    except: return 0.0

def pct_change(cur, prev):
    c,p = safe_float(cur), safe_float(prev)
    if p==0: return None
    return (c-p)/p*100

def status_badge(chg, cur_fob):
    cf = safe_float(cur_fob)
    if chg is None:  return "🆕 New"
    if cf==0:        return "⛔ Lost"
    if chg>=15:      return "🚀 Strong growth"
    if chg>=3:       return "🟢 Growing"
    if chg>=-5:      return "🟡 Stable"
    if chg>=-20:     return "🔻 Declining"
    return "🔴 At risk"

def safe_pivot_val(piv, key_col, key_val, year_col):
    row = piv[piv[key_col]==key_val]
    if row.empty or year_col not in row.columns: return 0.0
    return safe_float(row[year_col].values[0])

def metric_delta_str(cur, prev):
    ch = pct_change(cur, prev)
    return f"{ch:+.1f}%" if ch is not None else None

def n_shipments(df):
    if df.empty: return 0
    return df.groupby(SHIPMENT_KEYS)["shipment_id"].nunique().sum()

# ── UI components ─────────────────────────────────────────────────────────────
def divider():
    st.markdown('<div style="border-top:1px solid #DDD8D0;margin:32px 0;"></div>', unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding:40px 0 28px 0;border-bottom:1px solid #DDD8D0;margin-bottom:32px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;
                  color:#1A1A1A;letter-spacing:.015em;line-height:1.15;">{title}</div>
      {"<div style='font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#7A7A7A;margin-top:10px;'>"+subtitle+"</div>" if subtitle else ""}
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
    <div style="background:#FFFFFF;border-left:3px solid {accent};padding:14px 20px;
                margin:10px 0 20px 0;font-family:'Jost',sans-serif;font-size:.83rem;
                color:#1A1A1A;line-height:1.8;box-shadow:0 1px 6px rgba(26,26,26,.04);">{msg}</div>""",
    unsafe_allow_html=True)

def country_strip(country, n_ship, fob, accent="#8C3D3D"):
    fl = flag(country)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;padding:13px 20px;background:#FFFFFF;
                border-top:2px solid {accent};border-bottom:1px solid #EDE9E3;
                margin:20px 0 4px 0;box-shadow:0 2px 8px rgba(26,26,26,.04);">
      <span style="font-size:1.2rem;">{fl}</span>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:500;color:#1A1A1A;">{country}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:#7A7A7A;margin-left:6px;">
        {n_ship} shipment{"s" if n_ship!=1 else ""}
      </span>
      <span style="margin-left:auto;font-family:'Cormorant Garamond',serif;font-size:1.1rem;color:{accent};font-weight:500;">
        $ {fob:,.0f}
      </span>
    </div>""", unsafe_allow_html=True)

def shipment_row(customer, origin, n_lines, units, fob, accent):
    st.markdown(f"""
    <div style="background:#FAFAF8;border-bottom:1px solid #EDE9E3;padding:10px 18px;
                display:flex;flex-wrap:wrap;align-items:center;gap:10px;">
      <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:500;color:{accent};">📦 {customer}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.72rem;color:#7A7A7A;">from {origin}</span>
      <span style="margin-left:auto;font-family:'Jost',sans-serif;font-size:.72rem;color:#4A4A4A;">
        {n_lines} line{"s" if n_lines!=1 else ""} · {units:,} units · $ {fob:,.2f}
      </span>
    </div>""", unsafe_allow_html=True)

def plotly_layout(fig, height=None):
    fig.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        font_family="Jost", font_color="#1A1A1A", font_size=12,
        margin=dict(l=4,r=4,t=16,b=4),
        legend=dict(orientation="h",y=1.1,x=0,font=dict(size=11,color="#1A1A1A"),bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#EDE9E3",linecolor="#DDD8D0",tickcolor="#DDD8D0",tickfont=dict(color="#4A4A4A",size=11))
    fig.update_yaxes(gridcolor="#EDE9E3",linecolor="#DDD8D0",tickcolor="#DDD8D0",zeroline=False,tickfont=dict(color="#4A4A4A",size=11))
    if height: fig.update_layout(height=height)
    return fig

# ── Data helpers ──────────────────────────────────────────────────────────────
def extract_iata(series):
    s = series.astype(str).str.upper().str.strip()
    return s.str.extract(r'\b([A-Z]{3})\b',expand=False).fillna(s.str[:3])

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
        if opt not in df.columns: df[opt] = ""
    df["delivery_year"]  = pd.to_numeric(df["delivery_year"],  errors="coerce")
    df["delivery_week"]  = pd.to_numeric(df["delivery_week"],  errors="coerce")
    df["total_quantity"] = pd.to_numeric(df["total_quantity"], errors="coerce").fillna(0)
    df["total_price"]    = pd.to_numeric(df["total_price"],    errors="coerce").fillna(0)
    df["iata_code"]      = extract_iata(df["destination"])
    df["country"]        = df["iata_code"].map(IATA_COUNTRY).fillna("Unknown")
    df["shipment_id"]    = (
        df["customer_name"].astype(str)+"|"+
        df["delivery_year"].astype(str)+"-W"+
        df["delivery_week"].astype(str).str.zfill(2)+"|"+
        df["supply_source_name"].astype(str)+"→"+
        df["iata_code"].astype(str)
    )
    return df, ""

def filter_week(df, year, week):
    return df[(df["delivery_year"]==year)&(df["delivery_week"]==week)]

def add_weeks(year, week, delta):
    import datetime as dt
    d = date.fromisocalendar(year,week,1)+dt.timedelta(weeks=delta)
    iso = d.isocalendar()
    return iso[0],iso[1]

def week_label(y, w):
    try:
        d = date.fromisocalendar(y,w,1)
        return d.strftime(f"Week {w}  ·  %b %d, {y}")
    except: return f"Week {w} / {y}"

def apply_filters(df, origins, customers):
    if origins:   df = df[df["supply_source_name"].isin(origins)]
    if customers: df = df[df["customer_name"].isin(customers)]
    return df

# ════════════════════════════════════════════════════════════════════════════
# AUTH  ·  Passwords are stored as bcrypt hashes. Plaintext defaults below are
#         hashed automatically the first time each user signs in successfully,
#         so users.json on disk only ever contains hashes.
# ════════════════════════════════════════════════════════════════════════════
USERS_FILE = pathlib.Path(".streamlit/users.json")

_BUILTIN_USERS = {
    "admin":      {"password":"admin123",  "display":"Administrator","role":"admin"},
    "logistics":  {"password":"log2024",   "display":"Logistics",    "role":"user"},
    "commercial": {"password":"com2024",   "display":"Commercial",   "role":"user"},
}

def _hash_password(plain):
    """Hash a plaintext password using bcrypt (returns string)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def _is_hashed(value):
    """Detect whether a stored password is already a bcrypt hash."""
    return isinstance(value,str) and value.startswith(("$2a$","$2b$","$2y$"))

def _verify_password(plain, stored):
    """Verify a plaintext password against a stored value (hash or legacy plain)."""
    if not plain or not stored: return False
    if _is_hashed(stored):
        try: return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
        except (ValueError,TypeError): return False
    return plain==stored  # Legacy plaintext fallback (will be migrated on login)

def _get_users():
    try:
        raw = st.secrets.get("users",{})
        if raw:
            out={}
            for u,v in raw.items():
                u=str(u).strip().lower()
                if isinstance(v,str): out[u]={"password":v,"display":u.title(),"role":"user"}
                else: out[u]={"password":str(v.get("password","")),"display":str(v.get("display",u.title())),"role":str(v.get("role","user"))}
            if out: return out
    except: pass
    if USERS_FILE.exists():
        try:
            data=json.loads(USERS_FILE.read_text())
            if data: return data
        except: pass
    return dict(_BUILTIN_USERS)

def _save_users(users):
    try:
        USERS_FILE.parent.mkdir(parents=True,exist_ok=True)
        USERS_FILE.write_text(json.dumps(users,indent=2))
    except: pass

def _migrate_plaintext_to_hash(username, plain):
    """After a successful login with a legacy plaintext password, persist the
    bcrypt hash so subsequent logins are verified against the hash. No-op if
    users come from st.secrets (read-only) or already hashed."""
    try:
        users=_get_users()
        u=username.strip().lower()
        if u in users and not _is_hashed(users[u].get("password","")):
            users[u]["password"]=_hash_password(plain)
            _save_users(users)
    except Exception: pass

def check_credentials(username, password):
    if not username or not password: return False
    users=_get_users()
    u=username.strip().lower()
    if u not in users: return False
    stored=users[u].get("password","")
    if not _verify_password(password.strip(), stored): return False
    if not _is_hashed(stored):
        _migrate_plaintext_to_hash(u, password.strip())
    return True

def get_user(username):
    return _get_users().get(username.strip().lower(),{"display":username.title(),"role":"user"})

def render_login():
    components.html("""<style>
    html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],
    .main,.block-container{background-color:#F5F2ED!important;}
    </style>""",height=0)
    st.markdown("""
    <div style="text-align:center;padding:60px 0 32px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;color:#1A1A1A;letter-spacing:.02em;">✦ Export Ops</div>
      <div style="font-family:'Jost',sans-serif;font-size:.65rem;letter-spacing:.22em;text-transform:uppercase;color:#7A7A7A;margin-top:8px;">Management Suite</div>
    </div>""",unsafe_allow_html=True)
    _,mid,_=st.columns([1,2,1])
    with mid:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;padding:32px 32px 24px 32px;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:500;color:#1A1A1A;">Sign in</div>
          <div style="font-family:'Jost',sans-serif;font-size:.78rem;color:#7A7A7A;margin-top:4px;margin-bottom:20px;">Enter your credentials to continue</div>
        </div>""",unsafe_allow_html=True)
        with st.form("login_form"):
            username=st.text_input("Username",placeholder="username")
            password=st.text_input("Password",placeholder="••••••••",type="password")
            submitted=st.form_submit_button("Sign In →",use_container_width=True)
        if submitted:
            if check_credentials(username,password):
                st.session_state.update({"authenticated":True,"username":username.strip().lower(),"login_failed":False})
                st.rerun()
            else:
                st.session_state["login_failed"]=True
        if st.session_state.get("login_failed"):
            st.markdown("""<div style="background:#FFF5F5;border-left:3px solid #8C3D3D;padding:10px 14px;
                font-family:'Jost',sans-serif;font-size:.78rem;color:#8C3D3D;margin-top:8px;">
                Incorrect username or password.</div>""",unsafe_allow_html=True)
        st.markdown("""<div style="font-family:'Jost',sans-serif;font-size:.70rem;color:#9A9A9A;
            text-align:center;margin-top:16px;padding-bottom:8px;">
            Access restricted to authorised personnel.</div>""",unsafe_allow_html=True)

def render_admin():
    page_header("User Management","Add · Edit · Remove Users")
    users=_get_users()
    section_label("Current Users","#8C3D3D")
    st.dataframe(pd.DataFrame([{"Username":u,"Display":v["display"],"Role":v["role"]} for u,v in users.items()]),use_container_width=True,hide_index=True)
    divider()
    section_label("Add or Update User","#2D4A3E")
    c1,c2,c3,c4=st.columns(4)
    nu=c1.text_input("Username",key="adm_u",placeholder="e.g. maria")
    nd=c2.text_input("Display Name",key="adm_d",placeholder="e.g. María")
    np_=c3.text_input("Password",key="adm_p",type="password",placeholder="Password")
    nr=c4.selectbox("Role",["user","admin"],key="adm_r")
    if st.button("Save User",key="adm_save"):
        u=nu.strip().lower()
        if not u: st.warning("Username cannot be empty.")
        elif not np_ and u not in users: st.warning("Password required for new users.")
        elif np_ and len(np_)<6: st.warning("Password must be at least 6 characters.")
        else:
            stored_pw=_hash_password(np_) if np_ else users.get(u,{}).get("password","")
            users[u]={"password":stored_pw,"display":nd.strip() or u.title(),"role":nr}
            _save_users(users); st.success(f"User **{u}** saved."); st.rerun()
    divider()
    section_label("Remove User","#B8924A")
    removable=[u for u in users if u!=st.session_state.get("username")]
    if removable:
        du=st.selectbox("Select user to remove",removable,key="adm_del")
        if st.button("Remove User",key="adm_del_btn"):
            del users[du]; _save_users(users); st.success(f"User **{du}** removed."); st.rerun()
    else: st.info("No other users to remove.")
    divider()
    section_label("Change My Password","#4A6080")
    cp1,cp2=st.columns(2)
    cur_pw=cp1.text_input("Current password",type="password",key="cp_cur")
    new_pw=cp2.text_input("New password",type="password",key="cp_new")
    if st.button("Update Password",key="cp_btn"):
        me=st.session_state.get("username","")
        if not check_credentials(me,cur_pw): st.error("Current password incorrect.")
        elif len(new_pw)<6: st.warning("Password must be at least 6 characters.")
        else:
            users=_get_users()  # refresh after potential migration during check_credentials
            users[me]["password"]=_hash_password(new_pw); _save_users(users); st.success("Password updated.")

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated",False):
    render_login()
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# COMMERCIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
TARGETS_FILE = pathlib.Path(".streamlit/targets.json")

def _load_all_targets():
    """Load targets-by-year dict from disk. Shape: {'2026': {'Brazil': 20.0, ...}, ...}"""
    if not TARGETS_FILE.exists(): return {}
    try:
        data=json.loads(TARGETS_FILE.read_text())
        return data if isinstance(data,dict) else {}
    except Exception: return {}

def _save_all_targets(all_targets):
    try:
        TARGETS_FILE.parent.mkdir(parents=True,exist_ok=True)
        TARGETS_FILE.write_text(json.dumps(all_targets,indent=2,ensure_ascii=False))
    except Exception: pass

def load_targets_for_year(year, all_countries):
    """Return {country: pct} for the given year, hydrating from disk first,
    then DEFAULT_TARGETS_2026 (only for year 2026), then zeros."""
    yr_key=str(year)
    stored=_load_all_targets().get(yr_key,{})
    out={}
    for c in all_countries:
        if c in stored:
            try: out[c]=float(stored[c])
            except (TypeError,ValueError): out[c]=0.0
        elif year==2026 and c in DEFAULT_TARGETS_2026:
            out[c]=float(DEFAULT_TARGETS_2026[c])
        else:
            out[c]=0.0
    return out

def save_targets_for_year(year, year_targets):
    """Persist targets for a given year, preserving other years on disk."""
    all_t=_load_all_targets()
    # Drop zero values to keep file compact, but keep explicit overrides of presets
    all_t[str(year)]={c:float(v) for c,v in year_targets.items() if float(v)!=0.0}
    _save_all_targets(all_t)

def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    years_avail   = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(c for c in df["country"].dropna().unique() if c not in EXCLUDED_COUNTRIES)

    page_header("Commercial Intelligence","Year-over-Year Performance  ·  Growth Analysis  ·  Market Focus")

    ci_tabs = st.tabs(["📊  Overview & YoY","🎯  Country Targets","👥  Customer Intelligence","📅  Seasonality"])

    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]

    with st.expander("⚙  Filters & Scope", expanded=True):
        sc1,sc2=st.columns([1,2])
        with sc1:
            scope=st.radio("Scope",["📅  Year-to-Date","📆  Full Year"],key="ci_scope")
        use_ytd="Year-to-Date" in scope
        with sc2:
            if use_ytd: info_strip(f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. Prior years capped at week {current_week}.","#2D4A3E")
            else: info_strip("Comparing <strong>all weeks in the system</strong> per year — including future confirmed orders.","#B8924A")
        fc1,fc2,fc3=st.columns(3)
        default_years=years_avail[-3:] if len(years_avail)>=3 else years_avail
        sel_years    =fc1.multiselect("Years",years_avail,default=default_years,key="ci_years")
        sel_customers=fc2.multiselect("Customers",all_customers,default=[],key="ci_customers",placeholder="All customers")
        sel_countries=fc3.multiselect("Countries",all_countries,default=[],key="ci_countries",placeholder="All countries")

    if not sel_years: st.warning("Select at least one year."); return

    dff=df[df["delivery_year"].isin(sel_years)].copy()
    dff=dff[~dff["country"].isin(EXCLUDED_COUNTRIES)]
    if sel_customers: dff=dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff=dff[dff["country"].isin(sel_countries)]
    if use_ytd:       dff=dff[dff["delivery_week"]<=current_week]
    if dff.empty: st.info("No data matches the selected filters."); return

    cur_year  =max(sel_years)
    prev_year =cur_year-1
    prev2_year=cur_year-2
    cy,py,p2y =str(cur_year),str(prev_year),str(prev2_year)
    scope_lbl =f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df  =dff[dff["delivery_year"]==cur_year]
    prev_df =dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df=dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ── TAB 1: Overview & YoY ─────────────────────────────────────────────────
    with ci_tabs[0]:
        section_label(f"Summary  ·  {scope_lbl}  ·  {cur_year} vs {prev_year}")
        cur_ship =n_shipments(cur_df);  prev_ship=n_shipments(prev_df)
        cur_fob  =safe_float(cur_df["total_price"].sum())
        prev_fob =safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
        cur_units=safe_float(cur_df["total_quantity"].sum())
        prev_units=safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0
        k1,k2,k3,k4=st.columns(4)
        k1.metric("Shipments",       f"{cur_ship:,}",      delta=metric_delta_str(cur_ship, prev_ship))
        k2.metric("FOB Value",       f"$ {cur_fob:,.0f}",  delta=metric_delta_str(cur_fob,  prev_fob))
        k3.metric("Units Shipped",   f"{int(cur_units):,}",delta=metric_delta_str(cur_units,prev_units))
        k4.metric("Active Customers",f"{cur_df['customer_name'].nunique():,}")
        divider()
        section_label(f"Weekly FOB Trend  ·  {scope_lbl}")
        weekly=dff.groupby(["delivery_year","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        weekly["Year"]=weekly["delivery_year"].astype(str)
        fig_t=px.line(weekly,x="delivery_week",y="fob",color="Year",
                      labels={"delivery_week":"ISO Week","fob":"FOB (USD)"},
                      color_discrete_sequence=PALETTE,markers=True)
        fig_t.update_traces(line_width=2.5,marker_size=5)
        fig_t.update_yaxes(tickprefix="$ ")
        plotly_layout(fig_t,height=320); st.plotly_chart(fig_t,use_container_width=True)
        divider()
        section_label("FOB by Country  ·  3-Year Comparison")
        cy_grp=dff.groupby(["country","delivery_year"]).agg(fob=("total_price","sum"),ships=("shipment_id","nunique")).reset_index()
        cy_grp["Year"]=cy_grp["delivery_year"].astype(str)
        cy_grp["label"]=cy_grp["country"].apply(lambda c:f"{flag(c)} {c}")
        order=cy_grp[cy_grp["Year"]==cy].sort_values("fob",ascending=False)["country"].tolist()
        cy_grp["sort_key"]=cy_grp["country"].apply(lambda c:order.index(c) if c in order else 999)
        cy_grp=cy_grp.sort_values("sort_key")
        fig_c=px.bar(cy_grp,x="label",y="fob",color="Year",barmode="group",
                     labels={"label":"Country","fob":"FOB (USD)"},color_discrete_sequence=PALETTE)
        fig_c.update_yaxes(tickprefix="$ "); fig_c.update_xaxes(tickangle=-35)
        plotly_layout(fig_c,height=360); st.plotly_chart(fig_c,use_container_width=True)
        divider()
        section_label(f"Country Status Table  ·  {scope_lbl}")
        piv_fob=cy_grp.pivot_table(index="country",columns="Year",values="fob",  aggfunc="sum").reset_index()
        piv_shp=cy_grp.pivot_table(index="country",columns="Year",values="ships",aggfunc="sum").reset_index()
        country_rows=[]
        for c in piv_fob["country"].unique():
            c_fob =safe_float(safe_pivot_val(piv_fob,"country",c,cy))
            p_fob =safe_float(safe_pivot_val(piv_fob,"country",c,py))
            p2_fob=safe_float(safe_pivot_val(piv_fob,"country",c,p2y))
            c_shp =safe_int(safe_pivot_val(piv_shp,"country",c,cy))
            p_shp =safe_int(safe_pivot_val(piv_shp,"country",c,py))
            p2_shp=safe_int(safe_pivot_val(piv_shp,"country",c,p2y))
            chg_py=pct_change(c_fob,p_fob); chg_p2=pct_change(c_fob,p2_fob)
            badge=status_badge(chg_py,c_fob)
            country_rows.append({
                "Country":f"{flag(c)} {c}",
                f"Ships {cy}":c_shp, f"Ships {py}":p_shp or "—", f"Ships {p2y}":p2_shp or "—",
                f"FOB {cy}":f"$ {c_fob:,.0f}",
                f"FOB {py}":f"$ {p_fob:,.0f}" if p_fob else "—",
                f"FOB {p2y}":f"$ {p2_fob:,.0f}" if p2_fob else "—",
                f"vs {py}":f"{chg_py:+.1f}%" if chg_py is not None else "—",
                f"vs {p2y}":f"{chg_p2:+.1f}%" if chg_p2 is not None else "—",
                "Status":badge,
            })
        country_rows.sort(key=lambda x:safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")),reverse=True)
        st.dataframe(pd.DataFrame(country_rows),use_container_width=True,hide_index=True)
        divider()
        section_label(f"Customer Performance by Country  ·  {scope_lbl}")
        info_strip("Each country panel shows every customer active in any selected year.","#8C3D3D")
        ccy=dff.groupby(["country","customer_name","delivery_year"]).agg(
            fob=("total_price","sum"),ships=("shipment_id","nunique"),units=("total_quantity","sum")).reset_index()
        top_c=(ccy[ccy["delivery_year"]==cur_year].groupby("country")["fob"].sum()
               .sort_values(ascending=False).index.tolist())
        for country in top_c+[c for c in ccy["country"].unique() if c not in top_c]:
            cdf_c=ccy[ccy["country"]==country]
            if cdf_c.empty: continue
            tot_fob=safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
            tot_shp=safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())
            with st.expander(f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f}  ({scope_lbl} {cur_year})",expanded=False):
                pf=cdf_c.pivot_table(index="customer_name",columns="delivery_year",values="fob",  aggfunc="sum").reset_index()
                ps=cdf_c.pivot_table(index="customer_name",columns="delivery_year",values="ships",aggfunc="sum").reset_index()
                pu=cdf_c.pivot_table(index="customer_name",columns="delivery_year",values="units",aggfunc="sum").reset_index()
                cust_rows=[]
                for _,r in pf.iterrows():
                    cn=r["customer_name"]
                    cf=safe_float(r.get(cur_year,0)); pf_=safe_float(r.get(prev_year,0)); p2f=safe_float(r.get(prev2_year,0))
                    cs=safe_int(safe_pivot_val(ps,"customer_name",cn,cur_year))
                    ps_=safe_int(safe_pivot_val(ps,"customer_name",cn,prev_year))
                    cu=safe_int(safe_pivot_val(pu,"customer_name",cn,cur_year))
                    chg=pct_change(cf,pf_); chg2=pct_change(cf,p2f)
                    cust_rows.append({
                        "Customer":cn,f"FOB {cy}":f"$ {cf:,.0f}",
                        f"FOB {py}":f"$ {pf_:,.0f}" if pf_ else "—",
                        f"FOB {p2y}":f"$ {p2f:,.0f}" if p2f else "—",
                        f"vs {py}":f"{chg:+.1f}%" if chg is not None else "—",
                        f"vs {p2y}":f"{chg2:+.1f}%" if chg2 is not None else "—",
                        f"Ships {cy}":cs,f"Ships {py}":ps_ or "—",f"Units {cy}":f"{cu:,}",
                        "Status":status_badge(chg,cf),
                    })
                cust_rows.sort(key=lambda x:safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")),reverse=True)
                if cust_rows:
                    st.dataframe(pd.DataFrame(cust_rows),use_container_width=True,hide_index=True)
                    cdf_cur=cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob",ascending=False).head(12)
                    if not cdf_cur.empty:
                        fig_m=px.bar(cdf_cur,x="customer_name",y="fob",labels={"customer_name":"","fob":"FOB (USD)"},color_discrete_sequence=["#8C3D3D"])
                        fig_m.update_yaxes(tickprefix="$ "); fig_m.update_xaxes(tickangle=-30)
                        plotly_layout(fig_m,height=200); st.plotly_chart(fig_m,use_container_width=True)
        divider()
        section_label("Growth Opportunity Focus")
        decline=[r for r in country_rows if any(k in r["Status"] for k in ["Declining","At risk","Lost"])]
        growing=[r for r in country_rows if any(k in r["Status"] for k in ["Growing","Strong"])]
        new_mkt=[r for r in country_rows if "New" in r["Status"]]
        g1,g2,g3=st.columns(3)
        def focus_col(col,title,color,items):
            col.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;text-transform:uppercase;color:{color};margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid {color};">{title}</div>',unsafe_allow_html=True)
            if not items: col.markdown('<div style="font-family:Jost,sans-serif;font-size:.82rem;color:#7A7A7A;padding:6px 0;">None</div>',unsafe_allow_html=True)
            for r in items:
                chg=r.get(f"vs {py}","—")
                col.markdown(f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #EDE9E3;"><span style="font-family:Jost,sans-serif;font-size:.82rem;color:#1A1A1A;">{r["Country"]}</span><span style="font-family:Jost,sans-serif;font-size:.75rem;font-weight:500;color:{color};">{chg}</span></div>',unsafe_allow_html=True)
        focus_col(g1,"Needs attention","#8C3D3D",decline)
        focus_col(g2,"Growing markets","#2D4A3E",growing)
        focus_col(g3,"New markets","#B8924A",new_mkt)

    # ── TAB 2: Country Targets ────────────────────────────────────────────────
    with ci_tabs[1]:
        section_label(f"Country Growth Targets  ·  {cur_year}  ·  {scope_lbl}","#8C3D3D")
        info_strip(f"Set a FOB growth target (%) per country for <strong>{cur_year}</strong>. The dashboard calculates the required FOB, your current gap, and weekly pace.","#2D4A3E")

        cntry_cur =cur_df.groupby("country").agg(fob_cur=("total_price","sum"),ships_cur=("shipment_id","nunique")).reset_index()
        cntry_prev=prev_df.groupby("country").agg(fob_prev=("total_price","sum")).reset_index() if not prev_df.empty else pd.DataFrame(columns=["country","fob_prev"])
        cntry_base=cntry_cur.merge(cntry_prev,on="country",how="outer").fillna(0)
        if not prev_df.empty:
            prev_only=prev_df[~prev_df["country"].isin(cntry_base["country"])].groupby("country").agg(fob_prev=("total_price","sum")).reset_index()
            prev_only["fob_cur"]=0.0; prev_only["ships_cur"]=0
            cntry_base=pd.concat([cntry_base,prev_only],ignore_index=True)
        all_tgt_countries=sorted(cntry_base["country"].tolist())

        tgt_key=f"country_targets_{cur_year}"
        if tgt_key not in st.session_state:
            st.session_state[tgt_key]=load_targets_for_year(cur_year, all_tgt_countries)
        else:
            # Hydrate any new countries that may have appeared in the data after first load
            for c in all_tgt_countries:
                if c not in st.session_state[tgt_key]:
                    if cur_year==2026 and c in DEFAULT_TARGETS_2026:
                        st.session_state[tgt_key][c]=float(DEFAULT_TARGETS_2026[c])
                    else:
                        st.session_state[tgt_key][c]=0.0

        if cur_year==2026:
            set_countries=" · ".join(f"{flag(c)} {c} <strong>{v:+.0f}%</strong>" for c,v in DEFAULT_TARGETS_2026.items() if c in all_tgt_countries)
            info_strip(f"Pre-set 2026 targets (based on 2025 actuals): {set_countries}. You can override any value below.","#2D4A3E")
        info_strip("Targets are saved to disk and persist across sessions and restarts.","#4A6080")

        with st.form("target_form"):
            st.markdown('<div style="font-family:Jost,sans-serif;font-size:.78rem;color:#4A4A4A;margin-bottom:12px;">Enter a growth % target for each country. Leave at 0 to exclude.</div>',unsafe_allow_html=True)
            n_cols=4
            new_targets={}
            for chunk in [all_tgt_countries[i:i+n_cols] for i in range(0,len(all_tgt_countries),n_cols)]:
                cols=st.columns(n_cols)
                for col,country in zip(cols,chunk):
                    prev_val=safe_float(cntry_base[cntry_base["country"]==country]["fob_prev"].values[0] if country in cntry_base["country"].values else 0)
                    default=safe_float(st.session_state[tgt_key].get(country,0.0))
                    is_preset=cur_year==2026 and country in DEFAULT_TARGETS_2026
                    lbl=f"{flag(country)} {country}"+(" ✦" if is_preset else "")+f"\n(prev: $ {prev_val:,.0f})"
                    new_targets[country]=col.number_input(lbl,min_value=-100.0,max_value=500.0,value=default,step=1.0,key=f"tgt_{cur_year}_{country}")
            if st.form_submit_button("Save Targets  →"):
                st.session_state[tgt_key]=new_targets
                save_targets_for_year(cur_year, new_targets)
                st.success(f"Targets for {cur_year} saved to disk.")

        targets=st.session_state.get(tgt_key,load_targets_for_year(cur_year, all_tgt_countries))
        divider()
        section_label(f"Target Dashboard  ·  {cur_year}","#8C3D3D")

        tgt_rows=[]
        for _,r in cntry_base.iterrows():
            c=r["country"]; fob_cur=safe_float(r["fob_cur"]); fob_prev=safe_float(r["fob_prev"])
            tgt_pct=safe_float(targets.get(c,0.0))
            if tgt_pct==0 and fob_prev==0: continue
            tgt_fob=fob_prev*(1+tgt_pct/100) if fob_prev>0 else 0.0
            gap=tgt_fob-fob_cur
            pct_done=(fob_cur/tgt_fob*100) if tgt_fob>0 else (100.0 if fob_cur>0 else 0.0)
            expected=((current_week/(current_week if use_ytd else 52))*tgt_fob)
            on_track=fob_cur>=expected
            tgt_rows.append({
                "_country_raw":c,"_fob_cur":fob_cur,"_gap":gap,"_pct_done":pct_done,"_on_track":on_track,
                "Country":f"{flag(c)} {c}",
                f"FOB {py}":f"$ {fob_prev:,.0f}" if fob_prev else "—",
                "Target %":f"{tgt_pct:+.1f}%",
                "Target FOB":f"$ {tgt_fob:,.0f}" if tgt_fob else "—",
                f"FOB {cy}":f"$ {fob_cur:,.0f}",
                "% of Target":f"{pct_done:.1f}%",
                "Gap":f"✓ ahead $ {abs(gap):,.0f}" if gap<=0 else f"▼ $ {gap:,.0f}",
                "Pace":"✓ On track" if on_track else "⚠ Behind",
            })
        tgt_rows.sort(key=lambda x:x["_fob_cur"],reverse=True)
        st.dataframe(pd.DataFrame(tgt_rows)[["Country",f"FOB {py}","Target %","Target FOB",f"FOB {cy}","% of Target","Gap","Pace"]],use_container_width=True,hide_index=True)

        on_n=sum(1 for r in tgt_rows if r["_on_track"]); behind_n=len(tgt_rows)-on_n
        total_gap=sum(safe_float(r["_gap"]) for r in tgt_rows if r["_gap"]>0)
        total_ahead=sum(abs(safe_float(r["_gap"])) for r in tgt_rows if r["_gap"]<=0)
        s1,s2,s3,s4=st.columns(4)
        s1.metric("Countries tracked",f"{len(tgt_rows)}"); s2.metric("On track",f"{on_n}",delta=f"{behind_n} behind")
        s3.metric("Total gap to close",f"$ {total_gap:,.0f}"); s4.metric("Total ahead",f"$ {total_ahead:,.0f}")

        divider()
        section_label("Cumulative Pace per Country","#4A6080")
        info_strip("Each chart shows actual cumulative FOB vs the linear target pace needed to hit the annual goal.","#4A6080")
        pace_countries=[r["_country_raw"] for r in tgt_rows if targets.get(r["_country_raw"],0)!=0][:12]
        if pace_countries and not prev_df.empty:
            max_wk=current_week if use_ytd else 52
            for chunk in [pace_countries[i:i+2] for i in range(0,len(pace_countries),2)]:
                cols=st.columns(2)
                for col,country in zip(cols,chunk):
                    row=cntry_base[cntry_base["country"]==country]
                    if row.empty: continue
                    fp=safe_float(row["fob_prev"].values[0])
                    tp=safe_float(targets.get(country,10.0))
                    tf=fp*(1+tp/100)
                    wk_c=cur_df[cur_df["country"]==country].groupby("delivery_week").agg(fob=("total_price","sum")).reset_index().sort_values("delivery_week")
                    wk_c["cumulative"]=wk_c["fob"].cumsum()
                    all_wks=list(range(1,max_wk+1))
                    pace_line=[tf*(w/max_wk) for w in all_wks]
                    fig_cp=go.Figure()
                    fig_cp.add_trace(go.Scatter(x=wk_c["delivery_week"],y=wk_c["cumulative"],name="Actual",
                        line=dict(color="#8C3D3D",width=2.5),mode="lines+markers",marker_size=4,
                        fill="tozeroy",fillcolor="rgba(140,61,61,0.07)"))
                    fig_cp.add_trace(go.Scatter(x=all_wks,y=pace_line,name=f"Target ({tp:+.0f}%)",
                        line=dict(color="#2D4A3E",width=1.5,dash="dash"),mode="lines"))
                    fig_cp.update_layout(
                        title=dict(text=f"{flag(country)} {country}",font=dict(family="Cormorant Garamond",size=14,color="#1A1A1A")),
                        plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",font_family="Jost",
                        margin=dict(l=0,r=0,t=32,b=0),height=220,showlegend=False)
                    fig_cp.update_yaxes(tickprefix="$ ",tickfont=dict(size=9),gridcolor="#F0EDE8")
                    fig_cp.update_xaxes(title="Week",tickfont=dict(size=9),gridcolor="#F0EDE8")
                    col.plotly_chart(fig_cp,use_container_width=True)
        else:
            st.info("Set targets above and ensure prior-year data is available to see pace charts.")

    # ── TAB 3: Customer Intelligence ──────────────────────────────────────────
    with ci_tabs[2]:
        section_label("Customer Concentration & Dependency Risk","#8C3D3D")
        info_strip("High concentration in few customers = high revenue risk. A healthy portfolio spreads FOB across many accounts.","#8C3D3D")
        cust_fob=cur_df.groupby("customer_name").agg(fob=("total_price","sum"),ships=("shipment_id","nunique"),units=("total_quantity","sum"),countries=("country","nunique")).reset_index()
        cust_fob=cust_fob.sort_values("fob",ascending=False).reset_index(drop=True)
        total_fob_cur=safe_float(cust_fob["fob"].sum())
        cust_fob["share_%"]=cust_fob["fob"]/total_fob_cur*100 if total_fob_cur else 0
        cust_fob["cumulative_%"]=cust_fob["share_%"].cumsum()
        top80=int((cust_fob["cumulative_%"]<=80).sum())+1
        info_strip(f"<strong>{top80} customer{'s' if top80!=1 else ''}</strong> account for 80% of current-year FOB. Total active customers: <strong>{len(cust_fob)}</strong>.","#4A6080")
        fig_conc=px.bar(cust_fob.head(20),x="customer_name",y="fob",labels={"customer_name":"Customer","fob":"FOB (USD)"},color="share_%",color_continuous_scale=["#F0EAE2","#8C3D3D"])
        fig_conc.update_yaxes(tickprefix="$ "); fig_conc.update_xaxes(tickangle=-35)
        fig_conc.update_coloraxes(colorbar_title="Share %")
        plotly_layout(fig_conc,height=320); st.plotly_chart(fig_conc,use_container_width=True)
        divider()
        section_label("Top Growing & Declining Customers","#2D4A3E")
        if not prev_df.empty:
            cust_prev=prev_df.groupby("customer_name").agg(fob_prev=("total_price","sum")).reset_index()
            cust_comp=cust_fob[["customer_name","fob"]].merge(cust_prev,on="customer_name",how="outer").fillna(0)
            cust_comp["chg_pct"]=cust_comp.apply(lambda r:pct_change(r["fob"],r["fob_prev"]),axis=1)
            cust_comp=cust_comp[cust_comp["fob"]>0].dropna(subset=["chg_pct"]).sort_values("chg_pct",ascending=False)
            top5=cust_comp.head(5); bot5=cust_comp.tail(5).sort_values("chg_pct")
            cg1,cg2=st.columns(2)
            def ranked_list(col,title,color,rows_df):
                col.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:{color};margin-bottom:10px;border-bottom:2px solid {color};padding-bottom:6px;">{title}</div>',unsafe_allow_html=True)
                for i,(_,r) in enumerate(rows_df.iterrows(),1):
                    col.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #EDE9E3;"><span style="font-family:Cormorant Garamond,serif;font-size:1.1rem;font-weight:500;color:{color};min-width:20px;">{i}</span><span style="font-family:Jost,sans-serif;font-size:.84rem;color:#1A1A1A;flex:1;">{r["customer_name"]}</span><div style="text-align:right;"><div style="font-family:Jost,sans-serif;font-size:.82rem;font-weight:500;color:{color};">{r["chg_pct"]:+.1f}%</div><div style="font-family:Jost,sans-serif;font-size:.72rem;color:#7A7A7A;">$ {safe_float(r["fob"]):,.0f}</div></div></div>',unsafe_allow_html=True)
            ranked_list(cg1,"Top 5 Growing","#2D4A3E",top5)
            ranked_list(cg2,"Top 5 Declining","#8C3D3D",bot5)
        else: st.info("Need prior-year data to show growth/decline rankings.")
        divider()
        section_label(f"Weekly Run-Rate  ·  {cur_year} vs {prev_year}","#4A6080")
        info_strip(f"Compare each week this year against the same week last year — spot exactly which weeks are ahead or behind.","#4A6080")
        if not prev_df.empty:
            wk_cur=cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_prev=prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_rr=wk_cur.merge(wk_prev,on="delivery_week",how="outer").fillna(0).sort_values("delivery_week")
            wk_rr["diff"]=wk_rr["fob_cur"]-wk_rr["fob_prev"]
            fig_rr=go.Figure()
            fig_rr.add_bar(x=wk_rr["delivery_week"],y=wk_rr["fob_prev"],name=str(prev_year),marker_color="#DDD8D0")
            fig_rr.add_bar(x=wk_rr["delivery_week"],y=wk_rr["fob_cur"],name=str(cur_year),marker_color="#8C3D3D",opacity=0.85)
            fig_rr.update_layout(barmode="overlay")
            fig_rr.update_yaxes(tickprefix="$ "); fig_rr.update_xaxes(title="ISO Week")
            plotly_layout(fig_rr,height=300); st.plotly_chart(fig_rr,use_container_width=True)
            wk_rr["Week"]=wk_rr["delivery_week"].apply(lambda w:f"W{int(w)}")
            wk_rr[f"FOB {cy}"]=wk_rr["fob_cur"].apply(lambda x:f"$ {x:,.0f}")
            wk_rr[f"FOB {py}"]=wk_rr["fob_prev"].apply(lambda x:f"$ {x:,.0f}")
            wk_rr["Difference"]=wk_rr["diff"].apply(lambda x:f"▲ $ {abs(x):,.0f}" if x>=0 else f"▼ $ {abs(x):,.0f}")
            st.dataframe(wk_rr[["Week",f"FOB {cy}",f"FOB {py}","Difference"]],use_container_width=True,hide_index=True)
        else: st.info(f"No {prev_year} data available for run-rate comparison.")
        divider()
        section_label("New Customer Tracking","#B8924A")
        info_strip("Customers with no activity in any prior year. Monitor their trajectory to assess retention potential.","#B8924A")
        all_prev_custs=dff[dff["delivery_year"]<cur_year]["customer_name"].unique()
        new_custs_df=cur_df[~cur_df["customer_name"].isin(all_prev_custs)]
        if not new_custs_df.empty:
            nc_grp=new_custs_df.groupby("customer_name").agg(
                first_week=("delivery_week","min"),last_week=("delivery_week","max"),
                weeks_active=("delivery_week","nunique"),fob=("total_price","sum"),
                ships=("shipment_id","nunique"),
                countries=("country",lambda x:", ".join(f"{flag(c)} {c}" for c in sorted(x.unique())))).reset_index()
            nc_grp=nc_grp.sort_values("fob",ascending=False)
            nc_grp["FOB"]=nc_grp["fob"].apply(lambda x:f"$ {x:,.0f}")
            nc_grp["Avg FOB/wk"]=nc_grp.apply(lambda r:f"$ {safe_float(r['fob'])/max(safe_int(r['weeks_active']),1):,.0f}",axis=1)
            st.dataframe(nc_grp[["customer_name","first_week","last_week","weeks_active","ships","FOB","Avg FOB/wk","countries"]].rename(columns={"customer_name":"Customer","first_week":"First Week","last_week":"Last Week","weeks_active":"Active Weeks","ships":"Shipments","countries":"Countries"}),use_container_width=True,hide_index=True)
            divider()
            section_label(f"New Customer Weekly Trajectory  ·  {cur_year}","#B8924A")
            top_new=nc_grp.head(8)["customer_name"].tolist()
            nc_wk=new_custs_df[new_custs_df["customer_name"].isin(top_new)].groupby(["customer_name","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
            if not nc_wk.empty:
                for chunk in [top_new[i:i+4] for i in range(0,len(top_new),4)]:
                    cols=st.columns(4)
                    for col,cname in zip(cols,chunk):
                        cd=nc_wk[nc_wk["customer_name"]==cname].sort_values("delivery_week")
                        if cd.empty: continue
                        ttl=safe_float(cd["fob"].sum())
                        fig_sp=go.Figure()
                        fig_sp.add_trace(go.Bar(x=cd["delivery_week"],y=cd["fob"],marker_color="#B8924A",opacity=0.85))
                        fig_sp.update_layout(title=dict(text=f"{cname[:18]}\n$ {ttl:,.0f}",font=dict(family="Jost",size=11,color="#1A1A1A")),plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",margin=dict(l=0,r=0,t=40,b=0),height=160,showlegend=False)
                        fig_sp.update_yaxes(tickprefix="$ ",tickfont=dict(size=8),gridcolor="#F0EDE8")
                        fig_sp.update_xaxes(tickfont=dict(size=8))
                        col.plotly_chart(fig_sp,use_container_width=True)
        else: st.info(f"No new customers found in {cur_year} compared to prior years.")

        # ── Product Trend Analysis · Customer × Crop × Year ───────────────────
        divider()
        section_label(f"Product Trend Analysis  ·  Customer × Crop × Year  ·  {scope_lbl}","#6B4080")
        info_strip(f"Master table of FOB per <strong>customer × crop × year</strong>. The baseline is the average of all prior years selected above (in the same {scope_lbl} window). "
                   f"A deviation greater than <strong>±25%</strong> from that baseline is flagged so you can identify strong drops or gains while there is still time to react.",
                   "#6B4080")

        if "crop_name" not in dff.columns or dff["crop_name"].astype(str).str.strip().eq("").all():
            st.info("No `crop_name` data available in the loaded file — populate that column to enable product trend analysis.")
        else:
            trend_base = dff.copy()
            trend_base["crop_name"] = trend_base["crop_name"].astype(str).str.strip()
            trend_base = trend_base[trend_base["crop_name"]!=""]

            if trend_base.empty:
                st.info("No rows with a populated crop_name match the current filters.")
            else:
                # ── Local filters ─────────────────────────────────────────────
                all_crops = sorted(trend_base["crop_name"].dropna().unique())
                f_cols = st.columns([2,1,1])
                with f_cols[0]:
                    sel_crops = st.multiselect("Crops", all_crops, default=[],
                                               placeholder="All crops", key="trend_crops")
                with f_cols[1]:
                    flag_choice = st.selectbox("Show",
                        ["All","⚠ Strong drops only","🚀 Strong gains only","Out of trend (any)","✓ On trend only","🆕 New activity","⛔ Lost activity"],
                        key="trend_flag")
                with f_cols[2]:
                    sort_choice = st.selectbox("Sort by",
                        ["Largest deviation first","Largest current FOB first","Customer A→Z"],
                        key="trend_sort")

                if sel_crops:
                    trend_base = trend_base[trend_base["crop_name"].isin(sel_crops)]

                if trend_base.empty:
                    st.info("No data matches the selected crop filter.")
                else:
                    # ── Build pivot: customer × country × crop, columns = years ──
                    agg = (trend_base
                           .groupby(["customer_name","country","crop_name","delivery_year"])
                           ["total_price"].sum().reset_index())
                    piv = agg.pivot_table(index=["customer_name","country","crop_name"],
                                          columns="delivery_year",
                                          values="total_price",
                                          aggfunc="sum").reset_index()

                    available_years = sorted([y for y in piv.columns if isinstance(y,(int,np.integer))])
                    prior_years = [y for y in available_years if y < cur_year]
                    has_current = cur_year in available_years

                    if not prior_years and not has_current:
                        st.info("Need at least one year of data to build the trend table.")
                    else:
                        # ── Compute baseline + deviation per row ──────────────
                        rows=[]
                        for _,r in piv.iterrows():
                            row_record = {
                                "_customer": r["customer_name"],
                                "_country":  r["country"],
                                "_crop":     r["crop_name"],
                            }
                            # Year-by-year FOB values
                            year_vals = {}
                            for y in available_years:
                                v = safe_float(r.get(y, 0))
                                year_vals[y] = v
                            # Baseline = mean of non-zero prior years (avoid divide-by-zero from sparse history)
                            prior_nonzero = [year_vals[y] for y in prior_years if year_vals[y]>0]
                            baseline = sum(prior_nonzero)/len(prior_nonzero) if prior_nonzero else 0.0
                            current  = year_vals.get(cur_year, 0.0)
                            # Flag logic
                            if baseline==0 and current>0:
                                flag_lbl="🆕 New activity"; deviation=None
                            elif baseline>0 and current==0:
                                flag_lbl="⛔ Lost activity"; deviation=-100.0
                            elif baseline==0 and current==0:
                                continue   # skip empty rows
                            else:
                                deviation = (current-baseline)/baseline*100
                                if   deviation >=  25: flag_lbl="🚀 Strong gain"
                                elif deviation <= -25: flag_lbl="⚠ Strong drop"
                                else:                  flag_lbl="✓ On trend"
                            row_record.update({
                                "_baseline": baseline,
                                "_current":  current,
                                "_deviation": deviation if deviation is not None else 0.0,
                                "_flag": flag_lbl,
                                "_year_vals": year_vals,
                            })
                            rows.append(row_record)

                        if not rows:
                            st.info("No customer × crop combinations with activity in the selected scope.")
                        else:
                            # ── Apply flag filter ─────────────────────────────
                            def _passes(r):
                                f = r["_flag"]
                                if flag_choice=="All": return True
                                if flag_choice=="⚠ Strong drops only":  return f=="⚠ Strong drop"
                                if flag_choice=="🚀 Strong gains only":  return f=="🚀 Strong gain"
                                if flag_choice=="Out of trend (any)":   return f in ("⚠ Strong drop","🚀 Strong gain","⛔ Lost activity")
                                if flag_choice=="✓ On trend only":      return f=="✓ On trend"
                                if flag_choice=="🆕 New activity":      return f=="🆕 New activity"
                                if flag_choice=="⛔ Lost activity":      return f=="⛔ Lost activity"
                                return True
                            rows = [r for r in rows if _passes(r)]

                            # ── Sort ──────────────────────────────────────────
                            if sort_choice=="Largest deviation first":
                                rows.sort(key=lambda x: abs(x["_deviation"]), reverse=True)
                            elif sort_choice=="Largest current FOB first":
                                rows.sort(key=lambda x: x["_current"], reverse=True)
                            else:
                                rows.sort(key=lambda x: x["_customer"].lower())

                            # ── Build display df ──────────────────────────────
                            display_rows=[]
                            for r in rows:
                                d={
                                    "Customer": r["_customer"],
                                    "Country":  f"{flag(r['_country'])} {r['_country']}",
                                    "Crop":     r["_crop"],
                                }
                                for y in available_years:
                                    v=r["_year_vals"].get(y,0.0)
                                    d[f"FOB {y}"] = f"$ {v:,.0f}" if v>0 else "—"
                                d["Baseline (avg prior)"] = f"$ {r['_baseline']:,.0f}" if r["_baseline"]>0 else "—"
                                d[f"FOB {cur_year}"] = f"$ {r['_current']:,.0f}" if r["_current"]>0 else "—"
                                if r["_flag"]=="🆕 New activity":
                                    d["Deviation %"] = "🆕 new"
                                elif r["_flag"]=="⛔ Lost activity":
                                    d["Deviation %"] = "−100.0%"
                                else:
                                    d["Deviation %"] = f"{r['_deviation']:+.1f}%"
                                d["Flag"] = r["_flag"]
                                display_rows.append(d)

                            # Reorder columns: Customer, Country, Crop, FOB by year (chronological), Baseline, Current, Deviation, Flag
                            base_cols=["Customer","Country","Crop"]
                            year_cols=[f"FOB {y}" for y in prior_years if y!=cur_year]
                            tail_cols=["Baseline (avg prior)",f"FOB {cur_year}","Deviation %","Flag"]
                            # If cur_year was already in year_cols (shouldn't because filtered), de-dup
                            ordered_cols = base_cols + year_cols + tail_cols

                            df_display = pd.DataFrame(display_rows)
                            # Ensure all expected columns exist (in case of edge cases)
                            for c in ordered_cols:
                                if c not in df_display.columns: df_display[c]="—"
                            df_display = df_display[ordered_cols]

                            # ── Summary counters ───────────────────────────────
                            n_total = len(rows)
                            n_drop  = sum(1 for r in rows if r["_flag"]=="⚠ Strong drop")
                            n_gain  = sum(1 for r in rows if r["_flag"]=="🚀 Strong gain")
                            n_lost  = sum(1 for r in rows if r["_flag"]=="⛔ Lost activity")
                            n_new   = sum(1 for r in rows if r["_flag"]=="🆕 New activity")
                            n_ok    = sum(1 for r in rows if r["_flag"]=="✓ On trend")
                            sm1,sm2,sm3,sm4,sm5,sm6 = st.columns(6)
                            sm1.metric("Combinations", f"{n_total:,}")
                            sm2.metric("⚠ Strong drops", f"{n_drop:,}")
                            sm3.metric("🚀 Strong gains", f"{n_gain:,}")
                            sm4.metric("⛔ Lost",         f"{n_lost:,}")
                            sm5.metric("🆕 New",          f"{n_new:,}")
                            sm6.metric("✓ On trend",     f"{n_ok:,}")

                            # Cap at 500 rows for performance
                            if len(df_display)>500:
                                info_strip(f"Showing the first 500 of {len(df_display):,} rows. Tighten the filters above to narrow the view.","#B8924A")
                                df_display = df_display.head(500)

                            st.dataframe(df_display, use_container_width=True, hide_index=True)

                            # Excel download
                            buf=io.BytesIO()
                            df_display.to_excel(buf,index=False,engine="openpyxl")
                            st.download_button("⬇  Export trend table to Excel",
                                               data=buf.getvalue(),
                                               file_name=f"product_trend_{cur_year}_{scope_lbl.replace(' ','_').replace('–','-')}.xlsx",
                                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                               key="dl_trend_table")

    # ── TAB 4: Seasonality ────────────────────────────────────────────────────
    with ci_tabs[3]:
        section_label(f"Seasonality Heatmap  ·  FOB by Country & Week  ·  {cur_year}","#4A6080")
        info_strip("Which weeks are your strongest per market? Use this to plan commercial push timing, inventory, and staffing.","#4A6080")
        season=cur_df.groupby(["country","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        if not season.empty:
            heat_piv=season.pivot_table(index="country",columns="delivery_week",values="fob",aggfunc="sum").fillna(0)
            top_s=heat_piv.sum(axis=1).nlargest(15).index
            heat_piv=heat_piv.loc[top_s]
            heat_piv.index=[f"{flag(c)} {c}" for c in heat_piv.index]
            fig_sea=go.Figure(data=go.Heatmap(z=heat_piv.values,x=[f"W{int(w)}" for w in heat_piv.columns],y=heat_piv.index.tolist(),
                colorscale=[[0,"#F5F2ED"],[0.25,"#F0EAE2"],[0.6,"#C47A7A"],[1,"#5C1F1F"]],hoverongaps=False,
                hovertemplate="Country: %{y}<br>Week: %{x}<br>FOB: $ %{z:,.0f}<extra></extra>"))
            fig_sea.update_layout(plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",font_family="Jost",font_color="#1A1A1A",
                margin=dict(l=0,r=0,t=16,b=0),height=max(320,len(top_s)*34),
                xaxis=dict(side="top",tickfont=dict(size=10,color="#4A4A4A")),yaxis=dict(tickfont=dict(size=11,color="#1A1A1A")))
            st.plotly_chart(fig_sea,use_container_width=True)
        divider()
        section_label(f"Strongest Weeks Overall  ·  {cur_year}")
        wk_total=cur_df.groupby("delivery_week").agg(fob=("total_price","sum"),ships=("shipment_id","nunique"),customers=("customer_name","nunique")).reset_index()
        wk_total=wk_total.sort_values("fob",ascending=False).head(10)
        wk_total["Week"]=wk_total["delivery_week"].apply(lambda w:week_label(cur_year,int(w)))
        wk_total["FOB"]=wk_total["fob"].apply(lambda x:f"$ {x:,.0f}")
        st.dataframe(wk_total[["Week","FOB","ships","customers"]].rename(columns={"ships":"Shipments","customers":"Customers"}),use_container_width=True,hide_index=True)
        if not prev_df.empty:
            divider()
            section_label(f"Same-Week Comparison  ·  {cur_year} vs {prev_year}")
            wk_cp=cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_pp=prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_mrg=wk_cp.merge(wk_pp,on="delivery_week",how="outer").fillna(0).sort_values("delivery_week")
            fig_wk=go.Figure()
            fig_wk.add_trace(go.Scatter(x=wk_mrg["delivery_week"],y=wk_mrg["fob_prev"],name=str(prev_year),line=dict(color="#DDD8D0",width=2),mode="lines"))
            fig_wk.add_trace(go.Scatter(x=wk_mrg["delivery_week"],y=wk_mrg["fob_cur"],name=str(cur_year),line=dict(color="#8C3D3D",width=2.5),mode="lines+markers",marker_size=4))
            fig_wk.update_yaxes(tickprefix="$ "); fig_wk.update_xaxes(title="ISO Week")
            plotly_layout(fig_wk,height=300); st.plotly_chart(fig_wk,use_container_width=True)
            divider()
            section_label(f"Country Seasonality Shift  ·  {cur_year} vs {prev_year}")
            info_strip("Green = more FOB this year vs last in that week  ·  Red = less FOB  ·  White = no change","#4A6080")
            prev_heat=prev_df.groupby(["country","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
            if not prev_heat.empty and not season.empty:
                ph_piv=prev_heat.pivot_table(index="country",columns="delivery_week",values="fob",aggfunc="sum").fillna(0)
                raw_idx=[c.split(" ",1)[-1] for c in heat_piv.index]
                valid=[c for c in raw_idx if c in ph_piv.index]
                if valid:
                    cur_sub=heat_piv.loc[[f"{flag(c)} {c}" for c in valid]]
                    prv_sub=ph_piv.loc[valid]; prv_sub.index=[f"{flag(c)} {c}" for c in prv_sub.index]
                    common_wks=sorted(set(cur_sub.columns)&set(prv_sub.columns))
                    shift=cur_sub[common_wks]-prv_sub[common_wks]
                    fig_sh=go.Figure(data=go.Heatmap(z=shift.values,x=[f"W{int(w)}" for w in shift.columns],y=shift.index.tolist(),
                        colorscale=[[0,"#8C3D3D"],[0.35,"#F0EAE2"],[0.5,"#F5F2ED"],[0.65,"#C8DDD0"],[1,"#2D4A3E"]],zmid=0,hoverongaps=False,
                        hovertemplate="Country: %{y}<br>Week: %{x}<br>Δ FOB: $ %{z:,.0f}<extra></extra>"))
                    fig_sh.update_layout(plot_bgcolor="#FFFFFF",paper_bgcolor="rgba(0,0,0,0)",font_family="Jost",font_color="#1A1A1A",
                        margin=dict(l=0,r=0,t=16,b=0),height=max(280,len(shift)*34),
                        xaxis=dict(side="top",tickfont=dict(size=10,color="#4A4A4A")),yaxis=dict(tickfont=dict(size=11,color="#1A1A1A")))
                    st.plotly_chart(fig_sh,use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ALERTS  ·  Executive panel that surfaces issues needing attention right now.
#            All detectors are pure functions returning lists of dicts so they
#            are easy to unit-test and reuse.
# ════════════════════════════════════════════════════════════════════════════
ALERT_DECLINE_THRESHOLD = 20.0      # |%| drop vs prior year that triggers risk flag
ALERT_TOP_CUSTOMERS_N    = 20       # universe size for "top customers at risk"
ALERT_NEW_CUSTOMER_WEEKS = 8        # window (weeks) considered "recent new customer"
ALERT_CONCENTRATION_DELTA= 5.0      # +percentage-points in top-5 share that triggers concentration alert

def _ytd_slice(df, year, max_week):
    """Return df rows for `year` capped at `max_week`."""
    if df.empty: return df
    return df[(df["delivery_year"]==year) & (df["delivery_week"]<=max_week)]

def detect_top_customer_declines(df, current_year, current_week,
                                 threshold=ALERT_DECLINE_THRESHOLD,
                                 top_n=ALERT_TOP_CUSTOMERS_N):
    """Customers in this year's top-N (by FOB YTD) whose FOB dropped
    >= `threshold`% vs same window last year. Returns list of dicts."""
    if df.empty: return []
    cur_df  = _ytd_slice(df, current_year,   current_week)
    prev_df = _ytd_slice(df, current_year-1, current_week)
    if cur_df.empty or prev_df.empty: return []
    cur_df  = cur_df[~cur_df["country"].isin(EXCLUDED_COUNTRIES)]
    prev_df = prev_df[~prev_df["country"].isin(EXCLUDED_COUNTRIES)]
    cur_grp = (cur_df.groupby("customer_name")
               .agg(fob_cur=("total_price","sum"),
                    countries=("country", lambda x: ", ".join(sorted(set(x)))))
               .reset_index())
    prev_grp = prev_df.groupby("customer_name").agg(fob_prev=("total_price","sum")).reset_index()
    top_universe = cur_grp.sort_values("fob_cur", ascending=False).head(top_n)["customer_name"].tolist()
    merged = cur_grp.merge(prev_grp, on="customer_name", how="left").fillna({"fob_prev":0.0})
    merged = merged[merged["customer_name"].isin(top_universe)]
    out=[]
    for _,r in merged.iterrows():
        prev = safe_float(r["fob_prev"]); cur = safe_float(r["fob_cur"])
        if prev<=0: continue                # need prior to compare
        chg = (cur-prev)/prev*100
        if chg <= -threshold:
            out.append({
                "customer": r["customer_name"],
                "countries": r.get("countries",""),
                "fob_cur": cur, "fob_prev": prev,
                "change_pct": chg, "gap": prev-cur,
            })
    out.sort(key=lambda x: x["change_pct"])    # worst first
    return out

def detect_countries_behind_target(df, current_year, current_week, targets_by_country):
    """Countries whose YTD FOB is materially below their linear target pace.
    Uses the same logic as the Country Targets tab: required-by-week
    = (current_week / 52) * full_year_target. Flag when actual / required < 90%."""
    if df.empty or not targets_by_country: return []
    cur_df  = _ytd_slice(df, current_year,   current_week)
    prev_df = df[df["delivery_year"]==current_year-1]
    if cur_df.empty: return []
    cur_df  = cur_df[~cur_df["country"].isin(EXCLUDED_COUNTRIES)]
    prev_df = prev_df[~prev_df["country"].isin(EXCLUDED_COUNTRIES)]
    cur_g  = cur_df.groupby("country").agg(fob_cur=("total_price","sum")).reset_index()
    prev_g = prev_df.groupby("country").agg(fob_prev=("total_price","sum")).reset_index() if not prev_df.empty else pd.DataFrame(columns=["country","fob_prev"])
    base = cur_g.merge(prev_g, on="country", how="outer").fillna(0)
    out=[]
    for _,r in base.iterrows():
        c = r["country"]
        tgt_pct = safe_float(targets_by_country.get(c, 0.0))
        if tgt_pct == 0: continue
        prev = safe_float(r["fob_prev"]); cur = safe_float(r["fob_cur"])
        if prev <= 0: continue              # cannot project a target without baseline
        full_year_target = prev * (1 + tgt_pct/100)
        required_by_now  = full_year_target * (current_week / 52)
        if required_by_now <= 0: continue
        ratio   = cur / required_by_now
        if ratio >= 0.9: continue           # within 10% of pace → not flagged
        pct_done = (cur / full_year_target * 100) if full_year_target>0 else 0
        out.append({
            "country": c,
            "target_pct": tgt_pct,
            "full_year_target": full_year_target,
            "required_by_now": required_by_now,
            "fob_cur": cur,
            "pct_done": pct_done,
            "pace_ratio": ratio,
            "gap": required_by_now - cur,
        })
    out.sort(key=lambda x: x["pace_ratio"])  # worst pace first
    return out

def detect_missing_weekly_shipments(df, current_year, current_week):
    """Countries that historically had shipments in this exact ISO week
    (avg over up to 2 prior years) but have nothing this year for that week.
    Useful to catch gaps in customer follow-up."""
    if df.empty: return []
    this_wk = df[(df["delivery_year"]==current_year) & (df["delivery_week"]==current_week)]
    this_wk = this_wk[~this_wk["country"].isin(EXCLUDED_COUNTRIES)]
    countries_with_orders = set(this_wk["country"].unique())
    out=[]
    for years_back in (1,2):
        prev_yr = current_year - years_back
        prev_wk = df[(df["delivery_year"]==prev_yr) & (df["delivery_week"]==current_week)]
        prev_wk = prev_wk[~prev_wk["country"].isin(EXCLUDED_COUNTRIES)]
        if prev_wk.empty: continue
        prev_g = prev_wk.groupby("country").agg(fob=("total_price","sum"),
                                                ships=("shipment_id","nunique")).reset_index()
        for _,r in prev_g.iterrows():
            c = r["country"]
            if c in countries_with_orders: continue
            if safe_float(r["fob"]) <= 0: continue
            # Avoid duplicating if year-2 also flagged it
            if any(o["country"]==c for o in out): continue
            out.append({
                "country": c,
                "year_referenced": prev_yr,
                "prev_fob": safe_float(r["fob"]),
                "prev_ships": safe_int(r["ships"]),
                "iso_week": current_week,
            })
    out.sort(key=lambda x: x["prev_fob"], reverse=True)
    return out

def detect_new_customers_no_repeat(df, current_year, current_week,
                                   weeks_window=ALERT_NEW_CUSTOMER_WEEKS):
    """Customers whose first-ever appearance was in the last `weeks_window`
    weeks of the current year and who have not bought again since."""
    if df.empty: return []
    cur_df = _ytd_slice(df, current_year, current_week)
    cur_df = cur_df[~cur_df["country"].isin(EXCLUDED_COUNTRIES)]
    if cur_df.empty: return []
    # Only consider customers truly new (no prior-year activity)
    prior = df[df["delivery_year"]<current_year]["customer_name"].unique()
    new_only = cur_df[~cur_df["customer_name"].isin(prior)]
    if new_only.empty: return []
    grp = (new_only.groupby("customer_name")
           .agg(first_week=("delivery_week","min"),
                last_week =("delivery_week","max"),
                weeks_active=("delivery_week","nunique"),
                fob=("total_price","sum"),
                countries=("country", lambda x: ", ".join(sorted(set(x))))).reset_index())
    out=[]
    window_start = max(1, current_week - weeks_window)
    for _,r in grp.iterrows():
        first = safe_int(r["first_week"]); last = safe_int(r["last_week"])
        # Recent first appearance (within window) AND no recent re-buy
        if first < window_start: continue            # not a recent new customer
        weeks_since_last = current_week - last
        if weeks_since_last < 2: continue            # still active, give them time
        if safe_int(r["weeks_active"]) > 1: continue # they did repeat
        out.append({
            "customer": r["customer_name"],
            "first_week": first,
            "last_week":  last,
            "weeks_since_last": weeks_since_last,
            "fob": safe_float(r["fob"]),
            "countries": r["countries"],
        })
    out.sort(key=lambda x: x["fob"], reverse=True)
    return out

def detect_concentration_rising(df, current_year, current_week, top_n=5,
                                delta_pp=ALERT_CONCENTRATION_DELTA):
    """Returns a single-element list if top-N share grew by >= `delta_pp`
    percentage points vs same window last year, else empty."""
    if df.empty: return []
    cur_df  = _ytd_slice(df, current_year,   current_week)
    prev_df = _ytd_slice(df, current_year-1, current_week)
    cur_df  = cur_df[~cur_df["country"].isin(EXCLUDED_COUNTRIES)]
    prev_df = prev_df[~prev_df["country"].isin(EXCLUDED_COUNTRIES)]
    if cur_df.empty or prev_df.empty: return []
    def topn_share(d):
        tot = safe_float(d["total_price"].sum())
        if tot<=0: return None, []
        g = d.groupby("customer_name")["total_price"].sum().sort_values(ascending=False)
        top = g.head(top_n)
        return safe_float(top.sum())/tot*100, list(top.index)
    cur_share, cur_top  = topn_share(cur_df)
    prev_share,prev_top = topn_share(prev_df)
    if cur_share is None or prev_share is None: return []
    delta = cur_share - prev_share
    if delta < delta_pp: return []
    return [{
        "current_share": cur_share,
        "previous_share": prev_share,
        "delta_pp": delta,
        "top_customers": cur_top,
        "year_cur": current_year,
        "year_prev": current_year-1,
        "top_n": top_n,
    }]

# ── Alerts UI ─────────────────────────────────────────────────────────────────
def _alert_card(severity, title, body_html, accent):
    """Render a single alert card with consistent styling."""
    sev_label = {"critical":"CRITICAL","warning":"WARNING","info":"INFO"}.get(severity,"INFO")
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-left:4px solid {accent};
                padding:18px 22px;margin:8px 0;box-shadow:0 1px 6px rgba(26,26,26,.04);">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:8px;">
        <span style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;
                     text-transform:uppercase;color:{accent};font-weight:600;">{sev_label}</span>
        <span style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:500;color:#1A1A1A;">{title}</span>
      </div>
      <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;line-height:1.7;">{body_html}</div>
    </div>""", unsafe_allow_html=True)

def render_alerts(df):
    today_iso    = date.today().isocalendar()
    current_year = today_iso[0]
    current_week = today_iso[1]

    page_header("Executive Alerts", f"ISO Week {current_week}  ·  {date.today().strftime('%B %d, %Y')}  ·  Issues requiring attention")

    # Load persisted targets for the current year
    all_countries_in_data = sorted(c for c in df["country"].dropna().unique() if c not in EXCLUDED_COUNTRIES)
    targets = load_targets_for_year(current_year, all_countries_in_data)

    # Run detectors
    declines      = detect_top_customer_declines(df, current_year, current_week)
    behind_target = detect_countries_behind_target(df, current_year, current_week, targets)
    missing_wks   = detect_missing_weekly_shipments(df, current_year, current_week)
    new_no_repeat = detect_new_customers_no_repeat(df, current_year, current_week)
    concentration = detect_concentration_rising(df, current_year, current_week)

    total_alerts = len(declines)+len(behind_target)+len(missing_wks)+len(new_no_repeat)+len(concentration)

    # ── Summary strip ─────────────────────────────────────────────────────────
    s1,s2,s3,s4,s5 = st.columns(5)
    s1.metric("Customers at risk", f"{len(declines)}")
    s2.metric("Countries off pace", f"{len(behind_target)}")
    s3.metric("Missing this week",  f"{len(missing_wks)}")
    s4.metric("New no-repeat",      f"{len(new_no_repeat)}")
    s5.metric("Concentration",      "RISE" if concentration else "OK",
              delta=(f"+{concentration[0]['delta_pp']:.1f}pp" if concentration else None))

    if total_alerts == 0:
        divider()
        info_strip("✓ No alerts triggered. All tracked indicators are within healthy thresholds for ISO Week "
                   f"<strong>{current_week}</strong> of <strong>{current_year}</strong>.","#2D4A3E")
        return

    divider()

    # ── 1. Top customers in decline ───────────────────────────────────────────
    if declines:
        section_label(f"Top Customers Declining ≥ {int(ALERT_DECLINE_THRESHOLD)}% vs {current_year-1}", "#8C3D3D")
        info_strip(f"Customers in your top {ALERT_TOP_CUSTOMERS_N} (by YTD FOB) whose FOB dropped at least "
                   f"<strong>{int(ALERT_DECLINE_THRESHOLD)}%</strong> compared to the same week-1 to week-{current_week} window last year. "
                   "Action: contact account managers and clients before further erosion.","#8C3D3D")
        for a in declines:
            sev = "critical" if a["change_pct"] <= -50 else "warning"
            accent = "#8C3D3D" if sev=="critical" else "#B8924A"
            body = (f"<strong>{a['customer']}</strong> &nbsp;·&nbsp; "
                    f"FOB this year <strong>$ {a['fob_cur']:,.0f}</strong> vs "
                    f"$ {a['fob_prev']:,.0f} last year &nbsp;·&nbsp; "
                    f"<span style='color:#8C3D3D;font-weight:500;'>{a['change_pct']:+.1f}%</span> "
                    f"(gap $ {a['gap']:,.0f})<br>"
                    f"<span style='color:#7A7A7A;font-size:.78rem;'>Markets: {a['countries']}</span>")
            _alert_card(sev, "Customer in decline", body, accent)
        divider()

    # ── 2. Countries behind target ────────────────────────────────────────────
    if behind_target:
        section_label("Countries Behind Target Pace", "#B8924A")
        info_strip(f"Countries whose YTD FOB is below 90% of the linear pace required to meet their {current_year} target. "
                   "Action: review with commercial team and consider mid-year corrective actions. "
                   "Targets come from the Country Targets tab.","#B8924A")
        for a in behind_target:
            sev = "critical" if a["pace_ratio"] < 0.7 else "warning"
            accent = "#8C3D3D" if sev=="critical" else "#B8924A"
            body = (f"{flag(a['country'])} <strong>{a['country']}</strong> &nbsp;·&nbsp; "
                    f"target {a['target_pct']:+.0f}% &nbsp;·&nbsp; "
                    f"required by W{current_week}: <strong>$ {a['required_by_now']:,.0f}</strong> &nbsp;·&nbsp; "
                    f"actual: $ {a['fob_cur']:,.0f}<br>"
                    f"Pace ratio <strong>{a['pace_ratio']*100:.0f}%</strong> &nbsp;·&nbsp; "
                    f"gap to required: $ {a['gap']:,.0f} &nbsp;·&nbsp; "
                    f"% of full-year target: {a['pct_done']:.1f}%")
            _alert_card(sev, "Country off pace", body, accent)
        divider()

    # ── 3. Missing this-week shipments ────────────────────────────────────────
    if missing_wks:
        section_label(f"Countries with No Shipments in Week {current_week}", "#4A6080")
        info_strip(f"These countries had shipments in ISO Week <strong>{current_week}</strong> in prior years "
                   "but have nothing recorded for the same week this year. Action: verify with sales whether the "
                   "order is delayed, was lost, or is a seasonal gap.","#4A6080")
        for a in missing_wks:
            body = (f"{flag(a['country'])} <strong>{a['country']}</strong> &nbsp;·&nbsp; "
                    f"<strong>0 shipments</strong> in Week {a['iso_week']}, {current_year}<br>"
                    f"<span style='color:#7A7A7A;'>Same week in {a['year_referenced']}: "
                    f"{a['prev_ships']} shipment{'s' if a['prev_ships']!=1 else ''} "
                    f"&nbsp;·&nbsp; $ {a['prev_fob']:,.0f} FOB</span>")
            _alert_card("info", "Expected shipment missing", body, "#4A6080")
        divider()

    # ── 4. New customers without repeat ───────────────────────────────────────
    if new_no_repeat:
        section_label("New Customers Without Repeat Order", "#B8924A")
        info_strip(f"Customers whose first-ever order was within the last <strong>{ALERT_NEW_CUSTOMER_WEEKS} weeks</strong> "
                   "and who have not placed another order since. Risk of being lost before becoming recurring. "
                   "Action: outreach to confirm satisfaction and capture next order.","#B8924A")
        for a in new_no_repeat:
            body = (f"<strong>{a['customer']}</strong> &nbsp;·&nbsp; "
                    f"first order Week {a['first_week']}, last order Week {a['last_week']} &nbsp;·&nbsp; "
                    f"<strong>{a['weeks_since_last']} weeks</strong> since last activity<br>"
                    f"FOB so far: $ {a['fob']:,.0f} &nbsp;·&nbsp; "
                    f"<span style='color:#7A7A7A;font-size:.78rem;'>Markets: {a['countries']}</span>")
            _alert_card("warning", "Recent customer at risk", body, "#B8924A")
        divider()

    # ── 5. Concentration rising ───────────────────────────────────────────────
    if concentration:
        c = concentration[0]
        section_label("Customer Concentration Rising", "#6B4080")
        info_strip(f"Your top-{c['top_n']} customers account for a higher share of FOB than they did last year, "
                   "increasing dependency risk.","#6B4080")
        top_list = " &nbsp;·&nbsp; ".join(c["top_customers"])
        body = (f"Top {c['top_n']} share &nbsp;·&nbsp; "
                f"<strong>{c['current_share']:.1f}%</strong> in {c['year_cur']} vs "
                f"{c['previous_share']:.1f}% in {c['year_prev']} &nbsp;·&nbsp; "
                f"<span style='color:#6B4080;font-weight:500;'>+{c['delta_pp']:.1f}pp</span><br>"
                f"<span style='color:#7A7A7A;font-size:.78rem;'>Top accounts: {top_list}</span>")
        _alert_card("warning", "Concentration risk", body, "#6B4080")

# ════════════════════════════════════════════════════════════════════════════
# LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
def render_by_destination(df, accent, dl_key):
    if df.empty: st.info("No shipments found for this period."); return
    for country in sorted(df["country"].unique()):
        cdf=df[df["country"]==country]
        n_s=n_shipments(cdf); fob_t=safe_float(cdf["total_price"].sum())
        country_strip(country,n_s,fob_t,accent)
        for airport in sorted(cdf["iata_code"].dropna().unique()):
            adf=cdf[cdf["iata_code"]==airport]
            n_sa=n_shipments(adf); n_prod=len(adf)
            units=safe_int(adf["total_quantity"].sum()); fob_a=safe_float(adf["total_price"].sum())
            with st.expander(f"✈  {airport}   {n_sa} shipment{'s' if n_sa!=1 else ''}  ·  {n_prod} line{'s' if n_prod!=1 else ''}  ·  {units:,} units  ·  $ {fob_a:,.0f}",expanded=(n_s==1)):
                for sid,sdf in adf.groupby("shipment_id",sort=False):
                    shipment_row(sdf["customer_name"].iloc[0],sdf["supply_source_name"].iloc[0],len(sdf),safe_int(sdf["total_quantity"].sum()),safe_float(sdf["total_price"].sum()),accent)
                    line_cols=[c for c in ["crop_name","variety_name","product","total_quantity","total_price","order_type"] if c in sdf.columns]
                    ldf=sdf[line_cols].copy(); ldf.columns=[c.replace("_"," ").title() for c in ldf.columns]
                    if "Total Price"    in ldf.columns: ldf["Total Price"]   =ldf["Total Price"].apply(lambda x:f"$ {x:,.2f}")
                    if "Total Quantity" in ldf.columns: ldf["Total Quantity"]=ldf["Total Quantity"].apply(lambda x:f"{int(x):,}")
                    st.dataframe(ldf,use_container_width=True,hide_index=True)
    buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
    st.download_button("⬇  Export to Excel",data=buf.getvalue(),file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key=f"dl_{dl_key}")

def render_history_by_destination(df, accent, dl_key, file_name="logistics_history.xlsx"):
    """Same layout as render_by_destination but groups shipments inside each airport
    by ISO week (most recent first) and shows the week label above each shipment.
    Used by the History tab where shipments span many weeks."""
    if df.empty: st.info("No historical shipments found for this period."); return
    for country in sorted(df["country"].unique()):
        cdf=df[df["country"]==country]
        n_s=n_shipments(cdf); fob_t=safe_float(cdf["total_price"].sum())
        country_strip(country,n_s,fob_t,accent)
        for airport in sorted(cdf["iata_code"].dropna().unique()):
            adf=cdf[cdf["iata_code"]==airport]
            n_sa=n_shipments(adf); n_prod=len(adf)
            units=safe_int(adf["total_quantity"].sum()); fob_a=safe_float(adf["total_price"].sum())
            n_weeks=adf["delivery_week"].nunique()
            with st.expander(f"✈  {airport}   {n_sa} shipment{'s' if n_sa!=1 else ''}  ·  {n_prod} line{'s' if n_prod!=1 else ''}  ·  {n_weeks} week{'s' if n_weeks!=1 else ''}  ·  {units:,} units  ·  $ {fob_a:,.0f}",expanded=False):
                # Sort year-week pairs descending (most recent first)
                yw_pairs=sorted(adf[["delivery_year","delivery_week"]].drop_duplicates().values.tolist(),
                                key=lambda x:(int(x[0]),int(x[1])), reverse=True)
                for yw in yw_pairs:
                    wy,ww=int(yw[0]),int(yw[1])
                    wdf_h=adf[(adf["delivery_year"]==wy)&(adf["delivery_week"]==ww)]
                    wk_n_s=n_shipments(wdf_h); wk_units=safe_int(wdf_h["total_quantity"].sum())
                    wk_fob=safe_float(wdf_h["total_price"].sum())
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:12px;margin:14px 0 4px 0;
                                padding:6px 0;border-bottom:1px dashed #DDD8D0;">
                      <span style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;
                                   text-transform:uppercase;color:{accent};font-weight:500;">📅 {week_label(wy,ww)}</span>
                      <span style="margin-left:auto;font-family:Jost,sans-serif;font-size:.7rem;color:#7A7A7A;">
                        {wk_n_s} shipment{'s' if wk_n_s!=1 else ''} · {wk_units:,} units · $ {wk_fob:,.0f}
                      </span>
                    </div>""",unsafe_allow_html=True)
                    for sid,sdf in wdf_h.groupby("shipment_id",sort=False):
                        shipment_row(sdf["customer_name"].iloc[0],sdf["supply_source_name"].iloc[0],
                                     len(sdf),safe_int(sdf["total_quantity"].sum()),
                                     safe_float(sdf["total_price"].sum()),accent)
                        line_cols=[c for c in ["crop_name","variety_name","product","total_quantity","total_price","order_type"] if c in sdf.columns]
                        ldf=sdf[line_cols].copy(); ldf.columns=[c.replace("_"," ").title() for c in ldf.columns]
                        if "Total Price"    in ldf.columns: ldf["Total Price"]   =ldf["Total Price"].apply(lambda x:f"$ {x:,.2f}")
                        if "Total Quantity" in ldf.columns: ldf["Total Quantity"]=ldf["Total Quantity"].apply(lambda x:f"{int(x):,}")
                        st.dataframe(ldf,use_container_width=True,hide_index=True)
    buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
    st.download_button("⬇  Export History to Excel",data=buf.getvalue(),file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key=f"dl_{dl_key}")

def render_logistics(df_all):
    import plotly.graph_objects as go
    today=date.today(); iso=today.isocalendar(); cur_year,cur_week=iso[0],iso[1]
    VIEWS=[
        (-1,"Past Week",   "Quality Follow-up",  "#8C3D3D","The logistics team must contact the customer to confirm receipt and quality. If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
        ( 0,"Current Week","Arrival Monitoring", "#2D4A3E","Confirm material has arrived at destination. Send all final documents including the <strong>final commercial invoice</strong>."),
        ( 1,"Week +1",     "Dispatch Closure",   "#B8924A","Coordinate dispatch closure with customs agents. <em>If documentation is incomplete, shipments may be delayed with prior <strong>Sales Manager approval</strong>.</em>"),
        ( 2,"Week +2",     "Document Review",    "#4A6080","Review draft documents with customs agents: AWB, phytosanitary certificate, commercial invoice, packing list, and certificate of origin."),
        ( 3,"Week +3",     "Advance Preview",    "#6B4080","Verify special requirements: Colombia → certificate of origin; Brazil &amp; Costa Rica → import permit. Ask customers about last-minute additions."),
    ]
    week_dfs=[filter_week(df_all,*add_weeks(cur_year,cur_week,d)) for d,*_ in VIEWS]
    page_header("Logistics Dashboard",f"ISO Week {cur_week}  ·  {today.strftime('%B %d, %Y')}  ·  Air Freight Operations")
    tab_labels=["Overview","History"]+[v[1] for v in VIEWS]+["Future Shipments"]
    all_tabs=st.tabs(tab_labels)

    with all_tabs[0]:
        all_5w=pd.concat(week_dfs,ignore_index=True) if any(not d.empty for d in week_dfs) else pd.DataFrame()
        section_label("Five-Week Rolling Summary")
        n_s=n_shipments(all_5w) if not all_5w.empty else 0
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("Shipments",f"{n_s:,}"); c2.metric("Product Lines",f"{len(all_5w):,}")
        c3.metric("Total Units",f"{safe_int(all_5w['total_quantity'].sum() if not all_5w.empty else 0):,}")
        c4.metric("FOB Value",f"$ {safe_float(all_5w['total_price'].sum() if not all_5w.empty else 0):,.0f}")
        c5.metric("Destinations",f"{all_5w['country'].nunique() if not all_5w.empty else 0:,}")
        divider()
        section_label("Weekly Breakdown")
        ov_rows=[]
        for i,(delta,wt,vt,accent,_) in enumerate(VIEWS):
            vy,vw=add_weeks(cur_year,cur_week,delta); wdf=week_dfs[i]
            lbl="Past" if delta==-1 else ("Current" if delta==0 else f"+{delta}w")
            ov_rows.append({"Period":f"{lbl}  ·  {week_label(vy,vw)}","Stage":vt,"Shipments":n_shipments(wdf) if not wdf.empty else 0,"Lines":len(wdf),"Units":f"{safe_int(wdf['total_quantity'].sum()):,}","FOB":f"$ {safe_float(wdf['total_price'].sum()):,.0f}","Countries":wdf["country"].nunique() if not wdf.empty else 0})
        st.dataframe(pd.DataFrame(ov_rows),use_container_width=True,hide_index=True)
        if not all_5w.empty:
            divider(); section_label("Destination Breakdown  ·  All Active Weeks")
            dest=all_5w.groupby(["country","iata_code"]).agg(ships=("shipment_id","nunique"),lines=("total_quantity","count"),units=("total_quantity","sum"),fob=("total_price","sum")).reset_index().sort_values(["country","fob"],ascending=[True,False])
            dest["Country"]=dest["country"].apply(lambda c:f"{flag(c)}  {c}")
            dest=dest.rename(columns={"iata_code":"Airport","ships":"Shipments","lines":"Lines","units":"Units","fob":"FOB (USD)"})
            dest["FOB (USD)"]=dest["FOB (USD)"].apply(lambda x:f"$ {x:,.0f}"); dest["Units"]=dest["Units"].apply(lambda x:f"{int(x):,}")
            st.dataframe(dest[["Country","Airport","Shipments","Lines","Units","FOB (USD)"]],use_container_width=True,hide_index=True)

    # ── History tab (between Overview and Past Week) ─────────────────────────
    HISTORY_ACCENT="#5C1F1F"
    with all_tabs[1]:
        # Cutoff: anything strictly before the Past Week (W-1) Monday
        past_year, past_week = add_weeks(cur_year, cur_week, -1)
        try:
            cutoff_date = date.fromisocalendar(past_year, past_week, 1)
        except Exception:
            cutoff_date = today
        def _is_history(r):
            try:
                d = date.fromisocalendar(int(r["delivery_year"]), int(r["delivery_week"]), 1)
                return d < cutoff_date
            except Exception:
                return False
        if df_all.empty:
            history_df_all = df_all
        else:
            history_df_all = df_all[df_all.apply(_is_history, axis=1)]
        # Restrict to current year and previous year only
        history_df_all = history_df_all[history_df_all["delivery_year"].isin([cur_year, cur_year-1])]

        section_label("Shipment History  —  Past Dispatches", HISTORY_ACCENT)
        st.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">All shipments dispatched before {week_label(past_year,past_week)}</div>',unsafe_allow_html=True)
        info_strip("Historical record of past shipments for the current and previous year. Documentation and quality cycles for these shipments are already closed. Use this view for trend lookups, customer call preparation, and reference.", HISTORY_ACCENT)

        if history_df_all.empty:
            st.info("No historical shipments to show for the current or previous year.")
        else:
            # Year toggle (only show years with data)
            yr_choices=[]
            if cur_year in history_df_all["delivery_year"].values:
                yr_choices.append((cur_year, f"{cur_year}  ·  Current Year"))
            if (cur_year-1) in history_df_all["delivery_year"].values:
                yr_choices.append((cur_year-1, f"{cur_year-1}  ·  Previous Year"))
            yr_labels=[label for _,label in yr_choices]
            sel_label=st.radio("Year", yr_labels, horizontal=True, key="hist_year_sel")
            sel_year=next(y for y,lbl in yr_choices if lbl==sel_label)
            hist_df=history_df_all[history_df_all["delivery_year"]==sel_year]

            n_s=n_shipments(hist_df) if not hist_df.empty else 0
            n_weeks=hist_df["delivery_week"].nunique() if not hist_df.empty else 0
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Shipments",f"{n_s:,}")
            c2.metric("Product Lines",f"{len(hist_df):,}")
            c3.metric("Total Units",f"{safe_int(hist_df['total_quantity'].sum() if not hist_df.empty else 0):,}")
            c4.metric("FOB Value",f"$ {safe_float(hist_df['total_price'].sum() if not hist_df.empty else 0):,.0f}")
            c5.metric("Weeks Recorded",f"{n_weeks:,}")
            divider()
            section_label(f"Shipments by Destination  ·  {sel_year}", HISTORY_ACCENT)
            render_history_by_destination(hist_df, HISTORY_ACCENT,
                                          dl_key=f"history_{sel_year}",
                                          file_name=f"logistics_history_{sel_year}.xlsx")

    for tab,(delta,wt,vt,accent,msg),wdf in zip(all_tabs[2:-1],VIEWS,week_dfs):
        with tab:
            vy,vw=add_weeks(cur_year,cur_week,delta); n_s=n_shipments(wdf) if not wdf.empty else 0
            section_label(f"{wt}  —  {vt}",accent)
            st.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">{week_label(vy,vw)}</div>',unsafe_allow_html=True)
            info_strip(msg,accent)
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Shipments",f"{n_s:,}"); c2.metric("Product Lines",f"{len(wdf):,}")
            c3.metric("Total Units",f"{safe_int(wdf['total_quantity'].sum()):,}")
            c4.metric("FOB Value",f"$ {safe_float(wdf['total_price'].sum()):,.0f}")
            c5.metric("Destinations",f"{wdf['country'].nunique() if not wdf.empty else 0:,}")
            divider(); section_label("Shipments by Destination",accent)
            render_by_destination(wdf,accent,dl_key=f"{delta}_{vw}_{vy}")

    with all_tabs[-1]:
        import datetime as _dt
        cutoff_year,cutoff_week=add_weeks(cur_year,cur_week,3)
        cutoff_date=_dt.date.fromisocalendar(cutoff_year,cutoff_week,7)
        def row_date(r):
            try: return _dt.date.fromisocalendar(int(r["delivery_year"]),int(r["delivery_week"]),1)
            except: return _dt.date.min
        future_df=df_all[df_all.apply(lambda r:row_date(r)>cutoff_date,axis=1)].copy()
        section_label("Future Shipments  —  Beyond Week +3","#6B4080")
        st.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">All confirmed orders after {week_label(cutoff_year,cutoff_week)}</div>',unsafe_allow_html=True)
        info_strip("Confirmed orders already in the system beyond the active logistics window. Review with the commercial team to ensure documentation preparation starts on time.","#6B4080")
        if future_df.empty:
            st.info("No future shipments found beyond Week +3.")
        else:
            n_fut=n_shipments(future_df); n_weeks=future_df["delivery_week"].nunique()
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Shipments",f"{n_fut:,}"); c2.metric("Product Lines",f"{len(future_df):,}")
            c3.metric("Total Units",f"{safe_int(future_df['total_quantity'].sum()):,}")
            c4.metric("FOB Value",f"$ {safe_float(future_df['total_price'].sum()):,.0f}")
            c5.metric("Weeks Ahead",f"{n_weeks:,}")
            divider()
            for country in sorted(future_df["country"].unique()):
                cdf=future_df[future_df["country"]==country]
                country_strip(country,n_shipments(cdf),safe_float(cdf["total_price"].sum()),"#6B4080")
                for yw in sorted(cdf[["delivery_year","delivery_week"]].drop_duplicates().values.tolist()):
                    wy,ww=int(yw[0]),int(yw[1])
                    wdf_f=cdf[(cdf["delivery_year"]==wy)&(cdf["delivery_week"]==ww)]
                    with st.expander(f"📅  {week_label(wy,ww)}   ·   {n_shipments(wdf_f)} shipment{'s' if n_shipments(wdf_f)!=1 else ''}  ·  $ {safe_float(wdf_f['total_price'].sum()):,.0f} FOB",expanded=False):
                        for sid,sdf in wdf_f.groupby("shipment_id",sort=False):
                            shipment_row(f"{sdf['customer_name'].iloc[0]}  ✈ {sdf['iata_code'].iloc[0]}",sdf["supply_source_name"].iloc[0],len(sdf),safe_int(sdf["total_quantity"].sum()),safe_float(sdf["total_price"].sum()),"#6B4080")
                            lc=[c for c in ["crop_name","variety_name","product","total_quantity","total_price","order_type"] if c in sdf.columns]
                            ldf=sdf[lc].copy(); ldf.columns=[c.replace("_"," ").title() for c in ldf.columns]
                            if "Total Price"    in ldf.columns: ldf["Total Price"]   =ldf["Total Price"].apply(lambda x:f"$ {x:,.2f}")
                            if "Total Quantity" in ldf.columns: ldf["Total Quantity"]=ldf["Total Quantity"].apply(lambda x:f"{int(x):,}")
                            st.dataframe(ldf,use_container_width=True,hide_index=True)
            divider()
            buf=io.BytesIO(); future_df.to_excel(buf,index=False,engine="openpyxl")
            st.download_button("⬇  Export Future Shipments to Excel",data=buf.getvalue(),file_name="future_shipments.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",key="dl_future")

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    current_user=get_user(st.session_state.get("username",""))
    display_name=current_user["display"]; is_admin=current_user["role"]=="admin"
    st.markdown(f"""
    <div style="padding:32px 0 6px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:400;color:#F5EDE8;letter-spacing:.04em;line-height:1.2;">✦ Export Ops</div>
      <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:#C4A090;margin-top:4px;">Management Suite</div>
    </div>
    <div style="border-top:1px solid rgba(212,176,168,.25);margin:14px 0 10px 0;"></div>
    <div style="font-family:Jost,sans-serif;font-size:.74rem;color:#D4B8B0;padding-bottom:14px;">
      <span style="color:#C4A090;font-size:.60rem;letter-spacing:.12em;text-transform:uppercase;">Signed in as</span><br>
      <span style="color:#F5EDE8;font-weight:500;">{display_name}</span>
    </div>
    <div style="border-top:1px solid rgba(212,176,168,.25);margin:0 0 16px 0;"></div>
    """,unsafe_allow_html=True)
    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Navigation</p>',unsafe_allow_html=True)
    nav_options=["🔔  Alerts","📦  Logistics","📈  Commercial Intelligence"]
    if is_admin: nav_options.append("👤  User Management")
    page=st.radio("page_nav",nav_options,label_visibility="collapsed",key="page_selector")
    st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:16px 0;"></div>',unsafe_allow_html=True)
    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Data Source</p>',unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload Excel file",type=["xlsx","xls"],label_visibility="collapsed")
    if "df" in st.session_state and st.session_state.df is not None:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.07);border:1px solid rgba(212,176,168,.2);
                    padding:12px 14px;margin-top:10px;font-family:Jost,sans-serif;font-size:.74rem;line-height:2;">
          <span style="color:#D4B070;">●</span>
          <span style="color:#F5EDE8;margin-left:6px;">{st.session_state.filename}</span><br>
          <span style="color:#C4A090;">Updated&nbsp;&nbsp;</span><span style="color:#F5EDE8;">{st.session_state.loaded_at}</span><br>
          <span style="color:#C4A090;">Records&nbsp;&nbsp;&nbsp;</span><span style="color:#F5EDE8;">{len(st.session_state.df):,}</span>
        </div>""",unsafe_allow_html=True)
        if page=="📦  Logistics":
            st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:16px 0;"></div>',unsafe_allow_html=True)
            st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Filters</p>',unsafe_allow_html=True)
            origins  =st.multiselect("Origin",  sorted(st.session_state.df["supply_source_name"].dropna().unique()),placeholder="All origins",  key="log_origins")
            customers=st.multiselect("Customer",sorted(st.session_state.df["customer_name"].dropna().unique()),      placeholder="All customers",key="log_customers")
            st.session_state.origins=origins; st.session_state.customers=customers
    st.sidebar.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:24px 0 12px 0;"></div>',unsafe_allow_html=True)
    if st.sidebar.button("Sign Out",key="signout_btn"):
        for k in ["authenticated","username","login_failed","df","filename","loaded_at","origins","customers"]:
            st.session_state.pop(k,None)
        st.rerun()

# ── File processing ───────────────────────────────────────────────────────────
if uploaded is not None:
    df_new,err=load_and_validate(uploaded)
    if err: st.error(f"⚠️ {err}"); st.stop()
    st.session_state.df=df_new; st.session_state.filename=uploaded.name
    st.session_state.loaded_at=datetime.now().strftime("%b %d, %Y  %H:%M")
    if "origins"   not in st.session_state: st.session_state.origins=[]
    if "customers" not in st.session_state: st.session_state.customers=[]

# ── Welcome screen ────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state.df is None:
    st.markdown("""
    <div style="max-width:640px;margin:100px auto 0 auto;padding:0 24px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:300;color:#1A1A1A;letter-spacing:.01em;line-height:1.15;text-align:center;margin-bottom:6px;">Export Operations Suite</div>
      <div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;color:#7A7A7A;text-align:center;margin-bottom:48px;">Fresh Flowers &amp; Vegetables &nbsp;·&nbsp; Air Freight</div>
      <div style="border-top:1px solid #DDD8D0;border-bottom:1px solid #DDD8D0;padding:36px 0;margin-bottom:36px;text-align:center;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-style:italic;color:#7A7A7A;margin-bottom:16px;">Upload your weekly Excel file to begin</div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;line-height:1.9;">Use the <strong style="color:#8C3D3D;">sidebar uploader</strong> on the left.<br>Switch between <strong>Logistics</strong> and <strong>Commercial Intelligence</strong> using the navigation menu.</div>
      </div>
      <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;padding:28px 32px;">
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:#8C3D3D;margin-bottom:14px;">Required columns</div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;line-height:2.1;">delivery_year &nbsp;·&nbsp; delivery_week &nbsp;·&nbsp; customer_name<br>supply_source_name &nbsp;·&nbsp; destination &nbsp;·&nbsp; total_quantity &nbsp;·&nbsp; total_price</div>
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:#7A7A7A;margin:20px 0 10px 0;">Optional columns</div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#7A7A7A;line-height:2.1;">secondary_customer_name &nbsp;·&nbsp; crop_name &nbsp;·&nbsp; variety_name &nbsp;·&nbsp; order_type &nbsp;·&nbsp; product</div>
      </div>
    </div>""",unsafe_allow_html=True)
    st.stop()

# ── Routing ───────────────────────────────────────────────────────────────────
if page=="🔔  Alerts":
    render_alerts(st.session_state.df.copy())
elif page=="📈  Commercial Intelligence":
    render_commercial(st.session_state.df.copy())
elif page=="👤  User Management":
    if is_admin: render_admin()
    else: st.error("Access denied.")
else:
    df_log=apply_filters(st.session_state.df.copy(),st.session_state.get("origins",[]),st.session_state.get("customers",[]))
    render_logistics(df_log)
