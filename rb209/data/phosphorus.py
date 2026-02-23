"""Phosphorus (P2O5) recommendation tables.

Values are kg P2O5/ha, keyed by (crop, p_index).
P index ranges from 0 (deficient) to 4+ (high).
Based on RB209 9th edition.
"""

# (crop_value, p_index) -> kg P2O5/ha
PHOSPHORUS_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Cereals (wheat, barley, oats, rye)
    **{(crop, idx): val
       for crop in [
           "winter-wheat-feed", "winter-wheat-milling", "spring-wheat",
           "winter-barley", "spring-barley",
           "winter-oats", "spring-oats", "winter-rye",
       ]
       for idx, val in [(0, 110), (1, 85), (2, 60), (3, 30), (4, 0)]},

    # Oilseed rape
    **{(crop, idx): val
       for crop in ["winter-oilseed-rape", "spring-oilseed-rape"]
       for idx, val in [(0, 100), (1, 75), (2, 50), (3, 25), (4, 0)]},

    # Linseed
    ("linseed", 0): 80,
    ("linseed", 1): 55,
    ("linseed", 2): 35,
    ("linseed", 3): 15,
    ("linseed", 4): 0,

    # Peas and beans
    **{(crop, idx): val
       for crop in ["peas", "field-beans"]
       for idx, val in [(0, 80), (1, 55), (2, 30), (3, 0), (4, 0)]},

    # Sugar beet
    ("sugar-beet", 0): 120,
    ("sugar-beet", 1): 95,
    ("sugar-beet", 2): 65,
    ("sugar-beet", 3): 35,
    ("sugar-beet", 4): 0,

    # Forage maize
    ("forage-maize", 0): 120,
    ("forage-maize", 1): 95,
    ("forage-maize", 2): 65,
    ("forage-maize", 3): 35,
    ("forage-maize", 4): 0,

    # Potatoes
    ("potatoes-maincrop", 0): 250,
    ("potatoes-maincrop", 1): 200,
    ("potatoes-maincrop", 2): 150,
    ("potatoes-maincrop", 3): 50,
    ("potatoes-maincrop", 4): 0,

    ("potatoes-early", 0): 200,
    ("potatoes-early", 1): 150,
    ("potatoes-early", 2): 100,
    ("potatoes-early", 3): 35,
    ("potatoes-early", 4): 0,

    ("potatoes-seed", 0): 200,
    ("potatoes-seed", 1): 150,
    ("potatoes-seed", 2): 100,
    ("potatoes-seed", 3): 35,
    ("potatoes-seed", 4): 0,

    # Grass (cut - silage and hay)
    **{(crop, idx): val
       for crop in ["grass-silage", "grass-hay"]
       for idx, val in [(0, 120), (1, 80), (2, 50), (3, 20), (4, 0)]},

    # Grass (grazed)
    ("grass-grazed", 0): 80,
    ("grass-grazed", 1): 50,
    ("grass-grazed", 2): 30,
    ("grass-grazed", 3): 0,
    ("grass-grazed", 4): 0,

    # Grass (grazed + 1 cut)
    ("grass-grazed-one-cut", 0): 100,
    ("grass-grazed-one-cut", 1): 65,
    ("grass-grazed-one-cut", 2): 40,
    ("grass-grazed-one-cut", 3): 10,
    ("grass-grazed-one-cut", 4): 0,
}

# Vegetable crop phosphorus recommendations (Section 6).
# (crop_value, p_index) -> kg P2O5/ha; p_index clamped to 0-4.
PHOSPHORUS_VEG_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Asparagus (establishment)
    ("veg-asparagus-est", 0): 175, ("veg-asparagus-est", 1): 150,
    ("veg-asparagus-est", 2): 125, ("veg-asparagus-est", 3): 100,
    ("veg-asparagus-est", 4): 75,

    # Asparagus (subsequent)
    ("veg-asparagus", 0): 75,  ("veg-asparagus", 1): 75,
    ("veg-asparagus", 2): 50,  ("veg-asparagus", 3): 50,
    ("veg-asparagus", 4): 25,

    # Brassicas — 200/150/100/50/0
    **{(crop, idx): val
       for crop in [
           "veg-brussels-sprouts",
           "veg-cabbage-storage", "veg-cabbage-head-pre-dec", "veg-cabbage-head-post-dec",
           "veg-collards-pre-dec", "veg-collards-post-dec",
           "veg-cauliflower-summer", "veg-cauliflower-winter-seedbed",
           "veg-cauliflower-winter-topdress", "veg-calabrese",
       ]
       for idx, val in [(0, 200), (1, 150), (2, 100), (3, 50), (4, 0)]},

    # Celery — 250/200/150/100/50
    ("veg-celery-seedbed", 0): 250, ("veg-celery-seedbed", 1): 200,
    ("veg-celery-seedbed", 2): 150, ("veg-celery-seedbed", 3): 100,
    ("veg-celery-seedbed", 4): 50,

    # Peas (market) — 185/135/85/35/0
    ("veg-peas-market", 0): 185, ("veg-peas-market", 1): 135,
    ("veg-peas-market", 2): 85,  ("veg-peas-market", 3): 35,
    ("veg-peas-market", 4): 0,

    # Broad beans, dwarf/runner beans — 200/150/100/50/0
    **{(crop, idx): val
       for crop in ["veg-beans-broad", "veg-beans-dwarf"]
       for idx, val in [(0, 200), (1, 150), (2, 100), (3, 50), (4, 0)]},

    # Radish, sweetcorn — 175/125/75/25/0
    **{(crop, idx): val
       for crop in ["veg-radish", "veg-sweetcorn"]
       for idx, val in [(0, 175), (1, 125), (2, 75), (3, 25), (4, 0)]},

    # Lettuce (all types), rocket — 250/200/150/100/0
    **{(crop, idx): val
       for crop in ["veg-lettuce-whole", "veg-lettuce-baby", "veg-rocket"]
       for idx, val in [(0, 250), (1, 200), (2, 150), (3, 100), (4, 0)]},

    # Bulb/salad onions, leeks — 200/150/100/50/0
    **{(crop, idx): val
       for crop in ["veg-onions-bulb", "veg-onions-salad", "veg-leeks"]
       for idx, val in [(0, 200), (1, 150), (2, 100), (3, 50), (4, 0)]},

    # Beetroot, swedes, turnips/parsnips, carrots, bulbs — 200/150/100/50/0
    **{(crop, idx): val
       for crop in [
           "veg-beetroot", "veg-swedes", "veg-turnips-parsnips",
           "veg-carrots", "veg-bulbs",
       ]
       for idx, val in [(0, 200), (1, 150), (2, 100), (3, 50), (4, 0)]},

    # Coriander, mint (est + sub) — 175/125/75/25/0
    **{(crop, idx): val
       for crop in ["veg-coriander", "veg-mint-est", "veg-mint"]
       for idx, val in [(0, 175), (1, 125), (2, 75), (3, 25), (4, 0)]},

    # Courgettes — 175/125/75/25/0
    ("veg-courgettes-seedbed", 0): 175, ("veg-courgettes-seedbed", 1): 125,
    ("veg-courgettes-seedbed", 2): 75,  ("veg-courgettes-seedbed", 3): 25,
    ("veg-courgettes-seedbed", 4): 0,
}
