# APMC Vashi Agricultural Supply Chain Analytics

## Project Title
AGRICULTURAL SUPPLY CHAIN AND DISTRIBUTION NETWORK ANALYTICS

## Problem Statement
The agricultural supply chain from source locations to APMC Vashi involves multiple stages including farmer production, collection centres, transportation, market arrivals and distribution. The major challenges are price volatility, transport delays, supply losses, distribution inefficiencies and route-specific bottlenecks. This project analyses those patterns using real supply-chain data to identify operational issues and data-driven improvement opportunities.

## Objectives
- Analyse supply patterns from farmers to the market.
- Track daily, weekly and monthly arrival and price behaviour.
- Measure transportation delay, cost and damage.
- Evaluate distribution efficiency and product loss.
- Identify supply chain bottlenecks and generate evidence-based recommendations.
- Build a professional Streamlit dashboard for presentation and deployment.

## Field Visit Context
The analysis is centred on the APMC Vashi market in Navi Mumbai and the associated agricultural supply network for onion, potato and tomato. Data reflects source locations, collection centres, transport routes, market arrivals and distribution performance.

## Features
- Interactive KPI dashboard
- Date-range and commodity filters
- Daily, weekly and monthly aggregation
- Price and arrival analytics
- Sankey diagram for supply-chain flow
- Transportation bottleneck analysis
- Distribution efficiency review
- Farmer and source performance analysis
- Data quality validation
- Recommendation engine based on actual metrics
- CSV data export for filtered dashboard records

## Technology Stack
- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Openpyxl

## Dataset Description
The project uses the supplied CSV files and workbook in the workspace:
- farmers.csv
- market_prices.csv
- transportation.csv
- distribution.csv
- supply_chain_mapping.csv
- onion_economics_reference.csv
- data_dictionary.csv
- APMC_Vashi_Agricultural_Supply_Chain.xlsx

These datasets cover producers, commodity flows, distances, costs, arrival quantities, prices, losses and market distribution patterns.

## Dashboard Pages
1. Supply Chain Overview
2. Market Price & Arrival Analytics
3. APMC Vashi Supply Chain Map
4. Transportation & Bottleneck Analytics
5. Distribution Efficiency
6. Farmer & Source Analytics
7. Supply Chain Recommendations
8. Data Quality

## Key Calculations
- Loss % = Quantity Lost / Quantity Produced × 100
- Delay = Actual Time - Expected Time
- Damage % = Quantity Damaged / Quantity Transported × 100
- Transport Cost per Kg = Transport Cost / Quantity Transported
- Delivery Efficiency = Quantity Delivered / Quantity Received × 100
- Arrival Value = Arrival Quantity × Modal Price
- Estimated Revenue = Quantity Sold / 100 × Selling Price per Quintal
- Estimated Gross Return = Estimated Revenue - Production Cost
- Price Spread = Maximum Price - Minimum Price

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment Instructions
The project is prepared for Streamlit Community Cloud with `app.py` as the entry file and `requirements.txt` listing all runtime dependencies. See [DEPLOYMENT.md](DEPLOYMENT.md) for the full GitHub and deployment workflow.

## Team Contribution
This project is designed for a college CEP/field-project presentation and can be used by a student team for:
- data processing and analytics
- dashboard development
- chart creation and insight generation
- presentation preparation and report writing

## Open the deployed Streamlit URL to access the dashboard.
