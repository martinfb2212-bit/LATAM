# Export Operations Suite

**Fresh Flowers & Vegetables · Air Freight · Commercial + Logistics Intelligence**

A Streamlit executive suite for global export operations. Three integrated modules:

- **Executive Alerts** — first thing you see after sign-in. Auto-detects top customers in decline, countries off target pace, missing weekly shipments, new customers without repeat orders, and rising concentration risk.
- **Logistics Dashboard** — rolling 5-week operational view (Past Week → Week +3) plus a Future Shipments queue, with documentation-stage instructions per week.
- **Commercial Intelligence** — Year-over-Year analysis, Country Targets with pace tracking, customer concentration risk, growth/decline rankings, and seasonality heatmaps.

Authenticated, role-based access. Built with the project's burgundy / sage / ivory visual identity.

---

## Quick Start (Local)

```bash
# 1. Clone the repo
git clone <your-repo-url> logistics-dashboard
cd logistics-dashboard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

App opens at **http://localhost:8501**.

---

## Authentication

The app requires login. On first run, three default users are available:

| Username     | Default Password | Role  |
|--------------|------------------|-------|
| `admin`      | `admin123`       | admin |
| `logistics`  | `log2024`        | user  |
| `commercial` | `com2024`        | user  |

> **Important:** these defaults are intended only for first-run setup. Sign in as `admin` and change every password from **User Management → Change My Password** before sharing the URL.

### How passwords are stored

Passwords are persisted as **bcrypt hashes** in `.streamlit/users.json`. The defaults above exist as plaintext fallbacks in code; the very first time each user signs in, the app silently rehashes their password and writes the hash to disk — so the persistent file never contains plaintext.

You can also define users in `st.secrets` for Streamlit Cloud (see Deployment below).

### Roles

- **admin** — full access. Can add, edit, remove users, and change their own password from the **User Management** page.
- **user** — access to Logistics and Commercial Intelligence only.

---

## Modules

### Executive Alerts

The default landing page after sign-in. Runs five detectors against the loaded master file and surfaces only the items that actually need attention. Detectors are pure functions (covered by the test suite) and can be tuned via constants at the top of the Alerts section in `app.py`.

| Detector | Trigger | Default threshold |
|---|---|---|
| **Top customer decline** | Customer is in this year's top 20 by FOB and dropped vs same window last year | ≥ 20% drop (≥ 50% = critical) |
| **Country behind target** | YTD FOB below 90% of linear pace toward the year's target | Pace ratio < 0.7 = critical |
| **Missing weekly shipment** | Country had shipments in this exact ISO week last year (or 2 years ago) but nothing this year | Any missing |
| **New customer without repeat** | Customer's first ever order was within last 8 weeks and has not bought again for ≥ 2 weeks | Window-based |
| **Concentration rising** | Top-5 customers' YTD share grew vs same window last year | ≥ +5 percentage points |

The summary strip at the top shows a count for each category so you can see the day's situation at a glance. If no thresholds are crossed, the page shows a green "no alerts" notice.

### Logistics Dashboard

Auto-detects the current ISO week and renders 8 tabs:

| Tab | Period | Operational Action |
|---|---|---|
| **Overview** | All active weeks | Five-week rolling KPIs + destination breakdown |
| **History** | All weeks before W −1 (current + previous year) | Reference view of past dispatches grouped by destination, with week labels per shipment |
| **Past Week** | W −1 | Confirm receipt and material quality with customer |
| **Current Week** | W 0 | Confirm arrival, send final docs and commercial invoice |
| **Week +1** | W +1 | Coordinate dispatch closure with customs agents |
| **Week +2** | W +2 | Draft-review AWB, phyto certificate, invoice, packing list, COO |
| **Week +3** | W +3 | Verify special permits (Colombia COO, Brazil/Costa Rica import permits) |
| **Future Shipments** | Beyond W +3 | All confirmed orders queued ahead of the active window |

Each weekly tab groups shipments by destination country → IATA airport → individual shipment, with line-level product detail and an Excel export.

### Commercial Intelligence

Four tabs:

1. **Overview & YoY** — KPIs vs prior year (shipments, FOB, units, customers), weekly FOB trend, country comparison (3 years), country status table with growth badges, customer performance per country, growth opportunity focus columns.
2. **Country Targets** — Set FOB growth percentage per country for the current year. The dashboard computes required FOB, current gap, % completed, and on-track / behind status. Cumulative pace charts show actual vs linear target. **Targets persist across sessions** (saved to `.streamlit/targets.json`).
3. **Customer Intelligence** — Concentration risk (Pareto 80/20), top growing & declining customers, weekly run-rate vs prior year, new customer tracking with weekly trajectory.
4. **Seasonality** — Heatmap of FOB by country × ISO week, strongest weeks ranking, same-week comparison vs prior year, and a YoY shift heatmap.

Filters: Years (multi), Customers (multi), Countries (multi). Toggle scope between **Year-to-Date** (capped at current week) and **Full Year** (all weeks including future confirmed orders).

---

## Excel File Format

### Required Columns

| Column | Description |
|---|---|
| `delivery_year` | ISO year of delivery (e.g. `2026`) |
| `delivery_week` | ISO week number (1–53) |
| `customer_name` | Primary customer |
| `supply_source_name` | Origin country / farm (e.g. `Colombia`, `Ecuador`) |
| `destination` | IATA destination airport code (e.g. `MIA`, `AMS`) |
| `total_quantity` | Total units per order line |
| `total_price` | Total FOB value in USD |

### Optional Columns

| Column | Description |
|---|---|
| `secondary_customer_name` | End client when primary is a distributor |
| `crop_name` | Crop type (e.g. Rose, Carnation) |
| `variety_name` | Specific variety |
| `order_type` | Order classification |
| `product` | Product description |

The app extracts a 3-letter IATA code from `destination` and maps it to country and flag automatically. Unmapped IATAs fall under "Unknown".

`shipment_id` is computed internally as `customer | year-Wweek | origin → IATA` and is the unit of the **Shipments** count. Multiple product lines for the same shipment count as one shipment.

---

## Filters & Scope

**Sidebar filters (Logistics module only):**
- **Origin** — filter by `supply_source_name`
- **Customer** — filter by `customer_name`

**Commercial Intelligence has its own in-page filters** (Years, Customers, Countries, YTD/Full Year scope). Sidebar Origin/Customer filters do **not** propagate to Commercial Intelligence.

The countries Netherlands, Kenya, and Canada are excluded from Commercial Intelligence by design (configured as `EXCLUDED_COUNTRIES` in `app.py`).

---

## Persistence

The app maintains two small JSON files in `.streamlit/`:

| File | Purpose |
|---|---|
| `.streamlit/users.json` | Bcrypt-hashed user credentials (created on first password change or admin save) |
| `.streamlit/targets.json` | Country growth targets per year, e.g. `{"2026": {"Brazil": 20, ...}}` |

Both files are created automatically and updated when you change passwords or save targets. Back them up if you want to preserve state across machine resets.

> **On Streamlit Cloud:** the container's filesystem is ephemeral. Use `st.secrets` for users (read-only) and treat targets as needing to be re-saved if the container restarts — or add a remote storage backend.

---

## Deployment to Streamlit Cloud

1. Push the repo to GitHub.
2. Create a new Streamlit Cloud app pointing to `app.py`.
3. Set Python version: a `runtime.txt` with `python-3.12` is included in the repo.
4. Configure secrets in **Settings → Secrets**:

```toml
[users]
admin      = { password = "$2b$12$...bcrypt-hash...", display = "Administrator", role = "admin" }
logistics  = { password = "$2b$12$...bcrypt-hash...", display = "Logistics",     role = "user"  }
commercial = { password = "$2b$12$...bcrypt-hash...", display = "Commercial",    role = "user"  }
```

> Generate hashes locally with:
> ```python
> import bcrypt; print(bcrypt.hashpw(b"your-password", bcrypt.gensalt()).decode())
> ```

If `st.secrets["users"]` is set, it takes precedence over `users.json`. Plaintext passwords are also accepted in secrets for convenience but bcrypt hashes are strongly recommended for production.

---

## Updating Data

1. Use the **sidebar uploader** to load your `.xlsx` or `.xls` master file.
2. The app validates required columns and renders all views automatically.
3. To refresh, upload a new file — the dashboard updates without restarting.
4. The sidebar shows filename, last update timestamp, and record count.

---

## Tech Stack

- Python 3.12
- [Streamlit](https://streamlit.io) — UI framework
- [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) — data processing
- [openpyxl](https://openpyxl.readthedocs.io) — Excel I/O
- [Plotly](https://plotly.com/python) — interactive charts
- [bcrypt](https://github.com/pyca/bcrypt) — password hashing

---

## Visual Identity

| Token | Hex | Usage |
|---|---|---|
| Linen | `#F5F2ED` | Page background |
| Burgundy | `#8C3D3D` | Primary accent, headings |
| Deep Burgundy | `#5C1F1F` | Sidebar background |
| Forest | `#2D4A3E` | Secondary accent (growth) |
| Gold | `#B8924A` | Tertiary accent (new / advance) |
| Steel Blue | `#4A6080` | Pace / analytical accent |
| Plum | `#6B4080` | Future / out-of-window accent |
| Charcoal | `#1A1A1A` | Body text |

Typography: **Cormorant Garamond** (display) + **Jost** (body / metadata).

---

## File Structure

```
.
├── app.py                 # Single-file Streamlit app
├── requirements.txt       # Python dependencies (with version pinning)
├── runtime.txt            # Python version pin (3.12)
├── README.md              # This file
└── .streamlit/
    ├── users.json         # Bcrypt-hashed credentials (auto-created)
    ├── targets.json       # Persisted country targets (auto-created)
    └── secrets.toml       # Optional: Streamlit Cloud secrets (not in git)
```

---

## Changelog

### v2.2 — Logistics History tab
- **New tab in Logistics: History** — placed between Overview and Past Week. Shows all shipments dispatched before the Past Week boundary, restricted to current and previous year, with a year toggle and KPI strip in the same format as the weekly tabs. Inside each destination airport expander, shipments are grouped by ISO week (most recent first) so it's easy to scan back chronologically.
- New helper `render_history_by_destination` parallels `render_by_destination` but adds week labels per shipment.

### v2.1 — Executive Alerts module
- **New module: Executive Alerts** — first tab in the navigation, surfaces five categories of issues that need attention right now (customer declines, country pace, missing weekly shipments, new-customer drop-off, concentration rise).
- Detector functions are pure and unit-tested (`test_alerts.py`).
- Default thresholds: 20% decline, 0.7 pace ratio (critical), 8-week new-customer window, +5pp concentration delta. All tunable via constants at the top of the Alerts section.

### v2.0 — Priority 1 hardening
- **Auth:** passwords now stored as bcrypt hashes; existing plaintext passwords auto-migrate on first successful login.
- **Targets:** Country Targets now persist to `.streamlit/targets.json` across sessions.
- **Deps:** added `bcrypt`, pinned upper versions, added `runtime.txt`.
- **Docs:** README rewritten to reflect current feature set (Auth, Commercial Intelligence, Country Targets, Future Shipments, Streamlit Cloud deployment, real palette).
