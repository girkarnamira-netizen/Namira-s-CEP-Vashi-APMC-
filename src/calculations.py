import numpy as np
import pandas as pd


def safe_divide(numerator, denominator):
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def format_currency(value):
    return round(float(value), 2)


def aggregate_by_time(df, granularity="Daily", date_col="Date"):
    if df is None or df.empty:
        return pd.DataFrame()
    temp = df.copy()
    if date_col not in temp.columns:
        return pd.DataFrame()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna(subset=[date_col])
    if temp.empty:
        return pd.DataFrame()

    if granularity == "Weekly":
        temp[date_col] = temp[date_col].dt.to_period("W-MON").dt.start_time
    elif granularity == "Monthly":
        temp[date_col] = temp[date_col].dt.to_period("M").dt.start_time

    return temp.groupby(date_col, as_index=False).agg({
        "Arrival_Quantity_Tonnes": "sum",
        "Wholesale_Modal_INR_per_Qtl": "mean",
        "Wholesale_Min_INR_per_Qtl": "mean",
        "Wholesale_Max_INR_per_Qtl": "mean",
        "Transport_Cost_INR": "sum",
        "Delay_Hours": "mean",
        "Quantity_Damaged_kg": "sum",
        "Quantity_Lost_kg": "sum",
        "Quantity_Transported_kg": "sum",
        "Quantity_Delivered_kg": "sum",
        "Quantity_Produced_kg": "sum",
        "Quantity_Sold_kg": "sum",
        "Quantity_Wasted_kg": "sum",
        "Production_Cost_INR": "sum",
        "Selling_Price_INR_per_Qtl": "mean",
    })


def compute_kpis(farmers, market, transport, distribution):
    total_produced = float(farmers["Quantity_Produced_kg"].sum()) if not farmers.empty else 0.0
    total_sent = float(farmers["Quantity_Sold_kg"].sum()) if not farmers.empty else 0.0
    arrival_kg = float((market["Arrival_Quantity_Tonnes"] * 1000).sum()) if not market.empty else 0.0
    avg_modal_price = float(market["Wholesale_Modal_INR_per_Qtl"].mean()) if not market.empty else 0.0
    total_transport_cost = float(transport["Transport_Cost_INR"].sum()) if not transport.empty else 0.0
    total_waste = float(farmers["Quantity_Wasted_kg"].sum()) if not farmers.empty else 0.0
    total_distribution_loss = float(distribution["Quantity_Lost_kg"].sum()) if not distribution.empty else 0.0
    total_quantity_lost = total_waste + total_distribution_loss
    avg_loss_pct = safe_divide(total_quantity_lost, total_produced) * 100
    avg_delay = float(transport["Delay_Hours"].mean()) if not transport.empty else 0.0

    return {
        "total_quantity_produced": total_produced,
        "quantity_sent_to_market": total_sent,
        "quantity_arriving_at_apmc": arrival_kg,
        "average_modal_price": avg_modal_price,
        "total_transport_cost": total_transport_cost,
        "total_quantity_lost": total_quantity_lost,
        "average_loss_pct": avg_loss_pct,
        "average_transport_delay": avg_delay,
    }


def compute_time_series(market, granularity="Daily"):
    if market is None or market.empty:
        return pd.DataFrame(columns=["Date", "Arrival_Quantity_kg", "Modal_Price", "Min_Price", "Max_Price", "Transport_Cost", "Loss", "Damage", "Delay"])
    temp = market.copy()
    temp = temp.dropna(subset=["Date"])
    if temp.empty:
        return pd.DataFrame(columns=["Date", "Arrival_Quantity_kg", "Modal_Price", "Min_Price", "Max_Price", "Transport_Cost", "Loss", "Damage", "Delay"])

    if granularity == "Weekly":
        temp["Date"] = temp["Date"].dt.to_period("W-MON").dt.start_time
    elif granularity == "Monthly":
        temp["Date"] = temp["Date"].dt.to_period("M").dt.start_time

    agg = temp.groupby("Date", as_index=False).agg(
        Arrival_Quantity_kg=("Arrival_Quantity_Tonnes", lambda s: float((s * 1000).sum())),
        Modal_Price=("Wholesale_Modal_INR_per_Qtl", "mean"),
        Min_Price=("Wholesale_Min_INR_per_Qtl", "mean"),
        Max_Price=("Wholesale_Max_INR_per_Qtl", "mean"),
    )
    agg["Date"] = pd.to_datetime(agg["Date"])
    return agg


def compute_period_comparison(series_df, current_period_label="Current Month", previous_period_label="Previous Month"):
    if series_df is None or series_df.empty:
        return pd.DataFrame(columns=["Metric", "Current", "Previous", "Change_pct"])
    if "Date" not in series_df.columns:
        return pd.DataFrame(columns=["Metric", "Current", "Previous", "Change_pct"])

    series_df = series_df.copy()
    series_df["Date"] = pd.to_datetime(series_df["Date"])
    series_df = series_df.sort_values("Date")
    latest = series_df.iloc[-1]
    previous = series_df.iloc[-2] if len(series_df) > 1 else latest
    current_value = float(latest.get("Value", 0))
    previous_value = float(previous.get("Value", 0))
    change_pct = safe_divide(current_value - previous_value, previous_value) * 100
    return pd.DataFrame([
        {"Metric": current_period_label, "Current": current_value, "Previous": previous_value, "Change_pct": change_pct}
    ])


def compute_data_quality(datasets):
    report = []
    for name, df in datasets.items():
        if df is None or df.empty:
            continue
        missing = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        negative_quantities = 0
        invalid_dates = 0
        impossible_prices = 0

        for col in df.columns:
            if any(token in col.lower() for token in ["quantity", "kg", "tonnes"]):
                negative_quantities += int((df[col] < 0).sum())
            if "date" in col.lower():
                invalid_dates += int(df[col].isna().sum())
            if any(token in col.lower() for token in ["price", "cost", "inr"]):
                impossible_prices += int((df[col] < 0).sum())

        report.append({
            "Table": name,
            "Rows": int(len(df)),
            "Missing_Values": missing,
            "Duplicate_Rows": duplicate_rows,
            "Negative_Quantities": negative_quantities,
            "Invalid_Dates": invalid_dates,
            "Impossible_Prices": impossible_prices,
        })
    return pd.DataFrame(report)
