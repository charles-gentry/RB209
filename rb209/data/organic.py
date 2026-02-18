"""Organic material nutrient content tables.

Values are kg per tonne of fresh weight (FYM, compost, cake)
or kg per cubic metre (slurries).
Based on RB209 9th edition typical values.

Fields: total_n, available_n (crop-available year 1),
        p2o5, k2o, mgo, so3
"""
# ── Timing and incorporation factors ────────────────────────────────
#
# RB209 Section 2 tables: percentage of total N available to the
# next crop, by material type, application timing, soil category,
# and incorporation status.
#
# Key: (timing, soil_category, incorporated)
#   timing:        "autumn" | "winter" | "spring" | "summer"
#   soil_category: "sandy"       (light / shallow soils)
#                  "medium_heavy" (medium, heavy, and organic soils)
#   incorporated:  True  = soil-incorporated promptly after application
#                          (within 6 hours for slurries; 24 hours for solids)
#                  False = surface-applied (not incorporated)
#
# Values are fractions of total nitrogen (not percentages).
# "summer" + incorporated is listed as N/A in RB209 and is omitted.

# Table 2.3 — FYM (all livestock FYM types: cattle, pig, sheep, horse).
# All FYM types share the same availability fractions.
# Incorporated values use fresh FYM figures (autumn–winter: same as old;
# spring: 15 % for fresh vs 10 % for old FYM).
_FYM_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.05,
    ("autumn", "medium_heavy", False): 0.10,
    ("winter", "sandy",        False): 0.10,
    ("winter", "medium_heavy", False): 0.10,
    ("spring", "sandy",        False): 0.10,
    ("spring", "medium_heavy", False): 0.10,
    ("summer", "sandy",        False): 0.10,
    ("summer", "medium_heavy", False): 0.10,
    ("autumn", "sandy",        True):  0.05,
    ("autumn", "medium_heavy", True):  0.10,
    ("winter", "sandy",        True):  0.10,
    ("winter", "medium_heavy", True):  0.10,
    ("spring", "sandy",        True):  0.15,
    ("spring", "medium_heavy", True):  0.15,
    # ("summer", ..., True) -> N/A in RB209
}

# Table 2.6 — Poultry litter / broiler-turkey litter (typically ~40 % DM).
_POULTRY_LITTER_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.10,
    ("autumn", "medium_heavy", False): 0.25,
    ("winter", "sandy",        False): 0.20,
    ("winter", "medium_heavy", False): 0.25,
    ("spring", "sandy",        False): 0.30,
    ("spring", "medium_heavy", False): 0.30,
    ("summer", "sandy",        False): 0.30,
    ("summer", "medium_heavy", False): 0.30,
    ("autumn", "sandy",        True):  0.10,
    ("autumn", "medium_heavy", True):  0.30,
    ("winter", "sandy",        True):  0.20,
    ("winter", "medium_heavy", True):  0.30,
    ("spring", "sandy",        True):  0.40,
    ("spring", "medium_heavy", True):  0.40,
    # ("summer", ..., True) -> N/A in RB209
}

# Table 2.6 — Layer manure (typically ~20 % DM).
_LAYER_MANURE_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.15,
    ("autumn", "medium_heavy", False): 0.25,
    ("winter", "sandy",        False): 0.25,
    ("winter", "medium_heavy", False): 0.25,
    ("spring", "sandy",        False): 0.35,
    ("spring", "medium_heavy", False): 0.35,
    ("summer", "sandy",        False): 0.35,
    ("summer", "medium_heavy", False): 0.35,
    ("autumn", "sandy",        True):  0.15,
    ("autumn", "medium_heavy", True):  0.35,
    ("winter", "sandy",        True):  0.25,
    ("winter", "medium_heavy", True):  0.40,
    ("spring", "sandy",        True):  0.50,
    ("spring", "medium_heavy", True):  0.50,
    # ("summer", ..., True) -> N/A in RB209
}

# Table 2.9 — Cattle slurry liquid (typical 6 % DM).
_CATTLE_SLURRY_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.05,
    ("autumn", "medium_heavy", False): 0.25,
    ("winter", "sandy",        False): 0.25,
    ("winter", "medium_heavy", False): 0.25,
    ("spring", "sandy",        False): 0.35,
    ("spring", "medium_heavy", False): 0.35,
    ("summer", "sandy",        False): 0.25,
    ("summer", "medium_heavy", False): 0.25,
    ("autumn", "sandy",        True):  0.05,
    ("autumn", "medium_heavy", True):  0.30,
    ("winter", "sandy",        True):  0.20,
    ("winter", "medium_heavy", True):  0.30,
    ("spring", "sandy",        True):  0.40,
    ("spring", "medium_heavy", True):  0.40,
    # ("summer", ..., True) -> N/A in RB209
}

# Table 2.12 (RB209 Section 2): percentage of total N available to the
# next crop after pig slurry applications (typical value: 4% DM).
_PIG_SLURRY_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.10,
    ("autumn", "medium_heavy", False): 0.30,
    ("winter", "sandy",        False): 0.35,
    ("winter", "medium_heavy", False): 0.35,
    ("spring", "sandy",        False): 0.50,
    ("spring", "medium_heavy", False): 0.50,
    ("summer", "sandy",        False): 0.50,
    ("summer", "medium_heavy", False): 0.50,
    ("autumn", "sandy",        True):  0.10,
    ("autumn", "medium_heavy", True):  0.40,
    ("winter", "sandy",        True):  0.30,
    ("winter", "medium_heavy", True):  0.45,
    ("spring", "sandy",        True):  0.60,
    ("spring", "medium_heavy", True):  0.60,
    # ("summer", ..., True) -> N/A in RB209
}

# Table 2.15 — Biosolids digested cake (typical 25 % DM).
# All four biosolids product types have identical values; digested cake
# is the default for the "biosolids-cake" material entry.
_BIOSOLIDS_CAKE_N_FACTORS: dict[tuple, float] = {
    ("autumn", "sandy",        False): 0.10,
    ("autumn", "medium_heavy", False): 0.15,
    ("winter", "sandy",        False): 0.15,
    ("winter", "medium_heavy", False): 0.15,
    ("spring", "sandy",        False): 0.15,
    ("spring", "medium_heavy", False): 0.15,
    ("summer", "sandy",        False): 0.15,
    ("summer", "medium_heavy", False): 0.15,
    ("autumn", "sandy",        True):  0.10,
    ("autumn", "medium_heavy", True):  0.15,
    ("winter", "sandy",        True):  0.15,
    ("winter", "medium_heavy", True):  0.15,
    ("spring", "sandy",        True):  0.20,
    ("spring", "medium_heavy", True):  0.20,
    # ("summer", ..., True) -> N/A in RB209
}

# Maps each organic-material key to its timing-factor table.
# Only materials for which RB209 provides timing/incorporation data
# are included.  Composts (green-compost, green-food-compost) and
# paper-crumble are not listed in any RB209 timing table and therefore
# do not have entries here; use the flat available_n coefficient instead.
ORGANIC_N_TIMING_FACTORS: dict[str, dict[tuple, float]] = {
    "cattle-fym":      _FYM_N_FACTORS,
    "pig-fym":         _FYM_N_FACTORS,
    "sheep-fym":       _FYM_N_FACTORS,
    "horse-fym":       _FYM_N_FACTORS,
    "poultry-litter":  _POULTRY_LITTER_N_FACTORS,
    "layer-manure":    _LAYER_MANURE_N_FACTORS,
    "cattle-slurry":   _CATTLE_SLURRY_N_FACTORS,
    "pig-slurry":      _PIG_SLURRY_N_FACTORS,
    "biosolids-cake":  _BIOSOLIDS_CAKE_N_FACTORS,
}

# Maps SoilType values to the two soil categories used in timing tables.
TIMING_SOIL_CATEGORY: dict[str, str] = {
    "light":   "sandy",
    "medium":  "medium_heavy",
    "heavy":   "medium_heavy",
    "organic": "medium_heavy",
}

ORGANIC_MATERIAL_INFO: dict[str, dict] = {
    "cattle-fym": {
        "name": "Cattle FYM",
        "unit": "t",
        "total_n": 6.0,
        "available_n": 1.2,
        "p2o5": 3.2,
        "k2o": 8.0,
        "mgo": 1.8,
        "so3": 3.0,
    },
    "pig-fym": {
        "name": "Pig FYM",
        "unit": "t",
        "total_n": 7.0,
        "available_n": 1.4,
        "p2o5": 6.0,
        "k2o": 5.0,
        "mgo": 1.5,
        "so3": 3.0,
    },
    "sheep-fym": {
        "name": "Sheep FYM",
        "unit": "t",
        "total_n": 7.0,
        "available_n": 1.4,
        "p2o5": 3.2,
        "k2o": 6.0,
        "mgo": 2.0,
        "so3": 4.0,
    },
    "horse-fym": {
        "name": "Horse FYM",
        "unit": "t",
        "total_n": 5.0,
        "available_n": 1.0,
        "p2o5": 3.5,
        "k2o": 6.0,
        "mgo": 1.5,
        "so3": 2.0,
    },
    "poultry-litter": {
        "name": "Poultry Litter (broiler/turkey)",
        "unit": "t",
        "total_n": 19.0,
        "available_n": 5.7,
        "p2o5": 14.0,
        "k2o": 9.5,
        "mgo": 3.5,
        "so3": 5.0,
    },
    "layer-manure": {
        "name": "Layer Manure",
        "unit": "t",
        "total_n": 16.0,
        "available_n": 4.8,
        "p2o5": 13.0,
        "k2o": 8.0,
        "mgo": 3.0,
        "so3": 5.5,
    },
    "cattle-slurry": {
        "name": "Cattle Slurry (6% DM)",
        "unit": "m3",
        "total_n": 2.6,
        "available_n": 0.8,
        "p2o5": 1.2,
        "k2o": 2.5,
        "mgo": 0.5,
        "so3": 0.8,
    },
    "pig-slurry": {
        "name": "Pig Slurry (4% DM)",
        "unit": "m3",
        "total_n": 3.6,
        "available_n": 2.167,
        "p2o5": 2.0,
        "k2o": 1.6,
        "mgo": 0.5,
        "so3": 0.8,
    },
    "green-compost": {
        "name": "Green Compost",
        "unit": "t",
        "total_n": 4.3,
        "available_n": 0.4,
        "p2o5": 3.0,
        "k2o": 4.2,
        "mgo": 1.5,
        "so3": 2.5,
    },
    "green-food-compost": {
        "name": "Green/Food Compost",
        "unit": "t",
        "total_n": 8.0,
        "available_n": 0.8,
        "p2o5": 4.5,
        "k2o": 6.0,
        "mgo": 2.0,
        "so3": 4.0,
    },
    "biosolids-cake": {
        "name": "Biosolids Cake (sewage sludge)",
        "unit": "t",
        "total_n": 12.5,
        "available_n": 2.5,
        "p2o5": 12.0,
        "k2o": 0.5,
        "mgo": 2.0,
        "so3": 7.0,
    },
    "paper-crumble": {
        "name": "Paper Crumble",
        "unit": "t",
        "total_n": 3.0,
        "available_n": 0.3,
        "p2o5": 1.5,
        "k2o": 0.5,
        "mgo": 2.5,
        "so3": 4.0,
    },
}
