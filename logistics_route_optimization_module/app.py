import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import COMMODITIES, GEO_COORDINATES
from src.route_optimizer import optimize_route
from src.logistics import get_shipment_dashboard, get_inventory_snapshot, corridor_freight_audit
from src.optimizer import simulate_supply_chain_interventions
from src.partner_manager import list_partners, partner_summary
from src.data_pipeline import ensure_synthetic_ops_data

# Page Setup
st.set_page_config(
    page_title="AgriNexus · Logistics Route Optimization & Intelligence Module",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Luxury UI CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1c2433;
    }

    .stApp {
        background-color: #f7f4ed !important;
        background-image: radial-gradient(#e5dfd3 0.85px, transparent 0.85px), radial-gradient(#e5dfd3 0.85px, #f7f4ed 0.85px) !important;
        background-size: 32px 32px !important;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #0f766e 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(6, 78, 59, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    .hero-sub {
        font-size: 0.98rem;
        opacity: 0.9;
        font-weight: 400;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(8px);
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Card Containers */
    .content-box {
        background: #ffffff;
        border: 1px solid #e2dcd0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 18px;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2dcd0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #059669;
        margin-top: 4px;
        font-weight: 600;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #064e3b;
        margin-bottom: 14px;
    }
    .chart-caption {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Ensure synthetic ops datasets exist
ensure_synthetic_ops_data()

# Sidebar Navigation & Filters
st.sidebar.image("https://img.icons8.com/color/96/delivery-truck.png", width=70)
st.sidebar.title("🚛 Logistics Intelligence")
st.sidebar.markdown("---")

selected_commodity = st.sidebar.selectbox("Filter Target Commodity:", COMMODITIES, index=2)
st.sidebar.markdown("---")

tab_selection = st.sidebar.radio(
    "Select Module Component:",
    [
        "🛣️ Multi-Stop Route Solver",
        "📊 Fleet Operations & Telemetry",
        "🏛️ Cold Storage & Warehouse GIS",
        "⚡ What-If Intervention Simulator",
        "📋 Stakeholder & Fleet Registry"
    ]
)

# Header Banner
st.markdown(f"""
<div class="hero-banner">
    <div>
        <div class="hero-title">Logistics Route Optimization & Intelligence Module</div>
        <div class="hero-sub">Multi-Stop Collection Route Solver · Perishable Logistics Telemetry · Cold Chain GIS & What-If Simulator</div>
    </div>
    <div class="hero-badge">AgriFlow Logistics</div>
</div>
""", unsafe_allow_html=True)

# Provenance Note
st.markdown("""
<div style="background: rgba(6, 78, 59, 0.05); border: 1px solid rgba(6, 78, 59, 0.2); border-left: 4px solid #059669; border-radius: 10px; padding: 14px 18px; margin-bottom: 22px;">
    <div style="font-weight: 800; color: #064e3b; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center;">
        <span>🚛 Route Solver & Distribution Corridor Intelligence</span>
        <span style="font-size: 0.74rem; background: #064e3b; color: #ffffff; padding: 2px 8px; border-radius: 6px; font-weight: 700;">LIVE ENGINE</span>
    </div>
    <div style="font-size: 0.86rem; color: #1e293b; margin-top: 6px;">
        <b>Engine Integrity:</b> Geodesic network heuristics & OR-Tools VRP constraints. Calibrated against APMC Vashi baseline corridors (Nashik, Agra, Pune) and MAGNET/ADB project benchmarks.
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# COMPONENT 1: MULTI-STOP ROUTE SOLVER
# =============================================================================
if tab_selection == "🛣️ Multi-Stop Route Solver":
    st.markdown("""<div class="section-title">🛣️ Multi-Stop Produce Collection Route Solver</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="chart-caption">Solve optimal collection sequence across farmgate aggregation centers to minimize transit distance, freight expenditure, and in-transit perishable loss.</div>""", unsafe_allow_html=True)

    avail_nodes = list(GEO_COORDINATES.keys())
    m_col1, m_col2 = st.columns([1, 1.4])

    with m_col1:
        st.markdown("""<div class="content-box">""", unsafe_allow_html=True)
        st.markdown("**1. Select Aggregation Collection Points:**")

        default_stops = ["Lasalgaon (Nashik)", "Pimpalgaon (Nashik)", "Nashik"]
        selected_stops = st.multiselect(
            "Farm Assemblies / Cold Rooms:",
            options=avail_nodes,
            default=[s for s in default_stops if s in avail_nodes],
            key="multi_stop_select"
        )

        dest_options = ["APMC Vashi (Navi Mumbai)", "Mumbai", "Pune", "Nagpur", "Solapur"]
        selected_dest = st.selectbox(
            "Destination Terminal Mandi:",
            options=[d for d in dest_options if d in avail_nodes],
            index=0,
            key="multi_dest_select"
        )

        v_type = st.selectbox(
            "Transport Vehicle Fleet:",
            options=["Refrigerated Reefer (10 MT)", "Multi-Axle Truck (16 MT)", "Tata 407 (3.5 MT)", "Open Canopy Canter (5 MT)"],
            index=0,
            key="multi_vehicle_select"
        )

        solve_btn = st.button("✦ Solve Optimal Route Sequence →", type="primary", use_container_width=True)
        st.markdown("""</div>""", unsafe_allow_html=True)

    with m_col2:
        all_stops_to_solve = list(dict.fromkeys(selected_stops + [selected_dest]))
        if solve_btn or "solved_route_cache" not in st.session_state:
            res = optimize_route(all_stops_to_solve, start=selected_stops[0] if selected_stops else None, end=selected_dest)
            st.session_state["solved_route_cache"] = res
        else:
            res = st.session_state.get("solved_route_cache", optimize_route(all_stops_to_solve, start=selected_stops[0] if selected_stops else None, end=selected_dest))

        ordered_nodes = res.get("ordered_stops", all_stops_to_solve)
        approx_km = res.get("approx_distance_km", 0.0)
        engine_label = res.get("engine", "network_heuristic_greedy")

        st.markdown(f"""
        <div class="content-box" style="border-left: 4px solid #10b981;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 800; color: #064e3b; font-size: 1.05rem;">📍 Solved Collection Sequence</span>
                <span style="font-size: 0.75rem; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 6px; font-weight: 700;">Engine: {engine_label}</span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-top: 12px; line-height: 1.6;">
                {' ➔ '.join([f'<span style="background:#e0f2fe; color:#0369a1; padding:3px 10px; border-radius:6px;">{s}</span>' for s in ordered_nodes])}
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px dashed #cbd5e1;">
                <div><small style="color:#64748b;">Total Route Distance</small><br><b style="font-size:1.1rem; color:#064e3b;">{approx_km:.1f} km</b></div>
                <div><small style="color:#64748b;">Estimated Transit Time</small><br><b style="font-size:1.1rem; color:#0369a1;">{max(2.5, approx_km / 38.0):.1f} hours</b></div>
                <div><small style="color:#64748b;">Estimated Freight Cost</small><br><b style="font-size:1.1rem; color:#059669;">₹{max(1200, approx_km * 28.0):,.0f}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Interactive Route Map
    if len(ordered_nodes) >= 2:
        route_lat = [GEO_COORDINATES[n]["lat"] for n in ordered_nodes if n in GEO_COORDINATES]
        route_lon = [GEO_COORDINATES[n]["lon"] for n in ordered_nodes if n in GEO_COORDINATES]
        route_txt = [f"{idx+1}. {n} ({GEO_COORDINATES[n]['type']})" for idx, n in enumerate(ordered_nodes) if n in GEO_COORDINATES]

        fig_route = go.Figure()
        fig_route.add_trace(go.Scattermapbox(
            mode="lines",
            lon=route_lon,
            lat=route_lat,
            line=dict(width=4, color="#059669"),
            hoverinfo="none",
            name="Optimized Route Path"
        ))
        fig_route.add_trace(go.Scattermapbox(
            mode="markers+text",
            lon=route_lon,
            lat=route_lat,
            marker=dict(size=14, color=["#3b82f6"] * (len(route_lat)-1) + ["#ef4444"]),
            text=[f"Stop {i+1}" for i in range(len(route_lat))],
            textposition="top right",
            hovertext=route_txt,
            name="Route Nodes"
        ))
        fig_route.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=float(np.mean(route_lat)), lon=float(np.mean(route_lon))),
                zoom=7.5
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=440,
            showlegend=False
        )
        st.plotly_chart(fig_route, use_container_width=True)


# =============================================================================
# COMPONENT 2: FLEET OPERATIONS & TELEMETRY
# =============================================================================
elif tab_selection == "📊 Fleet Operations & Telemetry":
    st.markdown("""<div class="section-title">📊 Fleet Operations & Perishable Telemetry Dashboard</div>""", unsafe_allow_html=True)

    ship_data = get_shipment_dashboard(selected_commodity)
    inv_data = get_inventory_snapshot(selected_commodity)
    stk_summary = partner_summary()

    t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
    with t_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Dispatches</div>
            <div class="kpi-value">{ship_data.get('shipment_count', 0):,}</div>
            <div class="kpi-sub">Simulated Trips</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Registered Fleet/FPOs</div>
            <div class="kpi-value">{stk_summary.get('count', 0)}</div>
            <div class="kpi-sub">Active Partners</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Storage Inventory</div>
            <div class="kpi-value">{inv_data.get('total_quantity_mt', 0):,.0f} MT</div>
            <div class="kpi-sub">In Warehouses</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Transit Delay</div>
            <div class="kpi-value">+{ship_data.get('avg_transit_delay_hrs', 0):.1f} hrs</div>
            <div class="kpi-sub">Ghat Bottlenecks</div>
        </div>
        """, unsafe_allow_html=True)
    with t_col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Spoilage Rate</div>
            <div class="kpi-value">{ship_data.get('avg_transit_loss_pct', 0):.1f}%</div>
            <div class="kpi-sub">In-Transit Loss</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div class="content-box">""", unsafe_allow_html=True)
        st.markdown("**Perishable Spoilage Rate by Vehicle Type:**")
        if ship_data.get("by_vehicle"):
            df_veh = pd.DataFrame(list(ship_data["by_vehicle"].items()), columns=["Vehicle Type", "Avg Transit Loss (%)"])
            fig_veh = px.bar(df_veh, x="Vehicle Type", y="Avg Transit Loss (%)", color="Avg Transit Loss (%)", color_continuous_scale="Reds")
            fig_veh.update_layout(template="plotly_white", height=280)
            st.plotly_chart(fig_veh, use_container_width=True)
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""<div class="content-box">""", unsafe_allow_html=True)
        st.markdown("**Storage Capacity Distribution by Storage Type:**")
        if inv_data.get("by_storage"):
            df_inv = pd.DataFrame(list(inv_data["by_storage"].items()), columns=["Storage Type", "Quantity (MT)"])
            fig_inv = px.pie(df_inv, values="Quantity (MT)", names="Storage Type", hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_inv.update_layout(template="plotly_white", height=280)
            st.plotly_chart(fig_inv, use_container_width=True)
        st.markdown("""</div>""", unsafe_allow_html=True)

    st.markdown("**Recent Simulated Dispatch Records (Top 25):**")
    if ship_data.get("rows"):
        df_ship_rows = pd.DataFrame(ship_data["rows"])
        st.dataframe(df_ship_rows.head(25), height=300, use_container_width=True, hide_index=True)


# =============================================================================
# COMPONENT 3: COLD STORAGE & WAREHOUSE GIS
# =============================================================================
elif tab_selection == "🏛️ Cold Storage & Warehouse GIS":
    st.markdown("""<div class="section-title">🏛️ Maharashtra Cold Storage & Warehouse Infrastructure GIS</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="chart-caption">Interactive geospatial map of state warehousing facilities, APMC cold rooms, and mega food park terminal hubs across Maharashtra.</div>""", unsafe_allow_html=True)

    w_tab1, w_tab2 = st.tabs(["🗺️ Interactive GIS Map", "🏢 MSWC Portal & Storage Inventory"])

    with w_tab1:
        st.markdown("""
        <div style="border: 1px solid #cbd5e1; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06); margin-bottom: 16px;">
            <iframe src="https://www.google.com/maps/d/embed?mid=14DOKTr6__WeEQLeSe-OWuY4jQJ6GeplT&ehbc=2E312F" width="100%" height="520" style="border: none;"></iframe>
        </div>
        """, unsafe_allow_html=True)
        st.caption("📍 Integrated Maharashtra State Warehouses & Cold Storages GIS Layer (Google MyMaps Embed)")

    with w_tab2:
        m_w1, m_w2 = st.columns([1.2, 1])
        with m_w1:
            st.markdown("""
            <div class="content-box">
                <div class="section-title">Maharashtra State Warehousing Corporation (MSWC)</div>
                <p>MSWC operates a network of over <b>200+ specialized warehouses and cold storage units</b> across 36 districts of Maharashtra, offering scientific storage, electronic Negotiable Warehouse Receipts (e-NWRs), and pledge loan financing at subsidized interest rates.</p>
                <div style="margin-top: 14px;">
                    <a href="https://mswarehousing.com/MSwhs/" target="_blank" style="text-decoration: none;">
                        <button style="background: linear-gradient(135deg, #064e3b 0%, #059669 100%); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer;">
                            🔗 Access MSWC Official Portal ↗
                        </button>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with m_w2:
            inv_data = get_inventory_snapshot(selected_commodity)
            st.markdown("""<div class="content-box">""", unsafe_allow_html=True)
            st.markdown("**Storage Stock Distribution:**")
            if inv_data.get("by_storage"):
                df_inv_chart = pd.DataFrame(list(inv_data["by_storage"].items()), columns=["Storage Type", "Quantity (MT)"])
                fig_inv = px.pie(
                    df_inv_chart,
                    values="Quantity (MT)",
                    names="Storage Type",
                    color="Storage Type",
                    color_discrete_map={"Ambient Yard": "#f59e0b", "Cold Room": "#3b82f6", "CA Store": "#10b981"},
                    hole=0.45
                )
                fig_inv.update_layout(template="plotly_white", height=240, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_inv, use_container_width=True)
            st.markdown("""</div>""", unsafe_allow_html=True)


# =============================================================================
# COMPONENT 4: WHAT-IF INTERVENTION SIMULATOR
# =============================================================================
elif tab_selection == "⚡ What-If Intervention Simulator":
    st.markdown("""<div class="section-title">⚡ Supply Chain Modernization & Perishable Loss Reduction Simulator</div>""", unsafe_allow_html=True)
    st.markdown("""<div class="chart-caption">Simulate impact of transit time reduction, cold chain coverage, plastic crate packaging, and direct FPO marketing based on MAGNET/ADB project benchmarks.</div>""", unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 1.3])

    with sim_col1:
        st.markdown("""<div class="content-box">""", unsafe_allow_html=True)
        st.markdown("**Intervention Parameters:**")

        prod_mt = st.number_input("Annual Cluster Production (MT):", min_value=50000.0, max_value=2000000.0, value=500000.0, step=50000.0)
        t_red = st.slider("Transit Time Reduction (%):", 0, 60, 30)
        c_cov = st.slider("Cold Chain Coverage (%):", 0, 80, 40)
        p_upg = st.slider("Plastic Crate Packaging Upgrade (%):", 0, 90, 50)
        f_dir = st.slider("FPO Direct Marketing Share (%):", 0, 80, 35)

        st.markdown("""</div>""", unsafe_allow_html=True)

    with sim_col2:
        sim_res = simulate_supply_chain_interventions(
            commodity=selected_commodity,
            state_annual_production_mt=prod_mt,
            transit_time_reduction_pct=t_red,
            cold_chain_coverage_pct=c_cov,
            packaging_upgrade_pct=p_upg,
            fpo_direct_share_pct=f_dir
        )

        base = sim_res["baseline"]
        sim = sim_res["simulated"]

        st.markdown("""<div class="content-box" style="border-left: 4px solid #059669;">""", unsafe_allow_html=True)
        st.markdown(f"### 📈 Projected Outcomes for {selected_commodity}")

        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("Baseline Loss", f"{base['loss_pct']:.1f}%", f"{base['lost_food_mt']:,.0f} MT lost")
        with r2:
            st.metric("Simulated Loss", f"{sim['loss_pct']:.1f}%", f"-{base['loss_pct'] - sim['loss_pct']:.1f}% reduction", delta_color="normal")
        with r3:
            st.metric("Food Waste Saved", f"{sim['recovered_food_mt']:,.0f} MT", f"₹{sim['recovered_annual_value_cr']:.1f} Cr saved")

        st.markdown("---")
        r4, r5, r6 = st.columns(3)
        with r4:
            st.metric("Farmer Net Realization", f"₹{sim['farmer_new_realization_rs_qtl']:,.0f}/Qtl", f"+{sim['farmer_income_gain_pct']:.1f}% gain")
        with r5:
            st.metric("Required CAPEX", f"₹{sim['capex_investment_cr']:.1f} Cr", f"{sim['payback_period_years']} yrs payback", delta_color="inverse")
        with r6:
            st.metric("Emissions Avoided", f"{sim['spoilage_emissions_avoided_tco2e']:,.0f} tCO2e", "Carbon Offset")

        st.markdown("""</div>""", unsafe_allow_html=True)


# =============================================================================
# COMPONENT 5: STAKEHOLDER & FLEET REGISTRY
# =============================================================================
elif tab_selection == "📋 Stakeholder & Fleet Registry":
    st.markdown("""<div class="section-title">📋 Registered Stakeholder & Logistics Fleet Registry</div>""", unsafe_allow_html=True)

    stk_filter = st.selectbox("Filter Stakeholders by Role:", ["All Roles", "Farmer / FPO", "Transporter", "Wholesaler", "Retailer", "Commission Agent", "Cold Storage"])
    df_stk_view = list_partners(role=None if stk_filter == "All Roles" else stk_filter)

    if not df_stk_view.empty:
        st.dataframe(df_stk_view, height=450, use_container_width=True, hide_index=True)
    else:
        st.info("No matching stakeholders found in synthetic operational database.")
