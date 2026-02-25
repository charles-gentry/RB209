"""Fruit, vine and hop nutrient recommendation tables (RB209 Section 7).

Source: RB209 9th edition, updated February 2020, Section 7 — Fruit, Vines and Hops.
"""

# ── Table 7.3: Pre-planting P/K/Mg ──────────────────────────────────
# Indexed by (crop_group, nutrient, index).
# crop_group: "fruit-vines" or "hops"
# nutrient: "phosphate", "potash", or "magnesium"
# index: 0–5; index 5 means "5 and over"

FRUIT_PREPLANT_PKM: dict[tuple[str, str, int], float] = {
    # Fruit and vines
    ("fruit-vines", "phosphate", 0): 200,
    ("fruit-vines", "phosphate", 1): 100,
    ("fruit-vines", "phosphate", 2):  50,
    ("fruit-vines", "phosphate", 3):  50,
    ("fruit-vines", "phosphate", 4):   0,
    ("fruit-vines", "phosphate", 5):   0,

    ("fruit-vines", "potash", 0): 200,
    ("fruit-vines", "potash", 1): 100,
    ("fruit-vines", "potash", 2):  50,
    ("fruit-vines", "potash", 3):   0,
    ("fruit-vines", "potash", 4):   0,
    ("fruit-vines", "potash", 5):   0,

    ("fruit-vines", "magnesium", 0): 165,
    ("fruit-vines", "magnesium", 1): 125,
    ("fruit-vines", "magnesium", 2):  85,
    ("fruit-vines", "magnesium", 3):   0,
    ("fruit-vines", "magnesium", 4):   0,
    ("fruit-vines", "magnesium", 5):   0,

    # Hops
    ("hops", "phosphate", 0): 250,
    ("hops", "phosphate", 1): 175,
    ("hops", "phosphate", 2): 125,
    ("hops", "phosphate", 3): 100,
    ("hops", "phosphate", 4):  50,
    ("hops", "phosphate", 5):   0,

    ("hops", "potash", 0): 300,
    ("hops", "potash", 1): 250,
    ("hops", "potash", 2): 200,
    ("hops", "potash", 3): 150,
    ("hops", "potash", 4): 100,
    ("hops", "potash", 5):   0,

    ("hops", "magnesium", 0): 250,
    ("hops", "magnesium", 1): 165,
    ("hops", "magnesium", 2):  85,
    ("hops", "magnesium", 3):   0,
    ("hops", "magnesium", 4):   0,
    ("hops", "magnesium", 5):   0,
}


# ── Table 7.4: Top fruit nitrogen ───────────────────────────────────
# Keyed by (crop_slug, soil_category, orchard_management).
# soil_category: FruitSoilCategory values
# orchard_management: OrchardManagement values

FRUIT_TOP_NITROGEN: dict[tuple[str, str, str], float] = {
    # Dessert apples
    ("fruit-dessert-apple", "light-sand",    "grass-strip"):   80,
    ("fruit-dessert-apple", "light-sand",    "overall-grass"): 120,
    ("fruit-dessert-apple", "deep-silt",     "grass-strip"):   30,
    ("fruit-dessert-apple", "deep-silt",     "overall-grass"):  70,
    ("fruit-dessert-apple", "clay",          "grass-strip"):   40,
    ("fruit-dessert-apple", "clay",          "overall-grass"):  80,
    ("fruit-dessert-apple", "other-mineral", "grass-strip"):   60,
    ("fruit-dessert-apple", "other-mineral", "overall-grass"): 100,

    # Culinary and cider apples
    ("fruit-culinary-apple", "light-sand",    "grass-strip"):   110,
    ("fruit-culinary-apple", "light-sand",    "overall-grass"): 150,
    ("fruit-culinary-apple", "deep-silt",     "grass-strip"):    60,
    ("fruit-culinary-apple", "deep-silt",     "overall-grass"):  100,
    ("fruit-culinary-apple", "clay",          "grass-strip"):    70,
    ("fruit-culinary-apple", "clay",          "overall-grass"):  110,
    ("fruit-culinary-apple", "other-mineral", "grass-strip"):    90,
    ("fruit-culinary-apple", "other-mineral", "overall-grass"):  130,

    # Pears
    ("fruit-pear", "light-sand",    "grass-strip"):   140,
    ("fruit-pear", "light-sand",    "overall-grass"): 180,
    ("fruit-pear", "deep-silt",     "grass-strip"):    90,
    ("fruit-pear", "deep-silt",     "overall-grass"):  130,
    ("fruit-pear", "clay",          "grass-strip"):   100,
    ("fruit-pear", "clay",          "overall-grass"):  140,
    ("fruit-pear", "other-mineral", "grass-strip"):   120,
    ("fruit-pear", "other-mineral", "overall-grass"):  160,

    # Cherries
    ("fruit-cherry", "light-sand",    "grass-strip"):   140,
    ("fruit-cherry", "light-sand",    "overall-grass"): 180,
    ("fruit-cherry", "deep-silt",     "grass-strip"):    90,
    ("fruit-cherry", "deep-silt",     "overall-grass"):  130,
    ("fruit-cherry", "clay",          "grass-strip"):   100,
    ("fruit-cherry", "clay",          "overall-grass"):  140,
    ("fruit-cherry", "other-mineral", "grass-strip"):   120,
    ("fruit-cherry", "other-mineral", "overall-grass"):  160,

    # Plums
    ("fruit-plum", "light-sand",    "grass-strip"):   140,
    ("fruit-plum", "light-sand",    "overall-grass"): 180,
    ("fruit-plum", "deep-silt",     "grass-strip"):    90,
    ("fruit-plum", "deep-silt",     "overall-grass"):  130,
    ("fruit-plum", "clay",          "grass-strip"):   100,
    ("fruit-plum", "clay",          "overall-grass"):  140,
    ("fruit-plum", "other-mineral", "grass-strip"):   120,
    ("fruit-plum", "other-mineral", "overall-grass"):  160,
}


# ── Table 7.5: Top fruit P/K/Mg ─────────────────────────────────────
# All top fruit share identical rates; indexed by (nutrient, index).
# index: 0–4; index 4 means "4 and over"

FRUIT_TOP_PKM: dict[tuple[str, int], float] = {
    ("phosphate", 0): 80,
    ("phosphate", 1): 40,
    ("phosphate", 2): 20,
    ("phosphate", 3): 20,
    ("phosphate", 4):  0,

    ("potash", 0): 220,
    ("potash", 1): 150,
    ("potash", 2):  80,
    ("potash", 3):   0,
    ("potash", 4):   0,

    ("magnesium", 0): 100,
    ("magnesium", 1):  65,
    ("magnesium", 2):  50,
    ("magnesium", 3):   0,
    ("magnesium", 4):   0,
}


# ── Table 7.6: Soft fruit and vine nitrogen ──────────────────────────
# Keyed by (crop_slug, soil_category). Strawberries use Table 7.8 instead.

FRUIT_SOFT_NITROGEN: dict[tuple[str, str], float] = {
    # Blackcurrants
    ("fruit-blackcurrant", "light-sand"):   160,
    ("fruit-blackcurrant", "deep-silt"):    110,
    ("fruit-blackcurrant", "clay"):         120,
    ("fruit-blackcurrant", "other-mineral"): 140,

    # Redcurrants
    ("fruit-redcurrant", "light-sand"):   120,
    ("fruit-redcurrant", "deep-silt"):     70,
    ("fruit-redcurrant", "clay"):          80,
    ("fruit-redcurrant", "other-mineral"): 100,

    # Gooseberries
    ("fruit-gooseberry", "light-sand"):   120,
    ("fruit-gooseberry", "deep-silt"):     70,
    ("fruit-gooseberry", "clay"):          80,
    ("fruit-gooseberry", "other-mineral"): 100,

    # Raspberries
    ("fruit-raspberry", "light-sand"):   120,
    ("fruit-raspberry", "deep-silt"):     70,
    ("fruit-raspberry", "clay"):          80,
    ("fruit-raspberry", "other-mineral"): 100,

    # Loganberries
    ("fruit-loganberry", "light-sand"):   120,
    ("fruit-loganberry", "deep-silt"):     70,
    ("fruit-loganberry", "clay"):          80,
    ("fruit-loganberry", "other-mineral"): 100,

    # Tayberries
    ("fruit-tayberry", "light-sand"):   120,
    ("fruit-tayberry", "deep-silt"):     70,
    ("fruit-tayberry", "clay"):          80,
    ("fruit-tayberry", "other-mineral"): 100,

    # Blackberries
    ("fruit-blackberry", "light-sand"):   120,
    ("fruit-blackberry", "deep-silt"):     70,
    ("fruit-blackberry", "clay"):          80,
    ("fruit-blackberry", "other-mineral"): 100,

    # Vines
    ("fruit-vine", "light-sand"):    60,
    ("fruit-vine", "deep-silt"):      0,
    ("fruit-vine", "clay"):          20,
    ("fruit-vine", "other-mineral"): 40,
}


# ── Table 7.7: Soft fruit and vine P/K/Mg ───────────────────────────
# Group 1: blackcurrants, redcurrants, gooseberries, raspberries, loganberries, tayberries
# Group 2: blackberries, vines
# Magnesium is identical for all crops.
# Indexed by (crop_slug, nutrient, index); index 0–4.

_GROUP1_SLUGS = (
    "fruit-blackcurrant", "fruit-redcurrant", "fruit-gooseberry",
    "fruit-raspberry", "fruit-loganberry", "fruit-tayberry",
)
_GROUP2_SLUGS = ("fruit-blackberry", "fruit-vine")
_ALL_SOFT_SLUGS = _GROUP1_SLUGS + _GROUP2_SLUGS

FRUIT_SOFT_PKM: dict[tuple[str, str, int], float] = {
    # Group 1 — phosphate
    **{(slug, "phosphate", i): v for slug in _GROUP1_SLUGS
       for i, v in enumerate([110, 70, 40, 40, 0])},

    # Group 1 — potash
    **{(slug, "potash", i): v for slug in _GROUP1_SLUGS
       for i, v in enumerate([250, 180, 120, 60, 0])},

    # Group 2 — phosphate
    **{(slug, "phosphate", i): v for slug in _GROUP2_SLUGS
       for i, v in enumerate([110, 70, 40, 40, 0])},

    # Group 2 — potash
    **{(slug, "potash", i): v for slug in _GROUP2_SLUGS
       for i, v in enumerate([220, 150, 80, 0, 0])},

    # All crops — magnesium
    **{(slug, "magnesium", i): v for slug in _ALL_SOFT_SLUGS
       for i, v in enumerate([100, 65, 50, 0, 0])},
}


# ── Table 7.8: Strawberry nitrogen ──────────────────────────────────
# SNS-index-based. Three soil groups: light-sand, deep-silt, other-mineral.
# When soil_category == "clay", map to "other-mineral" before lookup.
# SNS Index 0–5; index 5 means "5 and over".

FRUIT_STRAWBERRY_NITROGEN: dict[tuple[str, str, int], float] = {
    # Main season
    ("fruit-strawberry-main", "light-sand",   0): 60,
    ("fruit-strawberry-main", "light-sand",   1): 50,
    ("fruit-strawberry-main", "light-sand",   2): 40,
    ("fruit-strawberry-main", "light-sand",   3): 30,
    ("fruit-strawberry-main", "light-sand",   4): 20,
    ("fruit-strawberry-main", "light-sand",   5):  0,

    ("fruit-strawberry-main", "deep-silt",    0):  0,
    ("fruit-strawberry-main", "deep-silt",    1):  0,
    ("fruit-strawberry-main", "deep-silt",    2):  0,
    ("fruit-strawberry-main", "deep-silt",    3):  0,
    ("fruit-strawberry-main", "deep-silt",    4):  0,
    ("fruit-strawberry-main", "deep-silt",    5):  0,

    ("fruit-strawberry-main", "other-mineral", 0): 40,
    ("fruit-strawberry-main", "other-mineral", 1): 40,
    ("fruit-strawberry-main", "other-mineral", 2): 30,
    ("fruit-strawberry-main", "other-mineral", 3): 20,
    ("fruit-strawberry-main", "other-mineral", 4):  0,
    ("fruit-strawberry-main", "other-mineral", 5):  0,

    # Everbearers
    ("fruit-strawberry-ever", "light-sand",   0): 80,
    ("fruit-strawberry-ever", "light-sand",   1): 70,
    ("fruit-strawberry-ever", "light-sand",   2): 60,
    ("fruit-strawberry-ever", "light-sand",   3): 40,
    ("fruit-strawberry-ever", "light-sand",   4): 20,
    ("fruit-strawberry-ever", "light-sand",   5):  0,

    ("fruit-strawberry-ever", "deep-silt",    0): 40,
    ("fruit-strawberry-ever", "deep-silt",    1): 30,
    ("fruit-strawberry-ever", "deep-silt",    2): 30,
    ("fruit-strawberry-ever", "deep-silt",    3): 20,
    ("fruit-strawberry-ever", "deep-silt",    4):  0,
    ("fruit-strawberry-ever", "deep-silt",    5):  0,

    ("fruit-strawberry-ever", "other-mineral", 0): 60,
    ("fruit-strawberry-ever", "other-mineral", 1): 50,
    ("fruit-strawberry-ever", "other-mineral", 2): 40,
    ("fruit-strawberry-ever", "other-mineral", 3): 20,
    ("fruit-strawberry-ever", "other-mineral", 4):  0,
    ("fruit-strawberry-ever", "other-mineral", 5):  0,
}


# ── Table 7.9: Strawberry P/K/Mg ────────────────────────────────────
# Indexed by (nutrient, index); index 0–4.

FRUIT_STRAWBERRY_PKM: dict[tuple[str, int], float] = {
    ("phosphate", 0): 110,
    ("phosphate", 1):  70,
    ("phosphate", 2):  40,
    ("phosphate", 3):  40,
    ("phosphate", 4):   0,

    ("potash",    0): 220,
    ("potash",    1): 150,
    ("potash",    2):  80,
    ("potash",    3):   0,
    ("potash",    4):   0,

    ("magnesium", 0): 100,
    ("magnesium", 1):  65,
    ("magnesium", 2):  50,
    ("magnesium", 3):   0,
    ("magnesium", 4):   0,
}


# ── Table 7.17: Hops nitrogen ────────────────────────────────────────
# Light sand and shallow soils not listed; engine raises ValueError for "light-sand".

FRUIT_HOPS_NITROGEN: dict[str, float] = {
    "deep-silt":     180,
    "clay":          200,
    "other-mineral": 220,
    # "light-sand" not in Table 7.17 — raise ValueError in engine
}


# ── Table 7.17: Hops P/K/Mg ─────────────────────────────────────────
# Extended index range 0–5; index 5 means "5 and over".

FRUIT_HOPS_PKM: dict[tuple[str, int], float] = {
    ("phosphate", 0): 250,
    ("phosphate", 1): 200,
    ("phosphate", 2): 150,
    ("phosphate", 3): 100,
    ("phosphate", 4):  50,
    ("phosphate", 5):   0,

    ("potash",    0): 425,
    ("potash",    1): 350,
    ("potash",    2): 275,
    ("potash",    3): 200,
    ("potash",    4): 100,
    ("potash",    5):   0,

    ("magnesium", 0): 150,
    ("magnesium", 1): 100,
    ("magnesium", 2):  50,
    ("magnesium", 3):   0,
    ("magnesium", 4):   0,
    ("magnesium", 5):   0,
}
