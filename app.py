import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_datasets, validate_datasets
from src.data_cleaning import clean_datasets
from src.recommendations import generate_recommendations

st.set_page_config(page_title="APMC Vashi - Supply Chain Analytics", layout="wide")


@st.cache_data(show_spinner=False)
def load_app_data():
    raw = load_datasets()
    cleaned = clean_datasets(raw)
    cleaned["_validation"] = validate_datasets(cleaned)
    return cleaned


def filter_data(data, commodity, start_date, end_date, source_location, transport_mode, collection_centre, distributor_type):
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


def render_metric_card(title, value, unit, delta=""):
    st.markdown(
        f"""
        <div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:12px; padding:16px 18px; min-height:110px; box-shadow:0 1px 2px rgba(15,23,42,0.03);">
            <div style="font-size:11px; letter-spacing:0.08em; color:#6b7280; text-transform:uppercase; margin-bottom:10px; font-weight:700;">{title}</div>
            <div style="font-size:2.2rem; font-weight:800; color:#111827; line-height:1.1;">{value}{unit}</div>
            <div style="font-size:12px; color:#6b7280; margin-top:8px;">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    values2 = values.copy()
    values3 = pd.to_numeric(mapping_df["Quantity_Sold_kg"], errors="coerce").fillna(0).astype(float).tolist()

    fig = go.Figure(
        data=[go.Sankey(
            arrangement="snap",
            node=dict(label=labels, pad=18, thickness=20, color=["#2e7d32"] * len(labels)),
            link=dict(
                source=source + second_source + third_source,
                target=target + second_target + third_target,
                value=values + values2 + values3,
                color=["rgba(46,125,50,0.35)"] * (len(source) + len(second_source) + len(third_source)),
            ),
        )]
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), template="plotly_white")
    return fig


st.markdown(
    """
    <style>
        .block-container { padding-top: 0.75rem; }
        .title { font-size: 3.2rem; font-weight: 900; letter-spacing: 0.02em; color: #111827; }
        .subtitle { font-size: 1.0rem; color: #4b5563; margin-top: -8px; }
        .subline { color: #6b7280; font-size: 1rem; margin-top: 6px; }
        [data-testid="stSidebar"] { background: #f4f6f8; }
        section[data-testid="stSidebar"] * { color: #1f2937; }
        div[role="radiogroup"] label { font-size: 0.9rem; }
        .stTabs [role="tablist"] { gap: 0.35rem; }
        .stTabs [role="tab"] { padding: 0.45rem 0.7rem; font-size: 0.95rem; }
        .stTabs [role="tab"][aria-selected="true"] {
            border-bottom: 3px solid #ef4444;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe_filter_values(df, col, value):
    if df.empty or col not in df.columns or value == "All":
        return df
    return df[df[col].astype(str).str.strip() == str(value)]


def main():
    data = load_app_data()
    validation = data.get("_validation", {})
    if not validation.get("ok", True):
        st.error("Required files or columns are missing.")
        st.json(validation)
        st.stop()

    market = data["market_prices"]
    if not market.empty and "Date" in market.columns:
        dates = pd.to_datetime(market["Date"], errors="coerce").dropna()
        min_date = dates.min().date() if not dates.empty else pd.Timestamp.today().date()
        max_date = dates.max().date() if not dates.empty else pd.Timestamp.today().date()
    else:
        min_date = pd.Timestamp.today().date()
        max_date = pd.Timestamp.today().date()

    with st.sidebar:
        st.markdown("<h3>Filters</h3>", unsafe_allow_html=True)
        commodity = st.selectbox("Commodity", ["All", "Onion", "Potato", "Tomato"])
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
        granularity = st.radio("Granularity", ["Daily", "Weekly", "Monthly"], horizontal=True)
        source_location = st.selectbox("Source District / Location", ["All"] + sorted(data["farmers"]["Location"].dropna().astype(str).unique().tolist()))
        market_name = st.selectbox("Market", ["All"] + sorted(data["market_prices"]["Market_Name"].dropna().astype(str).unique().tolist()))
        transport_mode = st.selectbox("Transport Mode", ["All"] + sorted(data["transportation"]["Transport_Mode"].dropna().astype(str).unique().tolist()))
        collection_centre = st.selectbox("Collection Centre", ["All"] + sorted(data["distribution"]["Collection_Centre"].dropna().astype(str).unique().tolist()))
        distributor_type = st.selectbox("Distributor Type", ["All"] + sorted(data["distribution"]["Distributor"].dropna().astype(str).unique().tolist()))
        if st.button("Reset Filters"):
            st.rerun()

    filtered = filter_data(data, commodity, start_date, end_date, source_location, transport_mode, collection_centre, distributor_type)
    if market_name != "All" and "Market_Name" in filtered["market_prices"].columns:
        filtered["market_prices"] = filtered["market_prices"][filtered["market_prices"]["Market_Name"].astype(str).str.strip() == market_name]
    if market_name != "All" and "Market" in filtered["distribution"].columns:
        filtered["distribution"] = filtered["distribution"][filtered["distribution"]["Market"].astype(str).str.strip() == market_name]

    summary = compute_summary(filtered)

    st.markdown("<div class='title'>APMC VASHI</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Agricultural Supply Chain Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='subline'>Onion • Potato • Tomato</div>", unsafe_allow_html=True)

    nav = st.sidebar.radio("Navigation", [
        "Overview",
        "Market & Price Analytics",
        "Supply Chain Map",
        "Transportation & Bottlenecks",
        "Distribution Efficiency",
        "Farmer & Source Analytics",
        "Price Grade Analysis",
        "Recommendations",
        "Data Quality",
    ])

    if nav == "Overview":
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: render_metric_card("Total Supply", f"{summary['total_supply']/1000:,.1f}", "k", "tonnes")
        with c2: render_metric_card("APMC Arrivals", f"{summary['arrival_tonnes']:,.0f}", "", "tonnes")
        with c3: render_metric_card("Avg. Modal Price", f"₹{summary['avg_modal_price']:,.0f}", "/qtl", "market price")
        with c4: render_metric_card("Total Quantity Lost", f"{summary['total_loss']:,.0f}", "", "kg")
        with c5: render_metric_card("Loss Rate", f"{summary['loss_rate']:,.1f}", "%", "across chain")
        with c6: render_metric_card("Avg. Transport Delay", f"{summary['avg_delay']:,.1f}", "", "hours")

        st.markdown("<h3>Supply Chain Flow</h3>", unsafe_allow_html=True)
        if filtered["supply_chain_mapping"].empty:
            st.info("No records match the selected filters.")
        else:
            st.plotly_chart(make_sankey(filtered["supply_chain_mapping"]), use_container_width=True)

        left, right = st.columns(2)
        with left:
            if filtered["farmers"].empty:
                st.info("No farmer data in the current selection.")
            else:
                source_summary = filtered["farmers"].groupby("Location", as_index=False)["Quantity_Produced_kg"].sum().sort_values("Quantity_Produced_kg", ascending=False).head(8)
                st.markdown("<h4>Supply from Key Districts</h4>", unsafe_allow_html=True)
                fig = px.bar(source_summary, x="Quantity_Produced_kg", y="Location", orientation="h", title="District Supply")
                fig.update_layout(template="plotly_white", yaxis={"autorange": "reversed"})
                st.plotly_chart(fig, use_container_width=True)
        with right:
            if filtered["farmers"].empty:
                st.info("No commodity data in the current selection.")
            else:
                commodity_summary = filtered["farmers"].groupby("Product", as_index=False)["Quantity_Produced_kg"].sum()
                st.markdown("<h4>Commodity-wise Arrival Quantity</h4>", unsafe_allow_html=True)
                fig = px.bar(commodity_summary, x="Product", y="Quantity_Produced_kg", color="Product", title="Commodity Quantity")
                fig.update_layout(template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

        if filtered["market_prices"].empty:
            st.info("No price trend data for the selected filters.")
        else:
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
            fig = px.line(trend, x="Date", y=["Modal_Price", "Min_Price", "Max_Price"], title="Modal Price Trend")
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        if "Grade" in filtered["market_prices"].columns:
            grade_df = filtered["market_prices"].copy()
            if not grade_df.empty:
                fig = px.box(filtered["market_prices"], x="Grade", y="Wholesale_Modal_INR_per_Qtl", color="Commodity", title="Grade-wise Price Variation")
                st.plotly_chart(fig, use_container_width=True)

    elif nav == "Market & Price Analytics":
        market_df = filtered["market_prices"]
        if market_df.empty:
            st.info("No market data available for the selected filters.")
        else:
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
            st.subheader("Modal Price Trend")
            st.plotly_chart(px.line(trend, x="Date", y=["Modal_Price", "Min_Price", "Max_Price"], title="Price Trend"), use_container_width=True)
            st.dataframe(market_df[["Date", "Commodity", "Market_Name", "Wholesale_Modal_INR_per_Qtl", "Arrival_Quantity_Tonnes"]].head(20), use_container_width=True)

    elif nav == "Supply Chain Map":
        mapping = filtered["supply_chain_mapping"]
        if mapping.empty:
            st.info("No records match the selected filters.")
        else:
            st.plotly_chart(make_sankey(mapping), use_container_width=True)
            st.dataframe(mapping[["Location", "Collection_Centre", "APMC_Market", "Distributor_Type", "Product", "Quantity_Produced_kg", "Quantity_Sold_kg"]].head(30), use_container_width=True)

    elif nav == "Transportation & Bottlenecks":
        transport = filtered["transportation"].copy()
        if transport.empty:
            st.info("No transportation data available for the selected filters.")
        else:
            transport["Damage_%"] = np.where(transport["Quantity_Transported_kg"].fillna(0) > 0, (transport["Quantity_Damaged_kg"].fillna(0) / transport["Quantity_Transported_kg"].fillna(0)) * 100, 0)
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.scatter(transport, x="Distance_km", y="Transport_Cost_INR", color="Product", title="Distance vs Cost"), use_container_width=True)
            with c2: st.plotly_chart(px.scatter(transport, x="Distance_km", y="Delay_Hours", color="Product", title="Distance vs Delay"), use_container_width=True)
            st.dataframe(transport[["Source", "Destination", "Product", "Distance_km", "Transport_Mode", "Transport_Cost_INR", "Delay_Hours", "Damage_%", "Quantity_Transported_kg"]].sort_values("Delay_Hours", ascending=False).head(20), use_container_width=True)

    elif nav == "Distribution Efficiency":
        dist = filtered["distribution"].copy()
        if dist.empty:
            st.info("No distribution data available for the selected filters.")
        else:
            dist["Loss_%"] = np.where(dist["Quantity_kg"].fillna(0) > 0, (dist["Quantity_Lost_kg"].fillna(0) / dist["Quantity_kg"].fillna(0)) * 100, 0)
            dist["Delivery_Efficiency_%"] = np.where(dist["Quantity_kg"].fillna(0) > 0, (dist["Quantity_Delivered_kg"].fillna(0) / dist["Quantity_kg"].fillna(0)) * 100, 0)
            st.plotly_chart(px.bar(dist.groupby("Product")["Loss_%"].mean().reset_index(), x="Product", y="Loss_%", title="Loss by Commodity"), use_container_width=True)
            st.dataframe(dist.groupby("Distributor", as_index=False).agg(Received=("Quantity_kg", "sum"), Delivered=("Quantity_Delivered_kg", "sum"), Lost=("Quantity_Lost_kg", "sum"), Delivery_Efficiency=("Quantity_Lost_kg", "mean")).head(20), use_container_width=True)

    elif nav == "Farmer & Source Analytics":
        farmers = filtered["farmers"].copy()
        if farmers.empty:
            st.info("No farmer-source data available.")
        else:
            farmers["Estimated_Revenue"] = (farmers["Quantity_Sold_kg"].fillna(0) / 100) * farmers["Selling_Price_INR_per_Qtl"].fillna(0)
            source_summary = farmers.groupby("Location", as_index=False)["Quantity_Produced_kg"].sum().sort_values("Quantity_Produced_kg", ascending=False)
            st.plotly_chart(px.bar(source_summary, x="Quantity_Produced_kg", y="Location", orientation="h", title="Source Contribution"), use_container_width=True)
            st.dataframe(farmers[["Farmer_ID", "Location", "Product", "Quantity_Produced_kg", "Quantity_Sold_kg", "Quantity_Wasted_kg", "Production_Cost_INR", "Selling_Price_INR_per_Qtl", "Estimated_Revenue"]].head(20), use_container_width=True)

    elif nav == "Price Grade Analysis":
        grade_df = filtered["market_prices"].copy()
        if grade_df.empty:
            st.info("No market records available for grade analysis.")
        elif "Grade" not in grade_df.columns:
            st.info("Grade-wise analysis requires a Grade field in the active market dataset. The current project files do not include a valid grade field for this slice.")
        else:
            st.subheader("Grade-wise Price Variation")
            commodity_tabs = st.tabs(["Onion", "Potato", "Tomato"])
            for idx, commodity in enumerate(["Onion", "Potato", "Tomato"]):
                with commodity_tabs[idx]:
                    part = grade_df[grade_df["Commodity"].astype(str).str.title() == commodity]
                    if part.empty:
                        st.info(f"No {commodity} records for the selected filter set.")
                    else:
                        fig = px.box(part, x="Grade", y="Wholesale_Modal_INR_per_Qtl", title=f"{commodity} Grade Price Range")
                        st.plotly_chart(fig, use_container_width=True)
                        st.dataframe(part.groupby("Grade", as_index=False).agg(
                            Min_Price=("Wholesale_Min_INR_per_Qtl", "min"),
                            Avg_Price=("Wholesale_Modal_INR_per_Qtl", "mean"),
                            Max_Price=("Wholesale_Max_INR_per_Qtl", "max"),
                            Arrival_Quantity=("Arrival_Quantity_Tonnes", "sum"),
                        ), use_container_width=True)

    elif nav == "Recommendations":
        recs = generate_recommendations(filtered["market_prices"], filtered["transportation"], filtered["distribution"], filtered["farmers"])
        if not recs:
            st.info("No material issues were detected for the current filter set.")
        else:
            for item in recs:
                st.markdown(
                    f"""
                    <div style="padding:12px 14px; border-left:4px solid #ef4444; border-radius:10px; background:#fff7ed; margin-bottom:12px;">
                        <strong>{item['ISSUE']}</strong><br>
                        Metric: {item['METRIC']}<br>
                        Actual value: {item['ACTUAL_VALUE']}<br>
                        Threshold: {item['THRESHOLD']}<br>
                        Action: {item['RECOMMENDED_ACTION']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    elif nav == "Data Quality":
        st.subheader("Data Quality")
        st.json(validation)


if __name__ == "__main__":
    main()
