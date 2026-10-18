"""Stakeholder registry backed by synthetic ops CSV (explicit provenance)."""
import pandas as pd
from src.data_pipeline import load_synthetic_table, ensure_synthetic_ops_data


def list_partners(role: str | None = None, commodity: str | None = None) -> pd.DataFrame:
    ensure_synthetic_ops_data()
    df = load_synthetic_table("stakeholders")
    if df is None or df.empty:
        return pd.DataFrame()
    if role:
        df = df[df["role"].astype(str).str.contains(role, case=False, na=False)]
    if commodity:
        df = df[df["commodities"].astype(str).str.contains(commodity, case=False, na=False)]
    return df.reset_index(drop=True)


def partner_summary() -> dict:
    df = list_partners()
    if df.empty:
        return {"count": 0, "by_role": {}, "data_provenance": "none"}
    by_role = df["role"].value_counts().to_dict()
    return {
        "count": int(len(df)),
        "by_role": by_role,
        "data_provenance": df["data_provenance"].iloc[0] if "data_provenance" in df.columns else "synthetic_ops",
    }
