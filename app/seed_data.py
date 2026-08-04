"""
Seed data based on real US tariff data for HTS Chapters 84-85.

Sources:
- HTS codes: USITC Harmonized Tariff Schedule (hts.usitc.gov)
- MFN rates: USITC HTS General rates of duty
- Section 301 tariffs: USTR Federal Register notices (Lists 1-4)
- Section 232 tariffs: Commerce Department steel/aluminum orders
- IEEPA reciprocal tariffs: Executive Orders 2025

Note: Rates shown are representative of real-world rates as of 2025-2026
but may not reflect the absolute latest changes. For production use,
always verify against the official Federal Register.
"""

from datetime import date


# =============================================================================
# HTS CODES — Chapter 84 (Nuclear reactors, boilers, machinery) & 85 (Electrical)
# =============================================================================

HTS_CODES = [
    # Chapter 84 - Nuclear reactors, boilers, machinery and mechanical appliances
    {"code": "84", "description": "Nuclear reactors, boilers, machinery and mechanical appliances; parts thereof", "parent_code": None},
    {"code": "8483", "description": "Transmission shafts and cranks; bearing housings; gears and gearing; ball or roller screws; gear boxes; flywheels; pulleys; clutches", "parent_code": "84"},
    {"code": "8483.10", "description": "Transmission shafts (including cam shafts and crank shafts) and cranks", "parent_code": "8483"},
    {"code": "8483.20", "description": "Bearing housings, incorporating ball or roller bearings", "parent_code": "8483"},
    {"code": "8483.30", "description": "Bearing housings, not incorporating ball or roller bearings; plain shaft bearings", "parent_code": "8483"},
    {"code": "8483.40", "description": "Gears and gearing; ball or roller screws; gear boxes and other speed changers, including torque converters", "parent_code": "8483"},
    {"code": "8483.50", "description": "Flywheels and pulleys, including pulley blocks", "parent_code": "8483"},
    {"code": "8483.60", "description": "Clutches and shaft couplings (including universal joints)", "parent_code": "8483"},
    {"code": "8483.90", "description": "Toothed wheels, chain sprockets and other transmission elements; parts", "parent_code": "8483"},

    {"code": "8481", "description": "Taps, cocks, valves and similar appliances for pipes, boiler shells, tanks, vats or the like", "parent_code": "84"},
    {"code": "8481.10", "description": "Pressure-reducing valves", "parent_code": "8481"},
    {"code": "8481.20", "description": "Valves for oleohydraulic or pneumatic transmissions", "parent_code": "8481"},
    {"code": "8481.80", "description": "Other appliances (taps, cocks, valves)", "parent_code": "8481"},

    {"code": "8482", "description": "Ball or roller bearings", "parent_code": "84"},
    {"code": "8482.10", "description": "Ball bearings", "parent_code": "8482"},
    {"code": "8482.20", "description": "Tapered roller bearings, including cone and tapered roller assemblies", "parent_code": "8482"},
    {"code": "8482.50", "description": "Other cylindrical roller bearings", "parent_code": "8482"},
    {"code": "8482.80", "description": "Other roller bearings, including combined ball/roller bearings", "parent_code": "8482"},

    {"code": "8484", "description": "Gaskets and similar joints of metal sheeting; mechanical seals", "parent_code": "84"},
    {"code": "8484.10", "description": "Gaskets and similar joints of metal sheeting combined with other material", "parent_code": "8484"},
    {"code": "8484.20", "description": "Mechanical seals", "parent_code": "8484"},

    {"code": "8479", "description": "Machines and mechanical appliances having individual functions, not specified elsewhere", "parent_code": "84"},
    {"code": "8479.89", "description": "Other machines and mechanical appliances n.e.s.", "parent_code": "8479"},

    {"code": "8471", "description": "Automatic data-processing machines and units thereof", "parent_code": "84"},
    {"code": "8471.30", "description": "Portable automatic data-processing machines (laptops)", "parent_code": "8471"},
    {"code": "8471.41", "description": "Other data-processing machines comprising a CPU, input and output unit", "parent_code": "8471"},

    # Chapter 85 - Electrical machinery and equipment
    {"code": "85", "description": "Electrical machinery and equipment and parts thereof; sound recorders and reproducers", "parent_code": None},
    {"code": "8501", "description": "Electric motors and generators", "parent_code": "85"},
    {"code": "8501.10", "description": "Motors of an output not exceeding 37.5 W", "parent_code": "8501"},
    {"code": "8501.31", "description": "DC motors, output > 750W but <= 75kW", "parent_code": "8501"},
    {"code": "8501.40", "description": "AC motors, single-phase", "parent_code": "8501"},
    {"code": "8501.51", "description": "AC motors, multi-phase, output <= 750W", "parent_code": "8501"},
    {"code": "8501.52", "description": "AC motors, multi-phase, output 750W to 75kW", "parent_code": "8501"},

    {"code": "8504", "description": "Electrical transformers, static converters and inductors", "parent_code": "85"},
    {"code": "8504.10", "description": "Ballasts for discharge lamps or tubes", "parent_code": "8504"},
    {"code": "8504.40", "description": "Static converters (power supplies, inverters)", "parent_code": "8504"},

    {"code": "8507", "description": "Electric accumulators (batteries), including separators", "parent_code": "85"},
    {"code": "8507.60", "description": "Lithium-ion batteries", "parent_code": "8507"},

    {"code": "8517", "description": "Telephone sets, including smartphones; other apparatus for transmission of voice/data", "parent_code": "85"},
    {"code": "8517.12", "description": "Telephones for cellular networks (smartphones)", "parent_code": "8517"},
    {"code": "8517.62", "description": "Machines for reception, conversion and transmission of data (routers, switches)", "parent_code": "8517"},

    {"code": "8541", "description": "Semiconductor devices; light-emitting diodes; photovoltaic cells", "parent_code": "85"},
    {"code": "8541.40", "description": "Photosensitive semiconductor devices, including photovoltaic cells", "parent_code": "8541"},

    {"code": "8542", "description": "Electronic integrated circuits", "parent_code": "85"},
    {"code": "8542.31", "description": "Processors and controllers (chips)", "parent_code": "8542"},
    {"code": "8542.32", "description": "Memories (semiconductor)", "parent_code": "8542"},
    {"code": "8542.39", "description": "Other integrated circuits", "parent_code": "8542"},

    # Chapter 61 - Articles of apparel and clothing accessories, knitted or crocheted
    {"code": "61", "description": "Articles of apparel and clothing accessories, knitted or crocheted", "parent_code": None},
    {"code": "6109", "description": "T-shirts, singlets, tank tops and similar garments, knitted or crocheted", "parent_code": "61"},
    {"code": "6109.10", "description": "T-shirts of cotton", "parent_code": "6109"},
    {"code": "6110", "description": "Jerseys, pullovers, cardigans, waistcoats, knitted or crocheted", "parent_code": "61"},
    {"code": "6110.20", "description": "Jerseys/pullovers of cotton", "parent_code": "6110"},

    # Chapter 73 - Articles of iron or steel
    {"code": "73", "description": "Articles of iron or steel", "parent_code": None},
    {"code": "7304", "description": "Tubes, pipes and hollow profiles, seamless, of iron or steel", "parent_code": "73"},
    {"code": "7304.19", "description": "Line pipe of stainless steel", "parent_code": "7304"},
    {"code": "7306", "description": "Other tubes, pipes and hollow profiles, of iron or steel", "parent_code": "73"},
    {"code": "7306.30", "description": "Welded tubes/pipes of iron or non-alloy steel, circular cross-section", "parent_code": "7306"},
    {"code": "7318", "description": "Screws, bolts, nuts, coach screws, screw hooks, rivets of iron or steel", "parent_code": "73"},
    {"code": "7318.15", "description": "Other screws and bolts of iron or steel", "parent_code": "7318"},

    # Chapter 76 - Aluminum and articles thereof
    {"code": "76", "description": "Aluminum and articles thereof", "parent_code": None},
    {"code": "7601", "description": "Unwrought aluminum", "parent_code": "76"},
    {"code": "7601.10", "description": "Aluminum, not alloyed, unwrought", "parent_code": "7601"},
    {"code": "7604", "description": "Aluminum bars, rods and profiles", "parent_code": "76"},
    {"code": "7604.21", "description": "Hollow profiles of aluminum alloys", "parent_code": "7604"},
    {"code": "7606", "description": "Aluminum plates, sheets and strip, thickness > 0.2mm", "parent_code": "76"},
    {"code": "7606.12", "description": "Aluminum alloy plates/sheets, rectangular", "parent_code": "7606"},

    # Chapter 87 - Vehicles other than railway
    {"code": "87", "description": "Vehicles other than railway or tramway rolling stock, and parts and accessories thereof", "parent_code": None},
    {"code": "8703", "description": "Motor cars and other motor vehicles principally designed for the transport of persons", "parent_code": "87"},
    {"code": "8703.23", "description": "Vehicles with spark-ignition engine, cylinder capacity 1500-3000 cc", "parent_code": "8703"},
    {"code": "8703.80", "description": "Electric vehicles for transport of persons", "parent_code": "8703"},
    {"code": "8708", "description": "Parts and accessories of motor vehicles", "parent_code": "87"},
    {"code": "8708.30", "description": "Brakes and servo-brakes and parts thereof", "parent_code": "8708"},

    # Chapter 90 - Optical, photographic, measuring, medical instruments
    {"code": "90", "description": "Optical, photographic, measuring, checking, precision, medical or surgical instruments and apparatus", "parent_code": None},
    {"code": "9018", "description": "Instruments and appliances used in medical or surgical sciences", "parent_code": "90"},
    {"code": "9018.90", "description": "Other medical instruments and appliances", "parent_code": "9018"},
    {"code": "9031", "description": "Measuring or checking instruments, not specified elsewhere", "parent_code": "90"},
    {"code": "9031.80", "description": "Other measuring/checking instruments", "parent_code": "9031"},

    # Chapter 95 - Toys, games and sports requisites
    {"code": "95", "description": "Toys, games and sports requisites; parts and accessories thereof", "parent_code": None},
    {"code": "9503", "description": "Tricycles, scooters, pedal cars, dolls, other toys; puzzles", "parent_code": "95"},
    {"code": "9503.00", "description": "Toys (general)", "parent_code": "9503"},
    {"code": "9504", "description": "Video game consoles, articles for funfair/table games", "parent_code": "95"},
    {"code": "9504.50", "description": "Video game consoles and machines", "parent_code": "9504"},
]


# =============================================================================
# TARIFF RULES — Based on real US tariff structure for Chinese imports
# =============================================================================

TARIFF_RULES = [
    # --- MFN Base Rates (General duty rates from USITC HTS) ---
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8483",
        "origin_country": "CN",
        "rate": 0.025,  # 2.5% general rate for transmission shafts/gears
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8483 - Transmission shafts, gears, gear boxes",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8481",
        "origin_country": "CN",
        "rate": 0.02,  # 2% general rate for valves
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8481 - Taps, cocks, valves",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8482",
        "origin_country": "CN",
        "rate": 0.09,  # 9% for ball/roller bearings
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8482 - Ball or roller bearings",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8501",
        "origin_country": "CN",
        "rate": 0.03,  # 3% for electric motors
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8501 - Electric motors and generators",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8504",
        "origin_country": "CN",
        "rate": 0.015,  # 1.5% for transformers
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8504 - Electrical transformers, static converters",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8507",
        "origin_country": "CN",
        "rate": 0.034,  # 3.4% for batteries
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8507 - Electric accumulators/batteries",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8517",
        "origin_country": "CN",
        "rate": 0.0,  # 0% (free) for telecom equipment
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8517 - Telephone/telecom apparatus (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8542",
        "origin_country": "CN",
        "rate": 0.0,  # 0% for ICs (ITA agreement)
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8542 - Electronic integrated circuits (free under ITA)",
        "source_reference": "USITC HTS General Rate Column 1 / ITA Agreement",
    },

    # --- MFN Base Rates for OTHER COUNTRIES (same rates — MFN is non-discriminatory) ---
    # MFN applies equally to all WTO members (US grants same base rate regardless of origin)
    # Only additional tariffs (301, 232, IEEPA) are country-specific
    *[
        {
            "tariff_type": "MFN",
            "hts_code_pattern": pattern,
            "origin_country": country,
            "rate": rate,
            "effective_from": date(2000, 1, 1),
            "effective_to": None,
            "stacks_with": [],
            "mutually_exclusive_with": [],
            "description": f"MFN base rate for HTS {pattern} - {country} origin",
            "source_reference": "USITC HTS General Rate Column 1",
        }
        for country in ["VN", "MX", "DE", "CA", "JP", "KR", "TW", "IN"]
        for pattern, rate in [
            ("8483", 0.025),
            ("8481", 0.02),
            ("8482", 0.09),
            ("8501", 0.03),
            ("8504", 0.015),
            ("8507", 0.034),
            ("8517", 0.0),
            ("8542", 0.0),
            ("6109", 0.168),
            ("6110", 0.168),
            ("7304", 0.0),
            ("7306", 0.0),
            ("7318", 0.038),
            ("7601", 0.025),
            ("7604", 0.05),
            ("7606", 0.03),
            ("8703", 0.025),
            ("8708", 0.025),
            ("9018", 0.0),
            ("9031", 0.033),
            ("9503", 0.0),
            ("9504", 0.0),
        ]
    ],

    # --- Section 301 Tariffs (China-specific) ---
    # List 1: 25% on $34B of Chinese goods (effective July 6, 2018)
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8483",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 7, 6),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 1 - 25% tariff on Chinese machinery parts (gears, shafts)",
        "source_reference": "USTR FR Notice 83 FR 28710; 84 FR 20459",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8482",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 7, 6),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 1 - 25% tariff on Chinese bearings",
        "source_reference": "USTR FR Notice 83 FR 28710",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8501",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 7, 6),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 1 - 25% tariff on Chinese electric motors",
        "source_reference": "USTR FR Notice 83 FR 28710",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8481",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 8, 23),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 2 - 25% tariff on Chinese valves",
        "source_reference": "USTR FR Notice 83 FR 40823; 84 FR 20459",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8504",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 9, 24),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 3 - 25% tariff on Chinese transformers/converters",
        "source_reference": "USTR FR Notice 83 FR 47974; 84 FR 20459",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8507.60",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2024, 8, 1),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 - Increased to 25% on Chinese lithium-ion batteries (2024 review)",
        "source_reference": "USTR 89 FR 46028 (2024 Four-Year Review)",
    },

    # --- Section 232 (National Security - Steel/Aluminum focused) ---
    # Note: Section 232 primarily targets steel (Ch 72-73) and aluminum (Ch 76)
    # but some derivative products in Ch 84/85 may be affected
    {
        "tariff_type": "SECTION_232",
        "hts_code_pattern": "8482.10",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 3, 23),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 232 - 25% on steel derivative products (ball bearings with steel content)",
        "source_reference": "Proclamation 9705; 83 FR 11625",
    },

    # --- IEEPA / Reciprocal Tariff (2025) ---
    # Broad-based reciprocal tariff on all Chinese goods
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "84",
        "origin_country": "CN",
        "rate": 0.145,  # 145% cumulative (but modeled here as the IEEPA-specific addition)
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff on Chinese goods - Chapter 84 (replaces 301/232 if higher)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "85",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff on Chinese goods - Chapter 85 (replaces 301/232 if higher)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },

    # --- MFN Base Rates for NEW CHAPTERS (CN origin) ---
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "6109",
        "origin_country": "CN",
        "rate": 0.168,  # 16.8% for cotton T-shirts
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 6109 - T-shirts, cotton",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "6110",
        "origin_country": "CN",
        "rate": 0.168,  # 16.8% for knit garments
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 6110 - Jerseys/pullovers",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7304",
        "origin_country": "CN",
        "rate": 0.0,  # Free for seamless pipes
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7304 - Seamless steel pipes (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7306",
        "origin_country": "CN",
        "rate": 0.0,
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7306 - Welded steel tubes (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7318",
        "origin_country": "CN",
        "rate": 0.038,  # 3.8% for fasteners
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7318 - Screws, bolts, nuts",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7601",
        "origin_country": "CN",
        "rate": 0.025,  # 2.5% for unwrought aluminum
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7601 - Unwrought aluminum",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7604",
        "origin_country": "CN",
        "rate": 0.05,  # 5% for aluminum profiles
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7604 - Aluminum bars/profiles",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "7606",
        "origin_country": "CN",
        "rate": 0.03,  # 3% for aluminum sheets
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 7606 - Aluminum plates/sheets",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8703",
        "origin_country": "CN",
        "rate": 0.025,  # 2.5% for passenger vehicles
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8703 - Motor vehicles for passengers",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "8708",
        "origin_country": "CN",
        "rate": 0.025,  # 2.5% for auto parts
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 8708 - Motor vehicle parts",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "9018",
        "origin_country": "CN",
        "rate": 0.0,  # Free for medical instruments
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 9018 - Medical instruments (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "9031",
        "origin_country": "CN",
        "rate": 0.033,  # 3.3%
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 9031 - Measuring instruments",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "9503",
        "origin_country": "CN",
        "rate": 0.0,  # Free for toys
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 9503 - Toys (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },
    {
        "tariff_type": "MFN",
        "hts_code_pattern": "9504",
        "origin_country": "CN",
        "rate": 0.0,  # Free for game consoles
        "effective_from": date(2000, 1, 1),
        "effective_to": None,
        "stacks_with": [],
        "mutually_exclusive_with": [],
        "description": "MFN base rate for HTS 9504 - Video game consoles (free)",
        "source_reference": "USITC HTS General Rate Column 1",
    },

    # --- Section 232 for STEEL (Chapter 73) and ALUMINUM (Chapter 76) ---
    {
        "tariff_type": "SECTION_232",
        "hts_code_pattern": "73",
        "origin_country": "CN",
        "rate": 0.25,  # 25% on all steel articles
        "effective_from": date(2018, 3, 23),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 232 - 25% tariff on steel (Chapter 73) from China",
        "source_reference": "Proclamation 9705; 83 FR 11625",
    },
    {
        "tariff_type": "SECTION_232",
        "hts_code_pattern": "76",
        "origin_country": "CN",
        "rate": 0.10,  # 10% on aluminum
        "effective_from": date(2018, 3, 23),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 232 - 10% tariff on aluminum (Chapter 76) from China",
        "source_reference": "Proclamation 9704; 83 FR 11619",
    },

    # --- Section 301 for NEW CHAPTERS ---
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8703",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 7, 6),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 1 - 25% on Chinese vehicles",
        "source_reference": "USTR 83 FR 28710",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "8708",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2018, 8, 23),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 2 - 25% on Chinese auto parts",
        "source_reference": "USTR 83 FR 40823",
    },
    {
        "tariff_type": "SECTION_301",
        "hts_code_pattern": "9503",
        "origin_country": "CN",
        "rate": 0.25,
        "effective_from": date(2019, 9, 1),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["IEEPA"],
        "description": "Section 301 List 4A - 25% on Chinese toys",
        "source_reference": "USTR 84 FR 43304",
    },

    # --- Anti-Dumping / Countervailing Duties (AD/CVD) ---
    # These are product+country specific, on top of everything else
    {
        "tariff_type": "AD_CVD",
        "hts_code_pattern": "7304.19",
        "origin_country": "CN",
        "rate": 1.3692,  # 136.92% combined AD+CVD for Chinese seamless pipe
        "effective_from": date(2010, 11, 10),
        "effective_to": None,
        "stacks_with": ["MFN", "SECTION_232"],
        "mutually_exclusive_with": [],
        "description": "AD/CVD - 136.92% on seamless steel pipe from China (A-570-956, C-570-957)",
        "source_reference": "75 FR 69052; ITC Investigation 701-TA-469",
    },
    {
        "tariff_type": "AD_CVD",
        "hts_code_pattern": "7606.12",
        "origin_country": "CN",
        "rate": 0.3762,  # 37.62% combined for aluminum sheet
        "effective_from": date(2018, 4, 17),
        "effective_to": None,
        "stacks_with": ["MFN", "SECTION_232"],
        "mutually_exclusive_with": [],
        "description": "AD/CVD - 37.62% on common alloy aluminum sheet from China (A-570-053, C-570-054)",
        "source_reference": "83 FR 17335; ITC Investigation 701-TA-591",
    },
    {
        "tariff_type": "AD_CVD",
        "hts_code_pattern": "7318.15",
        "origin_country": "CN",
        "rate": 0.6246,  # 62.46% for steel fasteners
        "effective_from": date(2012, 7, 13),
        "effective_to": None,
        "stacks_with": ["MFN", "SECTION_232"],
        "mutually_exclusive_with": [],
        "description": "AD/CVD - 62.46% on steel threaded rod from China (A-570-932)",
        "source_reference": "77 FR 41551",
    },

    # --- IEEPA for NEW CHAPTERS ---
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "61",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 61 (apparel)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "73",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 73 (steel)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "76",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 76 (aluminum)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "87",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 87 (vehicles)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "90",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 90 (instruments)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
    {
        "tariff_type": "IEEPA",
        "hts_code_pattern": "95",
        "origin_country": "CN",
        "rate": 0.145,
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "stacks_with": ["MFN"],
        "mutually_exclusive_with": ["SECTION_301", "SECTION_232"],
        "description": "IEEPA reciprocal tariff - Chapter 95 (toys)",
        "source_reference": "Executive Order 14257; 90 FR 15425",
    },
]


# =============================================================================
# EXCLUSIONS — Based on real USTR exclusion grants
# =============================================================================

EXCLUSIONS = [
    {
        "hts_code": "8471.30",
        "tariff_type": "SECTION_301",
        "origin_country": "CN",
        "effective_from": date(2025, 4, 11),
        "effective_to": date(2025, 7, 9),
        "description": "Temporary exclusion for laptops/portable computers from Section 301 List 4A",
        "source_reference": "USTR 90 FR 15658 (electronics exclusion)",
    },
    {
        "hts_code": "8517.12",
        "tariff_type": "SECTION_301",
        "origin_country": "CN",
        "effective_from": date(2025, 4, 11),
        "effective_to": date(2025, 7, 9),
        "description": "Temporary exclusion for smartphones from Section 301 List 4A",
        "source_reference": "USTR 90 FR 15658 (electronics exclusion)",
    },
    {
        "hts_code": "8542.31",
        "tariff_type": "IEEPA",
        "origin_country": "CN",
        "effective_from": date(2025, 4, 9),
        "effective_to": None,
        "description": "Semiconductor ICs excluded from IEEPA reciprocal tariff (Annex II)",
        "source_reference": "Executive Order 14257 Annex II; 90 FR 15425",
    },
]


# =============================================================================
# FX RATES — CNY/USD representative rates
# =============================================================================

FX_RATES = [
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1389, "date": date(2026, 8, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1388, "date": date(2026, 7, 31)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1390, "date": date(2026, 7, 30)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1385, "date": date(2026, 7, 15)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1380, "date": date(2026, 7, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1375, "date": date(2026, 6, 15)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1370, "date": date(2026, 6, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1365, "date": date(2026, 5, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1372, "date": date(2026, 4, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1378, "date": date(2026, 3, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1400, "date": date(2025, 4, 9)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1395, "date": date(2025, 1, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1410, "date": date(2024, 8, 1)},
    {"from_currency": "CNY", "to_currency": "USD", "rate": 0.1420, "date": date(2024, 1, 1)},
]
