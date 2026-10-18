# 🚛 Logistics Route Optimization & Intelligence Module

This is a standalone, decoupled module extracted from AgriFlow for **Logistics Route Optimization, Perishable Fleet Telemetry, Cold Chain Infrastructure GIS, and What-If Supply Chain Modernization**.

---

## 📁 Folder & Code Structure

```
logistics_route_optimization_module/
├── app.py                             # Standalone Interactive Streamlit Dashboard UI
├── requirements.txt                   # Module Python Dependencies
├── README.md                          # Comprehensive Documentation
├── src/                               # Core Python Module Source Code
│   ├── config.py                      # Geographic coordinates, baseline study parameters, & paths
│   ├── route_optimizer.py             # Multi-stop Collection Route Solver (VRP / Geodesic TSP)
│   ├── logistics.py                   # Fleet telemetry, shipment dispatches, & inventory analytics
│   ├── optimizer.py                   # Supply chain intervention & food loss reduction simulator
│   ├── partner_manager.py             # Stakeholder & fleet partner registry manager
│   └── data_pipeline.py               # Data loaders & synthetic operations generator caller
├── scripts/
│   └── generate_synthetic_data.py    # Synthetic operational dataset generator (seed=42)
└── data/
    └── processed/
        └── synthetic/                 # Operations datasets (shipments, inventory, corridors, etc.)
            ├── corridors.csv
            ├── inventory.csv
            ├── intervention_scenarios.csv
            ├── shipments.csv
            ├── stage_losses.csv
            └── stakeholders.csv
```

---

## 🛠️ Extracted Components & Code Functions

| Module File | Functionality & Code Purpose | Key Functions / Classes |
| :--- | :--- | :--- |
| `src/route_optimizer.py` | Calculates geodesic Haversine distance, solves optimal multi-stop produce collection sequence across farm hubs, and integrates OR-Tools VRP/TSP solver constraints. | `optimize_route()`, `_haversine_km()` |
| `src/logistics.py` | Provides fleet dispatch telemetry, transit delays, in-transit perishable loss analytics, and storage stock summaries. | `get_shipment_dashboard()`, `get_inventory_snapshot()`, `corridor_freight_audit()` |
| `src/optimizer.py` | What-if supply chain modernization simulator based on MAGNET/ADB project benchmarks (53264-001-smr-en) evaluating transit reduction, cold chain coverage, crate packaging, CAPEX, and food saved. | `simulate_supply_chain_interventions()` |
| `src/partner_manager.py` | Stakeholder registry for FPOs, transporters, cold storage operators, and wholesalers. | `list_partners()`, `partner_summary()` |
| `src/config.py` | Geographic node catalog (`GEO_COORDINATES`) for Maharashtra & inter-state supply hubs, baseline APMC study parameters (`VASHI_STUDY_BASELINE`), and system configuration. | `GEO_COORDINATES`, `VASHI_STUDY_BASELINE` |
| `src/data_pipeline.py` | Data loader and synthetic pipeline manager ensuring operational data availability. | `load_synthetic_table()`, `ensure_synthetic_ops_data()` |
| `scripts/generate_synthetic_data.py` | Generates reproducible synthetic fleet, shipment, inventory, corridor, and stakeholder datasets (seed=42). | `generate()` |
| `app.py` | Standalone interactive Streamlit web application providing a 5-in-1 logistics intelligence portal with live Plotly map rendering. | Full UI Dashboard Application |

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate / Verify Operational Datasets
```bash
python scripts/generate_synthetic_data.py --seed 42
```

### 3. Launch the Standalone Web App
```bash
streamlit run app.py
```

---

## 🗺️ Geo-Coordinates & Route Solver Nodes
The module includes built-in coordinates for all key production, assembly, and terminal market hubs:
- **Terminal Mandis**: APMC Vashi (Navi Mumbai), Mumbai, Pune, Nagpur, Solapur, Kolhapur, Chhatrapati Sambhajinagar.
- **Production Valley Hubs**: Nashik, Lasalgaon, Pimpalgaon, Junnar/Manchar, Ahilyanagar (Ahmednagar), Satara, Sangli, Jalgaon.
- **Inter-State Sources**: Agra (UP), Indore (MP), Deesa (Gujarat).
