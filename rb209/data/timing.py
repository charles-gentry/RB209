"""Nitrogen application timing and split dressing rules.

Each entry in NITROGEN_TIMING_RULES maps a crop value string to a list of
rule dicts. Rules are evaluated in order; the first matching rule is used.

Rule dict keys:
  "min_n":          Minimum total N for this rule to apply (inclusive, default 0).
  "max_n":          Maximum total N for this rule to apply (inclusive, default inf).
  "soil_condition": Optional callable(soil_type: str | None) -> bool. When
                    present, the rule only matches if the callable returns True.
  "splits":         list of {"fraction": float, "timing": str} dicts.
                    fraction is the share of total_n for this dressing.
                    All fractions in a rule should sum to 1.0.
  "notes":          list[str] of additional advisory notes for this rule.

Source: RB209 9th edition — S3 pp.14-15 (grassland), S4 pp.26-31 (arable),
S5 p.23 (potatoes).
"""

NITROGEN_TIMING_RULES: dict[str, list[dict]] = {}

# ── Winter Wheat (feed) — RB209 S4 pp.26-27 ─────────────────────────────────
# Up to 120 kg N/ha: apply as a single dressing at GS25-GS30.
# Above 120 kg N/ha: split equally between GS25-GS30 and GS31-GS32.

NITROGEN_TIMING_RULES["winter-wheat-feed"] = [
    {
        "max_n": 120,
        "splits": [
            {"fraction": 1.0, "timing": "GS25-GS30 (February-March)"},
        ],
        "notes": [],
    },
    {
        "min_n": 121,
        "splits": [
            {"fraction": 0.5, "timing": "GS25-GS30 (February-March)"},
            {"fraction": 0.5, "timing": "GS31-GS32 (late March-April)"},
        ],
        "notes": [],
    },
]

# ── Winter Wheat (milling) — same split schedule + protein dressing note ──────
# Milling wheat benefits from a late-season protein dressing at GS32-GS39.

NITROGEN_TIMING_RULES["winter-wheat-milling"] = [
    {
        "max_n": 120,
        "splits": [
            {"fraction": 1.0, "timing": "GS25-GS30 (February-March)"},
        ],
        "notes": [
            "Consider a late protein dressing (GS32-GS39) to increase grain "
            "N content for milling quality.",
        ],
    },
    {
        "min_n": 121,
        "splits": [
            {"fraction": 0.5, "timing": "GS25-GS30 (February-March)"},
            {"fraction": 0.5, "timing": "GS31-GS32 (late March-April)"},
        ],
        "notes": [
            "Consider a late protein dressing (GS32-GS39) to increase grain "
            "N content for milling quality.",
        ],
    },
]

# ── Spring Wheat — RB209 S4 p.28 ─────────────────────────────────────────────
# Up to 100 kg N/ha: single dressing at drilling.
# Above 100 kg N/ha: split equally between drilling and GS30-GS31.

NITROGEN_TIMING_RULES["spring-wheat"] = [
    {
        "max_n": 100,
        "splits": [
            {"fraction": 1.0, "timing": "At drilling or immediately after (March-April)"},
        ],
        "notes": [],
    },
    {
        "min_n": 101,
        "splits": [
            {"fraction": 0.5, "timing": "At drilling or immediately after (March-April)"},
            {"fraction": 0.5, "timing": "GS30-GS31 (4-6 weeks after drilling)"},
        ],
        "notes": [],
    },
]

# ── Winter Barley — RB209 S4 pp.28-29 ────────────────────────────────────────
# Below 100 kg N/ha: single dressing at GS30-31.
# 100-199 kg N/ha: two equal dressings (late tillering + GS30-31).
# 200+ kg N/ha: three dressings (40%/40%/20%) with lodging risk note.

NITROGEN_TIMING_RULES["winter-barley"] = [
    {
        "max_n": 99,
        "splits": [
            {"fraction": 1.0, "timing": "GS30-31 (late February/early March)"},
        ],
        "notes": [],
    },
    {
        "min_n": 100, "max_n": 199,
        "splits": [
            {"fraction": 0.5, "timing": "Late tillering (mid-February/early March)"},
            {"fraction": 0.5, "timing": "GS30-31"},
        ],
        "notes": [],
    },
    {
        "min_n": 200,
        "splits": [
            {"fraction": 0.4, "timing": "Late tillering (mid-February/early March)"},
            {"fraction": 0.4, "timing": "GS30-31"},
            {"fraction": 0.2, "timing": "GS32"},
        ],
        "notes": ["Consider reducing by 25 kg N/ha if lodging risk is high."],
    },
]

# ── Spring Barley — RB209 S4 p.29 ────────────────────────────────────────────
# Below 100 kg N/ha: single dressing at drilling.
# 100+ kg N/ha: two dressings (1/3 at drilling, 2/3 at GS25-GS30).

NITROGEN_TIMING_RULES["spring-barley"] = [
    {
        "max_n": 99,
        "splits": [
            {"fraction": 1.0, "timing": "At drilling or immediately after (February-April)"},
        ],
        "notes": [],
    },
    {
        "min_n": 100,
        "splits": [
            {"fraction": 1 / 3, "timing": "At drilling or immediately after (February-April)"},
            {"fraction": 2 / 3, "timing": "GS25-GS30 (4-6 weeks after drilling)"},
        ],
        "notes": [],
    },
]

# ── Winter Rye — RB209 S4 pp.29-30 ───────────────────────────────────────────
# Same split schedule as winter wheat (feed).  Lodging risk note always included.

NITROGEN_TIMING_RULES["winter-rye"] = [
    {
        "max_n": 120,
        "splits": [
            {"fraction": 1.0, "timing": "GS25-GS30 (February-March)"},
        ],
        "notes": [
            "Winter rye is susceptible to lodging. Reduce N rate by 25-30 kg/ha "
            "if lodging risk is high.",
        ],
    },
    {
        "min_n": 121,
        "splits": [
            {"fraction": 0.5, "timing": "GS25-GS30 (February-March)"},
            {"fraction": 0.5, "timing": "GS31-GS32 (late March-April)"},
        ],
        "notes": [
            "Winter rye is susceptible to lodging. Reduce N rate by 25-30 kg/ha "
            "if lodging risk is high.",
        ],
    },
]

# ── Potatoes (maincrop) — RB209 S5 p.23 ──────────────────────────────────────
# Light (sandy) soils: 2/3 in seedbed before planting, 1/3 post-emergence.
# Other soils: apply all in seedbed.

NITROGEN_TIMING_RULES["potatoes-maincrop"] = [
    {
        "soil_condition": lambda s: s == "light",
        "splits": [
            {"fraction": 2 / 3, "timing": "Seedbed (before planting)"},
            {"fraction": 1 / 3, "timing": "Post-emergence (when shoots emerge)"},
        ],
        "notes": [
            "On light soils, split to reduce N leaching risk.",
        ],
    },
    {
        # Matches any soil type (including None) not handled by the rule above.
        "splits": [
            {"fraction": 1.0, "timing": "Seedbed (before planting)"},
        ],
        "notes": [],
    },
]

# ── Potatoes (early) — same rule as maincrop ──────────────────────────────────

NITROGEN_TIMING_RULES["potatoes-early"] = [
    {
        "soil_condition": lambda s: s == "light",
        "splits": [
            {"fraction": 2 / 3, "timing": "Seedbed (before planting)"},
            {"fraction": 1 / 3, "timing": "Post-emergence (when shoots emerge)"},
        ],
        "notes": [
            "On light soils, split to reduce N leaching risk.",
        ],
    },
    {
        "splits": [
            {"fraction": 1.0, "timing": "Seedbed (before planting)"},
        ],
        "notes": [],
    },
]

# ── Potatoes (seed) — same rule as maincrop ───────────────────────────────────

NITROGEN_TIMING_RULES["potatoes-seed"] = [
    {
        "soil_condition": lambda s: s == "light",
        "splits": [
            {"fraction": 2 / 3, "timing": "Seedbed (before planting)"},
            {"fraction": 1 / 3, "timing": "Post-emergence (when shoots emerge)"},
        ],
        "notes": [
            "On light soils, split to reduce N leaching risk.",
        ],
    },
    {
        "splits": [
            {"fraction": 1.0, "timing": "Seedbed (before planting)"},
        ],
        "notes": [],
    },
]

# ── Grass Silage (multi-cut) — RB209 S3 pp.14-15 ────────────────────────────
# Divide total annual N across three to four cuts.
# At low total N, limit to fewer applications.

NITROGEN_TIMING_RULES["grass-silage"] = [
    {
        "max_n": 80,
        "splits": [
            {"fraction": 1.0, "timing": "Before 1st cut (January-February)"},
        ],
        "notes": [],
    },
    {
        "min_n": 81, "max_n": 180,
        "splits": [
            {"fraction": 0.5, "timing": "Before 1st cut (January-February)"},
            {"fraction": 0.5, "timing": "After 1st cut (May-June)"},
        ],
        "notes": [],
    },
    {
        "min_n": 181, "max_n": 280,
        "splits": [
            {"fraction": 0.40, "timing": "Before 1st cut (January-February)"},
            {"fraction": 0.30, "timing": "After 1st cut (May-June)"},
            {"fraction": 0.30, "timing": "After 2nd cut (July-August)"},
        ],
        "notes": [],
    },
    {
        "min_n": 281,
        "splits": [
            {"fraction": 0.30, "timing": "Before 1st cut (January-February)"},
            {"fraction": 0.25, "timing": "After 1st cut (May-June)"},
            {"fraction": 0.25, "timing": "After 2nd cut (July-August)"},
            {"fraction": 0.20, "timing": "After 3rd cut (September)"},
        ],
        "notes": [
            "Limit spring K2O for 1st cut to 80-90 kg/ha to minimise luxury uptake.",
        ],
    },
]

# ── Grass Grazed — RB209 S3 pp.14-15 ────────────────────────────────────────
# Apply before each rotation.  At higher rates, spread across more rotations.

NITROGEN_TIMING_RULES["grass-grazed"] = [
    {
        "max_n": 100,
        "splits": [
            {"fraction": 0.5, "timing": "Early spring (March-April)"},
            {"fraction": 0.5, "timing": "Mid-season (June)"},
        ],
        "notes": [],
    },
    {
        "min_n": 101, "max_n": 200,
        "splits": [
            {"fraction": 0.4, "timing": "Early spring (March-April)"},
            {"fraction": 0.3, "timing": "After 1st rotation (May-June)"},
            {"fraction": 0.3, "timing": "After 2nd rotation (July-August)"},
        ],
        "notes": [],
    },
    {
        "min_n": 201,
        "splits": [
            {"fraction": 0.2, "timing": "Early spring (March)"},
            {"fraction": 0.2, "timing": "After 1st rotation (April-May)"},
            {"fraction": 0.2, "timing": "After 2nd rotation (June)"},
            {"fraction": 0.2, "timing": "After 3rd rotation (July)"},
            {"fraction": 0.2, "timing": "After 4th rotation (August)"},
        ],
        "notes": ["Apply before each grazing rotation; avoid applications in drought."],
    },
]

# ── Grass Grazed (+ 1 silage cut) — RB209 S3 p.15 ───────────────────────────

NITROGEN_TIMING_RULES["grass-grazed-one-cut"] = [
    {
        "max_n": 120,
        "splits": [
            {"fraction": 0.5, "timing": "Early spring (February-March)"},
            {"fraction": 0.5, "timing": "After silage cut (May-June)"},
        ],
        "notes": [],
    },
    {
        "min_n": 121,
        "splits": [
            {"fraction": 0.4, "timing": "Early spring (February-March)"},
            {"fraction": 0.3, "timing": "After silage cut (May-June)"},
            {"fraction": 0.3, "timing": "Late summer (August)"},
        ],
        "notes": [],
    },
]

# ── Grass Hay — RB209 S3 p.15 ────────────────────────────────────────────────
# Single application before growth starts.

NITROGEN_TIMING_RULES["grass-hay"] = [
    {
        "splits": [
            {"fraction": 1.0, "timing": "Early February to mid-March (before growth starts)"},
        ],
        "notes": [],
    },
]
