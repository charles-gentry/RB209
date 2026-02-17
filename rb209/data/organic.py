"""Organic material nutrient content tables.

Values are kg per tonne of fresh weight (FYM, compost, cake)
or kg per cubic metre (slurries).
Based on RB209 9th edition typical values.

Fields: total_n, available_n (crop-available year 1),
        p2o5, k2o, mgo, so3
"""
# ── Timing and incorporation factors ────────────────────────────────
#
# Table 2.12 (RB209 Section 2): percentage of total N available to the
# next crop after pig slurry applications (typical value: 4% DM).
#
# Key: (timing, soil_category, incorporated)
#   timing:        "autumn" | "winter" | "spring" | "summer"
#   soil_category: "sandy"  (light / shallow soils)
#                  "medium_heavy" (medium, heavy, and organic soils)
#   incorporated:  True  = soil-incorporated within 6 hours of application
#                  False = surface-applied (not incorporated)
#
# Values are fractions of total nitrogen (not percentages).
# "summer" + incorporated is listed as N/A in RB209 and is omitted.

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

# Maps each organic-material key to its timing-factor table.
# Only materials for which RB209 provides timing/incorporation data
# are included.
ORGANIC_N_TIMING_FACTORS: dict[str, dict[tuple, float]] = {
    "pig-slurry": _PIG_SLURRY_N_FACTORS,
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
