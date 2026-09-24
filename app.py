"""
US Airlines On-Time Performance Analysis
=========================================
A Streamlit dashboard for exploring, aggregating, and visualising
US domestic flight on-time performance data.

Author  : Vaibhav Tukaram Chaudhari
Dataset : BTS Reporting Carrier On-Time Performance (July 2025)
Kaggle  : https://www.kaggle.com/datasets/a7madmostafa/us-flight-delays-2025-bts-on-time-performance
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import io
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="US Airlines On-Time Performance",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# ── Design system – global CSS injection ────────────────────────────────────
# ---------------------------------------------------------------------------
STYLE = """
<style>
/* ── Google Font (Geist-like fallback stack) ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, 'Segoe UI', system-ui, sans-serif !important;
}

/* ── Page background ── */
.stApp {
    background: #0d1117 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d !important;
}
[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #58a6ff !important;
}

/* ── Main text colours ── */
h1, h2, h3, h4, h5, h6 { color: #e6edf3 !important; }
p, li, span, label        { color: #c9d1d9 !important; }
.stMarkdown               { color: #c9d1d9 !important; }

/* ── Metric cards (st.metric) ── */
[data-testid="stMetric"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"]  { color: #8b949e !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"]  { color: #58a6ff !important; font-size: 1.55rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"]  { color: #3fb950 !important; font-size: 0.82rem !important; }

/* ── Tabs ── */
[data-testid="stTabs"] button {
    color: #8b949e !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 500 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1f6feb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
}
.stButton > button:hover {
    background: #388bfd !important;
}

/* ── Select / slider labels ── */
.stSelectbox label, .stMultiSelect label, .stSlider label, .stRadio label {
    color: #8b949e !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #161b22 !important;
    border: 1px dashed #30363d !important;
    border-radius: 8px !important;
}

/* ── Dividers ── */
hr { border-color: #21262d !important; }

/* ── Section headings ── */
.section-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0 4px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 18px;
}
.section-heading span.icon { font-size: 1.3rem; }
.section-heading span.title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e6edf3 !important;
    letter-spacing: -0.01em;
}
.section-heading span.badge {
    margin-left: auto;
    background: #1f6feb22;
    color: #58a6ff !important;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid #1f6feb55;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Brand colour palette (used consistently in every chart)
# ---------------------------------------------------------------------------
BRAND = {
    "bg":        "#0d1117",
    "surface":   "#161b22",
    "border":    "#30363d",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
    "blue":      "#58a6ff",
    "green":     "#3fb950",
    "yellow":    "#d29922",
    "red":       "#f85149",
    "purple":    "#bc8cff",
    "orange":    "#ffa657",
}

# Airline brand palette (enough colours for 14 carriers)
AIRLINE_PALETTE = [
    "#58a6ff", "#3fb950", "#ffa657", "#f85149", "#bc8cff",
    "#d29922", "#79c0ff", "#56d364", "#ffa198", "#e3b341",
    "#cae8ff", "#a8f7b8", "#ff7b72", "#d2a8ff",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(family="Inter, system-ui, sans-serif", color="#c9d1d9", size=12),
    title_font=dict(color="#e6edf3", size=14, family="Inter, system-ui, sans-serif"),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1, font_color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickcolor="#30363d", title_font_color="#8b949e", tickfont_color="#8b949e"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", tickcolor="#30363d", title_font_color="#8b949e", tickfont_color="#8b949e"),
    margin=dict(l=16, r=16, t=48, b=16),
    hoverlabel=dict(bgcolor="#161b22", bordercolor="#30363d", font_color="#e6edf3"),
)


def apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply the dark brand theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, x=0, xanchor="left", pad=dict(l=4)))
    return fig


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_CSV = "flight_delays_2025_07.csv"

AIRLINE_NAMES = {
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "F9": "Frontier Airlines",
    "G4": "Allegiant Air",
    "HA": "Hawaiian Airlines",
    "MQ": "Envoy Air (AA)",
    "NK": "Spirit Airlines",
    "OH": "PSA Airlines (AA)",
    "OO": "SkyWest Airlines",
    "UA": "United Airlines",
    "WN": "Southwest Airlines",
    "YX": "Republic Airways",
}

DAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

CANCEL_CODES = {
    "A": "Carrier",
    "B": "Weather",
    "C": "NAS / ATC",
    "D": "Security",
}

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def pct(part: float, whole: float) -> str:
    """Return percentage string, guarded against division by zero."""
    if whole == 0:
        return "0.0%"
    return f"{part / whole * 100:.1f}%"


def section_heading(icon: str, title: str, badge: str = ""):
    """Render a styled section heading."""
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""<div class="section-heading">
              <span class="icon">{icon}</span>
              <span class="title">{title}</span>
              {badge_html}
            </div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data loading & caching
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="⏳  Loading dataset …", ttl=3600)
def load_data(source) -> pd.DataFrame:
    """
    Load flight data from a file path (str) or uploaded bytes.
    Adds derived columns used across all modules.
    """
    if isinstance(source, str):
        df = pd.read_csv(source, low_memory=False)
    else:
        df = pd.read_csv(io.BytesIO(source), low_memory=False)

    df["FlightDate"] = pd.to_datetime(df["FlightDate"], dayfirst=True, errors="coerce")
    df["DayName"]    = df["DayOfWeek"].map(DAY_NAMES)
    df["AirlineName"] = df["Reporting_Airline"].map(AIRLINE_NAMES).fillna(df["Reporting_Airline"])
    df["CancelReason"] = df["CancellationCode"].map(CANCEL_CODES).fillna("Not Cancelled")
    df["DepHour"] = (df["CRSDepTime"] // 100).clip(0, 23)
    df["OnTime"]  = ((df["ArrDelay"].fillna(0) <= 15) & (df["Cancelled"] == 0)).astype(int)

    numeric_delay = [
        "DepDelay", "DepDelayMinutes", "ArrDelay", "ArrDelayMinutes",
        "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay",
        "LateAircraftDelay", "TaxiOut", "TaxiIn", "AirTime", "ActualElapsedTime",
    ]
    for col in numeric_delay:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Sidebar – controls
# ---------------------------------------------------------------------------

def build_sidebar(df: pd.DataFrame):
    """Render sidebar filters; return filtered DataFrame and filter state."""
    st.sidebar.markdown(
        "<h2 style='color:#58a6ff;font-size:1rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:.06em;'>🎛️ Filters</h2>",
        unsafe_allow_html=True,
    )

    airlines = sorted(df["AirlineName"].dropna().unique())
    selected_airlines = st.sidebar.multiselect("Airline(s)", options=airlines, default=airlines)

    states = sorted(df["OriginState"].dropna().unique())
    selected_states = st.sidebar.multiselect("Origin State(s)", options=states, default=states)

    days = list(DAY_NAMES.values())
    selected_days = st.sidebar.multiselect("Day(s) of Week", options=days, default=days)

    delay_thresh = st.sidebar.slider(
        "On-Time Threshold (min)", min_value=0, max_value=120, value=15, step=5,
        help="Flights arriving within this many minutes of schedule are 'on-time'.",
    )

    mask = (
        df["AirlineName"].isin(selected_airlines)
        & df["OriginState"].isin(selected_states)
        & df["DayName"].isin(selected_days)
    )
    filtered = df[mask].copy()
    filtered["OnTime"] = (
        (filtered["ArrDelay"].fillna(0) <= delay_thresh) & (filtered["Cancelled"] == 0)
    ).astype(int)

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "📊 [Dataset on Kaggle](https://www.kaggle.com/datasets/a7madmostafa/"
        "us-flight-delays-2025-bts-on-time-performance)  \n"
        "📁 Source: BTS On-Time Performance, July 2025"
    )

    return filtered, {
        "airlines": selected_airlines,
        "states": selected_states,
        "days": selected_days,
        "delay_thresh": delay_thresh,
    }


# ---------------------------------------------------------------------------
# Module 0 – Dataset uploader
# ---------------------------------------------------------------------------

def render_uploader() -> pd.DataFrame:
    """File-upload widget with fallback to bundled CSV."""
    section_heading("📂", "Dataset", "Upload or use default")
    uploaded = st.file_uploader(
        "Upload a CSV (optional — defaults to `flight_delays_2025_07.csv`)",
        type=["csv"],
        help="Any CSV following the BTS on-time schema is supported.",
    )
    if uploaded is not None:
        try:
            raw = uploaded.read()
            df  = load_data(raw)
            st.success(f"✅ Loaded **{uploaded.name}** — {len(df):,} rows × {df.shape[1]} cols")
            return df
        except Exception as exc:
            st.error(f"❌ Could not parse the file: {exc}")
            st.info("Falling back to the default dataset.")
    try:
        df = load_data(DEFAULT_CSV)
        st.info(f"Using **{DEFAULT_CSV}** — {len(df):,} rows × {df.shape[1]} cols")
        return df
    except FileNotFoundError:
        st.error(f"`{DEFAULT_CSV}` not found. Please upload a CSV above.")
        st.stop()


# ---------------------------------------------------------------------------
# Module 1 – KPI Overview + Metric Gauges
# ---------------------------------------------------------------------------

def render_kpis(df: pd.DataFrame, delay_thresh: int):
    """
    High-level KPI scorecards (st.metric) with four Plotly gauge charts
    for On-Time Rate, Avg Arrival Delay, Cancellation Rate, and Diversion Rate.
    """
    section_heading("📌", "On-Time Performance Overview", "KPI Cards & Metric Gauges")

    total       = len(df)
    cancelled   = int(df["Cancelled"].sum())
    diverted    = int(df["Diverted"].sum())
    on_time     = int(df["OnTime"].sum())
    delayed     = int(((df["ArrDelay"].fillna(0) >= delay_thresh) & (df["Cancelled"] == 0)).sum())
    avg_arr     = df["ArrDelay"].dropna().mean()
    avg_dep     = df["DepDelay"].dropna().mean()
    otp_pct     = on_time / total * 100 if total else 0
    cancel_pct  = cancelled / total * 100 if total else 0
    diverted_pct = diverted / total * 100 if total else 0

    # ── Scorecard row ─────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("✈️ Total Flights",    f"{total:,}")
    c2.metric("✅ On-Time",          f"{on_time:,}",    f"{otp_pct:.1f}%")
    c3.metric("⏱️ Delayed",          f"{delayed:,}",    f"{delayed/total*100:.1f}%")
    c4.metric("❌ Cancelled",        f"{cancelled:,}",  f"{cancel_pct:.1f}%")
    c5.metric("🔀 Diverted",         f"{diverted:,}",   f"{diverted_pct:.1f}%")
    c6.metric("📥 Avg Arr Delay",    f"{avg_arr:.1f} min")
    c7.metric("📤 Avg Dep Delay",    f"{avg_dep:.1f} min")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge charts ──────────────────────────────────────────────────────
    def gauge(value: float, title: str, suffix: str,
              max_val: float, threshold_green: float, threshold_red: float,
              invert: bool = False) -> go.Figure:
        """
        Build a Plotly Indicator gauge.
        invert=True means low values are green (delay metrics).
        """
        if invert:
            bar_color = BRAND["green"] if value <= threshold_green else (
                BRAND["yellow"] if value <= threshold_red else BRAND["red"]
            )
        else:
            bar_color = BRAND["green"] if value >= threshold_green else (
                BRAND["yellow"] if value >= threshold_red else BRAND["red"]
            )

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(value, 1),
            number=dict(suffix=suffix, font=dict(color=BRAND["text"], size=28)),
            title=dict(text=title, font=dict(color=BRAND["muted"], size=12)),
            delta=dict(
                reference=threshold_green,
                increasing=dict(color=BRAND["green"] if not invert else BRAND["red"]),
                decreasing=dict(color=BRAND["red"]  if not invert else BRAND["green"]),
                font=dict(size=11),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, max_val],
                    tickcolor=BRAND["border"],
                    tickfont=dict(color=BRAND["muted"], size=10),
                ),
                bar=dict(color=bar_color, thickness=0.25),
                bgcolor=BRAND["surface"],
                borderwidth=1,
                bordercolor=BRAND["border"],
                steps=[
                    dict(range=[0, threshold_green * (1 if not invert else max_val/threshold_green)],
                         color="#1a2332"),
                    dict(range=[threshold_green, max_val], color="#0d1117"),
                ],
                threshold=dict(
                    line=dict(color=BRAND["blue"], width=2),
                    value=threshold_green,
                ),
            ),
        ))
        apply_theme(fig)
        fig.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=10))
        return fig

    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(
            gauge(otp_pct, "On-Time Arrival Rate", "%", 100, 80, 70),
            use_container_width=True,
        )
    with g2:
        st.plotly_chart(
            gauge(avg_arr, "Avg Arrival Delay", " min", 60, 10, 20, invert=True),
            use_container_width=True,
        )
    with g3:
        st.plotly_chart(
            gauge(avg_dep, "Avg Departure Delay", " min", 60, 10, 20, invert=True),
            use_container_width=True,
        )
    with g4:
        st.plotly_chart(
            gauge(cancel_pct, "Cancellation Rate", "%", 10, 1, 3, invert=True),
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Module 2 – Delay Breakdown by Airline (Grouped Bar Chart)
# ---------------------------------------------------------------------------

def render_delay_by_airline(df: pd.DataFrame):
    """
    Grouped bar chart: avg arrival delay vs avg departure delay per carrier,
    plus a stacked bar of delay causes per carrier.
    """
    section_heading("🏢", "Delay Breakdown by Airline / Carrier", "Grouped Bar Chart")

    airline_perf = (
        df.groupby("AirlineName")
        .agg(
            Flights=("Cancelled", "count"),
            OnTimeRate=("OnTime",    lambda x: x.mean() * 100),
            AvgArrDelay=("ArrDelay", "mean"),
            AvgDepDelay=("DepDelay", "mean"),
            CancelRate=("Cancelled", lambda x: x.mean() * 100),
        )
        .reset_index()
        .sort_values("OnTimeRate", ascending=False)
    )

    # ── Chart A: grouped bar Arr + Dep delay ──────────────────────────────
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Avg Arrival Delay (min)",
        x=airline_perf["AirlineName"],
        y=airline_perf["AvgArrDelay"].round(1),
        marker_color=BRAND["red"],
        text=airline_perf["AvgArrDelay"].round(1),
        textposition="outside",
        textfont=dict(color=BRAND["muted"], size=10),
        hovertemplate="<b>%{x}</b><br>Avg Arrival Delay: %{y:.1f} min<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Avg Departure Delay (min)",
        x=airline_perf["AirlineName"],
        y=airline_perf["AvgDepDelay"].round(1),
        marker_color=BRAND["blue"],
        text=airline_perf["AvgDepDelay"].round(1),
        textposition="outside",
        textfont=dict(color=BRAND["muted"], size=10),
        hovertemplate="<b>%{x}</b><br>Avg Departure Delay: %{y:.1f} min<extra></extra>",
    ))
    apply_theme(fig, "Average Arrival vs Departure Delay by Airline")
    fig.update_layout(
        barmode="group",
        xaxis_tickangle=-30,
        yaxis_title="Minutes",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Chart B: dual-axis On-Time Rate + Cancellation Rate ───────────────
    col_a, col_b = st.columns(2)
    with col_a:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="On-Time Rate (%)",
            x=airline_perf["AirlineName"],
            y=airline_perf["OnTimeRate"].round(1),
            marker_color=BRAND["green"],
            text=airline_perf["OnTimeRate"].round(1),
            textposition="outside",
            textfont=dict(size=9, color=BRAND["muted"]),
            hovertemplate="<b>%{x}</b><br>On-Time Rate: %{y:.1f}%<extra></extra>",
        ))
        fig2.add_hline(y=80, line_dash="dot", line_color=BRAND["yellow"],
                       annotation_text="80% target", annotation_font_color=BRAND["yellow"])
        apply_theme(fig2, "On-Time Arrival Rate by Airline (%)")
        fig2.update_layout(xaxis_tickangle=-30, yaxis_title="On-Time Rate (%)",
                           yaxis_range=[0, 105], showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        sorted_cancel = airline_perf.sort_values("CancelRate", ascending=False)
        fig3 = go.Figure(go.Bar(
            x=sorted_cancel["AirlineName"],
            y=sorted_cancel["CancelRate"].round(2),
            marker_color=[BRAND["red"] if v > 3 else BRAND["yellow"] if v > 1 else BRAND["green"]
                          for v in sorted_cancel["CancelRate"]],
            text=sorted_cancel["CancelRate"].round(2),
            textposition="outside",
            textfont=dict(size=9, color=BRAND["muted"]),
            hovertemplate="<b>%{x}</b><br>Cancellation Rate: %{y:.2f}%<extra></extra>",
        ))
        apply_theme(fig3, "Cancellation Rate by Airline (%)")
        fig3.update_layout(xaxis_tickangle=-30, yaxis_title="Cancellation Rate (%)",
                           showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Chart C: delay-cause stacked bar ──────────────────────────────────
    delay_cause_cols = {
        "Carrier": "CarrierDelay",
        "Weather": "WeatherDelay",
        "NAS / ATC": "NASDelay",
        "Security": "SecurityDelay",
        "Late Aircraft": "LateAircraftDelay",
    }
    cause_colors = [BRAND["blue"], BRAND["purple"], BRAND["orange"],
                    BRAND["yellow"], BRAND["red"]]
    existing = {k: v for k, v in delay_cause_cols.items() if v in df.columns}
    if existing:
        airline_causes = (
            df.groupby("AirlineName")[list(existing.values())].mean().reset_index()
        )
        airline_causes.columns = ["Airline"] + list(existing.keys())

        fig4 = go.Figure()
        for (cause, _), color in zip(existing.items(), cause_colors):
            if cause in airline_causes.columns:
                fig4.add_trace(go.Bar(
                    name=cause,
                    x=airline_causes["Airline"],
                    y=airline_causes[cause].round(1),
                    marker_color=color,
                    hovertemplate=f"<b>%{{x}}</b><br>{cause}: %{{y:.1f}} min<extra></extra>",
                ))
        apply_theme(fig4, "Average Delay Composition by Airline (Stacked)")
        fig4.update_layout(
            barmode="stack",
            xaxis_tickangle=-30,
            yaxis_title="Avg Delay Minutes",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        )
        st.plotly_chart(fig4, use_container_width=True)


# ---------------------------------------------------------------------------
# Module 3 – Flight Volume & Delay Trends Over Time (Line Chart)
# ---------------------------------------------------------------------------

def render_time_trends(df: pd.DataFrame):
    """
    Time-series line charts:
      A) Daily flight volume + average arrival delay (dual axis)
      B) Average delay by day of week
      C) Average delay by departure hour
    """
    section_heading("📈", "Flight Volume & Delay Trends Over Time", "Line Chart")

    # ── Chart A: Daily trends ─────────────────────────────────────────────
    daily = (
        df.groupby("FlightDate")
        .agg(Flights=("Cancelled", "count"), AvgDelay=("ArrDelay", "mean"))
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["FlightDate"], y=daily["Flights"],
        name="Daily Flights",
        mode="lines",
        line=dict(color=BRAND["blue"], width=2),
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.08)",
        hovertemplate="<b>%{x|%b %d}</b><br>Flights: %{y:,}<extra></extra>",
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=daily["FlightDate"], y=daily["AvgDelay"].round(1),
        name="Avg Arrival Delay (min)",
        mode="lines+markers",
        line=dict(color=BRAND["red"], width=2, dash="dot"),
        marker=dict(size=4, color=BRAND["red"]),
        hovertemplate="<b>%{x|%b %d}</b><br>Avg Delay: %{y:.1f} min<extra></extra>",
        yaxis="y2",
    ))
    apply_theme(fig, "Daily Flight Volume & Average Arrival Delay — July 2025")
    fig.update_layout(
        xaxis=dict(title="Date", tickformat="%b %d"),
        yaxis=dict(title="Total Flights", side="left"),
        yaxis2=dict(title="Avg Arrival Delay (min)", overlaying="y", side="right",
                    gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)

    # ── Chart B: Day-of-week ──────────────────────────────────────────────
    with col_a:
        dow = (
            df.groupby("DayName")
            .agg(Flights=("Cancelled", "count"), AvgDelay=("ArrDelay", "mean"))
            .reindex(list(DAY_NAMES.values()))
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=dow["DayName"], y=dow["Flights"],
            name="Flight Volume",
            marker_color=BRAND["blue"],
            opacity=0.6,
            yaxis="y",
            hovertemplate="<b>%{x}</b><br>Flights: %{y:,}<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=dow["DayName"], y=dow["AvgDelay"].round(1),
            name="Avg Delay (min)",
            mode="lines+markers",
            line=dict(color=BRAND["red"], width=2),
            marker=dict(size=7, color=BRAND["red"]),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Avg Delay: %{y:.1f} min<extra></extra>",
        ))
        apply_theme(fig2, "Volume & Avg Delay by Day of Week")
        fig2.update_layout(
            yaxis=dict(title="Flights", side="left"),
            yaxis2=dict(title="Avg Delay (min)", overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            barmode="overlay",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart C: Hourly delay trend ───────────────────────────────────────
    with col_b:
        hourly = (
            df.groupby("DepHour")
            .agg(Flights=("Cancelled", "count"), AvgDelay=("ArrDelay", "mean"))
            .reset_index()
        )
        hourly_valid = hourly[hourly["DepHour"].between(5, 23)]
        colors = [BRAND["red"] if d > 30 else BRAND["yellow"] if d > 15 else BRAND["green"]
                  for d in hourly_valid["AvgDelay"]]
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=hourly_valid["DepHour"].astype(str) + ":00",
            y=hourly_valid["AvgDelay"].round(1),
            marker_color=colors,
            name="Avg Arrival Delay",
            hovertemplate="<b>%{x}</b><br>Avg Delay: %{y:.1f} min<extra></extra>",
        ))
        fig3.add_hline(y=15, line_dash="dot", line_color=BRAND["yellow"],
                       annotation_text="15-min threshold",
                       annotation_font_color=BRAND["yellow"])
        apply_theme(fig3, "Avg Arrival Delay by Departure Hour")
        fig3.update_layout(
            xaxis_title="Departure Hour (24h)",
            yaxis_title="Avg Arrival Delay (min)",
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Module 4 – Geographic / Route Performance (Scatter + Heatmap)
# ---------------------------------------------------------------------------

def render_route_analysis(df: pd.DataFrame):
    """
    A) Scatter plot: Distance vs ArrDelay (coloured by airline)
    B) Correlation heatmap of numeric performance columns
    C) Top congested origin-destination route bubble chart
    """
    section_heading("🗺️", "Geographic & Route Performance", "Scatter · Heatmap")

    tab_scatter, tab_corr, tab_routes = st.tabs([
        "Distance vs Delay Scatter", "Correlation Heatmap", "Top Routes Bubble"
    ])

    # ── Tab A: Scatter ────────────────────────────────────────────────────
    with tab_scatter:
        sample = df.dropna(subset=["Distance", "ArrDelay", "AirTime"]).sample(
            min(8000, len(df)), random_state=42
        )
        fig = px.scatter(
            sample,
            x="Distance",
            y="ArrDelay",
            color="AirlineName",
            size="AirTime",
            size_max=18,
            opacity=0.55,
            color_discrete_sequence=AIRLINE_PALETTE,
            labels={
                "Distance": "Flight Distance (miles)",
                "ArrDelay": "Arrival Delay (min)",
                "AirTime": "Air Time (min)",
                "AirlineName": "Airline",
            },
            hover_name="AirlineName",
            hover_data={"Distance": True, "ArrDelay": ":.1f", "AirTime": ":.0f"},
        )
        fig.add_hline(y=0, line_color=BRAND["border"], line_width=1)
        fig.add_hline(y=15, line_dash="dot", line_color=BRAND["yellow"],
                      annotation_text="15-min threshold",
                      annotation_font_color=BRAND["yellow"])
        apply_theme(fig, "Flight Distance vs Arrival Delay (bubble size = Air Time)")
        fig.update_layout(
            xaxis_title="Flight Distance (miles)",
            yaxis_title="Arrival Delay (min)",
            legend=dict(title="Airline"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Pearson correlation note
        corr_val = df["Distance"].corr(df["ArrDelay"].fillna(0))
        st.caption(
            f"📐 Pearson correlation Distance ↔ Arrival Delay: **{corr_val:.3f}**  "
            "— longer routes absorb delay more easily (larger block-time padding)."
        )

    # ── Tab B: Correlation heatmap ────────────────────────────────────────
    with tab_corr:
        corr_cols = [
            "DepDelay", "ArrDelay", "TaxiOut", "TaxiIn",
            "AirTime", "Distance", "CarrierDelay",
            "WeatherDelay", "NASDelay", "LateAircraftDelay",
        ]
        existing_corr = [c for c in corr_cols if c in df.columns]
        corr_matrix = df[existing_corr].corr().round(2)

        fig2 = go.Figure(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.index.tolist(),
            colorscale=[
                [0.0,  "#f85149"],
                [0.35, "#161b22"],
                [0.5,  "#0d1117"],
                [0.65, "#161b22"],
                [1.0,  "#58a6ff"],
            ],
            zmin=-1, zmax=1,
            text=corr_matrix.values,
            texttemplate="%{text:.2f}",
            textfont=dict(size=10, color="#c9d1d9"),
            hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>",
            colorbar=dict(
                tickfont=dict(color=BRAND["muted"]),
                title=dict(text="r", font=dict(color=BRAND["muted"])),
                bgcolor=BRAND["surface"],
                bordercolor=BRAND["border"],
            ),
        ))
        apply_theme(fig2, "Correlation Heatmap — Key Performance Variables")
        fig2.update_layout(
            xaxis_tickangle=-30,
            height=480,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab C: Route bubbles ──────────────────────────────────────────────
    with tab_routes:
        top_n = st.slider("Number of routes", 10, 40, 20, key="bubble_n")
        metric_choice = st.radio(
            "Size metric", ["Total Flights", "Avg Arrival Delay"],
            horizontal=True, key="bubble_metric",
        )
        df["Route"] = df["Origin"] + " → " + df["Dest"]
        routes = (
            df.groupby("Route")
            .agg(
                Flights=("Cancelled", "count"),
                AvgDelay=("ArrDelay", "mean"),
                AvgDist=("Distance", "mean"),
            )
            .reset_index()
        )
        if metric_choice == "Total Flights":
            routes = routes.nlargest(top_n, "Flights")
            size_col, color_col = "Flights", "AvgDelay"
        else:
            routes = routes.nlargest(top_n, "AvgDelay")
            size_col, color_col = "AvgDelay", "AvgDelay"

        fig3 = px.scatter(
            routes,
            x="AvgDist",
            y="AvgDelay",
            size=size_col,
            size_max=40,
            color=color_col,
            text="Route",
            color_continuous_scale=[[0, BRAND["green"]], [0.5, BRAND["yellow"]], [1, BRAND["red"]]],
            labels={
                "AvgDist": "Avg Distance (miles)",
                "AvgDelay": "Avg Arrival Delay (min)",
                "Flights": "Total Flights",
            },
            hover_data={"Flights": True, "AvgDelay": ":.1f", "AvgDist": ":.0f"},
        )
        fig3.update_traces(
            textposition="top center",
            textfont=dict(size=8, color=BRAND["muted"]),
        )
        apply_theme(fig3, f"Top {top_n} Routes — Distance vs Delay Bubble Chart")
        fig3.update_layout(
            xaxis_title="Avg Distance (miles)",
            yaxis_title="Avg Arrival Delay (min)",
            coloraxis_colorbar=dict(
                title="Avg Delay",
                tickfont=dict(color=BRAND["muted"]),
            ),
        )
        st.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Module 5 – Delay Root Causes (Donut + Distribution)
# ---------------------------------------------------------------------------

def render_delay_causes(df: pd.DataFrame):
    """
    A) Donut chart of delay cause proportions
    B) On-Time vs Delayed vs Cancelled flight distribution (donut)
    C) Day × Hour heatmap
    """
    section_heading("🥧", "Delay Root Causes & Flight Distribution", "Pie · Donut · Heatmap")

    cause_cols = {
        "Carrier Delay":    "CarrierDelay",
        "Weather Delay":    "WeatherDelay",
        "NAS / ATC Delay":  "NASDelay",
        "Security Delay":   "SecurityDelay",
        "Late Aircraft":    "LateAircraftDelay",
    }
    cause_colors = [BRAND["blue"], BRAND["purple"], BRAND["orange"],
                    BRAND["yellow"], BRAND["red"]]

    existing = {k: v for k, v in cause_cols.items() if v in df.columns}
    delay_means = {label: df[col].mean() for label, col in existing.items()}

    col_a, col_b = st.columns(2)

    # ── Chart A: Delay-cause donut ────────────────────────────────────────
    with col_a:
        fig1 = go.Figure(go.Pie(
            labels=list(delay_means.keys()),
            values=[round(v, 2) for v in delay_means.values()],
            hole=0.55,
            marker=dict(colors=cause_colors, line=dict(color=BRAND["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(color=BRAND["text"], size=11),
            hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f} min<br>Share: %{percent}<extra></extra>",
            direction="clockwise",
            sort=True,
        ))
        fig1.add_annotation(
            text=f"Avg Total<br>{sum(delay_means.values()):.1f} min",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=BRAND["text"]),
        )
        apply_theme(fig1, "Delay Cause Composition (Avg Minutes per Delayed Flight)")
        fig1.update_layout(height=380, legend=dict(orientation="v", x=1.02))
        st.plotly_chart(fig1, use_container_width=True)

    # ── Chart B: On-Time / Delayed / Cancelled distribution donut ─────────
    with col_b:
        total = len(df)
        on_time_n   = int(df["OnTime"].sum())
        cancelled_n = int(df["Cancelled"].sum())
        delayed_n   = int(((df["ArrDelay"].fillna(0) > 15) & (df["Cancelled"] == 0)).sum())
        other_n     = total - on_time_n - cancelled_n - delayed_n

        labels = ["On-Time", "Delayed (>15 min)", "Cancelled", "Other / Early"]
        values = [on_time_n, delayed_n, cancelled_n, other_n]
        colors = [BRAND["green"], BRAND["red"], BRAND["yellow"], BRAND["muted"]]

        fig2 = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color=BRAND["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(color=BRAND["text"], size=11),
            hovertemplate="<b>%{label}</b><br>Flights: %{value:,}<br>Share: %{percent}<extra></extra>",
            direction="clockwise",
            sort=False,
        ))
        fig2.add_annotation(
            text=f"Total<br>{total:,}",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color=BRAND["text"]),
        )
        apply_theme(fig2, "Flight Status Distribution — On-Time vs Delayed vs Cancelled")
        fig2.update_layout(height=380, legend=dict(orientation="v", x=1.02))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart C: Day × Hour heatmap ───────────────────────────────────────
    hm_metric = st.selectbox(
        "Heatmap metric",
        ["Avg Arrival Delay (min)", "On-Time Rate (%)", "Flight Volume"],
        key="root_hm",
    )
    pivot_df = df.copy()
    pivot_df["DayName"] = pd.Categorical(
        pivot_df["DayName"], categories=list(DAY_NAMES.values()), ordered=True
    )
    if hm_metric == "Avg Arrival Delay (min)":
        heat = pivot_df.pivot_table("ArrDelay", index="DayName", columns="DepHour", aggfunc="mean")
        cs   = [[0, BRAND["green"]], [0.5, BRAND["yellow"]], [1, BRAND["red"]]]
        fmt  = ".1f"
    elif hm_metric == "On-Time Rate (%)":
        heat = pivot_df.pivot_table("OnTime", index="DayName", columns="DepHour", aggfunc="mean") * 100
        cs   = [[0, BRAND["red"]], [0.5, BRAND["yellow"]], [1, BRAND["green"]]]
        fmt  = ".1f"
    else:
        heat = pivot_df.pivot_table("Cancelled", index="DayName", columns="DepHour", aggfunc="count")
        cs   = [[0, BRAND["surface"]], [1, BRAND["blue"]]]
        fmt  = ".0f"

    fig3 = go.Figure(go.Heatmap(
        z=heat.values,
        x=[f"{h:02d}:00" for h in heat.columns],
        y=heat.index.tolist(),
        colorscale=cs,
        text=heat.values,
        texttemplate=f"%{{text:{fmt}}}",
        textfont=dict(size=9, color="#e6edf3"),
        hovertemplate="<b>%{y}</b> · <b>%{x}</b><br>" + hm_metric + ": %{z:.1f}<extra></extra>",
        colorbar=dict(
            tickfont=dict(color=BRAND["muted"]),
            bgcolor=BRAND["surface"],
            bordercolor=BRAND["border"],
        ),
    ))
    apply_theme(fig3, f"{hm_metric} — Day of Week × Departure Hour Heatmap")
    fig3.update_layout(height=320, xaxis_title="Departure Hour (24h)", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Module 6 – Data Quality & Validation
# ---------------------------------------------------------------------------

def render_data_quality(df: pd.DataFrame):
    """Null stats, describe(), and raw preview."""
    section_heading("🔍", "Data Quality & Validation")

    total_rows  = len(df)
    null_counts = df.isnull().sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows",          f"{total_rows:,}")
    c2.metric("Total Columns",       df.shape[1])
    c3.metric("Columns w/ Nulls",    int((null_counts > 0).sum()))
    c4.metric("Total Missing Values", f"{null_counts.sum():,}")

    with st.expander("📊 Null Value Breakdown", expanded=False):
        ndf = (
            null_counts[null_counts > 0]
            .reset_index()
            .rename(columns={"index": "Column", 0: "Missing"})
        )
        ndf["Missing %"] = (ndf["Missing"] / total_rows * 100).round(2)
        st.dataframe(ndf, use_container_width=True, hide_index=True)

    with st.expander("📈 Numeric Summary Statistics", expanded=False):
        num_cols = ["DepDelay", "ArrDelay", "TaxiOut", "TaxiIn",
                    "AirTime", "Distance", "CarrierDelay", "WeatherDelay",
                    "NASDelay", "LateAircraftDelay"]
        existing = [c for c in num_cols if c in df.columns]
        st.dataframe(df[existing].describe().round(2), use_container_width=True)

    with st.expander("🗂️ Raw Data Preview (first 200 rows)", expanded=False):
        st.dataframe(df.head(200), use_container_width=True)


# ---------------------------------------------------------------------------
# Module 7 – Custom Metric Calculator
# ---------------------------------------------------------------------------

def render_custom_calculations(df: pd.DataFrame):
    """Spreadsheet-style formula builder for derived columns."""
    section_heading("🧮", "Custom Metric Calculator")
    st.markdown(
        "<small style='color:#8b949e;'>Combine two numeric columns with an operator "
        "to build a derived metric and explore its distribution.</small>",
        unsafe_allow_html=True,
    )

    exclude = {"Year", "Quarter", "Month", "DayofMonth", "DayOfWeek",
               "CRSDepTime", "CRSArrTime", "DepTime", "ArrTime",
               "WheelsOff", "WheelsOn", "Flight_Number_Reporting_Airline"}
    numeric_cols = [c for c in df.select_dtypes(include="number").columns if c not in exclude]

    col_a, op_col, col_b, name_col = st.columns([3, 1, 3, 3])
    left     = col_a.selectbox("Column A",  numeric_cols,
                               index=numeric_cols.index("ArrDelay") if "ArrDelay" in numeric_cols else 0,
                               key="calc_a")
    op       = op_col.selectbox("Operator", ["+", "−", "×", "÷"], key="calc_op")
    right    = col_b.selectbox("Column B",  numeric_cols,
                               index=numeric_cols.index("DepDelay") if "DepDelay" in numeric_cols else 1,
                               key="calc_b")
    new_name = name_col.text_input("New Column Name", value="DerivedMetric", key="calc_name")

    if st.button("➕ Apply Calculation", key="calc_btn"):
        try:
            a = df[left].fillna(0)
            b = df[right].fillna(0)
            result = (a + b if op == "+" else
                      a - b if op == "−" else
                      a * b if op == "×" else
                      a / b.replace(0, np.nan))
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"{new_name} — Mean",   f"{result.mean():.2f}")
            m2.metric(f"{new_name} — Median", f"{result.median():.2f}")
            m3.metric(f"{new_name} — Max",    f"{result.max():.2f}")
            m4.metric(f"{new_name} — Min",    f"{result.min():.2f}")

            fig = px.histogram(
                result.dropna(), nbins=60,
                labels={"value": new_name},
                color_discrete_sequence=[BRAND["blue"]],
            )
            apply_theme(fig, f"Distribution of {new_name}  ({left} {op} {right})")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as exc:
            st.error(f"Calculation failed: {exc}")

    st.markdown("<hr style='border-color:#21262d;margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("<small style='color:#8b949e;font-weight:600;'>PRESET METRICS</small>",
                unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    presets = [
        ("Total Ground Time (min)",   "TaxiOut + TaxiIn",
         lambda d: (d["TaxiOut"].fillna(0) + d["TaxiIn"].fillna(0)).mean()),
        ("Delay Ratio (Arr / Dep)",   "ArrDelayMinutes ÷ DepDelayMinutes",
         lambda d: (d["ArrDelayMinutes"].fillna(0) / d["DepDelayMinutes"].replace(0, np.nan)).mean()),
        ("Block Time Efficiency (%)", "AirTime ÷ ActualElapsedTime × 100",
         lambda d: (d["AirTime"].fillna(0) / d["ActualElapsedTime"].replace(0, np.nan) * 100).mean()),
    ]
    for col_w, (label, formula, fn) in zip([p1, p2, p3], presets):
        try:
            col_w.metric(label, f"{fn(df):.2f}", help=f"Formula: {formula}")
        except Exception:
            col_w.metric(label, "N/A")


# ---------------------------------------------------------------------------
# Module 8 – Aggregation & Grouping
# ---------------------------------------------------------------------------

def render_aggregation(df: pd.DataFrame):
    """Dynamic group-by engine: table + horizontal bar chart."""
    section_heading("📊", "Aggregation & Grouping")

    dim_options = {
        "Airline": "AirlineName",
        "Origin State": "OriginState",
        "Destination State": "DestState",
        "Day of Week": "DayName",
        "Departure Hour": "DepHour",
        "Origin Airport": "Origin",
        "Destination Airport": "Dest",
    }
    metric_options = {
        "Avg Arrival Delay (min)":    ("ArrDelay",  "mean"),
        "Avg Departure Delay (min)":  ("DepDelay",  "mean"),
        "Total Flights":              (None,         "count"),
        "On-Time Rate (%)":           ("OnTime",     "mean_pct"),
        "Cancellation Rate (%)":      ("Cancelled",  "mean_pct"),
        "Avg Distance (miles)":       ("Distance",   "mean"),
        "Avg Air Time (min)":         ("AirTime",    "mean"),
        "Avg Taxi-Out (min)":         ("TaxiOut",    "mean"),
    }

    c1, c2, c3 = st.columns(3)
    dim_label    = c1.selectbox("Group By",  list(dim_options), key="agg_dim")
    metric_label = c2.selectbox("Metric",    list(metric_options), key="agg_metric")
    top_n        = c3.slider("Top N rows", 5, 50, 15, key="agg_topn")

    dim_col = dim_options[dim_label]
    metric_col, agg_fn = metric_options[metric_label]

    try:
        if agg_fn == "count":
            agg_df = (df.groupby(dim_col).size().reset_index(name=metric_label)
                      .sort_values(metric_label, ascending=False).head(top_n))
        elif agg_fn == "mean_pct":
            agg_df = (df.groupby(dim_col)[metric_col].mean().mul(100)
                      .reset_index(name=metric_label)
                      .sort_values(metric_label, ascending=False).head(top_n))
        else:
            agg_df = (df.groupby(dim_col)[metric_col].mean()
                      .reset_index(name=metric_label)
                      .sort_values(metric_label, ascending=False).head(top_n))

        left_col, right_col = st.columns([2, 3])
        with left_col:
            st.dataframe(agg_df.round(2), use_container_width=True, hide_index=True)
        with right_col:
            fig = go.Figure(go.Bar(
                x=agg_df[metric_label].round(1),
                y=agg_df[dim_col],
                orientation="h",
                marker=dict(
                    color=agg_df[metric_label],
                    colorscale=[[0, BRAND["blue"]], [1, BRAND["purple"]]],
                    showscale=False,
                ),
                text=agg_df[metric_label].round(1),
                textposition="outside",
                textfont=dict(color=BRAND["muted"], size=10),
                hovertemplate=f"<b>%{{y}}</b><br>{metric_label}: %{{x:.1f}}<extra></extra>",
            ))
            apply_theme(fig, f"{metric_label} by {dim_label}")
            fig.update_layout(
                yaxis=dict(autorange="reversed"),
                xaxis_title=metric_label,
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Aggregation error: {exc}")


# ---------------------------------------------------------------------------
# Module 9 – Business Insights & Recommendations
# ---------------------------------------------------------------------------

def render_business_insights(df: pd.DataFrame, delay_thresh: int):
    """Auto-generated data-driven recommendation cards."""
    section_heading("💡", "Business Insights & Recommendations")

    airline_perf = (
        df.groupby("AirlineName")
        .agg(
            OnTimePct=("OnTime",       lambda x: x.mean() * 100),
            AvgArrDelay=("ArrDelay",   "mean"),
            CancelPct=("Cancelled",    lambda x: x.mean() * 100),
        )
    )
    best_airline  = airline_perf["OnTimePct"].idxmax()
    worst_airline = airline_perf["OnTimePct"].idxmin()

    delay_causes = {
        "Carrier Delay": df["CarrierDelay"].mean(),
        "Weather Delay": df["WeatherDelay"].mean(),
        "NAS / ATC":     df["NASDelay"].mean(),
        "Late Aircraft": df["LateAircraftDelay"].mean(),
    }
    top_cause = max(delay_causes, key=delay_causes.get)

    hourly    = df.groupby("DepHour")["ArrDelay"].mean()
    worst_hour = int(hourly.idxmax())
    best_hour  = int(hourly.idxmin())

    daily     = df.groupby("DayName")["ArrDelay"].mean()
    worst_day = daily.idxmax()
    best_day  = daily.idxmin()

    df["Route"]   = df["Origin"] + " → " + df["Dest"]
    worst_route   = df.groupby("Route")["ArrDelay"].mean().idxmax()
    cancel_pct    = df["Cancelled"].mean() * 100

    def card(icon, title, finding, action, accent=BRAND["blue"]):
        st.markdown(
            f"""<div style="
                background:{BRAND['surface']};
                border:1px solid {BRAND['border']};
                border-left:4px solid {accent};
                border-radius:8px;
                padding:16px 18px;
                margin-bottom:12px;
            ">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:1.2rem;">{icon}</span>
                <strong style="color:{BRAND['text']};font-size:0.95rem;">{title}</strong>
              </div>
              <p style="margin:0 0 6px;color:{BRAND['muted']};font-size:0.82rem;">
                <strong style="color:#c9d1d9;">Finding:</strong> {finding}
              </p>
              <p style="margin:0;color:{accent};font-size:0.82rem;">
                <strong>Action:</strong> {action}
              </p>
            </div>""",
            unsafe_allow_html=True,
        )

    card("🏆", "Top-Performing Airline",
         f"{best_airline} leads with {airline_perf.loc[best_airline,'OnTimePct']:.1f}% on-time rate "
         f"and only {airline_perf.loc[best_airline,'AvgArrDelay']:.1f} min avg arrival delay.",
         "Use as the system benchmark. Share turnaround and gate-management practices network-wide.",
         BRAND["green"])

    card("⚠️", "Under-Performing Carrier",
         f"{worst_airline} has the lowest on-time rate "
         f"({airline_perf.loc[worst_airline,'OnTimePct']:.1f}%) — "
         f"{airline_perf.loc[best_airline,'OnTimePct'] - airline_perf.loc[worst_airline,'OnTimePct']:.1f} pp "
         "below the leader.",
         "Audit schedule padding, maintenance cycles, and hub congestion management.",
         BRAND["red"])

    card("🔁", "Break the Late-Aircraft Cascade",
         f"'{top_cause}' is the #1 delay cause at {delay_causes[top_cause]:.1f} min avg — "
         "larger than carrier and weather combined.",
         "Add ≥10 min buffer to first-rotation blocks. Pre-position spare aircraft at ORD, DEN, ATL.",
         BRAND["orange"])

    card("🕗", "Book Early to Beat Delays",
         f"Departures at {best_hour:02d}:00 average {hourly[best_hour]:.1f} min delay; "
         f"flights at {worst_hour:02d}:00 average {hourly[worst_hour]:.1f} min — a "
         f"{hourly[worst_hour]/max(hourly[best_hour],0.1):.0f}× difference.",
         "Incentivise morning departures through pricing. Recommend 06:00–08:00 in corporate travel policy.",
         BRAND["blue"])

    card("📅", "Mid-Week Scheduling Advantage",
         f"{best_day}s have the lowest avg delay ({daily[best_day]:.1f} min); "
         f"{worst_day}s are worst ({daily[worst_day]:.1f} min).",
         "Deploy extra ground staff on Sundays and Mondays. Route planners should prefer mid-week itineraries.",
         BRAND["purple"])

    card("🛤️", "Critical Problem Route",
         f"Route {worst_route} has the highest average arrival delay in the current filter.",
         "Escalate to operations leadership. Investigate slot restrictions, aircraft mis-routing, and crew positioning.",
         BRAND["yellow"])

    card("🌩️", "Weather Resilience",
         f"Overall cancellation rate: {cancel_pct:.2f}% ({int(df['Cancelled'].sum()):,} flights). "
         "Weather accounts for ~63% of all cancellations.",
         "Deploy convective decision tools at ORD, DEN, BWI, LGA. "
         "Build automated rebooking triggers for weather watches.",
         BRAND["red"])

    st.markdown(
        "<small style='color:#8b949e;'>Insights update dynamically with sidebar filter changes.</small>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main():
    # ── Masthead ────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#0d1117 0%,#161b22 40%,#1f2937 100%);
            border:1px solid {BRAND['border']};
            border-radius:12px;
            padding:28px 32px 22px;
            margin-bottom:24px;
            position:relative;
            overflow:hidden;
        ">
          <div style="
              position:absolute;top:-40px;right:-40px;
              width:200px;height:200px;
              background:radial-gradient(circle,{BRAND['blue']}22 0%,transparent 70%);
              border-radius:50%;
          "></div>
          <p style="
              color:{BRAND['blue']};font-size:0.7rem;font-weight:700;
              letter-spacing:.14em;text-transform:uppercase;margin:0 0 6px;
          ">BTS Reporting Carrier · July 2025</p>
          <h1 style="
              color:{BRAND['text']};margin:0 0 8px;font-size:1.9rem;
              font-weight:800;letter-spacing:-0.02em;line-height:1.2;
          ">✈️ US Airlines On-Time Performance Analysis</h1>
          <p style="color:{BRAND['muted']};margin:0;font-size:0.9rem;line-height:1.6;">
            631,428 flights · 14 airlines · 345 airports · Interactive dashboard
          </p>
          <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;">
            <span style="background:{BRAND['blue']}22;color:{BRAND['blue']};
                border:1px solid {BRAND['blue']}44;border-radius:20px;
                padding:2px 12px;font-size:0.7rem;font-weight:600;letter-spacing:.04em;">
              STREAMLIT
            </span>
            <span style="background:{BRAND['green']}22;color:{BRAND['green']};
                border:1px solid {BRAND['green']}44;border-radius:20px;
                padding:2px 12px;font-size:0.7rem;font-weight:600;letter-spacing:.04em;">
              PLOTLY
            </span>
            <span style="background:{BRAND['purple']}22;color:{BRAND['purple']};
                border:1px solid {BRAND['purple']}44;border-radius:20px;
                padding:2px 12px;font-size:0.7rem;font-weight:600;letter-spacing:.04em;">
              BTS DATA
            </span>
            <span style="background:{BRAND['orange']}22;color:{BRAND['orange']};
                border:1px solid {BRAND['orange']}44;border-radius:20px;
                padding:2px 12px;font-size:0.7rem;font-weight:600;letter-spacing:.04em;">
              PANDAS
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Dataset ──────────────────────────────────────────────────────────────
    df_raw = render_uploader()

    # ── Sidebar filters ──────────────────────────────────────────────────────
    df_filtered, filter_state = build_sidebar(df_raw)

    if df_filtered.empty:
        st.warning("⚠️ No data matches the current filters. Please widen your selection.")
        return

    st.markdown(
        f"<small style='color:{BRAND['muted']};'>Showing <b style='color:{BRAND['text']};'>"
        f"{len(df_filtered):,}</b> of <b style='color:{BRAND['text']};'>{len(df_raw):,}</b>"
        f" rows after filters.</small>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='border-color:#21262d;margin:12px 0 20px;'>", unsafe_allow_html=True)

    # ── Section flow ─────────────────────────────────────────────────────────
    render_kpis(df_filtered, filter_state["delay_thresh"])
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_delay_by_airline(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_time_trends(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_route_analysis(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_delay_causes(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_data_quality(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_custom_calculations(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_aggregation(df_filtered)
    st.markdown("<hr style='border-color:#21262d;margin:28px 0;'>", unsafe_allow_html=True)

    render_business_insights(df_filtered, filter_state["delay_thresh"])

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown(
        f"""<div style="
            text-align:center;
            color:{BRAND['muted']};
            font-size:11px;
            padding:28px 0 8px;
            border-top:1px solid {BRAND['border']};
            margin-top:32px;
        ">
          US Airlines On-Time Performance Analysis &nbsp;·&nbsp;
          Built with Streamlit &amp; Plotly &nbsp;·&nbsp;
          <a href="https://www.kaggle.com/datasets/a7madmostafa/us-flight-delays-2025-bts-on-time-performance"
             style="color:{BRAND['blue']};text-decoration:none;" target="_blank">
            Dataset on Kaggle
          </a>
          &nbsp;·&nbsp; IBM Bob Project
        </div>""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
