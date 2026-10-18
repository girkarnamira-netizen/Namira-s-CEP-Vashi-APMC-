"""Logistics network intelligence — shipments, inventory, and corridor KPIs from synthetic ops tables."""
import pandas as pd
import numpy as np
from src.data_pipeline import load_synthetic_table, ensure_synthetic_ops_data


def get_shipment_dashboard(commodity: str | None = None) -> dict:
    ensure_synthetic_ops_data()
    df = load_synthetic_table("shipments")
    if df is None or df.empty:
        return {"status": "no_data", "rows": []}
    if commodity:
        df = df[df["commodity"].astype(str).str.contains(commodity, case=False, na=False)]
    df["delay_hrs"] = pd.to_numeric(df["actual_transit_hrs"], errors="coerce") - pd.to_numeric(
        df["scheduled_transit_hrs"], errors="coerce"
    )
    return {
        "status": "ok",
        "data_provenance": df["data_provenance"].iloc[0] if "data_provenance" in df.columns else "synthetic_ops",
        "shipment_count": int(len(df)),
        "avg_transit_delay_hrs": float(np.nanmean(df["delay_hrs"])) if len(df) else 0.0,
        "avg_transit_loss_pct": float(np.nanmean(pd.to_numeric(df["transit_loss_pct"], errors="coerce"))) if len(df) else 0.0,
        "by_vehicle": df.groupby("vehicle_type")["transit_loss_pct"].mean().round(2).to_dict() if "vehicle_type" in df.columns else {},
        "rows": df.head(50).to_dict(orient="records"),
    }


def get_inventory_snapshot(commodity: str | None = None) -> dict:
    ensure_synthetic_ops_data()
    df = load_synthetic_table("inventory")
    if df is None or df.empty:
        return {"status": "no_data", "rows": []}
    if commodity:
        df = df[df["commodity"] == commodity]
    return {
        "status": "ok",
        "data_provenance": df["data_provenance"].iloc[0] if "data_provenance" in df.columns else "synthetic_ops",
        "total_quantity_mt": float(pd.to_numeric(df["quantity_mt"], errors="coerce").sum()),
        "avg_spoilage_pct": float(pd.to_numeric(df["spoilage_pct"], errors="coerce").mean()),
        "by_storage": df.groupby("storage_type")["quantity_mt"].sum().round(1).to_dict(),
        "rows": df.to_dict(orient="records"),
    }


def corridor_freight_audit() -> pd.DataFrame:
    """Load corridor freight dataset for logistics network analysis."""
    df = load_synthetic_table("corridors")
    if df is not None and not df.empty:
        return df
    return pd.DataFrame()
