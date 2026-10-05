from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REQUIRED_FILES = {
    "farmers": "farmers.csv",
    "market_prices": "market_prices.csv",
    "transportation": "transportation.csv",
    "distribution": "distribution.csv",
    "supply_chain_mapping": "supply_chain_mapping.csv",
    "onion_economics_reference": "onion_economics_reference.csv",
    "data_dictionary": "data_dictionary.csv",
}

REQUIRED_COLUMNS = {
    "farmers": ["Farmer_ID", "Location", "Product", "Quantity_Produced_kg", "Quantity_Sold_kg", "Quantity_Wasted_kg", "Harvest_Date"],
    "market_prices": ["Date", "Commodity", "Wholesale_Modal_INR_per_Qtl", "Wholesale_Min_INR_per_Qtl", "Wholesale_Max_INR_per_Qtl", "Arrival_Quantity_Tonnes"],
    "transportation": ["Shipment_ID", "Product", "Source", "Distance_km", "Transport_Mode", "Transport_Cost_INR", "Delay_Hours", "Quantity_Transported_kg", "Quantity_Damaged_kg"],
    "distribution": ["Product", "Farmer_Source", "Collection_Centre", "Distributor", "Quantity_kg", "Quantity_Delivered_kg", "Quantity_Lost_kg"],
    "supply_chain_mapping": ["Farmer_ID", "Location", "Product", "Quantity_Produced_kg", "Quantity_Sold_kg", "Quantity_Wasted_kg", "Collection_Centre", "Transport_Mode", "APMC_Market", "Distributor_Type"],
}


def read_csv_file(filename):
    candidate_paths = [DATA_DIR / filename, ROOT / filename]
    for path in candidate_paths:
        if path.exists():
            try:
                return pd.read_csv(path)
            except Exception:
                return pd.DataFrame()
    return pd.DataFrame()


def load_datasets():
    return {
        "farmers": read_csv_file("farmers.csv"),
        "market_prices": read_csv_file("market_prices.csv"),
        "transportation": read_csv_file("transportation.csv"),
        "distribution": read_csv_file("distribution.csv"),
        "supply_chain_mapping": read_csv_file("supply_chain_mapping.csv"),
        "onion_economics_reference": read_csv_file("onion_economics_reference.csv"),
        "data_dictionary": read_csv_file("data_dictionary.csv"),
    }


def validate_datasets(datasets):
    missing_files = []
    missing_columns = {}
    for key, filename in REQUIRED_FILES.items():
        if key not in datasets or datasets[key] is None or datasets[key].empty:
            missing_files.append(filename)
            continue
        expected_cols = REQUIRED_COLUMNS.get(key, [])
        missing = [col for col in expected_cols if col not in datasets[key].columns]
        if missing:
            missing_columns[key] = missing

    ok = not missing_files and not missing_columns
    return {
        "ok": ok,
        "missing_files": missing_files,
        "missing_columns": missing_columns,
        "message": (
            "All required datasets and fields loaded successfully." if ok else "One or more required datasets or key columns are missing."
        ),
    }
