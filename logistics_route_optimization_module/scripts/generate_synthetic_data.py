"""
Generate connected synthetic operations datasets (stakeholders, shipments, losses, inventory).
Usage: python scripts/generate_synthetic_data.py [--seed 42]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import SYNTHETIC_DATA_DIR, COMMODITIES, GEO_COORDINATES, PROVENANCE_SYNTHETIC_OPS


def generate(seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    SYNTHETIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

    node_names = list(GEO_COORDINATES.keys())
    roles = ["Farmer / FPO", "Commission Agent", "Transporter", "Wholesaler", "Retailer", "Cold Storage"]
    stakeholders = []
    for i in range(1, 81):
        node = rng.choice(node_names)
        stakeholders.append({
            "stakeholder_id": f"STK_{i:03d}",
            "name": f"Stakeholder {i}",
            "role": rng.choice(roles),
            "node_name": node,
            "district": GEO_COORDINATES[node]["district"],
            "commodities": ",".join(rng.choice(COMMODITIES, size=rng.integers(1, 3), replace=False)),
            "data_provenance": PROVENANCE_SYNTHETIC_OPS,
            "random_seed": seed,
        })
    df_stk = pd.DataFrame(stakeholders)
    df_stk.to_csv(SYNTHETIC_DATA_DIR / "stakeholders.csv", index=False)

    corridors_template = [
        ("Nashik", "APMC Vashi (Navi Mumbai)", "Onion", 180, 6.5, 4.5, 90),
        ("Lasalgaon (Nashik)", "Mumbai", "Onion", 210, 7.0, 4.0, 100),
        ("Pimpalgaon (Nashik)", "APMC Vashi (Navi Mumbai)", "Tomato", 195, 6.8, 7.8, 110),
        ("Junnar/Manchar (Pune)", "APMC Vashi (Navi Mumbai)", "Tomato", 160, 5.2, 6.8, 90),
        ("Agra (Uttar Pradesh)", "APMC Vashi (Navi Mumbai)", "Potato", 1250, 36.0, 4.5, 280),
        ("Indore (Madhya Pradesh)", "APMC Vashi (Navi Mumbai)", "Potato", 580, 16.0, 3.2, 160),
    ]
    corridor_rows = []
    for src, tgt, crop, dist, hrs, loss, freight in corridors_template:
        corridor_rows.append({
            "source": src,
            "target": tgt,
            "commodity": crop,
            "distance_km": dist,
            "transit_hrs": hrs,
            "loss_pct": loss,
            "freight_rs_qtl": freight,
            "flow_mt": float(rng.uniform(15000, 145000)),
            "data_provenance": PROVENANCE_SYNTHETIC_OPS,
            "random_seed": seed,
        })
    df_corridors = pd.DataFrame(corridor_rows)
    df_corridors.to_csv(SYNTHETIC_DATA_DIR / "corridors.csv", index=False)

    stages = [
        "Field Harvest", "Farm Packaging", "Primary Transit", "Mandi Yard", "Wholesale Storage", "Retail"
    ]
    stage_loss_rows = []
    for crop in COMMODITIES:
        base = {"Tomato": 33.0, "Onion": 24.0, "Potato": 17.5}[crop]
        weights = rng.dirichlet(np.ones(len(stages)))
        for stage, w in zip(stages, weights):
            stage_loss_rows.append({
                "commodity": crop,
                "stage": stage,
                "loss_pct_of_total": np.round(base * w, 2),
                "data_provenance": PROVENANCE_SYNTHETIC_OPS,
                "random_seed": seed,
            })
    df_stage = pd.DataFrame(stage_loss_rows)
    df_stage.to_csv(SYNTHETIC_DATA_DIR / "stage_losses.csv", index=False)

    shipments = []
    for i in range(1, 121):
        cr = corridor_rows[int(rng.integers(0, len(corridor_rows)))]
        qty_mt = float(rng.uniform(5, 45))
        shipments.append({
            "shipment_id": f"SHP_{i:04d}",
            "origin": cr["source"],
            "destination": cr["target"],
            "commodity": cr["commodity"],
            "quantity_mt": np.round(qty_mt, 2),
            "dispatch_date": (pd.Timestamp("2026-09-01") + pd.Timedelta(days=int(rng.integers(0, 34)))).strftime("%Y-%m-%d"),
            "scheduled_transit_hrs": cr["transit_hrs"],
            "actual_transit_hrs": np.round(cr["transit_hrs"] + rng.uniform(0.5, 4.0), 1),
            "transit_loss_pct": np.round(cr["loss_pct"] * rng.uniform(0.6, 1.2), 2),
            "freight_rs_qtl": cr["freight_rs_qtl"],
            "vehicle_type": rng.choice(["Open Canter", "Tata 407", "Multi-Axle", "Reefer"]),
            "stakeholder_id": f"STK_{int(rng.integers(1, 81)):03d}",
            "data_provenance": PROVENANCE_SYNTHETIC_OPS,
            "random_seed": seed,
        })
    df_ship = pd.DataFrame(shipments)
    df_ship.to_csv(SYNTHETIC_DATA_DIR / "shipments.csv", index=False)

    inventory = []
    for i in range(1, 41):
        crop = rng.choice(COMMODITIES)
        inventory.append({
            "inventory_id": f"INV_{i:03d}",
            "facility_node": rng.choice(node_names),
            "commodity": crop,
            "quantity_mt": np.round(rng.uniform(20, 800), 1),
            "storage_type": rng.choice(["Ambient Yard", "Cold Room", "CA Store"]),
            "days_in_storage": int(rng.integers(1, 14)),
            "spoilage_pct": np.round(rng.uniform(0.5, 8.0), 2),
            "data_provenance": PROVENANCE_SYNTHETIC_OPS,
            "random_seed": seed,
        })
    df_inv = pd.DataFrame(inventory)
    df_inv.to_csv(SYNTHETIC_DATA_DIR / "inventory.csv", index=False)

    interventions = []
    for name, transit, cold, pack, fpo in [
        ("Baseline", 0, 0, 0, 0),
        ("Green Corridor Pilot", 30, 20, 40, 15),
        ("FPO Direct + Crates", 15, 35, 70, 45),
        ("Full Cold Chain Cluster", 40, 60, 55, 30),
    ]:
        interventions.append({
            "scenario_name": name,
            "transit_time_reduction_pct": transit,
            "cold_chain_coverage_pct": cold,
            "packaging_upgrade_pct": pack,
            "fpo_direct_share_pct": fpo,
            "data_provenance": PROVENANCE_SYNTHETIC_OPS,
            "random_seed": seed,
        })
    df_int = pd.DataFrame(interventions)
    df_int.to_csv(SYNTHETIC_DATA_DIR / "intervention_scenarios.csv", index=False)

    return {
        "stakeholders": len(df_stk),
        "corridors": len(df_corridors),
        "shipments": len(df_ship),
        "inventory": len(df_inv),
        "stage_losses": len(df_stage),
        "interventions": len(df_int),
        "output_dir": str(SYNTHETIC_DATA_DIR),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ops datasets")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    summary = generate(seed=args.seed)
    print("Synthetic data written:", summary)


if __name__ == "__main__":
    main()
