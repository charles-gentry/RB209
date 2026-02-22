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
# Source: RB209 Table 4.17 footnote "a", Defra NVZ guidance.
NVZ_NMAX: dict[str, float] = {
    "winter-wheat-feed": 220,
    "winter-wheat-milling": 220,
    "spring-wheat": 220,
    "winter-barley": 220,
    "spring-barley": 220,
    "winter-oats": 220,
    "spring-oats": 220,
    "winter-rye": 220,
    "winter-oilseed-rape": 250,
    "spring-oilseed-rape": 250,
    "grass-grazed": 300,
    "grass-silage": 300,
    "grass-hay": 300,
    "grass-grazed-one-cut": 300,
    "potatoes-maincrop": 270,
    "potatoes-early": 270,
    "potatoes-seed": 270,
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
