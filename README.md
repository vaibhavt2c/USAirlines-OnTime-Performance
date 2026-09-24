# ✈️ US Airlines On-Time Performance Analysis

An interactive **Streamlit** dashboard for exploring, aggregating, and visualising US domestic airline on-time performance data sourced from the Bureau of Transportation Statistics (BTS) — July 2025 snapshot.

![Dashboard Header](screenshots/01_dashboard_header.png)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit Dashboard

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

### 3. Run the Jupyter Notebook

```bash
jupyter notebook Vaibhav_Tukaram_Chaudhari_USAirlinesOnTimePerformance.ipynb
```

The notebook opens in your browser. Run all cells from top to bottom (`Kernel → Restart & Run All`).

---

## 📁 Project Structure

```
US Airline On Time Performance Analysis/
├── Vaibhav_Tukaram_Chaudhari_USAirlinesOnTimePerformance.ipynb  # Jupyter Notebook (10 sections, full analysis)
├── app.py                                      # Streamlit interactive dashboard
├── requirements.txt                            # Python dependencies
├── README.md                                   # This file
├── Vaibhav_Tukaram_Chaudhari_ProjectReport.docx                 # Full project report (8 sections, 9 tables)
├── flight_delays_2025_07.csv                   # Default dataset (BTS, July 2025)
└── screenshots/                                # 17 dashboard screenshot PNGs
```

---

## 📦 Requirements

| Package      | Version  | Purpose                          |
|-------------|----------|----------------------------------|
| `pandas`    | ≥2.0.0   | Data loading and wrangling       |
| `numpy`     | ≥1.24.0  | Numerical computations           |
| `streamlit` | ≥1.35.0  | Interactive web UI framework     |
| `plotly`    | ≥5.20.0  | Interactive charts               |
| `jupyter`   | ≥1.0.0   | Jupyter Notebook runtime         |
| `notebook`  | ≥7.0.0   | Classic notebook interface       |
| `ipykernel` | ≥6.0.0   | Python kernel for notebooks      |

Install them all at once:

```bash
pip install -r requirements.txt
```

---

## 🗂️ Dataset

**Default file:** `flight_delays_2025_07.csv`  
**Source:** [BTS Reporting Carrier On-Time Performance](https://www.transtats.bts.gov/)  
**Kaggle Dataset:** [US Flight Delays 2025 — BTS On-Time Performance](https://www.kaggle.com/datasets/a7madmostafa/us-flight-delays-2025-bts-on-time-performance)  
**Period:** July 2025  
**Size:** ~631,000 flight records across 40 columns

### Key Columns

| Column | Description |
|---|---|
| `Reporting_Airline` | Two-letter IATA carrier code |
| `FlightDate` | Scheduled flight date |
| `Origin` / `Dest` | Origin / destination IATA airport |
| `DepDelay` / `ArrDelay` | Departure / arrival delay (minutes) |
| `Cancelled` | 1 = cancelled flight |
| `CancellationCode` | A=Carrier, B=Weather, C=NAS, D=Security |
| `CarrierDelay`, `WeatherDelay`, … | Delay cause breakdown (minutes) |
| `Distance` | Great-circle distance (miles) |

---

## 🎛️ Features

### 1. Dynamic Dataset Uploader

Upload any CSV file following the BTS on-time schema via the sidebar file widget. If no file is uploaded, the app automatically falls back to the bundled `flight_delays_2025_07.csv`.

---

### 2. On-Time Performance Overview — KPI Cards & Metric Gauges

Seven headline KPI scorecards plus four Plotly Indicator gauges give an instant system-level health snapshot:
- **Total Flights · On-Time · Delayed · Cancelled · Diverted**
- **Avg Arrival Delay · Avg Departure Delay**
- Gauges for On-Time Rate, Avg Arrival Delay, Avg Departure Delay, and Cancellation Rate with traffic-light colouring

![KPI Scorecards and Gauge Charts](screenshots/02_kpi_gauges.png)

---

### 3. Data Quality & Validation

Automatically inspects the loaded dataset, identifies missing values, and displays summary statistics.

- Null-value overview by column (count + percentage)
- Numeric summary statistics (`describe()`) for all key delay/performance fields
- Raw data preview (first 200 rows)

![Data Quality & Validation Module](screenshots/13_data_quality.png)

![Numeric Summary Statistics](screenshots/14_numeric_stats.png)

![Raw Data Preview](screenshots/15_raw_data.png)

---

### 4. Delay Breakdown by Airline / Carrier

A grouped bar chart comparing average **arrival** and **departure** delays side-by-side across all 14 carriers, sorted by on-time rate. Clearly highlights which carriers lead and which lag.

![Average Arrival vs Departure Delay by Airline — Grouped Bar](screenshots/03_delay_grouped_bar.png)

On-time arrival rate per carrier with an **80% industry target** reference line, plus cancellation rate ranked by severity:

![On-Time Arrival Rate and Cancellation Rate by Airline](screenshots/04_ontime_cancel_rate.png)

---

### 5. Delay Root Causes — Donut & Stacked Bar Charts

A donut chart showing the five BTS delay cause proportions (**Late Aircraft 40.8% dominates**) plus a side-by-side flight status breakdown (On-Time 70.2% / Delayed 27.3% / Cancelled 2.45%):

![Delay Cause Composition Donut + Flight Status Distribution](screenshots/09_delay_donut_status.png)

Stacked bar chart decomposing delay cause contributions per airline — reveals which carriers are most exposed to each delay type:

![Average Delay Composition by Airline — Stacked Bar](screenshots/05_delay_stacked.png)

---

### 6. Flight Volume & Delay Trends Over Time

A dual-axis time-series showing daily flight volume (blue area) and average arrival delay (red dotted line) across all of July 2025:

![Daily Flight Volume and Average Arrival Delay — July 2025](screenshots/06_daily_trends.png)

Day-of-week performance (Saturday best at 11.8 min · Sunday worst at 21.9 min) and departure-hour bar chart coloured **green → yellow → red** from 05:00 to 18:00:

![Volume & Delay by Day of Week + Avg Delay by Departure Hour](screenshots/07_dow_hourly.png)

---

### 7. Geographic & Route Performance — Scatter Plot & Heatmaps

Scatter plot of **Flight Distance vs Arrival Delay** with bubble size = Air Time, coloured by airline. Shows the near-zero Pearson correlation (−0.006) — longer routes actually perform *better* due to block-time padding:

![Flight Distance vs Arrival Delay Scatter Plot](screenshots/08_scatter.png)

---

### 8. Day × Hour Heatmaps

Three configurable heatmaps (select from dropdown) covering the full 7-day × 24-hour grid:

**Average Arrival Delay (min)** — green in early morning, deep red at 16:00–19:00 peak PM:

![Avg Arrival Delay — Day of Week × Departure Hour Heatmap](screenshots/10_heatmap_avg_delay.png)

**On-Time Rate (%)** — shows the inverse pattern; highest OTP at 05:00–08:00:

![On-Time Rate (%) — Day of Week × Departure Hour Heatmap](screenshots/11_heatmap_ontime_rate.png)

**Flight Volume** — Thursday peaks as the busiest departure day:

![Flight Volume — Day of Week × Departure Hour Heatmap](screenshots/12_heatmap_flight_volume.png)

---

### 9. Custom Metric Calculator

A spreadsheet-style formula builder — pick any two numeric columns and an operator (+, −, ×, ÷) to create a derived metric. Three preset metrics are pre-computed:

- **Total Ground Time** = TaxiOut + TaxiIn → **27.04 min** avg
- **Delay Ratio** (Arr / Dep) → **1.11**
- **Block Time Efficiency (%)** = AirTime ÷ ActualElapsedTime × 100 → **77.52%**

![Custom Metric Calculator](screenshots/16_calculator.png)

---

### 10. Aggregation & Grouping

Dynamic group-by engine with 7 dimensions × 8 metrics. Results shown as a ranked table + colour-coded horizontal bar chart:

![Aggregation & Grouping — Avg Arrival Delay by Airline](screenshots/17_aggregation.png)

---

### 11. Business Insights & Recommendations

Seven auto-generated, filter-aware recommendation cards covering:
- Best & worst performing airline
- Optimal departure hour (05:00–08:00 vs 16:00–19:00)
- Best & worst day of week
- Primary delay driver (Late Aircraft at 33.2 min / 40.8%)
- Most problematic route (CKB→SFB: 325 min avg delay)
- Cancellation risk and mitigation strategy

All insights update dynamically when sidebar filters change.

---

## 🏗️ Architecture

```
main()
 ├── render_uploader()              # File upload + fallback loader
 ├── build_sidebar()                # Filters → returns filtered DataFrame
 ├── render_kpis()                  # 7 KPI metric cards + 4 gauge charts
 ├── render_delay_by_airline()      # Grouped bar + stacked bar by carrier
 ├── render_time_trends()           # Daily line + DOW + hourly bar charts
 ├── render_route_analysis()        # Scatter · Correlation heatmap · Bubbles
 ├── render_delay_causes()          # Donut charts + Day×Hour heatmap
 ├── render_data_quality()          # Null stats + describe + raw preview
 ├── render_custom_calculations()   # Formula builder + preset metrics
 ├── render_aggregation()           # Dynamic group-by table + bar chart
 └── render_business_insights()     # 7 derived recommendation cards
```

Data is loaded once per session via `@st.cache_data` (TTL = 1 hour) to keep interactions fast even on the full 631K-row dataset.

---

## 📊 Key Findings (July 2025)

| Metric | Value |
|---|---|
| Total Flights | 631,428 |
| On-Time Rate | **70.23%** (below 80% benchmark) |
| Average Arrival Delay | 17.35 min |
| Average Departure Delay | 21.51 min |
| Cancellations | 15,473 (2.45%) |
| Best Carrier OTP | Hawaiian Airlines — **80.91%** |
| Worst Carrier OTP | Frontier Airlines — **65.82%** |
| #1 Delay Cause | Late Aircraft Carry-Over — **33.2 min / 40.8%** |
| Best Departure Hour | 05:00 — **−2.1 min** (arrives early) |
| Worst Departure Hour | 17:00 — **+37.3 min** |
| Worst Route (avg delay) | CKB→SFB — **325 min** |

---

## 🔧 Customisation

- **Add a new airline name mapping:** edit the `AIRLINE_NAMES` dict in [`app.py`](app.py)
- **Add more aggregation dimensions:** extend `dim_options` inside `render_aggregation()`
- **Add new visualisations:** create a new tab inside `render_route_analysis()` or `render_delay_causes()`
- **Change the default delay threshold:** set a different `value` in the sidebar slider

---

## 📄 License

MIT — free to use, modify, and distribute.
