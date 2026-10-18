"""Load observed vs synthetic datasets with explicit provenance."""
from pathlib import Path
import pandas as pd
from logistics.config import (
    PROCESSED_DATA_DIR,
    SYNTHETIC_DATA_DIR,
    PROVENANCE_SYNTHETIC_OPS,
    PROVENANCE_ILLUSTRATIVE_NETWORK,
)


def load_synthetic_table(name: str):
    p = SYNTHETIC_DATA_DIR / f"{name}.csv"
    if not p.exists():
        return None
    return pd.read_csv(p)


def ensure_synthetic_ops_data(seed: int = 42) -> bool:
    """Generate synthetic ops CSVs if missing."""
    marker = SYNTHETIC_DATA_DIR / "shipments.csv"
    if marker.exists():
        return True
    try:
        import importlib.util
        gen_path = PROCESSED_DATA_DIR.parent.parent / "scripts" / "generate_synthetic_data.py"
        if not gen_path.exists():
            # Also check the logistics_route_optimization_module location
            from logistics.config import _MODULE_DIR
            gen_path = _MODULE_DIR / "scripts" / "generate_synthetic_data.py"
        spec = importlib.util.spec_from_file_location("generate_synthetic_data", gen_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.generate(seed=seed)
        return True
    except Exception:
        return False
