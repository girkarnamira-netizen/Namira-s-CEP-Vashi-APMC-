import pandas as pd


def safe_divide(n, d):
    if pd.isna(n) or pd.isna(d) or d == 0:
        return 0.0
    return float(n) / float(d)


def generate_recommendations(market_df, transport_df, distribution_df, farmer_df):
    recommendations = []

    if not farmer_df.empty:
        total_produced = float(farmer_df["Quantity_Produced_kg"].sum())
        total_waste = float(farmer_df["Quantity_Wasted_kg"].sum())
        loss_pct = safe_divide(total_waste, total_produced) * 100
        if loss_pct > 8:
            recommendations.append({
                "ISSUE": "HIGH PRODUCT LOSS",
                "METRIC": "Loss %",
                "ACTUAL_VALUE": round(loss_pct, 2),
                "THRESHOLD": 8,
                "RECOMMENDED_ACTION": "Investigate harvesting, handling, packaging and transport conditions to reduce post-harvest losses.",
            })

    if not transport_df.empty:
        avg_delay = float(transport_df["Delay_Hours"].mean())
        if avg_delay > 2:
            recommendations.append({
                "ISSUE": "TRANSPORTATION DELAY",
                "METRIC": "Average Delay (hours)",
                "ACTUAL_VALUE": round(avg_delay, 2),
                "THRESHOLD": 2,
                "RECOMMENDED_ACTION": "Review route planning, vehicle scheduling, lane assignment and departure timing for congestion-prone corridors.",
            })

        transport_cost_per_kg = safe_divide(transport_df["Transport_Cost_INR"].sum(), transport_df["Quantity_Transported_kg"].sum())
        if transport_cost_per_kg > 12:
            recommendations.append({
                "ISSUE": "HIGH TRANSPORT COST",
                "METRIC": "Transport Cost / kg",
                "ACTUAL_VALUE": round(transport_cost_per_kg, 2),
                "THRESHOLD": 12,
                "RECOMMENDED_ACTION": "Consider route optimization, shipment consolidation or alternate vehicle types to reduce unit transport cost.",
            })

    if not market_df.empty:
        price_spread = float((market_df["Wholesale_Max_INR_per_Qtl"] - market_df["Wholesale_Min_INR_per_Qtl"]).mean())
        if price_spread > 1800:
            recommendations.append({
                "ISSUE": "PRICE VARIATION",
                "METRIC": "Average Price Spread",
                "ACTUAL_VALUE": round(price_spread, 2),
                "THRESHOLD": 1800,
                "RECOMMENDED_ACTION": "Investigate commodity quality grading, market timing and sourcing strategy to reduce price volatility.",
            })

    if not distribution_df.empty:
        total_received = float(distribution_df["Quantity_kg"].sum()) if "Quantity_kg" in distribution_df.columns else float(distribution_df["Quantity_Delivered_kg"].sum())
        total_lost = float(distribution_df["Quantity_Lost_kg"].sum())
        dist_loss_pct = safe_divide(total_lost, total_received) * 100 if total_received else 0
        if dist_loss_pct > 6:
            recommendations.append({
                "ISSUE": "DISTRIBUTION LOSS",
                "METRIC": "Distribution Loss %",
                "ACTUAL_VALUE": round(dist_loss_pct, 2),
                "THRESHOLD": 6,
                "RECOMMENDED_ACTION": "Improve handling, loading/unloading coordination and storage practices at collection centres and distribution points.",
            })

    if not farmer_df.empty:
        source_share = farmer_df.groupby("Location")["Quantity_Produced_kg"].sum().sort_values(ascending=False)
        if not source_share.empty:
            top_share = safe_divide(source_share.iloc[0], source_share.sum()) * 100
            if top_share > 25:
                recommendations.append({
                    "ISSUE": "SUPPLY CONCENTRATION",
                    "METRIC": "Top Source Share %",
                    "ACTUAL_VALUE": round(top_share, 2),
                    "THRESHOLD": 25,
                    "RECOMMENDED_ACTION": "Diversify sourcing locations and increase supplier balancing to reduce dependence on a single source region.",
                })

    return recommendations
