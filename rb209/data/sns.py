"""Soil Nitrogen Supply (SNS) lookup tables.

SNS is determined by previous crop N-residue category, soil type,
and excess winter rainfall.
Based on RB209 9th edition field assessment method.
"""

# (n_residue_category, soil_type, rainfall) -> SNS index
# n_residue_category: "low", "medium", "high", "very-high"
# soil_type: "light", "medium", "heavy", "organic"
# rainfall: "low", "medium", "high"

SNS_LOOKUP: dict[tuple[str, str, str], int] = {
    # LOW N residue (cereals, sugar beet, linseed, forage maize, set-aside, fallow)
    ("low", "light", "low"): 1,
    ("low", "light", "medium"): 0,
    ("low", "light", "high"): 0,
    ("low", "medium", "low"): 1,
    ("low", "medium", "medium"): 1,
    ("low", "medium", "high"): 1,
    ("low", "heavy", "low"): 2,
    ("low", "heavy", "medium"): 2,
    ("low", "heavy", "high"): 1,
    ("low", "organic", "low"): 3,
    ("low", "organic", "medium"): 2,
    ("low", "organic", "high"): 2,

    # MEDIUM N residue (oilseed rape, potatoes)
    ("medium", "light", "low"): 2,
    ("medium", "light", "medium"): 1,
    ("medium", "light", "high"): 1,
    ("medium", "medium", "low"): 3,
    ("medium", "medium", "medium"): 2,
    ("medium", "medium", "high"): 2,
    ("medium", "heavy", "low"): 3,
    ("medium", "heavy", "medium"): 3,
    ("medium", "heavy", "high"): 2,
    ("medium", "organic", "low"): 4,
    ("medium", "organic", "medium"): 3,
    ("medium", "organic", "high"): 3,

    # HIGH N residue (peas/beans, vegetables, 1-2 yr grass)
    ("high", "light", "low"): 3,
    ("high", "light", "medium"): 2,
    ("high", "light", "high"): 1,
    ("high", "medium", "low"): 4,
    ("high", "medium", "medium"): 3,
    ("high", "medium", "high"): 2,
    ("high", "heavy", "low"): 4,
    ("high", "heavy", "medium"): 3,
    ("high", "heavy", "high"): 3,
    ("high", "organic", "low"): 5,
    ("high", "organic", "medium"): 4,
    ("high", "organic", "high"): 3,

    # VERY HIGH N residue (long-term grass 5+ years, lucerne)
    ("very-high", "light", "low"): 4,
    ("very-high", "light", "medium"): 3,
    ("very-high", "light", "high"): 2,
    ("very-high", "medium", "low"): 5,
    ("very-high", "medium", "medium"): 4,
    ("very-high", "medium", "high"): 3,
    ("very-high", "heavy", "low"): 5,
    ("very-high", "heavy", "medium"): 4,
    ("very-high", "heavy", "high"): 4,
    ("very-high", "organic", "low"): 6,
    ("very-high", "organic", "medium"): 5,
    ("very-high", "organic", "high"): 4,
}

# Table 4.6: SNS Indices following ploughing out of grass leys.
#
# Key: (soil_category, ley_row)
# soil_category:
#   "light"             – Light sands or shallow soils over sandstone (all rainfall)
#   "medium"            – Other medium soils and shallow soils, not over sandstone (all rainfall)
#   "heavy-low"         – Deep clayey/silty soils, low rainfall (500–600 mm annual)
#   "heavy-medium-high" – Deep clayey/silty soils, moderate or high rainfall
# ley_row:
#   "low-n-or-cut"          – All leys ≥2 cuts/yr with little/no manure; 1–2yr low N;
#                             1–2yr ≥1 cut; 3–5yr low N ≥1 cut
#   "high-n-grazed-or-mixed" – 1–2yr high N grazed; 3–5yr low N grazed;
#                              3–5yr high N 1 cut then grazed
#   "high-n-grazed-35yr"    – 3–5yr high N grazed (highest residues)
#
# Value: (year1_sns, year2_sns, year3_sns)

GRASS_LEY_SNS_LOOKUP: dict[tuple[str, str], tuple[int, int, int]] = {
    # Light sands or shallow soils over sandstone – all rainfall areas
    ("light", "low-n-or-cut"):           (0, 0, 0),
    ("light", "high-n-grazed-or-mixed"): (1, 2, 1),
    ("light", "high-n-grazed-35yr"):     (3, 2, 1),

    # Other medium soils and shallow soils – not over sandstone – all rainfall areas
    ("medium", "low-n-or-cut"):           (1, 1, 1),
    ("medium", "high-n-grazed-or-mixed"): (2, 2, 1),
    ("medium", "high-n-grazed-35yr"):     (3, 3, 2),

    # Deep clayey soils and deep silty soils in low rainfall areas (500–600 mm)
    ("heavy-low", "low-n-or-cut"):           (2, 2, 2),
    ("heavy-low", "high-n-grazed-or-mixed"): (3, 3, 2),
    ("heavy-low", "high-n-grazed-35yr"):     (5, 4, 3),

    # Deep clayey soils and deep silty soils in moderate or high rainfall areas
    ("heavy-medium-high", "low-n-or-cut"):           (1, 1, 1),
    ("heavy-medium-high", "high-n-grazed-or-mixed"): (3, 2, 1),
    ("heavy-medium-high", "high-n-grazed-35yr"):     (4, 3, 2),
}

# Table 4.10: SNS value (kg N/ha) to SNS index.
# Each tuple is (upper_bound_inclusive, sns_index).
# Evaluated in order; first match wins.
SNS_VALUE_TO_INDEX: list[tuple[float, int]] = [
    (60, 0),
    (80, 1),
    (100, 2),
    (120, 3),
    (160, 4),
    (240, 5),
    (float("inf"), 6),
]

# ── Vegetable SNS Tables (Section 6) ────────────────────────────────

# Tables 6.2–6.4: Vegetable SNS lookup.
# Key: (previous_crop, soil_type, rainfall) -> SNS index
# previous_crop: VegPreviousCrop value strings
# soil_type: VegSoilType value strings (light-sand, medium, deep-clay, deep-silt)
# rainfall: "low" (<600 mm / <150 mm EWR), "moderate" (600–700 mm), "high" (>700 mm / >250 mm EWR)
# Organic/peat soils are handled separately in the engine (advisory notes only).
VEG_SNS_LOOKUP: dict[tuple[str, str, str], int] = {
    # Table 6.2 — low rainfall
    ("beans",        "light-sand", "low"): 1,
    ("beans",        "medium",     "low"): 2,
    ("beans",        "deep-clay",  "low"): 3,
    ("beans",        "deep-silt",  "low"): 3,
    ("cereals",      "light-sand", "low"): 0,
    ("cereals",      "medium",     "low"): 1,
    ("cereals",      "deep-clay",  "low"): 2,
    ("cereals",      "deep-silt",  "low"): 2,
    ("forage-cut",   "light-sand", "low"): 0,
    ("forage-cut",   "medium",     "low"): 1,
    ("forage-cut",   "deep-clay",  "low"): 2,
    ("forage-cut",   "deep-silt",  "low"): 2,
    ("oilseed-rape", "light-sand", "low"): 1,
    ("oilseed-rape", "medium",     "low"): 2,
    ("oilseed-rape", "deep-clay",  "low"): 3,
    ("oilseed-rape", "deep-silt",  "low"): 3,
    ("peas",         "light-sand", "low"): 1,
    ("peas",         "medium",     "low"): 2,
    ("peas",         "deep-clay",  "low"): 3,
    ("peas",         "deep-silt",  "low"): 3,
    ("potatoes",     "light-sand", "low"): 1,
    ("potatoes",     "medium",     "low"): 2,
    ("potatoes",     "deep-clay",  "low"): 3,
    ("potatoes",     "deep-silt",  "low"): 3,
    ("sugar-beet",   "light-sand", "low"): 1,
    ("sugar-beet",   "medium",     "low"): 1,
    ("sugar-beet",   "deep-clay",  "low"): 2,
    ("sugar-beet",   "deep-silt",  "low"): 2,
    ("uncropped",    "light-sand", "low"): 1,
    ("uncropped",    "medium",     "low"): 2,
    ("uncropped",    "deep-clay",  "low"): 3,
    ("uncropped",    "deep-silt",  "low"): 3,
    ("veg-low-n",    "light-sand", "low"): 0,
    ("veg-low-n",    "medium",     "low"): 1,
    ("veg-low-n",    "deep-clay",  "low"): 2,
    ("veg-low-n",    "deep-silt",  "low"): 2,
    ("veg-medium-n", "light-sand", "low"): 1,
    ("veg-medium-n", "medium",     "low"): 3,
    ("veg-medium-n", "deep-clay",  "low"): 3,
    ("veg-medium-n", "deep-silt",  "low"): 3,
    ("veg-high-n",   "light-sand", "low"): 2,
    ("veg-high-n",   "medium",     "low"): 4,
    ("veg-high-n",   "deep-clay",  "low"): 4,
    ("veg-high-n",   "deep-silt",  "low"): 4,

    # Table 6.3 — moderate rainfall
    ("beans",        "light-sand", "moderate"): 1,
    ("beans",        "medium",     "moderate"): 2,
    ("beans",        "deep-clay",  "moderate"): 2,
    ("beans",        "deep-silt",  "moderate"): 3,
    ("cereals",      "light-sand", "moderate"): 0,
    ("cereals",      "medium",     "moderate"): 1,
    ("cereals",      "deep-clay",  "moderate"): 1,
    ("cereals",      "deep-silt",  "moderate"): 1,
    ("forage-cut",   "light-sand", "moderate"): 0,
    ("forage-cut",   "medium",     "moderate"): 1,
    ("forage-cut",   "deep-clay",  "moderate"): 1,
    ("forage-cut",   "deep-silt",  "moderate"): 1,
    ("oilseed-rape", "light-sand", "moderate"): 0,
    ("oilseed-rape", "medium",     "moderate"): 2,
    ("oilseed-rape", "deep-clay",  "moderate"): 2,
    ("oilseed-rape", "deep-silt",  "moderate"): 2,
    ("peas",         "light-sand", "moderate"): 1,
    ("peas",         "medium",     "moderate"): 2,
    ("peas",         "deep-clay",  "moderate"): 2,
    ("peas",         "deep-silt",  "moderate"): 3,
    ("potatoes",     "light-sand", "moderate"): 0,
    ("potatoes",     "medium",     "moderate"): 2,
    ("potatoes",     "deep-clay",  "moderate"): 2,
    ("potatoes",     "deep-silt",  "moderate"): 2,
    ("sugar-beet",   "light-sand", "moderate"): 0,
    ("sugar-beet",   "medium",     "moderate"): 1,
    ("sugar-beet",   "deep-clay",  "moderate"): 1,
    ("sugar-beet",   "deep-silt",  "moderate"): 1,
    ("uncropped",    "light-sand", "moderate"): 1,
    ("uncropped",    "medium",     "moderate"): 2,
    ("uncropped",    "deep-clay",  "moderate"): 2,
    ("uncropped",    "deep-silt",  "moderate"): 2,
    ("veg-low-n",    "light-sand", "moderate"): 0,
    ("veg-low-n",    "medium",     "moderate"): 1,
    ("veg-low-n",    "deep-clay",  "moderate"): 1,
    ("veg-low-n",    "deep-silt",  "moderate"): 1,
    ("veg-medium-n", "light-sand", "moderate"): 0,
    ("veg-medium-n", "medium",     "moderate"): 2,
    ("veg-medium-n", "deep-clay",  "moderate"): 3,
    ("veg-medium-n", "deep-silt",  "moderate"): 3,
    ("veg-high-n",   "light-sand", "moderate"): 1,
    ("veg-high-n",   "medium",     "moderate"): 3,
    ("veg-high-n",   "deep-clay",  "moderate"): 4,
    ("veg-high-n",   "deep-silt",  "moderate"): 4,

    # Table 6.4 — high rainfall
    ("beans",        "light-sand", "high"): 0,
    ("beans",        "medium",     "high"): 1,
    ("beans",        "deep-clay",  "high"): 2,
    ("beans",        "deep-silt",  "high"): 2,
    ("cereals",      "light-sand", "high"): 0,
    ("cereals",      "medium",     "high"): 1,
    ("cereals",      "deep-clay",  "high"): 1,
    ("cereals",      "deep-silt",  "high"): 1,
    ("forage-cut",   "light-sand", "high"): 0,
    ("forage-cut",   "medium",     "high"): 1,
    ("forage-cut",   "deep-clay",  "high"): 1,
    ("forage-cut",   "deep-silt",  "high"): 1,
    ("oilseed-rape", "light-sand", "high"): 0,
    ("oilseed-rape", "medium",     "high"): 1,
    ("oilseed-rape", "deep-clay",  "high"): 1,
    ("oilseed-rape", "deep-silt",  "high"): 2,
    ("peas",         "light-sand", "high"): 0,
    ("peas",         "medium",     "high"): 1,
    ("peas",         "deep-clay",  "high"): 2,
    ("peas",         "deep-silt",  "high"): 2,
    ("potatoes",     "light-sand", "high"): 0,
    ("potatoes",     "medium",     "high"): 1,
    ("potatoes",     "deep-clay",  "high"): 1,
    ("potatoes",     "deep-silt",  "high"): 2,
    ("sugar-beet",   "light-sand", "high"): 0,
    ("sugar-beet",   "medium",     "high"): 1,
    ("sugar-beet",   "deep-clay",  "high"): 1,
    ("sugar-beet",   "deep-silt",  "high"): 1,
    ("uncropped",    "light-sand", "high"): 0,
    ("uncropped",    "medium",     "high"): 1,
    ("uncropped",    "deep-clay",  "high"): 1,
    ("uncropped",    "deep-silt",  "high"): 2,
    ("veg-low-n",    "light-sand", "high"): 0,
    ("veg-low-n",    "medium",     "high"): 1,
    ("veg-low-n",    "deep-clay",  "high"): 1,
    ("veg-low-n",    "deep-silt",  "high"): 1,
    ("veg-medium-n", "light-sand", "high"): 0,
    ("veg-medium-n", "medium",     "high"): 1,
    ("veg-medium-n", "deep-clay",  "high"): 1,
    ("veg-medium-n", "deep-silt",  "high"): 2,
    ("veg-high-n",   "light-sand", "high"): 1,
    ("veg-high-n",   "medium",     "high"): 2,
    ("veg-high-n",   "deep-clay",  "high"): 2,
    ("veg-high-n",   "deep-silt",  "high"): 3,
}

# Table 6.6: SMN (kg N/ha) to SNS index thresholds for vegetable crops.
# Key: depth_cm -> list of (upper_bound, sns_index) in ascending order.
# Values above the last entry map to index 6.
VEG_SMN_SNS_THRESHOLDS: dict[int, list[tuple[float, int]]] = {
    30: [(19.9, 0), (27, 1), (33, 2), (40, 3), (53, 4), (80, 5)],   # >80 -> 6
    60: [(39.9, 0), (53, 1), (67, 2), (80, 3), (107, 4), (160, 5)], # >160 -> 6
    90: [(59.9, 0), (80, 1), (100, 2), (120, 3), (160, 4), (240, 5)], # >240 -> 6
}
