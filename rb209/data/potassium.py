"""Potassium (K2O) recommendation tables.

Values are kg K2O/ha, keyed by (crop, k_index).
K index ranges from 0 (deficient) to 4+ (high).
For cereals, separate tables for straw removed vs incorporated.
Based on RB209 9th edition.
"""

# Cereals with straw REMOVED
# (crop_value, k_index) -> kg K2O/ha
POTASSIUM_STRAW_REMOVED: dict[tuple[str, int], float] = {
    **{(crop, idx): val
       for crop in [
           "winter-wheat-feed", "winter-wheat-milling", "spring-wheat",
           "winter-barley", "spring-barley",
           "winter-oats", "spring-oats", "winter-rye",
       ]
       for idx, val in [(0, 105), (1, 75), (2, 55), (3, 0), (4, 0)]},
}

# Cereals with straw INCORPORATED
POTASSIUM_STRAW_INCORPORATED: dict[tuple[str, int], float] = {
    **{(crop, idx): val
       for crop in [
           "winter-wheat-feed", "winter-wheat-milling", "spring-wheat",
           "winter-barley", "spring-barley",
           "winter-oats", "spring-oats", "winter-rye",
       ]
       for idx, val in [(0, 65), (1, 40), (2, 25), (3, 0), (4, 0)]},
}

# Non-cereal crops (no straw option)
POTASSIUM_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Oilseed rape
    **{(crop, idx): val
       for crop in ["winter-oilseed-rape", "spring-oilseed-rape"]
       for idx, val in [(0, 95), (1, 65), (2, 45), (3, 0), (4, 0)]},

    # Linseed
    ("linseed", 0): 75,
    ("linseed", 1): 50,
    ("linseed", 2): 35,
    ("linseed", 3): 0,
    ("linseed", 4): 0,

    # Peas and beans
    **{(crop, idx): val
       for crop in ["peas", "field-beans"]
       for idx, val in [(0, 75), (1, 50), (2, 35), (3, 0), (4, 0)]},

    # Sugar beet
    ("sugar-beet", 0): 175,
    ("sugar-beet", 1): 130,
    ("sugar-beet", 2): 95,
    ("sugar-beet", 3): 0,
    ("sugar-beet", 4): 0,

    # Forage maize
    ("forage-maize", 0): 175,
    ("forage-maize", 1): 130,
    ("forage-maize", 2): 95,
    ("forage-maize", 3): 0,
    ("forage-maize", 4): 0,

    # Potatoes
    ("potatoes-maincrop", 0): 300,
    ("potatoes-maincrop", 1): 240,
    ("potatoes-maincrop", 2): 180,
    ("potatoes-maincrop", 3): 0,
    ("potatoes-maincrop", 4): 0,

    ("potatoes-early", 0): 250,
    ("potatoes-early", 1): 200,
    ("potatoes-early", 2): 150,
    ("potatoes-early", 3): 0,
    ("potatoes-early", 4): 0,

    ("potatoes-seed", 0): 250,
    ("potatoes-seed", 1): 200,
    ("potatoes-seed", 2): 150,
    ("potatoes-seed", 3): 0,
    ("potatoes-seed", 4): 0,

    # Grass (silage - high offtake)
    ("grass-silage", 0): 150,
    ("grass-silage", 1): 100,
    ("grass-silage", 2): 60,
    ("grass-silage", 3): 0,
    ("grass-silage", 4): 0,

    # Grass (hay)
    ("grass-hay", 0): 120,
    ("grass-hay", 1): 80,
    ("grass-hay", 2): 50,
    ("grass-hay", 3): 0,
    ("grass-hay", 4): 0,

    # Grass (grazed - low offtake, recycling via dung)
    ("grass-grazed", 0): 60,
    ("grass-grazed", 1): 30,
    ("grass-grazed", 2): 0,
    ("grass-grazed", 3): 0,
    ("grass-grazed", 4): 0,

    # Grass (grazed + 1 cut)
    ("grass-grazed-one-cut", 0): 100,
    ("grass-grazed-one-cut", 1): 60,
    ("grass-grazed-one-cut", 2): 30,
    ("grass-grazed-one-cut", 3): 0,
    ("grass-grazed-one-cut", 4): 0,
}

# Vegetable crop potassium recommendations (Section 6).
# (crop_value, k_index) -> kg K2O/ha; k_index clamped to 0-4.
# The index-2 value represents the lower half of K Index 2 (2-, soil K 121-180 mg/l).
POTASSIUM_VEG_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Asparagus (establishment) — 250/225/200/150/125 (no 2+/2- split)
    ("veg-asparagus-est", 0): 250, ("veg-asparagus-est", 1): 225,
    ("veg-asparagus-est", 2): 200, ("veg-asparagus-est", 3): 150,
    ("veg-asparagus-est", 4): 125,

    # Asparagus (subsequent) — 100/50/50/50/0
    ("veg-asparagus", 0): 100, ("veg-asparagus", 1): 50,
    ("veg-asparagus", 2): 50,  ("veg-asparagus", 3): 50,
    ("veg-asparagus", 4): 0,

    # Brussels sprouts + all cabbages/collards — 300/250/200/60/0
    **{(crop, idx): val
       for crop in [
           "veg-brussels-sprouts",
           "veg-cabbage-storage", "veg-cabbage-head-pre-dec", "veg-cabbage-head-post-dec",
           "veg-collards-pre-dec", "veg-collards-post-dec",
       ]
       for idx, val in [(0, 300), (1, 250), (2, 200), (3, 60), (4, 0)]},

    # Cauliflower (summer + winter seedbed + topdress) + Calabrese — 275/225/175/35/0
    **{(crop, idx): val
       for crop in [
           "veg-cauliflower-summer", "veg-cauliflower-winter-seedbed",
           "veg-cauliflower-winter-topdress", "veg-calabrese",
       ]
       for idx, val in [(0, 275), (1, 225), (2, 175), (3, 35), (4, 0)]},

    # Celery — 450/400/350/210/50
    ("veg-celery-seedbed", 0): 450, ("veg-celery-seedbed", 1): 400,
    ("veg-celery-seedbed", 2): 350, ("veg-celery-seedbed", 3): 210,
    ("veg-celery-seedbed", 4): 50,

    # Peas (market) — 190/140/90/0/0
    ("veg-peas-market", 0): 190, ("veg-peas-market", 1): 140,
    ("veg-peas-market", 2): 90,  ("veg-peas-market", 3): 0,
    ("veg-peas-market", 4): 0,

    # Broad beans + dwarf/runner — 200/150/100/0/0
    **{(crop, idx): val
       for crop in ["veg-beans-broad", "veg-beans-dwarf"]
       for idx, val in [(0, 200), (1, 150), (2, 100), (3, 0), (4, 0)]},

    # Radish, sweetcorn — 250/200/150/0/0
    **{(crop, idx): val
       for crop in ["veg-radish", "veg-sweetcorn"]
       for idx, val in [(0, 250), (1, 200), (2, 150), (3, 0), (4, 0)]},

    # Lettuce (all) + rocket — 250/200/150/0/0
    **{(crop, idx): val
       for crop in ["veg-lettuce-whole", "veg-lettuce-baby", "veg-rocket"]
       for idx, val in [(0, 250), (1, 200), (2, 150), (3, 0), (4, 0)]},

    # Bulb/salad onions + leeks — 275/225/175/35/0
    **{(crop, idx): val
       for crop in ["veg-onions-bulb", "veg-onions-salad", "veg-leeks"]
       for idx, val in [(0, 275), (1, 225), (2, 175), (3, 35), (4, 0)]},

    # Beetroot, swedes, turnips/parsnips — 300/250/200/60/0
    **{(crop, idx): val
       for crop in ["veg-beetroot", "veg-swedes", "veg-turnips-parsnips"]
       for idx, val in [(0, 300), (1, 250), (2, 200), (3, 60), (4, 0)]},

    # Carrots — 275/225/175/35/0
    ("veg-carrots", 0): 275, ("veg-carrots", 1): 225,
    ("veg-carrots", 2): 175, ("veg-carrots", 3): 35,
    ("veg-carrots", 4): 0,

    # Bulbs — 300/250/200/60/0
    ("veg-bulbs", 0): 300, ("veg-bulbs", 1): 250,
    ("veg-bulbs", 2): 200, ("veg-bulbs", 3): 60,
    ("veg-bulbs", 4): 0,

    # Coriander — 315/265/215/75/0
    ("veg-coriander", 0): 315, ("veg-coriander", 1): 265,
    ("veg-coriander", 2): 215, ("veg-coriander", 3): 75,
    ("veg-coriander", 4): 0,

    # Mint (establishment) — 200/150/100/0/0
    ("veg-mint-est", 0): 200, ("veg-mint-est", 1): 150,
    ("veg-mint-est", 2): 100, ("veg-mint-est", 3): 0,
    ("veg-mint-est", 4): 0,

    # Mint (subsequent) — 280/230/180/40/0
    ("veg-mint", 0): 280, ("veg-mint", 1): 230,
    ("veg-mint", 2): 180, ("veg-mint", 3): 40,
    ("veg-mint", 4): 0,

    # Courgettes — 250/200/150/0/0
    ("veg-courgettes-seedbed", 0): 250, ("veg-courgettes-seedbed", 1): 200,
    ("veg-courgettes-seedbed", 2): 150, ("veg-courgettes-seedbed", 3): 0,
    ("veg-courgettes-seedbed", 4): 0,
}

# Upper-half K Index 2 values (2+, soil K 181-240 mg/l).
# Crops without a documented 2-/2+ split are omitted (use 2- value for both).
POTASSIUM_VEG_K2_UPPER: dict[str, float] = {
    "veg-brussels-sprouts":           150,
    "veg-cabbage-storage":            150,
    "veg-cabbage-head-pre-dec":       150,
    "veg-cabbage-head-post-dec":      150,
    "veg-collards-pre-dec":           150,
    "veg-collards-post-dec":          150,
    "veg-cauliflower-summer":         125,
    "veg-cauliflower-winter-seedbed": 125,
    "veg-cauliflower-winter-topdress": 125,
    "veg-calabrese":                  125,
    "veg-celery-seedbed":             300,
    "veg-peas-market":                 40,
    "veg-beans-broad":                 50,
    "veg-beans-dwarf":                 50,
    "veg-radish":                     100,
    "veg-sweetcorn":                  100,
    "veg-lettuce-whole":              100,
    "veg-lettuce-baby":               100,
    "veg-rocket":                     100,
    "veg-onions-bulb":                125,
    "veg-onions-salad":               125,
    "veg-leeks":                      125,
    "veg-beetroot":                   150,
    "veg-swedes":                     150,
    "veg-turnips-parsnips":           150,
    "veg-carrots":                    125,
    "veg-bulbs":                      150,
    "veg-coriander":                  165,
    "veg-mint-est":                    50,
    "veg-mint":                       130,
    "veg-courgettes-seedbed":         100,
}
