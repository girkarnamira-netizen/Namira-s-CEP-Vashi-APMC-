import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_datasets, validate_datasets
from src.data_cleaning import clean_datasets
from src.recommendations import generate_recommendations

from logistics.config import GEO_COORDINATES
from logistics.route_optimizer import optimize_route

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="APMC Vashi",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
}

/* Dark sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(99,102,241,0.15) !important;
    border: 1px solid rgba(99,102,241,0.4) !important;
    color: #a5b4fc !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Main background */
.stApp { background: #f8fafc !important; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px; }

/* Page header */
.page-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 50%, #1d4ed8 100%);
    color: white;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    box-shadow: 0 8px 32px rgba(30,58,138,0.25);
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.page-header-title {
    font-size: 2rem; font-weight: 900; letter-spacing: -0.03em; margin-bottom: 4px;
}
.page-header-sub {
    font-size: 0.92rem; opacity: 0.75; font-weight: 400;
}
.page-header-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    backdrop-filter: blur(8px); margin-top: 10px;
}

/* Logistics page header (green) */
.page-header-green {
    background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0f766e 100%) !important;
    box-shadow: 0 8px 32px rgba(6,78,59,0.25) !important;
}

/* KPI metric cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    transition: box-shadow 0.2s;
    height: 100%;
}
.kpi-card:hover { box-shadow: 0 6px 20px rgba(15,23,42,0.08); }
.kpi-label {
    font-size: 0.72rem; font-weight: 700; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px;
}
.kpi-value {
    font-size: 2rem; font-weight: 900; color: #0f172a; line-height: 1.1;
}
.kpi-unit { font-size: 0.85rem; font-weight: 500; color: #64748b; margin-left: 3px; }
.kpi-delta { font-size: 0.78rem; color: #64748b; margin-top: 6px; }
.kpi-delta-up { color: #16a34a; font-weight: 600; }
.kpi-delta-down { color: #dc2626; font-weight: 600; }

/* Section titles */
.section-title {
    font-size: 1.1rem; font-weight: 800; color: #1e3a5f;
    margin-bottom: 14px; padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}
.section-title-green { color: #064e3b !important; border-bottom-color: #d1fae5 !important; }

/* Content cards */
.content-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    margin-bottom: 18px;
}

/* Alert / info box */
.info-box {
    background: rgba(30,64,175,0.05);
    border: 1px solid rgba(30,64,175,0.2);
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 18px;
    font-size: 0.88rem;
    color: #1e3a5f;
}
.info-box-green {
    background: rgba(6,78,59,0.05) !important;
    border-color: rgba(6,78,59,0.2) !important;
    border-left-color: #059669 !important;
    color: #064e3b !important;
}
.warning-box {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 4px solid #f97316;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}

/* Nav pills in sidebar */
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-bottom: 2px !important;
    transition: background 0.15s;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.07) !important;
}

/* Dataframe styling */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Tab styling */
.stTabs [role="tablist"] { gap: 4px; border-bottom: 2px solid #e2e8f0; }
.stTabs [role="tab"] {
    padding: 8px 18px; font-size: 0.9rem; font-weight: 600;
    color: #64748b; border-radius: 8px 8px 0 0;
    border: none; background: transparent;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #1e40af !important; background: rgba(30,64,175,0.06) !important;
    border-bottom: 3px solid #1e40af !important;
}

/* Buttons */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; padding: 0.55rem 1.4rem !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 6px 18px rgba(37,99,235,0.45) !important;
}

/* Sidebar logo area */
.sidebar-logo {
    text-align: center; padding: 12px 0 20px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 18px;
}
.sidebar-logo-title {
    font-size: 1.15rem; font-weight: 800; color: #f1f5f9 !important;
    letter-spacing: -0.02em; margin-top: 8px;
}
.sidebar-logo-sub {
    font-size: 0.72rem; color: #64748b !important; font-weight: 500;
}

/* Route node badges */
.route-badge {
    display: inline-block;
    background: #dbeafe; color: #1e40af;
    padding: 4px 12px; border-radius: 20px;
    font-weight: 700; font-size: 0.82rem; margin: 2px;
}
.route-arrow { color: #94a3b8; font-weight: 700; margin: 0 4px; }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_app_data():
    raw = load_datasets()
    cleaned = clean_datasets(raw)
    cleaned["_validation"] = validate_datasets(cleaned)
    return cleaned


def filter_data(data, commodity, start_date, end_date, source_location,
                transport_mode, collection_centre, distributor_type):
    filtered = {
        key: df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
        for key, df in data.items()
        if not key.startswith("_")
    }

    market = filtered["market_prices"]
    if not market.empty and "Date" in market.columns:
        market["Date"] = pd.to_datetime(market["Date"], errors="coerce")
        market = market[(market["Date"] >= pd.Timestamp(start_date)) & (market["Date"] <= pd.Timestamp(end_date))]
        if commodity != "All" and "Commodity" in market.columns:
            market = market[market["Commodity"].astype(str).str.title() == commodity]
        if source_location != "All" and "District" in market.columns:
            market = market[market["District"].astype(str).str.strip() == source_location]
        filtered["market_prices"] = market

    farmers = filtered["farmers"]
    if not farmers.empty and "Harvest_Date" in farmers.columns:
        farmers["Harvest_Date"] = pd.to_datetime(farmers["Harvest_Date"], errors="coerce")
        farmers = farmers[(farmers["Harvest_Date"] >= pd.Timestamp(start_date)) & (farmers["Harvest_Date"] <= pd.Timestamp(end_date))]
        if commodity != "All" and "Product" in farmers.columns:
            farmers = farmers[farmers["Product"].astype(str).str.title() == commodity]
        if source_location != "All" and "Location" in farmers.columns:
            farmers = farmers[farmers["Location"].astype(str).str.strip() == source_location]
        filtered["farmers"] = farmers

    transport = filtered["transportation"]
    if not transport.empty:
        if commodity != "All" and "Product" in transport.columns:
            transport = transport[transport["Product"].astype(str).str.title() == commodity]
        if source_location != "All" and "Source" in transport.columns:
            transport = transport[transport["Source"].astype(str).str.strip() == source_location]
        if transport_mode != "All" and "Transport_Mode" in transport.columns:
            transport = transport[transport["Transport_Mode"].astype(str).str.strip() == transport_mode]
        filtered["transportation"] = transport

    distribution = filtered["distribution"]
    if not distribution.empty:
        if commodity != "All" and "Product" in distribution.columns:
            distribution = distribution[distribution["Product"].astype(str).str.title() == commodity]
        if source_location != "All" and "Farmer_Source" in distribution.columns:
            distribution = distribution[distribution["Farmer_Source"].astype(str).str.strip() == source_location]
        if collection_centre != "All" and "Collection_Centre" in distribution.columns:
            distribution = distribution[distribution["Collection_Centre"].astype(str).str.strip() == collection_centre]
        if distributor_type != "All" and "Distributor" in distribution.columns:
            distribution = distribution[distribution["Distributor"].astype(str).str.strip() == distributor_type]
        filtered["distribution"] = distribution

    mapping = filtered["supply_chain_mapping"]
    if not mapping.empty:
        if commodity != "All" and "Product" in mapping.columns:
            mapping = mapping[mapping["Product"].astype(str).str.title() == commodity]
        if source_location != "All" and "Location" in mapping.columns:
            mapping = mapping[mapping["Location"].astype(str).str.strip() == source_location]
        filtered["supply_chain_mapping"] = mapping

    return filtered


def compute_summary(filtered):
    farmers = filtered["farmers"]
    market = filtered["market_prices"]
    transport = filtered["transportation"]
    distribution = filtered["distribution"]

    total_supply = float(pd.to_numeric(farmers["Quantity_Produced_kg"], errors="coerce").sum()) if not farmers.empty else 0.0
    arrival_tonnes = float(pd.to_numeric(market["Arrival_Quantity_Tonnes"], errors="coerce").sum()) if not market.empty else 0.0
    avg_modal_price = float(pd.to_numeric(market["Wholesale_Modal_INR_per_Qtl"], errors="coerce").mean()) if not market.empty else 0.0
    total_loss = 0.0
    if not farmers.empty:
        total_loss += float(pd.to_numeric(farmers["Quantity_Wasted_kg"], errors="coerce").sum())
    if not distribution.empty:
        total_loss += float(pd.to_numeric(distribution["Quantity_Lost_kg"], errors="coerce").sum())
    loss_rate = (total_loss / total_supply * 100) if total_supply else 0.0
    avg_delay = float(pd.to_numeric(transport["Delay_Hours"], errors="coerce").mean()) if not transport.empty else 0.0
    total_transport_cost = float(pd.to_numeric(transport["Transport_Cost_INR"], errors="coerce").sum()) if not transport.empty else 0.0
    return {
        "total_supply": total_supply,
        "arrival_tonnes": arrival_tonnes,
        "avg_modal_price": avg_modal_price,
        "total_loss": total_loss,
        "loss_rate": loss_rate,
        "avg_delay": avg_delay,
        "transport_cost": total_transport_cost,
    }


# ─── UI HELPERS ───────────────────────────────────────────────────────────────
def kpi_card(label, value, unit="", delta="", delta_type="neutral"):
    delta_class = "kpi-delta-up" if delta_type == "up" else ("kpi-delta-down" if delta_type == "down" else "kpi-delta")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div class="{delta_class}">{delta}</div>
    </div>
    """, unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-title">{title}</div>
        <div class="page-header-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def section_title(text, green=False):
    cls = "section-title section-title-green" if green else "section-title"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def make_sankey(mapping_df):
    if mapping_df is None or mapping_df.empty:
        return go.Figure()
    required_cols = ["Location", "Collection_Centre", "APMC_Market", "Distributor_Type"]
    if not all(col in mapping_df.columns for col in required_cols):
        return go.Figure()
    nodes = []
    for col in required_cols:
        nodes.extend(mapping_df[col].fillna("Unknown").astype(str).tolist())
    labels = list(dict.fromkeys(nodes))
    lookup = {label: idx for idx, label in enumerate(labels)}

    source = [lookup.get(str(v), 0) for v in mapping_df["Location"].fillna("Unknown").astype(str)]
    target = [lookup.get(str(v), 0) for v in mapping_df["Collection_Centre"].fillna("Collection Centre").astype(str)]
    second_source = [lookup.get(str(v), 0) for v in mapping_df["Collection_Centre"].fillna("Collection Centre").astype(str)]
    second_target = [lookup.get(str(v), 0) for v in mapping_df["APMC_Market"].fillna("APMC Vashi").astype(str)]
    third_source = [lookup.get(str(v), 0) for v in mapping_df["APMC_Market"].fillna("APMC Vashi").astype(str)]
    third_target = [lookup.get(str(v), 0) for v in mapping_df["Distributor_Type"].fillna("Distributor").astype(str)]

    values = pd.to_numeric(mapping_df["Quantity_Produced_kg"], errors="coerce").fillna(0).astype(float).tolist()
    values3 = pd.to_numeric(mapping_df["Quantity_Sold_kg"], errors="coerce").fillna(0).astype(float).tolist()

    node_colors = []
    for lbl in labels:
        if lbl in mapping_df["Location"].values:
            node_colors.append("#1e40af")
        elif lbl in mapping_df["Collection_Centre"].values:
            node_colors.append("#0891b2")
        elif lbl in mapping_df["APMC_Market"].values:
            node_colors.append("#047857")
        else:
            node_colors.append("#7c3aed")

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(label=labels, pad=20, thickness=18, color=node_colors),
        link=dict(
            source=source + second_source + third_source,
            target=target + second_target + third_target,
            value=values + values.copy() + values3,
            color=["rgba(30,64,175,0.25)"] * len(source) +
                  ["rgba(8,145,178,0.25)"] * len(second_source) +
                  ["rgba(4,120,87,0.25)"] * len(third_source),
        ),
    )])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), template="plotly_white", height=400)
    return fig


CHART_THEME = dict(template="plotly_white", margin=dict(l=10, r=10, t=35, b=10))


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
def render_sidebar(data):
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:2.2rem">🌾</div>
            <div class="sidebar-logo-title">APMC Vashi</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**NAVIGATION**")
        section = st.radio("", [
            "📊 Overview",
            "📈 Market & Price Analytics",
            "🔗 Supply Chain Map",
            "🚚 Transportation & Bottlenecks",
            "📦 Distribution Efficiency",
            "🌾 Farmer & Source Analytics",
            "🏷️ Price Grade Analysis",
            "💡 Recommendations",
            "🛣️ Route Optimizer",
        ], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("**FILTERS**")

        market = data.get("market_prices", pd.DataFrame())
        if not market.empty and "Date" in market.columns:
            dates = pd.to_datetime(market["Date"], errors="coerce").dropna()
            min_date = dates.min().date() if not dates.empty else pd.Timestamp.today().date()
            max_date = dates.max().date() if not dates.empty else pd.Timestamp.today().date()
        else:
            min_date = max_date = pd.Timestamp.today().date()

        commodity = st.selectbox("Commodity", ["All", "Onion", "Potato", "Tomato"])
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
        granularity = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)

        farmers_df = data.get("farmers", pd.DataFrame())
        source_location = st.selectbox("Source District", ["All"] + (
            sorted(farmers_df["Location"].dropna().astype(str).unique().tolist()) if not farmers_df.empty else []))

        market_name = st.selectbox("Market", ["All"] + (
            sorted(market["Market_Name"].dropna().astype(str).unique().tolist()) if not market.empty and "Market_Name" in market.columns else []))

        transport_df = data.get("transportation", pd.DataFrame())
        transport_mode = st.selectbox("Transport Mode", ["All"] + (
            sorted(transport_df["Transport_Mode"].dropna().astype(str).unique().tolist()) if not transport_df.empty else []))

        dist_df = data.get("distribution", pd.DataFrame())
        collection_centre = st.selectbox("Collection Centre", ["All"] + (
            sorted(dist_df["Collection_Centre"].dropna().astype(str).unique().tolist()) if not dist_df.empty else []))
        distributor_type = st.selectbox("Distributor", ["All"] + (
            sorted(dist_df["Distributor"].dropna().astype(str).unique().tolist()) if not dist_df.empty else []))

        if st.button("↺ Reset Filters", use_container_width=True):
            st.rerun()

    return section, commodity, start_date, end_date, granularity, source_location, market_name, transport_mode, collection_centre, distributor_type


# ─── PAGES ────────────────────────────────────────────────────────────────────

def page_overview(filtered, summary, granularity):
    page_header("APMC Vashi Supply Chain", "Agricultural Intelligence Dashboard · Onion · Potato · Tomato")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi_card("Total Supply", f"{summary['total_supply']/1000:,.1f}", "k kg", "Produced at farm")
    with c2: kpi_card("APMC Arrivals", f"{summary['arrival_tonnes']:,.0f}", "T", "Market arrivals")
    with c3: kpi_card("Modal Price", f"₹{summary['avg_modal_price']:,.0f}", "/qtl", "Wholesale avg")
    with c4: kpi_card("Qty Lost", f"{summary['total_loss']:,.0f}", "kg", "Post-harvest loss", "down" if summary['loss_rate'] > 8 else "neutral")
    with c5: kpi_card("Loss Rate", f"{summary['loss_rate']:,.1f}", "%", "Across chain", "down" if summary['loss_rate'] > 8 else "up")
    with c6: kpi_card("Avg Delay", f"{summary['avg_delay']:,.1f}", "hrs", "Transport delay", "down" if summary['avg_delay'] > 2 else "up")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    section_title("Supply Chain Flow")
    if filtered["supply_chain_mapping"].empty:
        st.info("No records match the selected filters.")
    else:
        st.plotly_chart(make_sankey(filtered["supply_chain_mapping"]), use_container_width=True)

    left, right = st.columns(2)
    with left:
        section_title("Top Source Districts")
        if not filtered["farmers"].empty:
            src = filtered["farmers"].groupby("Location", as_index=False)["Quantity_Produced_kg"].sum().sort_values("Quantity_Produced_kg", ascending=False).head(8)
            fig = px.bar(src, x="Quantity_Produced_kg", y="Location", orientation="h",
                         color="Quantity_Produced_kg", color_continuous_scale="Blues")
            fig.update_layout(**CHART_THEME, coloraxis_showscale=False, yaxis={"autorange": "reversed"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No farmer data for selected filters.")

    with right:
        section_title("Commodity-wise Supply")
        if not filtered["farmers"].empty:
            comm = filtered["farmers"].groupby("Product", as_index=False)["Quantity_Produced_kg"].sum()
            fig = px.pie(comm, values="Quantity_Produced_kg", names="Product", hole=0.45,
                         color_discrete_sequence=["#1e40af", "#047857", "#dc2626"])
            fig.update_layout(**CHART_THEME)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No commodity data for selected filters.")

    section_title("Price Trend")
    if not filtered["market_prices"].empty:
        m = filtered["market_prices"].copy()
        m["Date"] = pd.to_datetime(m["Date"], errors="coerce")
        if granularity == "Weekly":
            m["Date"] = m["Date"].dt.to_period("W-MON").dt.start_time
        elif granularity == "Monthly":
            m["Date"] = m["Date"].dt.to_period("M").dt.start_time
        trend = m.groupby("Date", as_index=False).agg(
            Modal_Price=("Wholesale_Modal_INR_per_Qtl", "mean"),
            Min_Price=("Wholesale_Min_INR_per_Qtl", "mean"),
            Max_Price=("Wholesale_Max_INR_per_Qtl", "mean"),
        )
        fig = px.line(trend, x="Date", y=["Modal_Price", "Min_Price", "Max_Price"],
                      color_discrete_map={"Modal_Price": "#1e40af", "Min_Price": "#64748b", "Max_Price": "#dc2626"})
        fig.update_layout(**CHART_THEME, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No price trend data for selected filters.")


def page_market_price(filtered, granularity):
    page_header("Market & Price Analytics", "Wholesale price trends, market arrivals, and commodity performance")

    market_df = filtered["market_prices"]
    if market_df.empty:
        st.info("No market data available for the selected filters.")
        return

    m = market_df.copy()
    m["Date"] = pd.to_datetime(m["Date"], errors="coerce")
    if granularity == "Weekly":
        m["Date"] = m["Date"].dt.to_period("W-MON").dt.start_time
    elif granularity == "Monthly":
        m["Date"] = m["Date"].dt.to_period("M").dt.start_time
    trend = m.groupby("Date", as_index=False).agg(
        Modal_Price=("Wholesale_Modal_INR_per_Qtl", "mean"),
        Min_Price=("Wholesale_Min_INR_per_Qtl", "mean"),
        Max_Price=("Wholesale_Max_INR_per_Qtl", "mean"),
        Arrival_Quantity=("Arrival_Quantity_Tonnes", "sum"),
    )

    t1, t2 = st.tabs(["📈 Price Trends", "📦 Arrivals & Raw Data"])
    with t1:
        section_title("Wholesale Price Band")
        fig = px.line(trend, x="Date", y=["Modal_Price", "Min_Price", "Max_Price"],
                      color_discrete_map={"Modal_Price": "#1e40af", "Min_Price": "#94a3b8", "Max_Price": "#ef4444"})
        fig.update_layout(**CHART_THEME, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        section_title("Commodity Price Distribution")
        if "Commodity" in market_df.columns:
            fig2 = px.box(market_df, x="Commodity", y="Wholesale_Modal_INR_per_Qtl", color="Commodity",
                          color_discrete_sequence=["#1e40af", "#047857", "#dc2626"])
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)

    with t2:
        section_title("Arrival Quantity Trend")
        fig3 = px.bar(trend, x="Date", y="Arrival_Quantity", color_discrete_sequence=["#1e40af"])
        fig3.update_layout(**CHART_THEME)
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(market_df[["Date", "Commodity", "Market_Name", "Wholesale_Modal_INR_per_Qtl", "Arrival_Quantity_Tonnes"]].head(40),
                     use_container_width=True, hide_index=True)


def page_supply_chain(filtered):
    page_header("Supply Chain Map", "Farmer → Collection Centre → APMC → Distributor flow visualization")
    mapping = filtered["supply_chain_mapping"]
    if mapping.empty:
        st.info("No records match the selected filters.")
        return
    section_title("Flow Diagram")
    st.plotly_chart(make_sankey(mapping), use_container_width=True)
    section_title("Raw Mapping Data")
    st.dataframe(mapping[["Location", "Collection_Centre", "APMC_Market", "Distributor_Type",
                           "Product", "Quantity_Produced_kg", "Quantity_Sold_kg"]].head(50),
                 use_container_width=True, hide_index=True)


def page_transportation(filtered):
    page_header("Transportation & Bottlenecks", "Route delays, costs, and damage analytics")
    transport = filtered["transportation"].copy()
    if transport.empty:
        st.info("No transportation data available for the selected filters.")
        return

    transport["Damage_%"] = np.where(
        transport["Quantity_Transported_kg"].fillna(0) > 0,
        (transport["Quantity_Damaged_kg"].fillna(0) / transport["Quantity_Transported_kg"].fillna(0)) * 100, 0)

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Avg Delay", f"{transport['Delay_Hours'].mean():.1f}", "hrs", "Mean transit delay")
    with c2: kpi_card("Total Cost", f"₹{transport['Transport_Cost_INR'].sum()/1e6:.1f}", "M", "Transport spend")
    with c3: kpi_card("Avg Damage", f"{transport['Damage_%'].mean():.1f}", "%", "In-transit damage")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section_title("Distance vs. Cost")
        fig1 = px.scatter(transport, x="Distance_km", y="Transport_Cost_INR", color="Product",
                  color_discrete_sequence=["#1e40af", "#047857", "#dc2626"])
        fig1.update_layout(**CHART_THEME)
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        section_title("Distance vs. Delay")
        fig2 = px.scatter(transport, x="Distance_km", y="Delay_Hours", color="Product",
                          color_discrete_sequence=["#1e40af", "#047857", "#dc2626"])
        fig2.update_layout(**CHART_THEME)
        st.plotly_chart(fig2, use_container_width=True)

    section_title("Delay by Transport Mode")
    if "Transport_Mode" in transport.columns:
        mode_agg = transport.groupby("Transport_Mode", as_index=False)["Delay_Hours"].mean().sort_values("Delay_Hours", ascending=False)
        fig3 = px.bar(mode_agg, x="Transport_Mode", y="Delay_Hours",
                      color="Delay_Hours", color_continuous_scale="RdYlGn_r")
        fig3.update_layout(**CHART_THEME, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    section_title("High-Delay Shipments")
    st.dataframe(transport[["Source", "Destination", "Product", "Distance_km", "Transport_Mode",
                             "Transport_Cost_INR", "Delay_Hours", "Damage_%", "Quantity_Transported_kg"
                             ]].sort_values("Delay_Hours", ascending=False).head(25),
                 use_container_width=True, hide_index=True)


def page_distribution(filtered):
    page_header("Distribution Efficiency", "Loss rates, distributor performance, and delivery analytics")
    dist = filtered["distribution"].copy()
    if dist.empty:
        st.info("No distribution data available for the selected filters.")
        return

    dist["Loss_%"] = np.where(dist["Quantity_kg"].fillna(0) > 0,
                               (dist["Quantity_Lost_kg"].fillna(0) / dist["Quantity_kg"].fillna(0)) * 100, 0)
    dist["Delivery_Efficiency_%"] = np.where(dist["Quantity_kg"].fillna(0) > 0,
                                              (dist["Quantity_Delivered_kg"].fillna(0) / dist["Quantity_kg"].fillna(0)) * 100, 0)

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Avg Loss Rate", f"{dist['Loss_%'].mean():.1f}", "%", "Distribution loss")
    with c2: kpi_card("Delivery Efficiency", f"{dist['Delivery_Efficiency_%'].mean():.1f}", "%", "Delivered / received")
    with c3: kpi_card("Total Lost", f"{dist['Quantity_Lost_kg'].sum():,.0f}", "kg", "Quantity lost")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section_title("Loss by Commodity")
        if "Product" in dist.columns:
            loss_by_prod = dist.groupby("Product")["Loss_%"].mean().reset_index()
            fig1 = px.bar(loss_by_prod, x="Product", y="Loss_%",
                          color="Product", color_discrete_sequence=["#1e40af", "#047857", "#dc2626"])
            fig1.update_layout(**CHART_THEME, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        section_title("Top Distributors by Efficiency")
        distr_agg = dist.groupby("Distributor", as_index=False).agg(
            Received=("Quantity_kg", "sum"),
            Delivered=("Quantity_Delivered_kg", "sum"),
            Lost=("Quantity_Lost_kg", "sum"),
        )
        distr_agg["Eff_%"] = (distr_agg["Delivered"] / distr_agg["Received"].replace(0, np.nan) * 100).round(1)
        fig2 = px.bar(distr_agg.sort_values("Eff_%", ascending=False).head(10),
                      x="Eff_%", y="Distributor", orientation="h", color="Eff_%",
                      color_continuous_scale="Greens")
        fig2.update_layout(**CHART_THEME, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    section_title("Distributor Performance Table")
    st.dataframe(distr_agg.sort_values("Eff_%", ascending=False), use_container_width=True, hide_index=True)


def page_farmer_analytics(filtered):
    page_header("Farmer & Source Analytics", "Farm-gate production, revenue, and regional performance")
    farmers = filtered["farmers"].copy()
    if farmers.empty:
        st.info("No farmer-source data available.")
        return

    farmers["Estimated_Revenue"] = (farmers["Quantity_Sold_kg"].fillna(0) / 100) * farmers["Selling_Price_INR_per_Qtl"].fillna(0)

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Total Farmers", f"{farmers['Farmer_ID'].nunique():,}", "", "In selection")
    with c2: kpi_card("Total Produced", f"{farmers['Quantity_Produced_kg'].sum()/1000:,.0f}", "T", "Farm-gate production")
    with c3: kpi_card("Estimated Revenue", f"₹{farmers['Estimated_Revenue'].sum()/1e6:.1f}", "M", "All farmers")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section_title("Production by District")
        src = farmers.groupby("Location", as_index=False)["Quantity_Produced_kg"].sum().sort_values("Quantity_Produced_kg", ascending=False).head(12)
        fig1 = px.bar(src, x="Quantity_Produced_kg", y="Location", orientation="h",
                      color="Quantity_Produced_kg", color_continuous_scale="Blues")
        fig1.update_layout(**CHART_THEME, coloraxis_showscale=False, yaxis={"autorange": "reversed"})
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        section_title("Waste by District")
        waste = farmers.groupby("Location", as_index=False)["Quantity_Wasted_kg"].sum().sort_values("Quantity_Wasted_kg", ascending=False).head(12)
        fig2 = px.bar(waste, x="Quantity_Wasted_kg", y="Location", orientation="h",
                      color="Quantity_Wasted_kg", color_continuous_scale="Reds")
        fig2.update_layout(**CHART_THEME, coloraxis_showscale=False, yaxis={"autorange": "reversed"})
        st.plotly_chart(fig2, use_container_width=True)

    section_title("Farmer Detail Table")
    st.dataframe(farmers[["Farmer_ID", "Location", "Product", "Quantity_Produced_kg",
                           "Quantity_Sold_kg", "Quantity_Wasted_kg", "Selling_Price_INR_per_Qtl", "Estimated_Revenue"]].head(30),
                 use_container_width=True, hide_index=True)


def page_price_grade(filtered):
    page_header("Price Grade Analysis", "Grade-wise wholesale price variation by commodity")
    grade_df = filtered["market_prices"].copy()
    if grade_df.empty:
        st.info("No market records available for grade analysis.")
        return
    if "Grade" not in grade_df.columns:
        st.info("Grade-wise analysis requires a Grade field in the active market dataset.")
        return

    tabs = st.tabs(["🧅 Onion", "🥔 Potato", "🍅 Tomato"])
    for idx, comm in enumerate(["Onion", "Potato", "Tomato"]):
        with tabs[idx]:
            part = grade_df[grade_df["Commodity"].astype(str).str.title() == comm]
            if part.empty:
                st.info(f"No {comm} records for the selected filter set.")
            else:
                fig = px.box(part, x="Grade", y="Wholesale_Modal_INR_per_Qtl", color="Grade")
                fig.update_layout(**CHART_THEME)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(part.groupby("Grade", as_index=False).agg(
                    Min_Price=("Wholesale_Min_INR_per_Qtl", "min"),
                    Avg_Price=("Wholesale_Modal_INR_per_Qtl", "mean"),
                    Max_Price=("Wholesale_Max_INR_per_Qtl", "max"),
                    Arrival_Qty=("Arrival_Quantity_Tonnes", "sum"),
                ), use_container_width=True, hide_index=True)


def page_recommendations(filtered):
    page_header("Recommendations", "Actions based on measured supply-chain metrics and the selected filters")
    recs = generate_recommendations(filtered["market_prices"], filtered["transportation"],
                                    filtered["distribution"], filtered["farmers"])
    if not recs:
        st.markdown("""
        <div class="info-box">
            ✅ <strong>No material issues detected</strong> for the current filter set. Supply chain performance is within acceptable thresholds.
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in recs:
            st.markdown(f"""
            <div class="warning-box">
                <strong style="color:#c2410c">⚠ {item['ISSUE']}</strong><br>
                <span style="font-size:0.88rem;color:#374151">
                    <b>Priority:</b> {item['PRIORITY']} &nbsp;|&nbsp;
                    <b>Metric:</b> {item['METRIC']} &nbsp;|&nbsp;
                    <b>Actual:</b> {item['ACTUAL_VALUE']} &nbsp;|&nbsp;
                    <b>Threshold:</b> {item['THRESHOLD']}<br>
                    <b>Action:</b> {item['RECOMMENDED_ACTION']}
                </span>
            </div>
            """, unsafe_allow_html=True)


# ─── ROUTE OPTIMIZER PAGE ─────────────────────────────────────────────────────

def page_route_optimizer():
    page_header(
        "Multi-Stop Route Optimizer",
        "Plan a collection sequence · nearest-neighbour ordering using straight-line distances",
    )

    avail_nodes = list(GEO_COORDINATES.keys())

    col1, col2 = st.columns([1, 1.6])

    with col1:
        section_title("Route Parameters")
        default_stops = ["Lasalgaon (Nashik)", "Pimpalgaon (Nashik)", "Nashik", "Ahilyanagar (Ahmednagar)"]
        selected_stops = st.multiselect(
            "Farm / Collection Points",
            options=avail_nodes,
            default=[s for s in default_stops if s in avail_nodes],
        )
        dest_options = ["APMC Vashi (Navi Mumbai)", "Mumbai", "Pune", "Nagpur", "Solapur"]
        selected_dest = st.selectbox(
            "Destination Terminal Mandi",
            options=[d for d in dest_options if d in avail_nodes],
            index=0,
        )
        solve_btn = st.button("Solve Optimal Route", type="primary", use_container_width=True)

    with col2:
        all_stops = list(dict.fromkeys((selected_stops or []) + [selected_dest]))
        if solve_btn or "route_cache" not in st.session_state:
            res = optimize_route(
                all_stops,
                start=selected_stops[0] if selected_stops else None,
                end=selected_dest,
            )
            st.session_state["route_cache"] = res
        else:
            res = st.session_state["route_cache"]

        ordered = res.get("ordered_stops", all_stops)
        approx_km = res.get("approx_distance_km", 0.0)
        engine = res.get("engine", "heuristic")

        section_title("Solved Sequence")
        badges = " → ".join(ordered)
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;'
            f'padding:14px 18px;font-weight:600;color:#064e3b;font-size:0.9rem;'
            f'line-height:2;margin-bottom:16px">{badges}</div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        with m1:
            kpi_card("Straight-Line Distance", f"{approx_km:.1f}", "km", f"Method: {engine}")
        with m2:
            kpi_card("Est. Transit", f"{max(2.5, approx_km / 38.0):.1f}", "hrs", "Avg 38 km/h")
        with m3:
            kpi_card("Est. Freight", f"Rs.{max(1200, approx_km * 28.0):,.0f}", "", "Indicative")
        st.caption(res.get("disclaimer", "Distance is a straight-line estimate, not a road distance."))

    # Map
    valid = [n for n in ordered if n in GEO_COORDINATES]
    if len(valid) >= 2:
        import numpy as _np
        lats = [GEO_COORDINATES[n]["lat"] for n in valid]
        lons = [GEO_COORDINATES[n]["lon"] for n in valid]
        hover = [f"{i+1}. {n}" for i, n in enumerate(valid)]
        node_colors = ["#1e40af"] * (len(lats) - 1) + ["#dc2626"]

        fig = go.Figure()
        map_trace = getattr(go, "Scattermap", None)
        map_layout_key = "map"
        if map_trace is None:
            map_trace = go.Scattermapbox
            map_layout_key = "mapbox"

        fig.add_trace(map_trace(
            mode="lines", lon=lons, lat=lats,
            line=dict(width=4, color="#1e40af"),
            hoverinfo="none", name="Route",
        ))
        fig.add_trace(map_trace(
            mode="markers+text", lon=lons, lat=lats,
            marker=dict(size=15, color=node_colors),
            text=[f"{i+1}" for i in range(len(lats))],
            textposition="top right",
            hovertext=hover,
            hoverinfo="text",
            name="Stops",
        ))
        fig.update_layout(
            **{map_layout_key: dict(
                style="open-street-map",
                center=dict(lat=float(_np.mean(lats)), lon=float(_np.mean(lons))),
                zoom=6,
            )},
            margin=dict(l=0, r=0, t=0, b=0),
            height=480,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    if res.get("missing_nodes"):
        st.markdown(
            f'<div class="warning-box">⚠ Coordinates not found for: '
            f'{", ".join(res["missing_nodes"])}</div>',
            unsafe_allow_html=True,
        )


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    data = load_app_data()
    validation = data.get("_validation", {})
    if not validation.get("ok", True):
        issues = []
        if validation.get("missing_files"):
            issues.append("Missing files: " + ", ".join(validation["missing_files"]))
        if validation.get("missing_columns"):
            details = "; ".join(
                f"{dataset}: {', '.join(columns)}"
                for dataset, columns in validation["missing_columns"].items()
            )
            issues.append("Missing columns: " + details)
        st.warning("Required dashboard data is incomplete. " + " ".join(issues))

    (section, commodity, start_date, end_date, granularity,
     source_location, market_name, transport_mode,
     collection_centre, distributor_type) = render_sidebar(data)

    filtered = filter_data(data, commodity, start_date, end_date,
                           source_location, transport_mode, collection_centre, distributor_type)
    if market_name != "All" and "Market_Name" in filtered["market_prices"].columns:
        filtered["market_prices"] = filtered["market_prices"][
            filtered["market_prices"]["Market_Name"].astype(str).str.strip() == market_name]

    summary = compute_summary(filtered)

    if section == "📊 Overview":
        page_overview(filtered, summary, granularity)
    elif section == "📈 Market & Price Analytics":
        page_market_price(filtered, granularity)
    elif section == "🔗 Supply Chain Map":
        page_supply_chain(filtered)
    elif section == "🚚 Transportation & Bottlenecks":
        page_transportation(filtered)
    elif section == "📦 Distribution Efficiency":
        page_distribution(filtered)
    elif section == "🌾 Farmer & Source Analytics":
        page_farmer_analytics(filtered)
    elif section == "🏷️ Price Grade Analysis":
        page_price_grade(filtered)
    elif section == "💡 Recommendations":
        page_recommendations(filtered)
    elif section == "🛣️ Route Optimizer":
        page_route_optimizer()


if __name__ == "__main__":
    main()
