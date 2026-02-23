# VEG.md — Implementation Plan: Section 6 Vegetables and Bulbs

Source reference: `ref/section6_vegetables.md` (RB209 9th edition, updated January 2021).

---

## Overview

This plan adds full support for **33 vegetable and bulb crop types** from RB209 Section 6.
It requires changes across six data files, the recommendation engine, the CLI, and a new
test module. The work is broken into self-contained steps that can be reviewed and merged
independently.

Key differences from existing arable/grassland crops that drive most of the design decisions:

| Concern | Arable | Vegetables (Section 6) |
|---|---|---|
| SNS tables | Tables 4.3–4.5 (4 soil columns) | Tables 6.2–6.4 (4 soil columns + advisory for organic/peat) |
| Previous crop residue categories | 4 (low/medium/high/very-high) | 11 (beans, cereals, forage-cut, osr, peas, potatoes, sugar-beet, uncropped, veg-low-n, veg-medium-n, veg-high-n) |
| Soil type columns | light / medium / heavy / organic | light-sand / medium / deep-clay / deep-silt (organic & peat are advisory-only) |
| Potassium Index 2 | Single value | Split: 2- (121–180 mg/l) vs 2+ (181–240 mg/l) |
| Magnesium at Index 0 / 1 | 90 / 60 kg MgO/ha | 150 / 100 kg MgO/ha (all veg crops) |
| Nitrogen split dressings | Via `timing.py` | Per-crop seedbed + top-dressing, captured as separate crop slugs |

---

## 1. New Crop Catalogue — `rb209/data/crops.py`

Add the following 33 entries to `CROP_INFO`. All use `"category": "vegetables"`.

| Slug | `name` | Notes field (brief) |
|---|---|---|
| `veg-asparagus-est` | Asparagus (establishment year) | Apply N in three equal splits: pre-sowing, mid-June/July, end-August. |
| `veg-asparagus` | Asparagus (subsequent years) | Year 2: 120 kg N/ha by end-Feb. Later years: 40–80 kg N/ha timing based on winter rainfall. Seek FACTS advice. |
| `veg-brussels-sprouts` | Brussels Sprouts | No more than 100 kg N/ha before transplanting on light soils. |
| `veg-cabbage-storage` | Storage Cabbage | Reduce N on fertile soils to minimise storage losses. |
| `veg-cabbage-head-pre-dec` | Head Cabbage (pre-31 Dec) | Harvest before 31 December. |
| `veg-cabbage-head-post-dec` | Head Cabbage (post-31 Dec) | Harvest after 31 December. |
| `veg-collards-pre-dec` | Collards (pre-31 Dec) | Harvest before 31 December. |
| `veg-collards-post-dec` | Collards (post-31 Dec) | Harvest after 31 December. |
| `veg-cauliflower-summer` | Cauliflower (summer/autumn) | No more than 100 kg N/ha at sowing/transplanting where leaching risk exists. |
| `veg-cauliflower-winter-seedbed` | Cauliflower (winter — seedbed N) | Seedbed dressing only; pair with veg-cauliflower-winter-topdress. |
| `veg-cauliflower-winter-topdress` | Cauliflower (winter — top dressing N) | Apply after establishment; band placement of seedbed N reduces total by 33% if applied half-width. |
| `veg-calabrese` | Calabrese | Band spreading of seedbed N may be beneficial. |
| `veg-celery-seedbed` | Self-blanching Celery (seedbed N) | Apply 75–150 kg N/ha top dressing 4–6 weeks after planting. Celery responds to sodium on all but peat/fen silt soils. |
| `veg-peas-market` | Peas (market pick) | N-fixing crop; no fertiliser N required. |
| `veg-beans-broad` | Broad Beans | N-fixing crop; no fertiliser N required. |
| `veg-beans-dwarf` | Dwarf/Runner Beans (seedbed N) | No more than 100 kg N/ha at sowing; apply remainder after establishment. |
| `veg-radish` | Radish | No more than 100 kg N/ha in seedbed. |
| `veg-sweetcorn` | Sweetcorn | No more than 100 kg N/ha in seedbed. |
| `veg-lettuce-whole` | Lettuce (whole head) | Reduce N for late-season crops to avoid EU tissue nitrate limits. Starter fertiliser beneficial. |
| `veg-lettuce-baby` | Lettuce (baby leaf) | Use SMN measurement for second and third crops in same season. |
| `veg-rocket` | Wild Rocket | Use SMN measurement for sequential crops. |
| `veg-onions-bulb` | Bulb Onions | At SNS 0 on light sands with SMN ≤ 30 kg N/ha, an extra 15 kg N/ha may be applied. Starter fertiliser beneficial. |
| `veg-onions-salad` | Salad Onions | Starter fertiliser beneficial. |
| `veg-leeks` | Leeks | No fertiliser N during NVZ closed period without written FACTS advice. |
| `veg-beetroot` | Beetroot | No more than 100 kg N/ha in seedbed. |
| `veg-swedes` | Swedes | No more than 100 kg N/ha in seedbed. |
| `veg-turnips-parsnips` | Turnips and Parsnips | No more than 100 kg N/ha in seedbed. |
| `veg-carrots` | Carrots | No more than 100 kg N/ha in seedbed. |
| `veg-bulbs` | Bulbs and Bulb Flowers | Apply N as top dressing just before emergence. Narcissus: extra 50 kg N/ha in year 2 if poor growth. |
| `veg-coriander` | Coriander | No more than 100 kg N/ha in seedbed. |
| `veg-mint-est` | Mint (establishment year) | — |
| `veg-mint` | Mint (subsequent years) | — |
| `veg-courgettes-seedbed` | Courgettes (seedbed N) | Up to 75 kg N/ha top dressing may also be required. |

Each entry also needs `"has_straw_option": False`.

---

## 2. Vegetable SNS Tables — `rb209/data/sns.py` and `rb209/models.py`

### 2a. New `VegSoilType` enum in `models.py`

The vegetable SNS uses four mineral soil columns (organic/peat soils require FACTS advice).
Add a new string enum alongside the existing `SoilType`:

```python
class VegSoilType(str, Enum):
    LIGHT_SAND = "light-sand"   # light sand soils or shallow soils over sandstone
    MEDIUM     = "medium"       # medium soils or shallow soils not over sandstone
    DEEP_CLAY  = "deep-clay"    # deep clayey soils
    DEEP_SILT  = "deep-silt"    # deep silty soils
    ORGANIC    = "organic"      # advisory only — SNS Index 3–6, consult FACTS
    PEAT       = "peat"         # advisory only — SNS Index 4–6, consult FACTS
```

### 2b. New `VegPreviousCrop` enum in `models.py`

```python
class VegPreviousCrop(str, Enum):
    BEANS       = "beans"
    CEREALS     = "cereals"
    FORAGE_CUT  = "forage-cut"
    OSR         = "oilseed-rape"
    PEAS        = "peas"
    POTATOES    = "potatoes"
    SUGAR_BEET  = "sugar-beet"
    UNCROPPED   = "uncropped"
    VEG_LOW_N   = "veg-low-n"    # carrots, onions, radish, swedes, turnips
    VEG_MEDIUM_N = "veg-medium-n" # lettuce, leeks, long-season brassicas
    VEG_HIGH_N  = "veg-high-n"   # calabrese, Brussels sprouts, cauliflower
```

### 2c. New `VEG_SNS_LOOKUP` in `sns.py`

Key: `(previous_crop: str, soil_type: str, rainfall: str) -> int`

Rainfall strings: `"low"` (< 600 mm / < 150 mm EWR), `"moderate"` (600–700 mm),
`"high"` (> 700 mm / > 250 mm EWR).

Values from Tables 6.2, 6.3, 6.4 (columns: light-sand, medium, deep-clay, deep-silt):

```
Table 6.2 — low rainfall:
  beans:        1, 2, 3, 3
  cereals:      0, 1, 2, 2
  forage-cut:   0, 1, 2, 2
  oilseed-rape: 1, 2, 3, 3
  peas:         1, 2, 3, 3
  potatoes:     1, 2, 3, 3
  sugar-beet:   1, 1, 2, 2
  uncropped:    1, 2, 3, 3
  veg-low-n:    0, 1, 2, 2
  veg-medium-n: 1, 3, 3, 3
  veg-high-n:   2, 4, 4, 4

Table 6.3 — moderate rainfall:
  beans:        1, 2, 2, 3
  cereals:      0, 1, 1, 1
  forage-cut:   0, 1, 1, 1
  oilseed-rape: 0, 2, 2, 2
  peas:         1, 2, 2, 3
  potatoes:     0, 2, 2, 2
  sugar-beet:   0, 1, 1, 1
  uncropped:    1, 2, 2, 2
  veg-low-n:    0, 1, 1, 1
  veg-medium-n: 0, 2, 3, 3
  veg-high-n:   1, 3, 4, 4

Table 6.4 — high rainfall:
  beans:        0, 1, 2, 2
  cereals:      0, 1, 1, 1
  forage-cut:   0, 1, 1, 1
  oilseed-rape: 0, 1, 1, 2
  peas:         0, 1, 2, 2
  potatoes:     0, 1, 1, 2
  sugar-beet:   0, 1, 1, 1
  uncropped:    0, 1, 1, 2
  veg-low-n:    0, 1, 1, 1
  veg-medium-n: 0, 1, 1, 2
  veg-high-n:   1, 2, 2, 3
```

Organic soils: return SNS Index 4 with a note "Organic soils typically SNS 3–6; consult FACTS Qualified Adviser."
Peat soils: return SNS Index 5 with a note "Peat soils typically SNS 4–6; consult FACTS Qualified Adviser."

### 2d. New function `calculate_veg_sns()` in `engine.py`

Mirrors `calculate_sns()` but uses `VEG_SNS_LOOKUP`, `VegPreviousCrop`, and `VegSoilType`.

```python
def calculate_veg_sns(
    previous_crop: str,     # VegPreviousCrop value
    soil_type: str,         # VegSoilType value
    rainfall: str,          # "low" | "moderate" | "high"
) -> SNSResult:
```

Also expose a new `smn_to_sns_index_veg()` helper that uses **Table 6.6** thresholds
(which differ from the arable Table 4.10 used by `sns_value_to_index()`):

```
Table 6.6 — SNS Index from SMN:
  Index 0: SMN to 30 cm < 20  | to 60 cm < 40   | to 90 cm < 60
  Index 1: SMN to 30 cm 20–27 | to 60 cm 41–53  | to 90 cm 61–80
  Index 2: SMN to 30 cm 28–33 | to 60 cm 54–67  | to 90 cm 81–100
  Index 3: SMN to 30 cm 34–40 | to 60 cm 68–80  | to 90 cm 101–120
  Index 4: SMN to 30 cm 41–53 | to 60 cm 81–107 | to 90 cm 121–160
  Index 5: SMN to 30 cm 54–80 | to 60 cm 108–160| to 90 cm 161–240
  Index 6: SMN to 30 cm > 80  | to 60 cm > 160  | to 90 cm > 240
```

Signature:
```python
def smn_to_sns_index_veg(smn: float, depth_cm: int) -> int:
    """Convert SMN (kg N/ha) to SNS index using Table 6.6.

    Args:
        smn: Soil mineral nitrogen measured to depth_cm.
        depth_cm: Sampling depth — 30, 60, or 90.
    """
```

Store the threshold table in `sns.py` as `VEG_SMN_SNS_THRESHOLDS`:
```python
# (depth_cm, upper_bound) -> sns_index (sorted ascending by upper_bound per depth)
VEG_SMN_SNS_THRESHOLDS: dict[int, list[tuple[float, int]]] = {
    30: [(19.9, 0), (27, 1), (33, 2), (40, 3), (53, 4), (80, 5)],  # >80 -> 6
    60: [(39.9, 0), (53, 1), (67, 2), (80, 3), (107, 4), (160, 5)], # >160 -> 6
    90: [(59.9, 0), (80, 1), (100, 2), (120, 3), (160, 4), (240, 5)], # >240 -> 6
}
```

---

## 3. Nitrogen Data — `rb209/data/nitrogen.py`

Add a new `NITROGEN_VEG_RECOMMENDATIONS` dict. Key: `(crop_slug, sns_index)` for
sns_index 0–6. Values in kg N/ha from Tables 6.11–6.26.

```python
NITROGEN_VEG_RECOMMENDATIONS: dict[tuple[str, int], float] = {

    # Table 6.11 — Asparagus (establishment year)
    ("veg-asparagus-est", 0): 150, ("veg-asparagus-est", 1): 150,
    ("veg-asparagus-est", 2): 150, ("veg-asparagus-est", 3): 90,
    ("veg-asparagus-est", 4): 20,  ("veg-asparagus-est", 5): 0,
    ("veg-asparagus-est", 6): 0,

    # Table 6.11 — Asparagus (subsequent years, year 2 benchmark)
    # All indices return 120 kg N/ha; timing is fixed (end-Feb/early-Mar).
    # For years 3+, recommendation depends on winter rainfall — see notes.
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

    # Table 6.16 — Self-blanching Celery (seedbed N — uniform 75 at indices 0–3)
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

    # Table 6.25 — Mint (subsequent years) — same N levels as establishment
    ("veg-mint", 0): 180, ("veg-mint", 1): 170,
    ("veg-mint", 2): 160, ("veg-mint", 3): 150,
    ("veg-mint", 4): 130, ("veg-mint", 5): 100,
    ("veg-mint", 6): 70,

    # Table 6.26 — Courgettes (seedbed dressing)
    ("veg-courgettes-seedbed", 0): 100, ("veg-courgettes-seedbed", 1): 100,
    ("veg-courgettes-seedbed", 2): 100, ("veg-courgettes-seedbed", 3): 40,
    ("veg-courgettes-seedbed", 4): 0,   ("veg-courgettes-seedbed", 5): 0,
    ("veg-courgettes-seedbed", 6): 0,
}
```

---

## 4. Phosphorus Data — `rb209/data/phosphorus.py`

Add `PHOSPHORUS_VEG_RECOMMENDATIONS: dict[tuple[str, int], float]`.
Indices clamped to 0–4 as with existing crops (index 5+ treated as 4 → 0 for most crops).

```
Asparagus (establishment):   175, 150, 125, 100, 75
Asparagus (subsequent):       75,  75,  50,  50, 25
Brussels sprouts:            200, 150, 100,  50,  0
All storage/head/collard cabbages:  200, 150, 100, 50, 0
Cauliflower (summer):        200, 150, 100,  50,  0
Cauliflower (winter seedbed + topdress): 200, 150, 100, 50, 0
Calabrese:                   200, 150, 100,  50,  0
Celery:                      250, 200, 150, 100, 50
Peas (market):               185, 135,  85,  35,  0
Broad beans, dwarf/runner:   200, 150, 100,  50,  0
Radish, sweetcorn:           175, 125,  75,  25,  0
Lettuce (all types), rocket: 250, 200, 150, 100,  0  *
Bulb/salad onions, leeks:    200, 150, 100,  50,  0  *
Beetroot:                    200, 150, 100,  50,  0
Swedes, turnips/parsnips:    200, 150, 100,  50,  0
Carrots:                     200, 150, 100,  50,  0
Bulbs:                       200, 150, 100,  50,  0
Coriander, mint (est+sub):   175, 125,  75,  25,  0
Courgettes:                  175, 125,  75,  25,  0
```

\* For lettuce (all) and onions/leeks: at P Index 4 and 5, up to 60 kg P₂O₅/ha as starter
fertiliser may be beneficial (add as a note in the engine, not as a data value).

---

## 5. Potassium Data — `rb209/data/potassium.py`

### 5a. Primary table (2- value stored at index 2)

Add `POTASSIUM_VEG_RECOMMENDATIONS: dict[tuple[str, int], float]` with indices 0–4.
The index-2 value represents the **lower half** of K Index 2 (2−, i.e. soil K 121–180 mg/l).

```
Asparagus (establishment):      250, 225, 200, 150, 125  (no 2-/2+ split documented)
Asparagus (subsequent):         100,  50,  50,  50,   0
Brussels sprouts + all cabbages/collards: 300, 250, 200, 60, 0
Cauliflower (summer + winter seedbed + topdress): 275, 225, 175, 35, 0
Calabrese:                      275, 225, 175,  35,   0
Celery:                         450, 400, 350, 210,  50
Peas (market):                  190, 140,  90,   0,   0
Broad beans + dwarf/runner:     200, 150, 100,   0,   0
Radish, sweetcorn:              250, 200, 150,   0,   0
Lettuce (all) + rocket:         250, 200, 150,   0,   0
Bulb/salad onions + leeks:      275, 225, 175,  35,   0
Beetroot:                       300, 250, 200,  60,   0
Swedes:                         300, 250, 200,  60,   0
Turnips/parsnips:               300, 250, 200,  60,   0
Carrots:                        275, 225, 175,  35,   0
Bulbs:                          300, 250, 200,  60,   0
Coriander:                      315, 265, 215,  75,   0
Mint (establishment):           200, 150, 100,   0,   0
Mint (subsequent):              280, 230, 180,  40,   0
Courgettes:                     250, 200, 150,   0,   0
```

### 5b. Upper-half K Index 2 values (2+, soil K 181–240 mg/l)

Add `POTASSIUM_VEG_K2_UPPER: dict[str, float]` mapping crop slug to the 2+ K₂O value.
Crops without a documented 2-/2+ split are omitted (the 2- value is used for both).

```python
POTASSIUM_VEG_K2_UPPER: dict[str, float] = {
    "veg-brussels-sprouts":        150,
    "veg-cabbage-storage":         150,
    "veg-cabbage-head-pre-dec":    150,
    "veg-cabbage-head-post-dec":   150,
    "veg-collards-pre-dec":        150,
    "veg-collards-post-dec":       150,
    "veg-cauliflower-summer":      125,
    "veg-cauliflower-winter-seedbed": 125,
    "veg-cauliflower-winter-topdress": 125,
    "veg-calabrese":               125,
    "veg-celery-seedbed":          300,
    "veg-peas-market":              40,
    "veg-beans-broad":              50,
    "veg-beans-dwarf":              50,
    "veg-radish":                  100,
    "veg-sweetcorn":               100,
    "veg-lettuce-whole":           100,
    "veg-lettuce-baby":            100,
    "veg-rocket":                  100,
    "veg-onions-bulb":             125,
    "veg-onions-salad":            125,
    "veg-leeks":                   125,
    "veg-beetroot":                150,
    "veg-swedes":                  150,
    "veg-turnips-parsnips":        150,
    "veg-carrots":                 125,
    "veg-bulbs":                   150,
    "veg-coriander":               165,
    "veg-mint-est":                 50,
    "veg-mint":                    130,
    "veg-courgettes-seedbed":      100,
}
```

### 5c. Engine interface change

Add `k_upper_half: bool = False` parameter to `recommend_potassium()` and `recommend_all()`.
When `k_index == 2 and k_upper_half and crop in POTASSIUM_VEG_K2_UPPER`, return
`POTASSIUM_VEG_K2_UPPER[crop]` instead of the normal index-2 lookup.

---

## 6. Magnesium Data — `rb209/data/magnesium.py`

All 33 vegetable crops use the same Mg recommendation (RB209 Section 6, p.16):

```
Mg Index 0 → 150 kg MgO/ha
Mg Index 1 → 100 kg MgO/ha
Mg Index 2+ →   0 kg MgO/ha
```

Add a constant dict:

```python
VEG_MAGNESIUM_RECOMMENDATIONS: dict[int, float] = {
    0: 150, 1: 100, 2: 0, 3: 0, 4: 0,
}
```

In `engine.py`, detect vegetable crops by `CROP_INFO[crop]["category"] == "vegetables"`
and use `VEG_MAGNESIUM_RECOMMENDATIONS` instead of `MAGNESIUM_RECOMMENDATIONS`.

---

## 7. Sulfur Data — `rb209/data/sulfur.py`

Add vegetable crop SO₃ entries (kg SO₃/ha, for S-deficiency-risk situations):

```python
# Brassica vegetables — 50 kg SO3/ha (RB209 recommends 50–75; use 50 as minimum)
"veg-brussels-sprouts": 50,
"veg-cabbage-storage":  50,
"veg-cabbage-head-pre-dec":  50,
"veg-cabbage-head-post-dec": 50,
"veg-collards-pre-dec":      50,
"veg-collards-post-dec":     50,
"veg-cauliflower-summer":    50,
"veg-cauliflower-winter-seedbed":   50,
"veg-cauliflower-winter-topdress":  50,
"veg-calabrese":             50,
"veg-swedes":                50,   # swedes are brassicas
"veg-turnips-parsnips":      50,   # turnips are brassicas

# Other vegetables — 25 kg SO3/ha where deficiency is recognised or expected
"veg-asparagus-est":    25,
"veg-asparagus":        25,
"veg-celery-seedbed":   25,
"veg-radish":           25,
"veg-sweetcorn":        25,
"veg-lettuce-whole":    25,
"veg-lettuce-baby":     25,
"veg-rocket":           25,
"veg-onions-bulb":      25,
"veg-onions-salad":     25,
"veg-leeks":            25,
"veg-beetroot":         25,
"veg-carrots":          25,
"veg-bulbs":            25,
"veg-coriander":        25,
"veg-mint-est":         25,
"veg-mint":             25,
"veg-courgettes-seedbed": 25,

# N-fixing — no S response documented
"veg-peas-market":  0,
"veg-beans-broad":  0,
"veg-beans-dwarf":  0,
```

---

## 8. Engine Changes — `rb209/engine.py`

### 8a. Import new data

```python
from rb209.data.magnesium import VEG_MAGNESIUM_RECOMMENDATIONS
from rb209.data.nitrogen import NITROGEN_VEG_RECOMMENDATIONS
from rb209.data.phosphorus import PHOSPHORUS_VEG_RECOMMENDATIONS
from rb209.data.potassium import POTASSIUM_VEG_RECOMMENDATIONS, POTASSIUM_VEG_K2_UPPER
from rb209.data.sns import VEG_SNS_LOOKUP, VEG_SMN_SNS_THRESHOLDS
from rb209.models import VegPreviousCrop, VegSoilType
```

### 8b. Update `_validate_crop()`

No change needed — `CROP_INFO` is the single source of truth. Vegetable slugs appear there.

### 8c. Update `recommend_nitrogen()`

After the existing lookup logic, fall through to `NITROGEN_VEG_RECOMMENDATIONS`:

```python
key = (crop, sns_index)
if key in NITROGEN_RECOMMENDATIONS:
    base = NITROGEN_RECOMMENDATIONS[key]
elif key in NITROGEN_VEG_RECOMMENDATIONS:
    base = NITROGEN_VEG_RECOMMENDATIONS[key]
else:
    raise ValueError(f"No nitrogen data for crop '{crop}' at SNS {sns_index}")
```

### 8d. Update `recommend_phosphorus()`

```python
if key in PHOSPHORUS_RECOMMENDATIONS:
    base = PHOSPHORUS_RECOMMENDATIONS[key]
elif key in PHOSPHORUS_VEG_RECOMMENDATIONS:
    base = PHOSPHORUS_VEG_RECOMMENDATIONS[key]
else:
    raise ValueError(f"No phosphorus data for crop '{crop}'")
```

### 8e. Update `recommend_potassium()`

Add `k_upper_half: bool = False` parameter. After normal lookup:

```python
if k_index == 2 and k_upper_half and crop in POTASSIUM_VEG_K2_UPPER:
    return POTASSIUM_VEG_K2_UPPER[crop]
if key in POTASSIUM_VEG_RECOMMENDATIONS:
    base = POTASSIUM_VEG_RECOMMENDATIONS[key]
```

### 8f. Update `recommend_magnesium()`

Add optional `crop: str | None = None` parameter. When crop is provided and is a
vegetable, use `VEG_MAGNESIUM_RECOMMENDATIONS`:

```python
def recommend_magnesium(mg_index: int, crop: str | None = None) -> float:
    _validate_index("Mg index", mg_index, 0, 9)
    clamped = _clamp_index(mg_index, 4)
    if crop and CROP_INFO.get(crop, {}).get("category") == "vegetables":
        return VEG_MAGNESIUM_RECOMMENDATIONS[clamped]
    return MAGNESIUM_RECOMMENDATIONS[clamped]
```

Update `recommend_all()` to pass `crop` to `recommend_magnesium()`.

### 8g. Update `recommend_all()`

Add `k_upper_half: bool = False` parameter and pass it through to `recommend_potassium()`.

Add vegetable-specific notes in `recommend_all()`:

- **N-fixing note**: detect `veg-peas-market` and `veg-beans-broad` (same as existing peas/field-beans).
- **Seedbed N cap note**: for crops flagged with seedbed split, add note "Apply no more than 100 kg N/ha in the seedbed. Apply remainder after establishment."
  Affected crops: `veg-beans-dwarf`, `veg-radish`, `veg-sweetcorn`, `veg-beetroot`, `veg-swedes`, `veg-turnips-parsnips`, `veg-carrots`, `veg-coriander`.
- **Asparagus note**: for `veg-asparagus`, add note explaining year-2 vs year-3+ timing differences.
- **Celery top-dress note**: for `veg-celery-seedbed`, add note that 75–150 kg N/ha top dressing is required 4–6 weeks after planting.
- **Lettuce nitrate note**: for `veg-lettuce-whole`, `veg-lettuce-baby`, `veg-rocket`, add note about EU tissue-nitrate limits for late-season crops.
- **Leeks NVZ note**: for `veg-leeks`, add note about NVZ closed period restriction.
- **K₂O 2+/2- note**: when `k_index == 2`, add note "K index 2 is split into 2- (121–180 mg/l) and 2+ (181–240 mg/l). Use `--k-upper-half` flag if soil K is in the upper half."

### 8h. New function `calculate_veg_sns()`

As specified in Section 2d above. Returns an `SNSResult` with:
- `method = "veg-field-assessment"`
- notes describing the soil type, previous crop category, rainfall, and resulting index
- advisory note appended when soil type is `"organic"` or `"peat"`

### 8i. New function `smn_to_sns_index_veg()`

As specified in Section 2d above. Raises `ValueError` if `depth_cm` not in {30, 60, 90}.

---

## 9. CLI Changes — `rb209/cli.py`

### 9a. Update crop list / help text

The vegetable crops are automatically available once added to `CROP_INFO`, but:

- Add `--k-upper-half` / `-ku` boolean flag to `recommend` and `all` subcommands.
  When set, pass `k_upper_half=True` to `recommend_potassium()` / `recommend_all()`.
  Help text: "Use K Index 2+ value (181–240 mg/l) instead of 2- for vegetable crops."

- Add a `veg-sns` subcommand (or extend `sns`) to call `calculate_veg_sns()`.
  Arguments: `--previous-crop` (choices: all `VegPreviousCrop` values),
  `--soil-type` (choices: all `VegSoilType` values), `--rainfall` (low/moderate/high).

- Add a `veg-smn` subcommand to call `smn_to_sns_index_veg()`.
  Arguments: `--smn` (float, kg N/ha), `--depth` (int, choices: 30/60/90).

### 9b. Group vegetable crops in `--list` output

When listing available crops, group by category. Output should show a `vegetables` section
listing all 33 veg slugs alongside their display names.

---

## 10. Tests — `tests/test_veg.py`

Create a new test file covering:

1. **SNS lookups** — spot-check all three rainfall tables for representative previous-crop
   and soil-type combinations (at least 10 assertions from Tables 6.2–6.4).
   - Example from reference: Brussels sprouts on deep silt after cereals at moderate
     rainfall → SNS 1 → N = 300 kg/ha.

2. **SMN → SNS index** — test all three depths against boundary values from Table 6.6.

3. **Nitrogen recommendations** — one assertion per crop at SNS 0, 2, and 6.

4. **Phosphorus** — spot-check 5 crops across P Index range 0–4.

5. **Potassium** — for 5 crops: verify index 0, 2 (2- value), 2 (2+ value via k_upper_half),
   and index 3.

6. **Magnesium** — verify that vegetable crops return 150 at Mg index 0 and 100 at index 1,
   not the arable values of 90 and 60.

7. **Sulfur** — verify brassica crops return 50, other veg return 25, N-fixing return 0.

8. **Engine integration** — call `recommend_all()` for 6 representative crops and assert
   all five nutrient values (N, P, K, Mg, S) match expected values.

9. **Notes content** — verify that key advisory notes appear in the output for:
   - `veg-lettuce-whole` (nitrate warning)
   - `veg-leeks` (NVZ closed period)
   - `veg-celery-seedbed` (top-dressing reminder)
   - `veg-asparagus` (year-2 timing note)

10. **Error handling** — confirm `ValueError` is raised for unknown crops and out-of-range
    indices, consistent with existing test patterns.

---

## 11. Implementation Order

1. `models.py` — add `VegSoilType` and `VegPreviousCrop` enums
2. `data/sns.py` — add `VEG_SNS_LOOKUP` and `VEG_SMN_SNS_THRESHOLDS`
3. `data/crops.py` — add 33 vegetable crop entries
4. `data/nitrogen.py` — add `NITROGEN_VEG_RECOMMENDATIONS`
5. `data/phosphorus.py` — add `PHOSPHORUS_VEG_RECOMMENDATIONS`
6. `data/potassium.py` — add `POTASSIUM_VEG_RECOMMENDATIONS` and `POTASSIUM_VEG_K2_UPPER`
7. `data/magnesium.py` — add `VEG_MAGNESIUM_RECOMMENDATIONS`
8. `data/sulfur.py` — add vegetable SO₃ entries
9. `engine.py` — all changes described in Section 8
10. `cli.py` — `--k-upper-half` flag and `veg-sns` / `veg-smn` subcommands
11. `tests/test_veg.py` — full test suite

---

## 12. Out of Scope

The following are documented in Section 6 but are not part of this implementation plan:

- **Leaf analysis tables** (Tables 6.10, 6.13, 6.15, 6.21, 6.23) — reference only, no
  recommendations to compute.
- **Yield adjustment data** (`Table 6.27`) — the methodology requires crop-specific dry
  matter, harvest index, and mineralisation parameters not yet integrated into the engine.
  Add to `yield_adjustments.py` in a follow-up plan.
- **Nitrogen timing rules** for vegetable crops — the seedbed/top-dressing splits are
  captured as separate crop slugs (e.g. `veg-cauliflower-winter-seedbed` vs
  `veg-cauliflower-winter-topdress`) rather than through the `timing.py` machinery.
  A dedicated vegetable timing module may be added in future.
- **Sodium recommendations** — Asparagus (up to 500 kg Na₂O/ha) and Celery (responsive
  on most soils). Out of scope until a general sodium module is added.
- **Micronutrient guidance** (Table 6.9) — qualitative risk factors only; no kg/ha values
  to implement.
- **Fertigation guidance** — advisory text only.
