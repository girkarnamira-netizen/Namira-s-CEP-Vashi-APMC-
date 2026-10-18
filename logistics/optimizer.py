import numpy as np
import pandas as pd
from logistics.config import VASHI_STUDY_BASELINE

def simulate_supply_chain_interventions(
    commodity="Tomato",
    state_annual_production_mt=500000.0,
    transit_time_reduction_pct=30.0,
    cold_chain_coverage_pct=40.0,
    packaging_upgrade_pct=50.0,
    fpo_direct_share_pct=35.0
):
    base = VASHI_STUDY_BASELINE.get(commodity, VASHI_STUDY_BASELINE["Tomato"])

    baseline_loss_pct = 33.0 if commodity == "Tomato" else (24.0 if commodity == "Onion" else 17.5)
    farmer_net_price = base["farmer_net_price_rs_qtl"]
    retail_price = base["retail_price_rs_qtl"]
    baseline_marketing_cost = base["farmer_marketing_cost_rs_qtl"] + base["wholesaler_cost_rs_qtl"] + base["retailer_cost_rs_qtl"]

    transit_loss_saving = (baseline_loss_pct * 0.25) * (transit_time_reduction_pct / 100.0)
    cold_chain_loss_saving = (baseline_loss_pct * 0.35) * (cold_chain_coverage_pct / 100.0)
    packaging_loss_saving = (baseline_loss_pct * 0.20) * (packaging_upgrade_pct / 100.0)

    total_loss_reduction_pct = min(baseline_loss_pct * 0.70, transit_loss_saving + cold_chain_loss_saving + packaging_loss_saving)
    simulated_loss_pct = baseline_loss_pct - total_loss_reduction_pct

    baseline_lost_mt = state_annual_production_mt * (baseline_loss_pct / 100.0)
    simulated_lost_mt = state_annual_production_mt * (simulated_loss_pct / 100.0)
    recovered_food_mt = baseline_lost_mt - simulated_lost_mt

    recovered_value_rs = recovered_food_mt * (farmer_net_price * 10.0)
    recovered_value_cr = recovered_value_rs / 1e7

    commission_saved_rs_qtl = (farmer_net_price * 0.06) * (fpo_direct_share_pct / 100.0)
    freight_saved_rs_qtl = 25.0 * (fpo_direct_share_pct / 100.0)
    farmer_gain_rs_qtl = commission_saved_rs_qtl + freight_saved_rs_qtl + (recovered_value_rs / (state_annual_production_mt * 10.0))
    simulated_farmer_price = farmer_net_price + farmer_gain_rs_qtl
    farmer_income_increase_pct = (farmer_gain_rs_qtl / farmer_net_price) * 100.0

    simulated_marketing_cost = baseline_marketing_cost - commission_saved_rs_qtl - (freight_saved_rs_qtl * 0.5)
    simulated_me_acharya = simulated_farmer_price / (simulated_marketing_cost + base["wholesaler_margin_rs_qtl"] + base["retailer_margin_rs_qtl"])

    capex_cr = 45.0 * ((cold_chain_coverage_pct + packaging_upgrade_pct) / 100.0)
    payback_years = np.round(capex_cr / max(recovered_value_cr, 1.0), 1)

    emissions_avoided_tco2e = (recovered_food_mt * 1000 * 1.8) / 1000.0

    return {
        "commodity": commodity,
        "parameters": {
            "transit_time_reduction_pct": transit_time_reduction_pct,
            "cold_chain_coverage_pct": cold_chain_coverage_pct,
            "packaging_upgrade_pct": packaging_upgrade_pct,
            "fpo_direct_share_pct": fpo_direct_share_pct,
            "annual_production_mt": state_annual_production_mt
        },
        "baseline": {
            "loss_pct": baseline_loss_pct,
            "lost_food_mt": np.round(baseline_lost_mt, 1),
            "farmer_realization_rs_qtl": np.round(farmer_net_price, 1),
            "marketing_cost_rs_qtl": np.round(baseline_marketing_cost, 1),
            "marketing_efficiency_acharya": np.round(base["marketing_efficiency_acharya"], 2)
        },
        "simulated": {
            "loss_pct": np.round(simulated_loss_pct, 1),
            "lost_food_mt": np.round(simulated_lost_mt, 1),
            "recovered_food_mt": np.round(recovered_food_mt, 1),
            "recovered_annual_value_cr": np.round(recovered_value_cr, 2),
            "farmer_new_realization_rs_qtl": np.round(simulated_farmer_price, 1),
            "farmer_income_gain_pct": np.round(farmer_income_increase_pct, 1),
            "simulated_marketing_cost_rs_qtl": np.round(simulated_marketing_cost, 1),
            "new_marketing_efficiency_acharya": np.round(simulated_me_acharya, 2),
            "capex_investment_cr": np.round(capex_cr, 1),
            "payback_period_years": payback_years,
            "spoilage_emissions_avoided_tco2e": np.round(emissions_avoided_tco2e, 1)
        }
    }
