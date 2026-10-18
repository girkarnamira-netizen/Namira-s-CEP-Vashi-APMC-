import pandas as pd


def safe_divide(n, d):
    if pd.isna(n) or pd.isna(d) or d == 0:
        return 0.0
    return float(n) / float(d)


def numeric_values(frame, column):
    if column not in frame.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").dropna()


def recommendation(issue, metric, actual, threshold, action):
    return {
        "ISSUE": issue,
        "METRIC": metric,
        "ACTUAL_VALUE": round(actual, 2),
        "THRESHOLD": threshold,
        "PRIORITY": "High" if actual >= threshold * 1.5 else "Medium",
        "RECOMMENDED_ACTION": action,
    }


def generate_recommendations(market_df, transport_df, distribution_df, farmer_df):
    recommendations = []

    if not farmer_df.empty and {"Quantity_Produced_kg", "Quantity_Wasted_kg"}.issubset(farmer_df.columns):
        total_produced = float(numeric_values(farmer_df, "Quantity_Produced_kg").sum())
        total_waste = float(numeric_values(farmer_df, "Quantity_Wasted_kg").sum())
        loss_pct = safe_divide(total_waste, total_produced) * 100
        if loss_pct > 8:
            recommendations.append(recommendation(
                "HIGH PRODUCT LOSS", "Loss %", loss_pct, 8,
                "Investigate harvesting, handling, packaging and transport conditions to reduce post-harvest losses.",
            ))

    if not transport_df.empty and "Delay_Hours" in transport_df.columns:
        delays = numeric_values(transport_df, "Delay_Hours")
        avg_delay = float(delays.mean()) if not delays.empty else 0.0
        if avg_delay > 2:
            recommendations.append(recommendation(
                "TRANSPORTATION DELAY", "Average Delay (hours)", avg_delay, 2,
                "Review route planning, vehicle scheduling, lane assignment and departure timing for congestion-prone corridors.",
            ))

        if {"Transport_Cost_INR", "Quantity_Transported_kg"}.issubset(transport_df.columns):
            transport_cost_per_kg = safe_divide(
                numeric_values(transport_df, "Transport_Cost_INR").sum(),
                numeric_values(transport_df, "Quantity_Transported_kg").sum(),
            )
            if transport_cost_per_kg > 12:
                recommendations.append(recommendation(
                    "HIGH TRANSPORT COST", "Transport Cost / kg", transport_cost_per_kg, 12,
                    "Consider route optimization, shipment consolidation or alternate vehicle types to reduce unit transport cost.",
                ))

    if not market_df.empty and {"Wholesale_Max_INR_per_Qtl", "Wholesale_Min_INR_per_Qtl"}.issubset(market_df.columns):
        price_spread = float((
            numeric_values(market_df, "Wholesale_Max_INR_per_Qtl")
            - numeric_values(market_df, "Wholesale_Min_INR_per_Qtl")
        ).dropna().mean())
        if price_spread > 1800:
            if pd.notna(price_spread):
                recommendations.append(recommendation(
                    "PRICE VARIATION", "Average Price Spread", price_spread, 1800,
                    "Investigate commodity quality grading, market timing and sourcing strategy to reduce price volatility.",
                ))

    if not distribution_df.empty and "Quantity_Lost_kg" in distribution_df.columns:
        quantity_column = "Quantity_kg" if "Quantity_kg" in distribution_df.columns else "Quantity_Delivered_kg"
        total_received = float(numeric_values(distribution_df, quantity_column).sum())
        total_lost = float(numeric_values(distribution_df, "Quantity_Lost_kg").sum())
        dist_loss_pct = safe_divide(total_lost, total_received) * 100 if total_received else 0
        if dist_loss_pct > 6:
            recommendations.append(recommendation(
                "DISTRIBUTION LOSS", "Distribution Loss %", dist_loss_pct, 6,
                "Improve handling, loading/unloading coordination and storage practices at collection centres and distribution points.",
            ))

    if not farmer_df.empty and {"Location", "Quantity_Produced_kg"}.issubset(farmer_df.columns):
        source_data = farmer_df[["Location"]].copy()
        source_data["Quantity_Produced_kg"] = numeric_values(farmer_df, "Quantity_Produced_kg")
        source_share = source_data.groupby("Location")["Quantity_Produced_kg"].sum().sort_values(ascending=False)
        if not source_share.empty:
            top_share = safe_divide(source_share.iloc[0], source_share.sum()) * 100
            if top_share > 25:
                recommendations.append(recommendation(
                    "SUPPLY CONCENTRATION", "Top Source Share %", top_share, 25,
                    "Diversify sourcing locations and increase supplier balancing to reduce dependence on a single source region.",
                ))

    return recommendations
