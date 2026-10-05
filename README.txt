APMC VASHI FIELD PROJECT DATASET
Project Topic:
Agricultural Supply Chain and Distribution Network Analytics

Field-project framing:
The analysis is centred on mapping the agricultural supply chain from producers/source locations
through collection and transportation to APMC Vashi, Navi Mumbai, and analysing bottlenecks,
losses, prices and distribution efficiency for Onion, Potato and Tomato.

Dataset structure:
1. Farmers - producer/source-side variables.
2. Market_Prices - Maharashtra mandi price and arrival records from the supplied source dataset.
3. Transportation - route, distance, cost, delay and damage variables.
4. Distribution - collection centre, distributor, delivery and loss variables.
5. Supply_Chain_Map - simplified farmer/source -> collection centre -> APMC Vashi -> distributor mapping.
6. Onion_Economics - supplementary onion economics data.
7. Data_Dictionary - dashboard parameter definitions.

Important provenance note:
The market-price table uses the supplied mandi data. The farmer, transportation, distribution and
mapping tables contain constructed/estimated values for modelling and dashboard development.
They should not be presented as independently verified measurements from the APMC visit.

Recommended dashboard:
- KPI cards: total quantity, average modal price, total transport cost, estimated loss %
- Supply-chain flow: Source -> Collection Centre -> APMC Vashi -> Distributor
- Commodity comparison: Onion vs Potato vs Tomato
- Price analysis: modal/min/max price and arrival quantity
- Bottleneck analysis: delay, transport cost, damage/loss
- Recommendations: high-loss routes, high-cost routes, price opportunities
