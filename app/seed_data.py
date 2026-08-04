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
