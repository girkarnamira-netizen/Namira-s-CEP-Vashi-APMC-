import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
SYNTHETIC_DATA_DIR = PROCESSED_DATA_DIR / "synthetic"
DEFAULT_RANDOM_SEED = 42

# Data lineage labels
PROVENANCE_SYNTHETIC_OPS = "synthetic_ops_simulation_seed_42"
PROVENANCE_ILLUSTRATIVE_NETWORK = "illustrative_network_intelligence"
PROVENANCE_VASHI_STUDY = "observed_apmc_vashi_study_baseline"

# Ensure directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Commodity List
COMMODITIES = ["Onion", "Potato", "Tomato"]

# Target Markets & Coordinates (Maharashtra & National Supply Hubs)
GEO_COORDINATES = {
    # Major Maharashtra Consumption & APMC Hubs
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "type": "Terminal APMC & Consumption", "district": "Mumbai"},
    "APMC Vashi (Navi Mumbai)": {"lat": 19.0771, "lon": 73.0033, "type": "Primary Terminal Mandi", "district": "Thane/Mumbai"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "type": "Major Mandi & Consumption", "district": "Pune"},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "type": "Regional Hub & APMC", "district": "Nagpur"},
    "Solapur": {"lat": 17.6599, "lon": 75.9064, "type": "Secondary Mandi & Production", "district": "Solapur"},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433, "type": "Secondary Mandi & Consumption", "district": "Kolhapur"},
    "Chattrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433, "type": "Regional Mandi Hub", "district": "Chattrapati Sambhajinagar"},

    # Major Maharashtra Production Hubs
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "type": "Primary Production Hub (Onion/Tomato)", "district": "Nashik"},
    "Lasalgaon (Nashik)": {"lat": 20.1472, "lon": 74.2267, "type": "Asia's Largest Onion Mandi", "district": "Nashik"},
    "Pimpalgaon (Nashik)": {"lat": 20.1667, "lon": 73.9833, "type": "Major Tomato & Onion Mandi", "district": "Nashik"},
    "Ahilyanagar (Ahmednagar)": {"lat": 19.0948, "lon": 74.7480, "type": "Major Onion Production & Mandi", "district": "Ahilyanagar"},
    "Rahata/Shirdi (Ahilyanagar)": {"lat": 19.6644, "lon": 74.4820, "type": "Assembly Mandi", "district": "Ahilyanagar"},
    "Junnar/Manchar (Pune)": {"lat": 19.2065, "lon": 73.8767, "type": "Tomato Production Valley", "district": "Pune"},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626, "type": "Production & Assembly Mandi", "district": "Jalgaon"},
    "Satara": {"lat": 17.6805, "lon": 73.9997, "type": "Assembly & Potato Hub", "district": "Satara"},
    "Sangli": {"lat": 16.8524, "lon": 74.5815, "type": "Assembly Mandi", "district": "Sangli"},
    "Amravati": {"lat": 20.9374, "lon": 77.7796, "type": "Vidarbha Mandi", "district": "Amravati"},

    # Inter-state potato sourcing hubs (from Vashi study)
    "Agra (Uttar Pradesh)": {"lat": 27.1767, "lon": 78.0081, "type": "Inter-State Potato Source", "district": "Agra"},
    "Indore (Madhya Pradesh)": {"lat": 22.7196, "lon": 75.8577, "type": "Inter-State Potato Source", "district": "Indore"},
    "Deesa (Gujarat)": {"lat": 24.2586, "lon": 72.1812, "type": "Inter-State Potato Source", "district": "Banaskantha"}
}

# Baseline Logistics & Cost Benchmarks from APMC Vashi Field Study
VASHI_STUDY_BASELINE = {
    "Potato": {
        "farmer_net_price_rs_qtl": 1020.0,
        "farmer_marketing_cost_rs_qtl": 100.0,
        "wholesaler_cost_rs_qtl": 354.0,
        "wholesaler_margin_rs_qtl": 88.0,
        "retailer_cost_rs_qtl": 135.0,
        "retailer_margin_rs_qtl": 803.0,
        "retail_price_rs_qtl": 2500.0,
        "price_spread_rs_qtl": 1480.0,
        "marketing_efficiency_acharya": 0.69,
        "farmer_share_pct": 40.8
    },
    "Onion": {
        "farmer_net_price_rs_qtl": 1250.0,
        "farmer_marketing_cost_rs_qtl": 100.0,
        "wholesaler_cost_rs_qtl": 254.0,
        "wholesaler_margin_rs_qtl": 96.0,
        "retailer_cost_rs_qtl": 137.0,
        "retailer_margin_rs_qtl": 1163.0,
        "retail_price_rs_qtl": 3000.0,
        "price_spread_rs_qtl": 1750.0,
        "marketing_efficiency_acharya": 0.71,
        "farmer_share_pct": 41.7
    },
    "Tomato": {
        "farmer_net_price_rs_qtl": 1100.0,
        "farmer_marketing_cost_rs_qtl": 140.0,
        "wholesaler_cost_rs_qtl": 280.0,
        "wholesaler_margin_rs_qtl": 120.0,
        "retailer_cost_rs_qtl": 160.0,
        "retailer_margin_rs_qtl": 1200.0,
        "retail_price_rs_qtl": 3000.0,
        "price_spread_rs_qtl": 1900.0,
        "marketing_efficiency_acharya": 0.58,
        "farmer_share_pct": 36.7
    }
}
