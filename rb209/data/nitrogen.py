"""Nitrogen (N) recommendation tables.

Values are kg N/ha, keyed by (crop, sns_index).
SNS index ranges from 0 (low soil N) to 6 (very high soil N).
Based on RB209 9th edition recommendation tables.
"""

# (crop_value, sns_index) -> kg N/ha
NITROGEN_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Winter Wheat (feed) - RB209 Section 4
    ("winter-wheat-feed", 0): 220,
    ("winter-wheat-feed", 1): 180,
    ("winter-wheat-feed", 2): 150,
    ("winter-wheat-feed", 3): 120,
    ("winter-wheat-feed", 4): 120,
    ("winter-wheat-feed", 5): 40,
    ("winter-wheat-feed", 6): 0,

    # Winter Wheat (milling) - feed + 40 kg/ha
    ("winter-wheat-milling", 0): 260,
    ("winter-wheat-milling", 1): 220,
    ("winter-wheat-milling", 2): 190,
    ("winter-wheat-milling", 3): 160,
    ("winter-wheat-milling", 4): 120,
    ("winter-wheat-milling", 5): 80,
    ("winter-wheat-milling", 6): 40,

    # Spring Wheat
    ("spring-wheat", 0): 160,
    ("spring-wheat", 1): 130,
    ("spring-wheat", 2): 100,
    ("spring-wheat", 3): 80,
    ("spring-wheat", 4): 50,
    ("spring-wheat", 5): 20,
    ("spring-wheat", 6): 0,

    # Winter Barley
    ("winter-barley", 0): 180,
    ("winter-barley", 1): 155,
    ("winter-barley", 2): 130,
    ("winter-barley", 3): 100,
    ("winter-barley", 4): 65,
    ("winter-barley", 5): 30,
    ("winter-barley", 6): 0,

    # Spring Barley
    ("spring-barley", 0): 160,
    ("spring-barley", 1): 120,
    ("spring-barley", 2): 100,
    ("spring-barley", 3): 80,
    ("spring-barley", 4): 50,
    ("spring-barley", 5): 20,
    ("spring-barley", 6): 0,

    # Winter Oats
    ("winter-oats", 0): 170,
    ("winter-oats", 1): 140,
    ("winter-oats", 2): 110,
    ("winter-oats", 3): 80,
    ("winter-oats", 4): 50,
    ("winter-oats", 5): 20,
    ("winter-oats", 6): 0,

    # Spring Oats
    ("spring-oats", 0): 130,
    ("spring-oats", 1): 100,
    ("spring-oats", 2): 80,
    ("spring-oats", 3): 60,
    ("spring-oats", 4): 30,
    ("spring-oats", 5): 0,
    ("spring-oats", 6): 0,

    # Winter Rye
    ("winter-rye", 0): 170,
    ("winter-rye", 1): 140,
    ("winter-rye", 2): 110,
    ("winter-rye", 3): 80,
    ("winter-rye", 4): 50,
    ("winter-rye", 5): 20,
    ("winter-rye", 6): 0,

    # Winter Oilseed Rape
    ("winter-oilseed-rape", 0): 220,
    ("winter-oilseed-rape", 1): 190,
    ("winter-oilseed-rape", 2): 160,
    ("winter-oilseed-rape", 3): 130,
    ("winter-oilseed-rape", 4): 80,
    ("winter-oilseed-rape", 5): 30,
    ("winter-oilseed-rape", 6): 0,

    # Spring Oilseed Rape
    ("spring-oilseed-rape", 0): 150,
    ("spring-oilseed-rape", 1): 120,
    ("spring-oilseed-rape", 2): 100,
    ("spring-oilseed-rape", 3): 80,
    ("spring-oilseed-rape", 4): 50,
    ("spring-oilseed-rape", 5): 20,
    ("spring-oilseed-rape", 6): 0,

    # Linseed
    ("linseed", 0): 100,
    ("linseed", 1): 70,
    ("linseed", 2): 40,
    ("linseed", 3): 20,
    ("linseed", 4): 0,
    ("linseed", 5): 0,
    ("linseed", 6): 0,

    # Peas (N-fixing, no N required)
    ("peas", 0): 0,
    ("peas", 1): 0,
    ("peas", 2): 0,
    ("peas", 3): 0,
    ("peas", 4): 0,
    ("peas", 5): 0,
    ("peas", 6): 0,

    # Field Beans (N-fixing, no N required)
    ("field-beans", 0): 0,
    ("field-beans", 1): 0,
    ("field-beans", 2): 0,
    ("field-beans", 3): 0,
    ("field-beans", 4): 0,
    ("field-beans", 5): 0,
    ("field-beans", 6): 0,

    # Sugar Beet
    ("sugar-beet", 0): 120,
    ("sugar-beet", 1): 120,
    ("sugar-beet", 2): 80,
    ("sugar-beet", 3): 50,
    ("sugar-beet", 4): 0,
    ("sugar-beet", 5): 0,
    ("sugar-beet", 6): 0,

    # Forage Maize
    ("forage-maize", 0): 150,
    ("forage-maize", 1): 120,
    ("forage-maize", 2): 80,
    ("forage-maize", 3): 50,
    ("forage-maize", 4): 0,
    ("forage-maize", 5): 0,
    ("forage-maize", 6): 0,

    # Potatoes (maincrop)
    ("potatoes-maincrop", 0): 270,
    ("potatoes-maincrop", 1): 220,
    ("potatoes-maincrop", 2): 180,
    ("potatoes-maincrop", 3): 140,
    ("potatoes-maincrop", 4): 100,
    ("potatoes-maincrop", 5): 60,
    ("potatoes-maincrop", 6): 0,

    # Potatoes (early)
    ("potatoes-early", 0): 200,
    ("potatoes-early", 1): 160,
    ("potatoes-early", 2): 130,
    ("potatoes-early", 3): 100,
    ("potatoes-early", 4): 60,
    ("potatoes-early", 5): 30,
    ("potatoes-early", 6): 0,

    # Potatoes (seed)
    ("potatoes-seed", 0): 160,
    ("potatoes-seed", 1): 130,
    ("potatoes-seed", 2): 100,
    ("potatoes-seed", 3): 80,
    ("potatoes-seed", 4): 50,
    ("potatoes-seed", 5): 20,
    ("potatoes-seed", 6): 0,

    # Grass (grazed only) - annual total
    ("grass-grazed", 0): 250,
    ("grass-grazed", 1): 220,
    ("grass-grazed", 2): 180,
    ("grass-grazed", 3): 150,
    ("grass-grazed", 4): 100,
    ("grass-grazed", 5): 60,
    ("grass-grazed", 6): 0,

    # Grass (silage, multi-cut) - annual total
    ("grass-silage", 0): 320,
    ("grass-silage", 1): 280,
    ("grass-silage", 2): 240,
    ("grass-silage", 3): 200,
    ("grass-silage", 4): 160,
    ("grass-silage", 5): 100,
    ("grass-silage", 6): 40,

    # Grass (hay)
    ("grass-hay", 0): 200,
    ("grass-hay", 1): 170,
    ("grass-hay", 2): 140,
    ("grass-hay", 3): 110,
    ("grass-hay", 4): 70,
    ("grass-hay", 5): 30,
    ("grass-hay", 6): 0,

    # Grass (grazed + 1 silage cut) - annual total
    ("grass-grazed-one-cut", 0): 280,
    ("grass-grazed-one-cut", 1): 240,
    ("grass-grazed-one-cut", 2): 200,
    ("grass-grazed-one-cut", 3): 170,
    ("grass-grazed-one-cut", 4): 130,
    ("grass-grazed-one-cut", 5): 80,
    ("grass-grazed-one-cut", 6): 20,
}

# Soil-type-specific nitrogen recommendations.
# (crop_value, sns_index, soil_type) -> kg N/ha
# Where a crop has soil-specific data, this table takes precedence
# over the generic NITROGEN_RECOMMENDATIONS when soil_type is given.

# NVZ whole-farm N-max limits by crop group (kg N/ha).
# Source: Defra Nitrate Pollution Prevention Regulations 2015, Schedule 8
# (reproduced in ref/NVZ max limits.md).
NVZ_NMAX: dict[str, float] = {
    # Wheat — autumn/early winter-sown base: 220; milling adds 40 → 260
    "winter-wheat-feed": 220,
    "winter-wheat-milling": 260,
    # Spring-sown wheat: 180
    "spring-wheat": 180,
    # Barley
    "winter-barley": 180,
    "spring-barley": 150,
    # Other cereals (not listed in Schedule 8; use wheat/barley analogues)
    "winter-oats": 220,
    "spring-oats": 220,
    "winter-rye": 220,
    # Oilseed rape
    "winter-oilseed-rape": 250,
    "spring-oilseed-rape": 250,
    # Grass — base 300; multi-cut silage (≥3 cuts) qualifies for +40 → 340
    "grass-grazed": 300,
    "grass-silage": 340,
    "grass-hay": 300,
    "grass-grazed-one-cut": 300,
    # Other arable crops
    "sugar-beet": 120,
    "forage-maize": 150,
    "field-beans": 0,
    "peas": 0,
    # Potatoes — all types: 270
    "potatoes-maincrop": 270,
    "potatoes-early": 270,
    "potatoes-seed": 270,
    # Vegetables — Group 1: asparagus, carrots, radishes, swedes (180 kg/ha)
    "veg-asparagus": 180,
    "veg-asparagus-est": 180,
    "veg-carrots": 180,
    "veg-radish": 180,
    "veg-swedes": 180,
    # Vegetables — Group 2: celery, courgettes, dwarf/runner beans, lettuce,
    #   onions, parsnips, runner beans, sweetcorn, turnips (280 kg/ha)
    "veg-celery-seedbed": 280,
    "veg-courgettes-seedbed": 280,
    "veg-courgettes-topdress": 280,
    "veg-beans-dwarf": 280,
    "veg-lettuce-whole": 280,
    "veg-lettuce-baby": 280,
    "veg-onions-bulb": 280,
    "veg-onions-salad": 280,
    "veg-turnips-parsnips": 280,
    "veg-sweetcorn": 280,
    # Vegetables — Group 3: beetroot, brussels sprouts, cabbage, calabrese,
    #   cauliflower, leeks (370 kg/ha)
    "veg-beetroot": 370,
    "veg-brussels-sprouts": 370,
    "veg-cabbage-storage": 370,
    "veg-cabbage-head-pre-dec": 370,
    "veg-cabbage-head-post-dec": 370,
    "veg-collards-pre-dec": 370,
    "veg-collards-post-dec": 370,
    "veg-calabrese": 370,
    "veg-cauliflower-summer": 370,
    "veg-cauliflower-winter-seedbed": 370,
    "veg-cauliflower-winter-topdress": 370,
    "veg-leeks": 370,
    # N-fixing vegetable crops — no manufactured N permitted
    "veg-peas-market": 0,
    "veg-beans-broad": 0,
}

NITROGEN_VEG_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    # Table 6.11 — Asparagus (establishment year)
    ("veg-asparagus-est", 0): 150, ("veg-asparagus-est", 1): 150,
    ("veg-asparagus-est", 2): 150, ("veg-asparagus-est", 3): 90,
    ("veg-asparagus-est", 4): 20,  ("veg-asparagus-est", 5): 0,
    ("veg-asparagus-est", 6): 0,

    # Table 6.11 — Asparagus (subsequent years, year 2 benchmark)
    ("veg-asparagus", 0): 120, ("veg-asparagus", 1): 120,
    ("veg-asparagus", 2): 120, ("veg-asparagus", 3): 120,
    ("veg-asparagus", 4): 120, ("veg-asparagus", 5): 120,
    ("veg-asparagus", 6): 120,

    # Table 6.12 — Brussels Sprouts
    ("veg-brussels-sprouts", 0): 330, ("veg-brussels-sprouts", 1): 300,
    ("veg-brussels-sprouts", 2): 270, ("veg-brussels-sprouts", 3): 230,
    ("veg-brussels-sprouts", 4): 180, ("veg-brussels-sprouts", 5): 80,
    ("veg-brussels-sprouts", 6): 0,

    # Table 6.12 — Storage Cabbage
    ("veg-cabbage-storage", 0): 340, ("veg-cabbage-storage", 1): 310,
    ("veg-cabbage-storage", 2): 280, ("veg-cabbage-storage", 3): 240,
    ("veg-cabbage-storage", 4): 190, ("veg-cabbage-storage", 5): 90,
    ("veg-cabbage-storage", 6): 0,

    # Table 6.12 — Head Cabbage (harvest pre-31 December)
    ("veg-cabbage-head-pre-dec", 0): 325, ("veg-cabbage-head-pre-dec", 1): 290,
    ("veg-cabbage-head-pre-dec", 2): 260, ("veg-cabbage-head-pre-dec", 3): 220,
    ("veg-cabbage-head-pre-dec", 4): 170, ("veg-cabbage-head-pre-dec", 5): 70,
    ("veg-cabbage-head-pre-dec", 6): 0,

    # Table 6.12 — Head Cabbage (harvest post-31 December)
    ("veg-cabbage-head-post-dec", 0): 240, ("veg-cabbage-head-post-dec", 1): 210,
    ("veg-cabbage-head-post-dec", 2): 180, ("veg-cabbage-head-post-dec", 3): 140,
    ("veg-cabbage-head-post-dec", 4): 90,  ("veg-cabbage-head-post-dec", 5): 0,
    ("veg-cabbage-head-post-dec", 6): 0,

    # Table 6.12 — Collards (harvest pre-31 December)
    ("veg-collards-pre-dec", 0): 210, ("veg-collards-pre-dec", 1): 190,
    ("veg-collards-pre-dec", 2): 180, ("veg-collards-pre-dec", 3): 160,
    ("veg-collards-pre-dec", 4): 140, ("veg-collards-pre-dec", 5): 90,
    ("veg-collards-pre-dec", 6): 0,

    # Table 6.12 — Collards (harvest post-31 December)
    ("veg-collards-post-dec", 0): 310, ("veg-collards-post-dec", 1): 290,
    ("veg-collards-post-dec", 2): 270, ("veg-collards-post-dec", 3): 240,
    ("veg-collards-post-dec", 4): 210, ("veg-collards-post-dec", 5): 140,
    ("veg-collards-post-dec", 6): 90,

    # Table 6.14 — Cauliflower (summer/autumn)
    ("veg-cauliflower-summer", 0): 290, ("veg-cauliflower-summer", 1): 260,
    ("veg-cauliflower-summer", 2): 235, ("veg-cauliflower-summer", 3): 210,
    ("veg-cauliflower-summer", 4): 170, ("veg-cauliflower-summer", 5): 80,
    ("veg-cauliflower-summer", 6): 0,

    # Table 6.14 — Cauliflower (winter hardy / Roscoff) — seedbed dressing
    ("veg-cauliflower-winter-seedbed", 0): 100, ("veg-cauliflower-winter-seedbed", 1): 100,
    ("veg-cauliflower-winter-seedbed", 2): 100, ("veg-cauliflower-winter-seedbed", 3): 100,
    ("veg-cauliflower-winter-seedbed", 4): 60,  ("veg-cauliflower-winter-seedbed", 5): 0,
    ("veg-cauliflower-winter-seedbed", 6): 0,

    # Table 6.14 — Cauliflower (winter hardy / Roscoff) — top dressing
    ("veg-cauliflower-winter-topdress", 0): 190, ("veg-cauliflower-winter-topdress", 1): 160,
    ("veg-cauliflower-winter-topdress", 2): 135, ("veg-cauliflower-winter-topdress", 3): 110,
    ("veg-cauliflower-winter-topdress", 4): 100, ("veg-cauliflower-winter-topdress", 5): 80,
    ("veg-cauliflower-winter-topdress", 6): 0,

    # Table 6.14 — Calabrese
    ("veg-calabrese", 0): 235, ("veg-calabrese", 1): 200,
    ("veg-calabrese", 2): 165, ("veg-calabrese", 3): 135,
    ("veg-calabrese", 4): 80,  ("veg-calabrese", 5): 0,
    ("veg-calabrese", 6): 0,

    # Table 6.16 — Self-blanching Celery (seedbed N)
    ("veg-celery-seedbed", 0): 75, ("veg-celery-seedbed", 1): 75,
    ("veg-celery-seedbed", 2): 75, ("veg-celery-seedbed", 3): 75,
    ("veg-celery-seedbed", 4): 0,  ("veg-celery-seedbed", 5): 0,
    ("veg-celery-seedbed", 6): 0,

    # Table 6.17a — Peas (market pick) — N-fixing, no fertiliser N
    **{("veg-peas-market", i): 0 for i in range(7)},

    # Table 6.17b — Broad Beans — N-fixing, no fertiliser N
    **{("veg-beans-broad", i): 0 for i in range(7)},

    # Table 6.17b — Dwarf/Runner Beans (seedbed dressing)
    ("veg-beans-dwarf", 0): 180, ("veg-beans-dwarf", 1): 150,
    ("veg-beans-dwarf", 2): 120, ("veg-beans-dwarf", 3): 80,
    ("veg-beans-dwarf", 4): 30,  ("veg-beans-dwarf", 5): 0,
    ("veg-beans-dwarf", 6): 0,

    # Table 6.18 — Radish
    ("veg-radish", 0): 100, ("veg-radish", 1): 90,
    ("veg-radish", 2): 80,  ("veg-radish", 3): 65,
    ("veg-radish", 4): 50,  ("veg-radish", 5): 20,
    ("veg-radish", 6): 0,

    # Table 6.18 — Sweetcorn
    ("veg-sweetcorn", 0): 220, ("veg-sweetcorn", 1): 175,
    ("veg-sweetcorn", 2): 125, ("veg-sweetcorn", 3): 75,
    ("veg-sweetcorn", 4): 0,   ("veg-sweetcorn", 5): 0,
    ("veg-sweetcorn", 6): 0,

    # Table 6.19 — Lettuce (whole head — Crisp/Escarole)
    ("veg-lettuce-whole", 0): 200, ("veg-lettuce-whole", 1): 180,
    ("veg-lettuce-whole", 2): 160, ("veg-lettuce-whole", 3): 150,
    ("veg-lettuce-whole", 4): 125, ("veg-lettuce-whole", 5): 75,
    ("veg-lettuce-whole", 6): 30,

    # Table 6.19 — Lettuce (baby leaf)
    ("veg-lettuce-baby", 0): 60, ("veg-lettuce-baby", 1): 50,
    ("veg-lettuce-baby", 2): 40, ("veg-lettuce-baby", 3): 30,
    ("veg-lettuce-baby", 4): 10, ("veg-lettuce-baby", 5): 0,
    ("veg-lettuce-baby", 6): 0,

    # Table 6.19 — Wild Rocket
    ("veg-rocket", 0): 125, ("veg-rocket", 1): 115,
    ("veg-rocket", 2): 100, ("veg-rocket", 3): 90,
    ("veg-rocket", 4): 75,  ("veg-rocket", 5): 40,
    ("veg-rocket", 6): 0,

    # Table 6.20 — Bulb Onions
    ("veg-onions-bulb", 0): 160, ("veg-onions-bulb", 1): 130,
    ("veg-onions-bulb", 2): 110, ("veg-onions-bulb", 3): 90,
    ("veg-onions-bulb", 4): 60,  ("veg-onions-bulb", 5): 0,
    ("veg-onions-bulb", 6): 0,

    # Table 6.20 — Salad Onions
    ("veg-onions-salad", 0): 130, ("veg-onions-salad", 1): 120,
    ("veg-onions-salad", 2): 110, ("veg-onions-salad", 3): 100,
    ("veg-onions-salad", 4): 80,  ("veg-onions-salad", 5): 50,
    ("veg-onions-salad", 6): 20,

    # Table 6.20 — Leeks
    ("veg-leeks", 0): 200, ("veg-leeks", 1): 190,
    ("veg-leeks", 2): 170, ("veg-leeks", 3): 160,
    ("veg-leeks", 4): 130, ("veg-leeks", 5): 80,
    ("veg-leeks", 6): 40,

    # Table 6.22 — Beetroot
    ("veg-beetroot", 0): 290, ("veg-beetroot", 1): 260,
    ("veg-beetroot", 2): 240, ("veg-beetroot", 3): 220,
    ("veg-beetroot", 4): 190, ("veg-beetroot", 5): 120,
    ("veg-beetroot", 6): 60,

    # Table 6.22 — Swedes
    ("veg-swedes", 0): 135, ("veg-swedes", 1): 100,
    ("veg-swedes", 2): 70,  ("veg-swedes", 3): 30,
    ("veg-swedes", 4): 0,   ("veg-swedes", 5): 0,
    ("veg-swedes", 6): 0,

    # Table 6.22 — Turnips and Parsnips
    ("veg-turnips-parsnips", 0): 170, ("veg-turnips-parsnips", 1): 130,
    ("veg-turnips-parsnips", 2): 100, ("veg-turnips-parsnips", 3): 70,
    ("veg-turnips-parsnips", 4): 20,  ("veg-turnips-parsnips", 5): 0,
    ("veg-turnips-parsnips", 6): 0,

    # Table 6.22 — Carrots
    ("veg-carrots", 0): 100, ("veg-carrots", 1): 70,
    ("veg-carrots", 2): 40,  ("veg-carrots", 3): 0,
    ("veg-carrots", 4): 0,   ("veg-carrots", 5): 0,
    ("veg-carrots", 6): 0,

    # Table 6.24 — Bulbs and Bulb Flowers
    ("veg-bulbs", 0): 125, ("veg-bulbs", 1): 100,
    ("veg-bulbs", 2): 50,  ("veg-bulbs", 3): 0,
    ("veg-bulbs", 4): 0,   ("veg-bulbs", 5): 0,
    ("veg-bulbs", 6): 0,

    # Table 6.25 — Coriander
    ("veg-coriander", 0): 140, ("veg-coriander", 1): 125,
    ("veg-coriander", 2): 115, ("veg-coriander", 3): 105,
    ("veg-coriander", 4): 90,  ("veg-coriander", 5): 55,
    ("veg-coriander", 6): 30,

    # Table 6.25 — Mint (establishment year)
    ("veg-mint-est", 0): 180, ("veg-mint-est", 1): 170,
    ("veg-mint-est", 2): 160, ("veg-mint-est", 3): 150,
    ("veg-mint-est", 4): 130, ("veg-mint-est", 5): 100,
    ("veg-mint-est", 6): 70,

    # Table 6.25 — Mint (subsequent years)
    ("veg-mint", 0): 180, ("veg-mint", 1): 170,
    ("veg-mint", 2): 160, ("veg-mint", 3): 150,
    ("veg-mint", 4): 130, ("veg-mint", 5): 100,
    ("veg-mint", 6): 70,

    # Table 6.26 — Courgettes (seedbed dressing)
    ("veg-courgettes-seedbed", 0): 100, ("veg-courgettes-seedbed", 1): 100,
    ("veg-courgettes-seedbed", 2): 100, ("veg-courgettes-seedbed", 3): 40,
    ("veg-courgettes-seedbed", 4): 0,   ("veg-courgettes-seedbed", 5): 0,
    ("veg-courgettes-seedbed", 6): 0,

    # Table 6.26 — Courgettes (top dressing, up to 75 kg N/ha)
    # Top dressing applied after establishment at SNS Index 0–3.
    ("veg-courgettes-topdress", 0): 75, ("veg-courgettes-topdress", 1): 75,
    ("veg-courgettes-topdress", 2): 75, ("veg-courgettes-topdress", 3): 75,
    ("veg-courgettes-topdress", 4): 0,  ("veg-courgettes-topdress", 5): 0,
    ("veg-courgettes-topdress", 6): 0,
}

NITROGEN_SOIL_SPECIFIC: dict[tuple[str, int, str], float] = {
    # Table 4.17: Winter wheat (feed) — light sand soils
    ("winter-wheat-feed", 0, "light"): 180,
    ("winter-wheat-feed", 1, "light"): 150,
    ("winter-wheat-feed", 2, "light"): 120,
    ("winter-wheat-feed", 3, "light"): 90,
    ("winter-wheat-feed", 4, "light"): 60,
    ("winter-wheat-feed", 5, "light"): 30,
    ("winter-wheat-feed", 6, "light"): 20,

    # Table 4.17: Winter wheat (feed) — medium soils
    ("winter-wheat-feed", 0, "medium"): 250,
    ("winter-wheat-feed", 1, "medium"): 220,
    ("winter-wheat-feed", 2, "medium"): 190,
    ("winter-wheat-feed", 3, "medium"): 160,
    ("winter-wheat-feed", 4, "medium"): 120,
    ("winter-wheat-feed", 5, "medium"): 60,
    ("winter-wheat-feed", 6, "medium"): 20,

    # Table 4.17: Winter wheat (feed) — deep clayey soils
    ("winter-wheat-feed", 0, "heavy"): 250,
    ("winter-wheat-feed", 1, "heavy"): 220,
    ("winter-wheat-feed", 2, "heavy"): 190,
    ("winter-wheat-feed", 3, "heavy"): 160,
    ("winter-wheat-feed", 4, "heavy"): 120,
    ("winter-wheat-feed", 5, "heavy"): 60,
    ("winter-wheat-feed", 6, "heavy"): 20,

    # Table 4.17: Winter wheat (feed) — organic soils (SNS 0-2 not applicable)
    ("winter-wheat-feed", 3, "organic"): 120,
    ("winter-wheat-feed", 4, "organic"): 80,
    ("winter-wheat-feed", 5, "organic"): 60,
    ("winter-wheat-feed", 6, "organic"): 20,
}
