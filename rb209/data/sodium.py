"""Sodium (Na₂O) recommendation data from RB209.

Sodium recommendations are crop-specific and not universally needed.
The data is drawn from:
  - Section 4, Table 4.36: Sugar beet — sodium by K Index
  - Section 6: Asparagus (up to 500 kg Na₂O/ha) and celery (responsive
    on most soils)
  - Section 3: Grassland — 140 kg Na₂O/ha for herbage mineral balance
"""

# ── Sugar Beet — Table 4.36 ──────────────────────────────────────────
# Sodium recommendations for sugar beet are keyed by K Index.
# Sodium can partly replace potash in sugar beet nutrition when soils
# contain too little crop-available potash.
# Key: (crop, k_index) → kg Na₂O/ha
SODIUM_RECOMMENDATIONS: dict[tuple[str, int], float] = {
    ("sugar-beet", 0): 200,
    ("sugar-beet", 1): 200,
    ("sugar-beet", 2): 100,
    ("sugar-beet", 3): 0,
    ("sugar-beet", 4): 0,
}

# ── Asparagus — Section 6 ────────────────────────────────────────────
# Asparagus can respond to applied sodium.  Apply up to 500 kg Na₂O/ha
# per year at the end of June, but not in the establishment year.
# This is a flat rate, not index-dependent.
SODIUM_FLAT_RATES: dict[str, float] = {
    "veg-asparagus": 500,
}

# ── Grassland — Section 3 ────────────────────────────────────────────
# Sodium has no effect on grass growth but a minimum of 0.15% Na (DM
# basis) in the diet is essential for livestock health.  Apply 140 kg
# Na₂O/ha in early spring for herbage mineral balance where Na levels
# are low (<0.15%) or K:Na ratio > 20:1.
SODIUM_GRASSLAND_RATE: float = 140

# Crops for which the grassland sodium rate applies.
SODIUM_GRASSLAND_CROPS: set[str] = {
    "grass-grazed",
    "grass-silage",
    "grass-hay",
    "grass-grazed-one-cut",
}

# ── Advisory notes ────────────────────────────────────────────────────

SODIUM_NOTES: dict[str, list[str]] = {
    "sugar-beet": [
        "Sodium can partly replace potash in sugar beet nutrition when "
        "soils contain too little crop-available potash.",
        "On K Index 2 soils, only apply sodium if soil Na < 25 mg/l. "
        "Fen peats, silts and clays usually contain sufficient sodium.",
        "Apply inorganic fertilisers containing sodium at least two weeks "
        "before sowing and incorporate into the soil to avoid reducing "
        "plant populations in dry conditions, especially on sandy soils.",
    ],
    "veg-asparagus": [
        "Asparagus can respond to applied sodium. Apply up to "
        "500 kg Na₂O/ha per year at the end of June.",
        "Do not apply sodium in the establishment year.",
    ],
    "veg-asparagus-est": [
        "Do not apply sodium in the asparagus establishment year.",
    ],
    "veg-celery-seedbed": [
        "Celery is responsive to sodium on all soils except peaty and "
        "some Fen silt soils, which generally contain adequate sodium. "
        "Consult a FACTS Qualified Adviser for rate guidance.",
    ],
    "grassland": [
        "Sodium has no effect on grass growth but is essential for "
        "livestock health (minimum 0.15% Na in diet, dry matter basis).",
        "Apply 140 kg Na₂O/ha in early spring where herbage Na is low "
        "(<0.15%) or the K:Na ratio exceeds 20:1.",
        "For palatability, apply regular dressings of 10 kg Na₂O/ha "
        "throughout the season.",
    ],
}
