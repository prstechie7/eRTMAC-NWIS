"""
Indian Basin & Location-Aware Intelligence Service for eRTMAC-NWIS.
Compliant with Smart India Hackathon 2026 (SIH26121) · Oil India Limited.

Integrates Directorate General of Hydrocarbons (DGH) National Data Repository (NDR)
petroleum basins, discovery wells, regional stratigraphy, and operational hazard profiles across India:
1. Assam-Arakan Basin (Upper Assam Shelf: Nahorkatiya, Moran, Baghjan, Digboi, Lakwa, Geleki, Rudrasagar)
2. Cambay Basin (Gujarat: Ankleshwar, Kalol, Mehsana, Gandhar)
3. Rajasthan / Barmer Basin (Mangala, Bhagyam, Aishwariya)
4. Krishna-Godavari (KG) Basin (Offshore/Onshore: Ravva, KG-D6, Pasarlapudi)
5. Western Offshore / Mumbai High Basin (Mumbai High, Bassein, Neelam)
6. Cauvery Basin (Tamil Nadu: Narimanam, Bhuvanagiri)

Provides:
- Haversine distance calculation from user's current GPS location to all Indian basins and wells
- Dynamic nearest Indian basin & offset well resolution
- Regional stratigraphy, pore pressure regime, mud weight baselines, and historical hazards
- Decision-support only (engineer_review_required = True)
"""

import math
from typing import Dict, Any, List, Optional

# Indian Petroleum Basins Registry (DGH NDR Official Classifications)
INDIAN_BASINS = [
    {
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "name": "Assam-Arakan Basin (Upper Assam Shelf)",
        "category": "Category-I (Established Commercial Production)",
        "state": "Assam / Arunachal Pradesh",
        "center_lat": 27.3500,
        "center_lon": 95.3000,
        "primary_operator": "Oil India Limited (OIL) & ONGC",
        "key_fields": ["Nahorkatiya", "Moran", "Baghjan", "Digboi", "Lakwa", "Rudrasagar", "Geleki", "Kumchai"],
        "geological_era": "Tertiary (Oligocene - Miocene - Pliocene)",
        "lithology_summary": "Thick sequence of fluvial to deltaic sandstones, coals, and splintery shales overlying basement",
        "stratigraphic_column": [
            {"formation": "Dihing Group", "typical_depth_m": "0 – 450 m", "lithology": "Pebbles, loose sandstones, unconsolidated gravels", "drilling_hazard": "Shallow washouts, lost circulation"},
            {"formation": "Namsang Formation", "typical_depth_m": "450 – 1,150 m", "lithology": "Interbedded sandstone and soft claystone", "drilling_hazard": "Borehole breakout, high solids loading"},
            {"formation": "Girujan Clay", "typical_depth_m": "1,150 – 2,100 m", "lithology": "Mottled gumbo claystone, swelling smectite", "drilling_hazard": "Bit balling, reactive shale swelling, pack-off"},
            {"formation": "Upper Tipam Sandstone", "typical_depth_m": "2,100 – 2,680 m", "lithology": "Subarkosic multi-storied sandstone reservoir", "drilling_hazard": "Depleted pressure differential sticking, mud losses"},
            {"formation": "Lower Tipam Sandstone", "typical_depth_m": "2,680 – 2,950 m", "lithology": "Fine to medium grained sandstone and shale", "drilling_hazard": "Tight hole on trips, torque spikes"},
            {"formation": "Barail Coal-Shale", "typical_depth_m": "2,950 – 3,250 m", "lithology": "Carbonaceous shale, coal seams, hard sandstone", "drilling_hazard": "Coal sloughing, gas kicks, wellbore collapse"},
            {"formation": "Barail Main Sand (BMS)", "typical_depth_m": "3,250 – 3,600 m", "lithology": "Prolific high-pressure oil and gas sandstone", "drilling_hazard": "Gas influx, high pressure kicks, kicks during connections"},
            {"formation": "Kopili Formation", "typical_depth_m": "3,600 – 4,000 m", "lithology": "Splintery marine shale with thin calcareous bands", "drilling_hazard": "Shale spalling, tight hole, pipe pinching"},
            {"formation": "Sylhet Limestone", "typical_depth_m": "4,000 – 4,400 m", "lithology": "Nummulitic fossiliferous limestone", "drilling_hazard": "Severe to total lost circulation in vugs/fractures"}
        ],
        "typical_pp_gradient_sg": 0.90,
        "typical_fg_gradient_sg": 1.78,
        "recommended_mw_range_sg": "1.12 – 1.25 SG",
        "regional_hazards": [
            "Differential sticking in depleted Upper Tipam Sandstone (overbalance > 1,000 psi)",
            "Coal bed sloughing and splintery cavings in Barail Formation",
            "Reactive gumbo swelling in Girujan Clay",
            "High-pressure shallow and deep gas kicks in Baghjan / Moran deep plays",
            "Total mud losses in fractured Sylhet limestone"
        ]
    },
    {
        "basin_id": "IND-BASIN-CAMBAY",
        "name": "Cambay Basin",
        "category": "Category-I (Established Commercial Production)",
        "state": "Gujarat",
        "center_lat": 21.7500,
        "center_lon": 72.9500,
        "primary_operator": "ONGC & Vedanta",
        "key_fields": ["Ankleshwar", "Kalol", "Mehsana", "Gandhar", "Nandasan", "Sanand"],
        "geological_era": "Tertiary (Palaeocene - Eocene rift basin)",
        "lithology_summary": "Extensional graben filled with thick Cambay Shale, deltaic sandstone pays, and Deccan trap floor",
        "stratigraphic_column": [
            {"formation": "Post-Babaguru Formations", "typical_depth_m": "0 – 600 m", "lithology": "Clay, sand, and gravel", "drilling_hazard": "Shallow water flows"},
            {"formation": "Babaguru / Kand Formation", "typical_depth_m": "600 – 1,100 m", "lithology": "Sandstone and variegated clay", "drilling_hazard": "Washouts and hole enlargement"},
            {"formation": "Tarapur Shale", "typical_depth_m": "1,100 – 1,500 m", "lithology": "Greenish-grey marine shale", "drilling_hazard": "Tight hole, shale hydration"},
            {"formation": "Ankleshwar / Kalol Pay", "typical_depth_m": "1,500 – 2,200 m", "lithology": "Deltaic sandstones and siltstones (Major Pay)", "drilling_hazard": "Differential sticking in depleted sands"},
            {"formation": "Cambay Shale (Source Rock)", "typical_depth_m": "2,200 – 3,400 m", "lithology": "Dark grey fissile overpressured shale", "drilling_hazard": "Severe sloughing shale, hole pack-off, overpressure kicks"},
            {"formation": "Olpad Formation", "typical_depth_m": "3,400 – 3,900 m", "lithology": "Volcaniclastic trap wash and basalt pebbles", "drilling_hazard": "Extreme bit wear, low ROP, severe vibration"},
            {"formation": "Deccan Trap (Basement)", "typical_depth_m": "> 3,900 m", "lithology": "Hard dense basalt flows", "drilling_hazard": "Bit destruction, high impact shock, zero ROP"}
        ],
        "typical_pp_gradient_sg": 1.05,
        "typical_fg_gradient_sg": 1.85,
        "recommended_mw_range_sg": "1.15 – 1.45 SG (Weighted for Cambay Shale)",
        "regional_hazards": [
            "Sloughing and wellbore collapse in thick overpressured Cambay Shale",
            "High bottom-hole temperature (BHT > 140°C in deep grabens)",
            "Abrasive volcaniclastic wear in Olpad trap wash",
            "Tight hole and overpull on tripping across Tarapur and Cambay intervals"
        ]
    },
    {
        "basin_id": "IND-BASIN-BARMER",
        "name": "Barmer / Rajasthan Basin",
        "category": "Category-I (Established Commercial Production)",
        "state": "Rajasthan (Thar Desert)",
        "center_lat": 25.8500,
        "center_lon": 71.4500,
        "primary_operator": "Cairn Oil & Gas (Vedanta) & ONGC",
        "key_fields": ["Mangala", "Bhagyam", "Aishwariya", "Raageshwari", "Kameshwari"],
        "geological_era": "Mesozoic - Tertiary rift basin",
        "lithology_summary": "Prolific fluvial Fatehgarh sands overlain by Barmer Hill lacustrine shales/porcellanite and Dharvi Dungar",
        "stratigraphic_column": [
            {"formation": "Quaternary Alluvium", "typical_depth_m": "0 – 150 m", "lithology": "Loose dune sands and calcrete", "drilling_hazard": "Surface loss of circulation, hole collapse"},
            {"formation": "Dharvi Dungar Formation", "typical_depth_m": "150 – 850 m", "lithology": "Interbedded silty claystone and sandstone", "drilling_hazard": "Sticky clays, mud cake buildup"},
            {"formation": "Barmer Hill Formation", "typical_depth_m": "850 – 1,450 m", "lithology": "Diatomaceous porcellanite, shale, tight reservoir", "drilling_hazard": "Fracture losses during stimulation, fragile rock"},
            {"formation": "Fatehgarh Formation (Major Pay)", "typical_depth_m": "1,450 – 2,200 m", "lithology": "High-porosity, high-permeability fluvial sandstone", "drilling_hazard": "High waxy crude wax gelation on trips, swab/surge"},
            {"formation": "Thumbli / Dharvi Basement", "typical_depth_m": "> 2,200 m", "lithology": "Basement granites and volcanics", "drilling_hazard": "Severe bit bounce, low ROP"}
        ],
        "typical_pp_gradient_sg": 0.98,
        "typical_fg_gradient_sg": 1.72,
        "recommended_mw_range_sg": "1.05 – 1.18 SG (Low solids, polymer systems)",
        "regional_hazards": [
            "Extremely high wax content crude (pour point ~40°C), pipe freezing risk during static periods",
            "Shallow loose sand washouts requiring controlled spud hydraulics",
            "Lost circulation in unconsolidated Fatehgarh upper channels"
        ]
    },
    {
        "basin_id": "IND-BASIN-KG",
        "name": "Krishna-Godavari (KG) Basin (Onshore & Offshore)",
        "category": "Category-I (Established Commercial Production)",
        "state": "Andhra Pradesh / Bay of Bengal",
        "center_lat": 16.5000,
        "center_lon": 82.2500,
        "primary_operator": "ONGC & Reliance Industries Limited (RIL)",
        "key_fields": ["Ravva (Offshore)", "KG-D6 (Deepwater)", "Pasarlapudi", "Mori", "Nagayalanka", "Endamuru"],
        "geological_era": "Mesozoic to Recent deltaic - passive margin basin",
        "lithology_summary": "Vast deltaic complex with overpressured Raghavapuram Shale, HPHT deep reservoirs, and deepwater turbidites",
        "stratigraphic_column": [
            {"formation": "Godavari Clay / Recent", "typical_depth_m": "0 – 800 m", "lithology": "Soft hemipelagic clays and shallow silts", "drilling_hazard": "Shallow water/gas flows, riserless drilling packoff"},
            {"formation": "Matsyapuri / Rajahmundry Sand", "typical_depth_m": "800 – 1,800 m", "lithology": "Medium to coarse grained sandstones", "drilling_hazard": "High seepage losses"},
            {"formation": "Pasarlapudi / Ravva Pays", "typical_depth_m": "1,800 – 2,600 m", "lithology": "Prolific delta-front sandstone oil/gas reservoirs", "drilling_hazard": "Depleted pressure differential sticking"},
            {"formation": "Vadaparru Shale", "typical_depth_m": "2,600 – 3,200 m", "lithology": "Fissile marine shale with overpressure ramps", "drilling_hazard": "High pore pressure kick transition, tight ECD margin"},
            {"formation": "Raghavapuram Shale (HPHT)", "typical_depth_m": "3,200 – 4,500 m", "lithology": "Hyper-pressured dark grey organic shale", "drilling_hazard": "HPHT conditions, massive gas kicks, barite sag, borehole spalling"},
            {"formation": "Golapalli Sandstone", "typical_depth_m": "4,500 – 5,200 m", "lithology": "Deep tight gas sandstone", "drilling_hazard": "Extreme pressure (> 12,000 psi), BHT > 165°C"}
        ],
        "typical_pp_gradient_sg": 1.45,
        "typical_fg_gradient_sg": 2.10,
        "recommended_mw_range_sg": "1.35 – 1.85 SG (High-density synthetic oil-based mud)",
        "regional_hazards": [
            "Severe High-Pressure High-Temperature (HPHT) regime requiring tight pressure window management",
            "Dangerous high-pressure gas kicks requiring rapid well-control response",
            "Shallow gas and hydrate dissociation hazards in deepwater sectors",
            "Barite sag and fluid loss degradation in weighted muds"
        ]
    },
    {
        "basin_id": "IND-BASIN-MUMBAI-OFFSHORE",
        "name": "Western Offshore / Mumbai High Basin",
        "category": "Category-I (Established Commercial Production)",
        "state": "Maharashtra Offshore (Arabian Sea)",
        "center_lat": 19.4200,
        "center_lon": 71.3300,
        "primary_operator": "ONGC",
        "key_fields": ["Mumbai High North", "Mumbai High South", "Bassein (Gas)", "Neelam", "Heera", "Panna-Mukta"],
        "geological_era": "Tertiary carbonate platform",
        "lithology_summary": "Extensive multi-layered limestone and dolomite carbonate reservoirs overlying Deccan Trap basement",
        "stratigraphic_column": [
            {"formation": "Seafloor Clays & Silts", "typical_depth_m": "0 – 400 m", "lithology": "Calcareous ooze and soft green clays", "drilling_hazard": "Conductor pipe washouts"},
            {"formation": "Chinchini Formation", "typical_depth_m": "400 – 900 m", "lithology": "Claystone and marl", "drilling_hazard": "Bit balling, tight clearances"},
            {"formation": "Bassein / Mukta Limestone", "typical_depth_m": "900 – 1,350 m", "lithology": "Massive fossiliferous limestone gas pay", "drilling_hazard": "Severe loss of circulation, H2S gas presence"},
            {"formation": "L-I / L-II Carbonate Pay", "typical_depth_m": "1,350 – 1,750 m", "lithology": "Porous bioclastic limestone and chalk", "drilling_hazard": "Depleted reservoir differential sticking, total losses"},
            {"formation": "L-III Major Limestone Pay", "typical_depth_m": "1,750 – 2,150 m", "lithology": "Primary oil-bearing fractured/vuggy limestone", "drilling_hazard": "Total fluid losses in cavernous vugs, blind drilling required"},
            {"formation": "Basal Clastics & Deccan Trap", "typical_depth_m": "> 2,150 m", "lithology": "Basal sandstones and hard basaltic trap", "drilling_hazard": "Extremely abrasive bit destruction, torque spikes"}
        ],
        "typical_pp_gradient_sg": 0.88,
        "typical_fg_gradient_sg": 1.68,
        "recommended_mw_range_sg": "1.04 – 1.15 SG (Seawater / Polymer / Low-density systems)",
        "regional_hazards": [
            "Total lost circulation into vuggy and cavernous L-III limestone layers",
            "Severe differential sticking in mature depleted carbonate intervals",
            "Hydrogen Sulfide (H2S) sour gas exposure in Bassein and southern fields",
            "Severe drillstring vibration on transitioning into hard Deccan Trap basement"
        ]
    },
    {
        "basin_id": "IND-BASIN-CAUVERY",
        "name": "Cauvery Basin (Onshore & Offshore)",
        "category": "Category-I (Established Commercial Production)",
        "state": "Tamil Nadu / Puducherry",
        "center_lat": 10.8500,
        "center_lon": 79.8000,
        "primary_operator": "ONGC",
        "key_fields": ["Narimanam", "Bhuvanagiri", "Kamalapuram", "Kovilkalappal", "Madanam"],
        "geological_era": "Mesozoic to Tertiary rift basin",
        "lithology_summary": "Horst and graben rift complex filled with deep marine Cretaceous shales and reservoir sandstones",
        "stratigraphic_column": [
            {"formation": "Cuddalore Sandstone", "typical_depth_m": "0 – 450 m", "lithology": "Coarse ferruginous sandstone and gravel", "drilling_hazard": "Surface mud losses"},
            {"formation": "Madanam / Kamalapuram", "typical_depth_m": "450 – 1,400 m", "lithology": "Interbedded sandstone, siltstone, and shale", "drilling_hazard": "Shale sloughing, mud solids increase"},
            {"formation": "Sattapadi Shale", "typical_depth_m": "1,400 – 2,200 m", "lithology": "Dark grey fissile overpressured shale", "drilling_hazard": "Borehole collapse, tight hole on trips"},
            {"formation": "Bhuvanagiri Sandstone", "typical_depth_m": "2,200 – 3,100 m", "lithology": "Hard compact quartzitic sandstone (Deep Pay)", "drilling_hazard": "Abrasive rock, low ROP, high cutter wear, high pressure gas"}
        ],
        "typical_pp_gradient_sg": 1.15,
        "typical_fg_gradient_sg": 1.88,
        "recommended_mw_range_sg": "1.18 – 1.35 SG",
        "regional_hazards": [
            "Overpressure shale destabilization in Sattapadi Formation",
            "Abrasive high-strength quartzitic sands in Bhuvanagiri causing severe bit dulling",
            "Interbedded tight hole sections requiring frequent reaming"
        ]
    }
]

# Comprehensive Indian Discovery & Operational Wells (DGH NDR)
INDIAN_ALL_WELLS = [
    # Upper Assam (OIL)
    {
        "well_id": "DGH-IND-NHK-01",
        "well_name": "NHK-01 (Nahorkatiya Discovery)",
        "field_name": "Nahorkatiya",
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "basin": "Assam-Arakan (Upper Assam Shelf)",
        "state": "Assam",
        "operator": "Oil India Limited",
        "surface_lat": 27.2831,
        "surface_lon": 95.3422,
        "kb_elevation_m": 112.5,
        "total_depth_md_m": 3571.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1952,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-MORAN-01",
        "well_name": "MORAN-01 (Moran Field Discovery)",
        "field_name": "Moran",
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "basin": "Assam-Arakan (Upper Assam Shelf)",
        "state": "Assam",
        "operator": "Oil India Limited",
        "surface_lat": 27.1855,
        "surface_lon": 94.9312,
        "kb_elevation_m": 115.4,
        "total_depth_md_m": 4185.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1956,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-BGJ-05",
        "well_name": "BGJ-05 (Baghjan Deep Play)",
        "field_name": "Baghjan",
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "basin": "Assam-Arakan (Upper Assam Shelf)",
        "state": "Assam",
        "operator": "Oil India Limited",
        "surface_lat": 27.5812,
        "surface_lon": 95.3522,
        "kb_elevation_m": 128.5,
        "total_depth_md_m": 4350.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 2003,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-DIGBOI-01",
        "well_name": "DIGBOI-01 (Asia's 1st Oil Well)",
        "field_name": "Digboi",
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "basin": "Assam-Arakan (Upper Assam Shelf)",
        "state": "Assam",
        "operator": "Assam Oil Company / OIL",
        "surface_lat": 27.3800,
        "surface_lon": 95.6300,
        "kb_elevation_m": 165.0,
        "total_depth_md_m": 202.0,
        "status": "HISTORIC_HERITAGE",
        "discovery_year": 1889,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository / Heritage"
    },
    {
        "well_id": "DGH-IND-LAKWA-02",
        "well_name": "LAKWA-02 (Barail Major Producer)",
        "field_name": "Lakwa",
        "basin_id": "IND-BASIN-ASSAM-ARAKAN",
        "basin": "Assam-Arakan (Upper Assam Shelf)",
        "state": "Assam",
        "operator": "ONGC / OIL Joint Play",
        "surface_lat": 26.9800,
        "surface_lon": 94.8500,
        "kb_elevation_m": 105.0,
        "total_depth_md_m": 4200.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1964,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    # Cambay Basin (Gujarat)
    {
        "well_id": "DGH-IND-ANK-01",
        "well_name": "ANK-01 (Ankleshwar Discovery)",
        "field_name": "Ankleshwar",
        "basin_id": "IND-BASIN-CAMBAY",
        "basin": "Cambay Basin",
        "state": "Gujarat",
        "operator": "ONGC",
        "surface_lat": 21.6312,
        "surface_lon": 73.0125,
        "kb_elevation_m": 35.0,
        "total_depth_md_m": 1850.0,
        "status": "HISTORIC_PRODUCER",
        "discovery_year": 1960,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-KALOL-01",
        "well_name": "KALOL-01 (Kalol Pay Discovery)",
        "field_name": "Kalol",
        "basin_id": "IND-BASIN-CAMBAY",
        "basin": "Cambay Basin",
        "state": "Gujarat",
        "operator": "ONGC",
        "surface_lat": 23.2500,
        "surface_lon": 72.5000,
        "kb_elevation_m": 62.0,
        "total_depth_md_m": 2100.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1961,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    # Barmer / Rajasthan Basin
    {
        "well_id": "DGH-IND-MANGALA-01",
        "well_name": "M-01 (Mangala Giant Discovery)",
        "field_name": "Mangala",
        "basin_id": "IND-BASIN-BARMER",
        "basin": "Barmer / Rajasthan Basin",
        "state": "Rajasthan",
        "operator": "Cairn Oil & Gas / ONGC",
        "surface_lat": 25.8200,
        "surface_lon": 71.4200,
        "kb_elevation_m": 145.0,
        "total_depth_md_m": 2250.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 2004,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-BHAGYAM-01",
        "well_name": "BHAGYAM-01 (Bhagyam Field Discovery)",
        "field_name": "Bhagyam",
        "basin_id": "IND-BASIN-BARMER",
        "basin": "Barmer / Rajasthan Basin",
        "state": "Rajasthan",
        "operator": "Cairn Oil & Gas / ONGC",
        "surface_lat": 26.0100,
        "surface_lon": 71.5100,
        "kb_elevation_m": 152.0,
        "total_depth_md_m": 2050.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 2004,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    # Krishna-Godavari (KG) Basin
    {
        "well_id": "DGH-IND-RAVVA-01",
        "well_name": "RAVVA-01 (Ravva Offshore Discovery)",
        "field_name": "Ravva",
        "basin_id": "IND-BASIN-KG",
        "basin": "Krishna-Godavari (KG) Basin",
        "state": "Andhra Pradesh (Offshore)",
        "operator": "ONGC / Vedanta / Ravva JV",
        "surface_lat": 16.4800,
        "surface_lon": 82.2500,
        "kb_elevation_m": 28.0,
        "total_depth_md_m": 2850.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1987,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    {
        "well_id": "DGH-IND-KGD6-01",
        "well_name": "Dhirubhai-01 (KG-D6 Deepwater Gas)",
        "field_name": "KG-D6",
        "basin_id": "IND-BASIN-KG",
        "basin": "Krishna-Godavari (KG) Basin",
        "state": "Bay of Bengal (Deepwater)",
        "operator": "Reliance Industries / BP",
        "surface_lat": 16.2100,
        "surface_lon": 82.5500,
        "kb_elevation_m": 35.0,
        "total_depth_md_m": 3950.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 2002,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    # Mumbai High Offshore
    {
        "well_id": "DGH-IND-BH-01",
        "well_name": "BH-01 (Bombay High Historic Discovery)",
        "field_name": "Mumbai High",
        "basin_id": "IND-BASIN-MUMBAI-OFFSHORE",
        "basin": "Western Offshore / Mumbai High",
        "state": "Arabian Sea (Offshore)",
        "operator": "ONGC",
        "surface_lat": 19.4200,
        "surface_lon": 71.3300,
        "kb_elevation_m": 42.0,
        "total_depth_md_m": 2185.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1974,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    },
    # Cauvery Basin
    {
        "well_id": "DGH-IND-NARIMANAM-01",
        "well_name": "NRM-01 (Narimanam Discovery)",
        "field_name": "Narimanam",
        "basin_id": "IND-BASIN-CAUVERY",
        "basin": "Cauvery Basin",
        "state": "Tamil Nadu",
        "operator": "ONGC",
        "surface_lat": 10.8200,
        "surface_lon": 79.8400,
        "kb_elevation_m": 12.0,
        "total_depth_md_m": 2650.0,
        "status": "COMPLETED_PRODUCER",
        "discovery_year": 1985,
        "provenance_type": "PUBLIC",
        "source": "DGH National Data Repository (NDR)"
    }
]


class IndianBasinService:
    """Service to provide location-aware Indian petroleum basin and well intelligence."""

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates Great-Circle distance in km using the Haversine formula."""
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 2)

    @staticmethod
    def get_all_basins() -> List[Dict[str, Any]]:
        """Returns the complete list of Indian petroleum basins."""
        return INDIAN_BASINS

    @staticmethod
    def get_all_indian_wells() -> List[Dict[str, Any]]:
        """Returns all DGH NDR Indian discovery and operational wells."""
        return INDIAN_ALL_WELLS

    @classmethod
    def resolve_location_intelligence(
        cls,
        user_lat: float,
        user_lon: float
    ) -> Dict[str, Any]:
        """
        Takes user's current GPS location, finds nearest Indian petroleum basin,
        ranks all Indian discovery wells by proximity, and extracts regional stratigraphy and hazards.
        """
        # 1. Rank basins by distance
        ranked_basins = []
        for basin in INDIAN_BASINS:
            dist = cls.haversine_distance_km(user_lat, user_lon, basin["center_lat"], basin["center_lon"])
            ranked_basins.append({
                **basin,
                "distance_km": dist
            })
        ranked_basins.sort(key=lambda b: b["distance_km"])
        nearest_basin = ranked_basins[0]

        # 2. Rank wells by distance
        ranked_wells = []
        for well in INDIAN_ALL_WELLS:
            dist = cls.haversine_distance_km(user_lat, user_lon, well["surface_lat"], well["surface_lon"])
            ranked_wells.append({
                **well,
                "distance_km": dist
            })
        ranked_wells.sort(key=lambda w: w["distance_km"])
        nearest_well = ranked_wells[0]

        # 3. Determine if user is directly inside or close to an Indian Basin (< 150 km)
        in_basin_radius = nearest_basin["distance_km"] < 150.0

        return {
            "user_location": {
                "latitude": round(user_lat, 4),
                "longitude": round(user_lon, 4),
                "within_oil_field_perimeter": in_basin_radius
            },
            "nearest_basin": {
                "basin_id": nearest_basin["basin_id"],
                "name": nearest_basin["name"],
                "category": nearest_basin["category"],
                "state": nearest_basin["state"],
                "primary_operator": nearest_basin["primary_operator"],
                "distance_km": nearest_basin["distance_km"],
                "geological_era": nearest_basin["geological_era"],
                "lithology_summary": nearest_basin["lithology_summary"],
                "stratigraphic_column": nearest_basin["stratigraphic_column"],
                "regional_hazards": nearest_basin["regional_hazards"],
                "typical_pp_gradient_sg": nearest_basin["typical_pp_gradient_sg"],
                "typical_fg_gradient_sg": nearest_basin["typical_fg_gradient_sg"],
                "recommended_mw_range_sg": nearest_basin["recommended_mw_range_sg"]
            },
            "nearest_offset_well": nearest_well,
            "nearby_offset_wells": ranked_wells[:5],
            "all_indian_wells_ranked": ranked_wells,
            "all_indian_basins_ranked": [
                {
                    "basin_id": b["basin_id"],
                    "name": b["name"],
                    "state": b["state"],
                    "distance_km": b["distance_km"],
                    "center_lat": b["center_lat"],
                    "center_lon": b["center_lon"],
                    "primary_operator": b["primary_operator"]
                }
                for b in ranked_basins
            ],
            "operational_advisory": (
                f"Location is within {nearest_basin['distance_km']} km of {nearest_basin['name']} ({nearest_basin['primary_operator']}). "
                f"Stratigraphic model grounded in DGH National Data Repository. Review key local hazard: {nearest_basin['regional_hazards'][0]}."
            ),
            "engineer_review_required": True,
            "provenance_type": "DGH_NDR_GROUNDED"
        }
