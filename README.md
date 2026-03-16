# Export Logistics Dashboard
**Fresh Flowers & Vegetables · Air Freight Operations**

A Streamlit executive dashboard for monitoring weekly export shipment logistics — from advance order preview through quality follow-up — built with the Rosaprima visual identity.

---

## Quick Start

```bash
# 1. Clone or copy the project folder
cd logistics-dashboard

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## Loading & Updating Data

1. Use the **sidebar uploader** to load your `.xlsx` or `.xls` file.
2. The dashboard validates the file and renders all 5 views automatically.
3. To update data, simply upload a new Excel file — the dashboard refreshes **without restarting**.
4. The sidebar shows the filename, last update timestamp, and record count.

---

## Excel File Format

### Required Columns

| Column | Description |
|---|---|
| `delivery_year` | ISO year of delivery (e.g. `2024`) |
| `delivery_week` | ISO week number of delivery (e.g. `14`) |
| `customer_name` | Primary customer name |
| `supply_source_name` | Product origin country (e.g. `Colombia`, `Ecuador`) |
| `destination` | IATA destination airport code (e.g. `MIA`, `AMS`) |
| `total_quantity` | Total units per order line |
| `total_price` | Total FOB value in USD |

### Optional Columns

| Column | Description |
|---|---|
| `secondary_customer_name` | End client when primary customer is a distributor |
| `crop_name` | Crop type (e.g. `Rose`, `Carnation`) |
| `variety_name` | Specific variety name |
| `order_type` | Order classification |
| `product` | Product description |
| `Total_Unit_Price` | FOB unit price |

---

## Dashboard Views

| Tab | Scope | Key Action |
|---|---|---|
| **Past Week — Quality Follow-up** | Week −1 | Confirm receipt & material quality with customer |
| **Current Week — Arrival Monitoring** | Week 0 | Confirm arrival; send final docs & invoice |
| **Week +1 — Dispatch Closure** | Week +1 | Coordinate customs closure; flag doc delays |
| **Week +2 — Document Review** | Week +2 | Draft-review AWB, phyto cert, invoice, packing list, COO |
| **Week +3 — Advance Order Preview** | Week +3 | Verify special permits; offer last-minute add-ons |

The **current week** is detected automatically from the system clock (ISO 8601).

---

## Filters (Sidebar)

- **Origin** — filter by `supply_source_name`
- **Customer** — filter by `customer_name`

Filters apply across all 5 views simultaneously.

---

## Export

Each view has a **⬇ Export to Excel** button that downloads the filtered table for that week.

---

## Tech Stack

- Python 3.9+
- [Streamlit](https://streamlit.io) — UI framework
- [Pandas](https://pandas.pydata.org) — data processing
- [openpyxl](https://openpyxl.readthedocs.io) — Excel I/O

---

## Visual Identity

| Token | Hex | Usage |
|---|---|---|
| Ivory | `#FAF7F2` | Page background |
| Burgundy | `#9C4A52` | Primary accent, headings |
| Sage | `#8A9E85` | Secondary accent |
| Gold | `#B8974A` | Ornamental elements |
| Charcoal | `#2C2825` | Sidebar, body text |

Typography: **Cormorant Garamond** (titles) + **Jost** (body)
