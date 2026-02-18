---
title: Data Description
nav_order: 4
---

This framework contains information about the following sectors in Europe:
* Variable Renewable Energy
* Hydro, reservoirs and run-of-river
* Biomass
* Energy conversion and storage
* Electricity transmission (cross-border)
* Methane and hydrogen
* Cargo transport, biomass, hydrocarbon liquids and methanol
* Industry, chemicals, glass, fertilisers, refineries, cement and steel
* Buildings, non-residential and residential, heating and cooling
* Transport, road, rail, aviation and shipping
* Residual electricity demand

# Spatial Scope
This dataset includes data of EU27 plus UK, CH and NO.

# Resolution
* __PECD1__: We use this resolution as country level.
* __PECD2__: Spatial distribution carries out in ENTSO-E studies, see explanation [here](https://corres.windenergy.dtu.dk/open-data).
* __NUTS2__: Basic regions, see details [here](https://ec.europa.eu/eurostat/web/nuts/) (v2021).
* __NUTS3__: Small regions, see details [here](https://ec.europa.eu/eurostat/web/nuts/) (v2021).

# VRE
This pipeline counts with a set of different technologies:

* Onshore wind - specific power (W/m2) could be 199, 270 or 335 and hub height (m) could be 100, 150 or 200. 
* Offshore wind, fixed bottom or floating - specific power (W/m2) could be 316 or 370 and hub height (m) could be 155. 
* Solar PV: rooftop, no tracking axis and one tracking axis.

## Parameters
* Capacity factors: weather years 1980-2021
* Existing capacity and expected decommissions
* Installable capacity per technology type and region: solar, onshore wind and offshore wind.
* Investment cost, fixed cost and operational cost for 2030, 2040 and 2050 (EUR 2025)

## Resolution
* __Data resolution__: PECD2
* To transform data to PECD1, existing and installable capacity are added and capacity factors are weighted average based on capacity for existing techs and installable capacity for future techs.
* For NUTS2 and NUTS3, existing and installable capacity are transformed using the area as a conversion factor the area and the average capacity factors of the polygons intersecting the target polygon.

# Hydro
Reservoir-based turbines and run-of-river technologies are included. Pumped hydro is not yet part of this dataset.

Run-of-river generation is modeled as fixed production without curtailment.

Reservoirs are modeled as storage where the hydro turbine production is the discharge and the inflows are the charge.

## Parameters
* Inflow
* Run-of-river generation
* Maximum and minimum hydro turbine production
* Reservoir and turbine existing capacities
* Ramp constraints for the turbines
* Efficiency of hydro turbines (piecewise linear function).
* Operational and fixed costs for 2030, 2040 and 2050 (EUR 2025)

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, existing capacity is transformed using the area as a conversion factor and, for time series, using the average of the polygons intersecting the target polygon.

# Biomass
For this pipeline, this dataset includes the annual production of biomass per region, where there are three potential scenarios, low, medium and high.

The biomass is modeled as a dummy storage that starts with the amount of energy that is produced during the year. This storage can only discharge.

## Parameters
* Annual production
* Production cost

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, annual production is transformed using the area as a conversion factor and, for the operational cost, using the average of the polygons intersecting the target polygon.
* Raw data can be imported in NUTS3 but an updated version from 2013.

# Energy Conversion and Storage
This pipelines models the power sector existing assets, mainly thermal generation and storage.

## Thermal generation & Other
* Super Pulvurized Coal Power Plant
* Nuclear Power Plant
* Combined-cycle Power Plant
* Open-cycle Power Plant
* Biomass steam turbine
* Waste steam turbine
* Hydrogen-based gas turbine

## Storage
* Lithium Battery Storage, utility scale
* Iron Air Storage

## Parameters
* Existing capacity and expected decommissions
* Investment, fixed and operational costs for 2030, 2040 and 2050 (EUR 2025)
* Efficiency
* Carbon capture rate

## Resolution
* __Data resolution__: PECD1, PECD2, NUTS2, NUTS3
* The raw data can be imported using all mopo resolutions. The user just need to configure the corresponding importer.

# Electricity Transmission
This dataset accounts for the cross-border power capacity in Europe modeling it as net transfer capacity.

## Parameters
* Exiting capacity
* Installable capacity
* Investment cost for 2030, 2040, 2050 (EUR 2025)

## Resolution
* __Data resolution__: PECD1
* Working on having more resolutions available.

# Methane and Hydrogen
In this pipeline, methane and hydrogen networks (investments available) are modeled as well as technologies to produce syn- and bio-gases. The networks are modeled for cross-border resolution and as net transfer capacities. Additionally, it includes data for gas underground (CH4) and salt-cavern (H2) storages.

## Methane
* LNG terminals
* Gas extractions
* Imports to EU
* Methanation
* Biomass digestion and upgrading
* Biomass digestion and methanation
* Biomass gasification and methanation

## Hydrogen
* Steam methane reforming
* Steam methane reforming with carbon capture
* Electrolysis, PEAM, AEC and SOEC
* Gas pyrolysis

## Parameters
* Investment, fixed and operational costs for 2030, 2040 and 2050 (EUR 2025)
* Efficiency
* Carbon capture rate
* Existing capacity
* Tariff
* Installable capacity

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, the area is used as a conversion factor. For operational cost, we use the average of the polygons intersecting the target polygon.

# Cargo Transport
Cargo transport has been developed through a set of assumptions. The network for each country is created considering an existing connection of neighboring countries. The distance between countries is calculated through the centroids of each polygon and if the centroids are connected through a maritime route, then that route is realized using ships.

The energy carriers transfered in this network are biomass, methanol and hydrocarbon liquids (diesel, gasoline, kerosene, etc).

There is a fixed price per energy carrier, route type and distance.

## Resolution
* __Data resolution__: PECD1
* Working on having more resolutions available.

# Buildings 
Heating and cooling are modeled endogenously as end-use demand. This dataset includes the final demands and the technologies that provide the demand.

## Demands
* Non-residential space heating
* Residential space heating
* Non-residential domestic hot water
* Residential domestic hot water
* Non-residential cooling 
* Residential cooling

## Technologies
* Air heatpumps
* Ground heatpumps
* Biomass boilers
* Oil boilers
* Gas boilers
* Coal boilers
* Electric heaters

The dataset accounts for district heating technologies but no demand has been implemented for this end use.

For the sake of tractibility, the heat pumps have been simplified to supply a global heat demand that distributes the production among the different types. Therefore, the COP has been weighted to consider the expected domestic hot water and space heating demand. For instance, on average in x country, the domestic hot water demand is 20% and space heating is 80%, then we weighted the average COP that goes to space and water use.

## Parameters

* Demand profiles (1995, 2008, 2009, 2012, 2015)
* Demand annual scale
* COP (1995, 2008, 2009, 2012, 2015), air-to-air, air-to-water and ground-to-water
* Invesment, fixed and operational cost for 2030, 2040 and 2050 (EUR 2025)
* Efficiency
* Existing capacity and expected decommissions

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, existing capacity is transformed using the population as a conversion factor. For time series, as they are normalized and at country level, they are replicated in subsequent target polygons.


# Industry
This dataset includes different sectors: steel, cement, glass, fertilisers, chemicals.

There are in total around 80 investable routes. Each route is modeled in a multi-input multi-output framework.

## Parameters
* Demand (constant, flat profile), scenarios: current trend and high expectation
* Investment, fixed and operational cost for 2030, 2040 and 2050 (EUR 2025)
* Conversion rates
* Carbon capture rate
* Emission rates
* Existing capacity

# Transport
Transport demand covers road, train, aviation and shipping.

## Road transport
* Car
* Van
* Bus
* Truck

## Non-road transport
* Electric trains
* Combustion trains
* Planes
* Ships

## Parameters
For electric road transport, the profiles are hourly and flexibility is allowed through scenarios, 10% or 20% of the vehicles have G2V and V2G services, considering this fleet as virtual storage connected to the grid. The remaining vehicles have weekly profiles

* Demand profiles (no weather dependent data, the same profiles is adjusted and repeated per weather year).
* Demand annual scale, scenarios DE and GA TYNDP 2024.

## Flexibility parameters
* Vehicles connected to the grid
* Available capacity connected to the grid
* Energy leaving the grid (vehicle disconnection)
* Discharging and charging power available
* Discharging and charging efficiency based on connected chargers

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, existing fleet capacity and annual demand are transformed using the population as a conversion factor. For time series, as they are normalized and at country level, they are replicated in subsequent target polygons.

# Residual Electricity Demand

## Parameters
* Demand profiles: weather years 1982-2021

## Resolution
* __Data resolution__: PECD1
* For PEC2, NUTS2 and NUTS3, the demand time series are transformed using the population as a conversion factor. 
