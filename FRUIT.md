# FRUIT.md — Implementation Plan: Section 7 Fruit, Vines and Hops

Source reference: `ref/section7_fruit_vines_hops.md` (RB209 9th edition, updated February 2020).

**Implementation status: PLANNED** — Steps below are not yet implemented.

---

## Overview

This plan adds full support for **18 fruit, vine and hop crop types** from RB209 Section 7.
It requires a new data module, changes across four existing data files, the recommendation
engine, the CLI, and a new test module. Steps are self-contained and can be reviewed
independently.

Key differences from existing arable/vegetable crops that drive most of the design decisions:

| Concern | Arable / Vegetables | Fruit, Vines & Hops (Section 7) |
|---|---|---|
| N index type | SNS Index 0–6 | Soil category (4 groups) |
| N for strawberries | — | SNS Index via Section 6 system (Table 7.8) |
| Management system | Not applicable | Grass/herbicide strip vs overall grass (top fruit only) |
| P/K/Mg index range | Indices 0–4+ | Hops use indices 0–5+ (wider range) |
| Pre-planting table | Not applicable | Separate pre-planting recommendations (Table 7.3) |
| Soil category enum | `SoilType` / `VegSoilType` | New `FruitSoilCategory` |
| Soft fruit K flag | — | Sulphate of potash required for raspberries/redcurrants/gooseberries at K > 120 kg/ha |

---

## 1. New Crop Catalogue — `rb209/data/crops.py`

Add the following 18 entries to `CROP_INFO`. All use `"category": "fruit"`.

### 1a. Pre-planting

| Slug | `name` | Notes |
|---|---|---|
| `fruit-preplant` | Fruit and Vines (before planting) | No N required. Apply K in autumn and incorporate to avoid root scorch. P/K/Mg by Index 0–5+. |
| `hops-preplant` | Hops (before planting) | Potted hop plants benefit from 70–80 kg N/ha in the spring before planting. P/K/Mg by Index 0–5+. |

### 1b. Top fruit (established orchards)

| Slug | `name` | Notes |
|---|---|---|
| `fruit-dessert-apple` | Dessert Apples (established) | N by soil category and orchard management. Larger N may be needed for varieties with regular heavy cropping potential (>40 t/ha). |
| `fruit-culinary-apple` | Culinary and Cider Apples (established) | N by soil category and orchard management. Cider apples respond to K Index 3 and Mg Index 3. |
| `fruit-pear` | Pears (established) | N by soil category and orchard management. |
| `fruit-cherry` | Cherries (established) | N by soil category and orchard management. |
| `fruit-plum` | Plums (established) | N by soil category and orchard management. |

### 1c. Soft fruit and vines (established)

| Slug | `name` | Notes |
|---|---|---|
| `fruit-blackcurrant` | Blackcurrants (established) | N by soil category. Ben-series varieties typically require 70–120 kg N/ha. |
| `fruit-redcurrant` | Redcurrants (established) | N by soil category. Use sulphate of potash where K > 120 kg/ha. |
| `fruit-gooseberry` | Gooseberries (established) | N by soil category. Use sulphate of potash where K > 120 kg/ha. |
| `fruit-raspberry` | Raspberries (established) | N by soil category. Use sulphate of potash where K > 120 kg/ha. |
| `fruit-loganberry` | Loganberries (established) | N by soil category. |
| `fruit-tayberry` | Tayberries (established) | N by soil category. |
| `fruit-blackberry` | Blackberries (established) | N by soil category. |
| `fruit-strawberry-main` | Strawberries — Main Season (established) | N by SNS index and soil category (Table 7.8). Uses Section 6 SNS assessment. |
| `fruit-strawberry-ever` | Strawberries — Everbearers (established) | N by SNS index and soil category (Table 7.8). Higher N than main season. |
| `fruit-vine` | Vines (established) | N by soil category. Reduce N where growth is excessive. |

### 1d. Hops

| Slug | `name` | Notes |
|---|---|---|
| `fruit-hops` | Hops (established) | N by soil category (deep silty, clay, other mineral only). Split N into 2–3 dressings: late March/April, May, late June/early July. Reduce to 125–165 kg N/ha where Verticillium wilt risk present. |

Each entry also needs `"has_straw_option": False`.

---

## 2. New `FruitSoilCategory` Enum and `OrchardManagement` Enum — `rb209/models.py`

### 2a. New `FruitSoilCategory` enum

Section 7 groups the 7 soil types from Table 7.1 into 4 nitrogen-recommendation categories.
Add alongside the existing enums:

```python
class FruitSoilCategory(str, Enum):
    LIGHT_SAND  = "light-sand"    # Light sand soils AND shallow soils
    DEEP_SILT   = "deep-silt"     # Deep silty soils
    CLAY        = "clay"          # Deep clayey soils
    OTHER       = "other-mineral" # Medium soils, organic soils, peat soils
```

**Mapping from full Table 7.1 soil types to `FruitSoilCategory`:**

| Table 7.1 soil type | `FruitSoilCategory` |
|---|---|
| Light sand soils | `LIGHT_SAND` |
| Shallow soils | `LIGHT_SAND` |
| Medium soils | `OTHER` |
| Deep clayey soils | `CLAY` |
| Deep silty soils | `DEEP_SILT` |
| Organic soils | `OTHER` |
| Peat soils | `OTHER` |

### 2b. New `OrchardManagement` enum

```python
class OrchardManagement(str, Enum):
    GRASS_STRIP    = "grass-strip"    # Grass alley with herbicide strip
    OVERALL_GRASS  = "overall-grass"  # Overall grass (or very weedy) management
```

This applies to top fruit only (`fruit-dessert-apple`, `fruit-culinary-apple`, `fruit-pear`,
`fruit-cherry`, `fruit-plum`). The grass/strip value is for the complete orchard area and can
be reduced where nitrogen is applied to the bare soil strip only.

---

## 3. New Data Module — `rb209/data/fruit.py`

Create a new file containing all Section 7 lookup tables. This keeps fruit-specific data
isolated, consistent with the existing pattern of one module per crop category concern.

### 3a. Pre-planting P/K/Mg — Table 7.3

Indexed by `(crop_group, nutrient, index)` where `crop_group` is `"fruit-vines"` or `"hops"`,
`nutrient` is `"phosphate"`, `"potash"`, or `"magnesium"`, and `index` is 0–5.
Index 5 means "5 and over".

```python
FRUIT_PREPLANT_PKM: dict[tuple[str, str, int], float] = {
    # Fruit and vines — Table 7.3
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

    # Hops — Table 7.3
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
```

### 3b. Top fruit nitrogen — Table 7.4

Keyed by `(crop_slug, soil_category, orchard_management)`.

```python
FRUIT_TOP_NITROGEN: dict[tuple[str, str, str], float] = {
    # Dessert apples
    ("fruit-dessert-apple", "light-sand", "grass-strip"):   80,
    ("fruit-dessert-apple", "light-sand", "overall-grass"): 120,
    ("fruit-dessert-apple", "deep-silt",  "grass-strip"):   30,
    ("fruit-dessert-apple", "deep-silt",  "overall-grass"):  70,
    ("fruit-dessert-apple", "clay",        "grass-strip"):   40,
    ("fruit-dessert-apple", "clay",        "overall-grass"):  80,
    ("fruit-dessert-apple", "other-mineral","grass-strip"):  60,
    ("fruit-dessert-apple", "other-mineral","overall-grass"):100,

    # Culinary and cider apples
    ("fruit-culinary-apple", "light-sand",  "grass-strip"):  110,
    ("fruit-culinary-apple", "light-sand",  "overall-grass"):150,
    ("fruit-culinary-apple", "deep-silt",   "grass-strip"):   60,
    ("fruit-culinary-apple", "deep-silt",   "overall-grass"): 100,
    ("fruit-culinary-apple", "clay",         "grass-strip"):   70,
    ("fruit-culinary-apple", "clay",         "overall-grass"): 110,
    ("fruit-culinary-apple", "other-mineral","grass-strip"):   90,
    ("fruit-culinary-apple", "other-mineral","overall-grass"): 130,

    # Pears (same rates as cherries and plums)
    ("fruit-pear", "light-sand",  "grass-strip"):  140,
    ("fruit-pear", "light-sand",  "overall-grass"): 180,
    ("fruit-pear", "deep-silt",   "grass-strip"):   90,
    ("fruit-pear", "deep-silt",   "overall-grass"): 130,
    ("fruit-pear", "clay",         "grass-strip"):  100,
    ("fruit-pear", "clay",         "overall-grass"): 140,
    ("fruit-pear", "other-mineral","grass-strip"):  120,
    ("fruit-pear", "other-mineral","overall-grass"): 160,

    # Cherries (same rates as pears and plums)
    ("fruit-cherry", "light-sand",  "grass-strip"):  140,
    ("fruit-cherry", "light-sand",  "overall-grass"): 180,
    ("fruit-cherry", "deep-silt",   "grass-strip"):   90,
    ("fruit-cherry", "deep-silt",   "overall-grass"): 130,
    ("fruit-cherry", "clay",         "grass-strip"):  100,
    ("fruit-cherry", "clay",         "overall-grass"): 140,
    ("fruit-cherry", "other-mineral","grass-strip"):  120,
    ("fruit-cherry", "other-mineral","overall-grass"): 160,

    # Plums (same rates as pears and cherries)
    ("fruit-plum", "light-sand",  "grass-strip"):  140,
    ("fruit-plum", "light-sand",  "overall-grass"): 180,
    ("fruit-plum", "deep-silt",   "grass-strip"):   90,
    ("fruit-plum", "deep-silt",   "overall-grass"): 130,
    ("fruit-plum", "clay",         "grass-strip"):  100,
    ("fruit-plum", "clay",         "overall-grass"): 140,
    ("fruit-plum", "other-mineral","grass-strip"):  120,
    ("fruit-plum", "other-mineral","overall-grass"): 160,
}
```

### 3c. Top fruit P/K/Mg — Table 7.5

All top fruit share identical P/K/Mg rates; indexed by `(nutrient, index)` with index 0–4.
Index 4 means "4 and over".

```python
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
```

### 3d. Soft fruit and vine nitrogen — Table 7.6

Keyed by `(crop_slug, soil_category)`. Strawberries are handled separately (Section 3f).

```python
FRUIT_SOFT_NITROGEN: dict[tuple[str, str], float] = {
    # Blackcurrants
    ("fruit-blackcurrant", "light-sand"):  160,
    ("fruit-blackcurrant", "deep-silt"):   110,
    ("fruit-blackcurrant", "clay"):        120,
    ("fruit-blackcurrant", "other-mineral"):140,

    # Redcurrants, gooseberries, raspberries, loganberries, tayberries, blackberries
    ("fruit-redcurrant",  "light-sand"):  120,
    ("fruit-redcurrant",  "deep-silt"):    70,
    ("fruit-redcurrant",  "clay"):         80,
    ("fruit-redcurrant",  "other-mineral"):100,

    ("fruit-gooseberry",  "light-sand"):  120,
    ("fruit-gooseberry",  "deep-silt"):    70,
    ("fruit-gooseberry",  "clay"):         80,
    ("fruit-gooseberry",  "other-mineral"):100,

    ("fruit-raspberry",   "light-sand"):  120,
    ("fruit-raspberry",   "deep-silt"):    70,
    ("fruit-raspberry",   "clay"):         80,
    ("fruit-raspberry",   "other-mineral"):100,

    ("fruit-loganberry",  "light-sand"):  120,
    ("fruit-loganberry",  "deep-silt"):    70,
    ("fruit-loganberry",  "clay"):         80,
    ("fruit-loganberry",  "other-mineral"):100,

    ("fruit-tayberry",    "light-sand"):  120,
    ("fruit-tayberry",    "deep-silt"):    70,
    ("fruit-tayberry",    "clay"):         80,
    ("fruit-tayberry",    "other-mineral"):100,

    ("fruit-blackberry",  "light-sand"):  120,
    ("fruit-blackberry",  "deep-silt"):    70,
    ("fruit-blackberry",  "clay"):         80,
    ("fruit-blackberry",  "other-mineral"):100,

    # Vines
    ("fruit-vine", "light-sand"):   60,
    ("fruit-vine", "deep-silt"):     0,
    ("fruit-vine", "clay"):         20,
    ("fruit-vine", "other-mineral"):40,
}
```

### 3e. Soft fruit and vine P/K/Mg — Table 7.7

Two groups: (1) blackcurrants, redcurrants, gooseberries, raspberries, loganberries, tayberries
and (2) blackberries and vines. Magnesium is the same for all crops. Indexed by
`(crop_slug, nutrient, index)` with index 0–4.

```python
# Group 1 slugs: fruit-blackcurrant, fruit-redcurrant, fruit-gooseberry,
#   fruit-raspberry, fruit-loganberry, fruit-tayberry
# Group 2 slugs: fruit-blackberry, fruit-vine

FRUIT_SOFT_PKM: dict[tuple[str, str, int], float] = {
    # Group 1 — phosphate
    # (repeated for each slug in group 1)
    **{(slug, "phosphate", i): v for slug in (
        "fruit-blackcurrant","fruit-redcurrant","fruit-gooseberry",
        "fruit-raspberry","fruit-loganberry","fruit-tayberry"
    ) for i, v in enumerate([110, 70, 40, 40, 0])},

    # Group 1 — potash (sulphate of potash required for raspberries/redcurrants/
    #   gooseberries at Index 0 and 1 where K > 120 kg/ha)
    **{(slug, "potash", i): v for slug in (
        "fruit-blackcurrant","fruit-redcurrant","fruit-gooseberry",
        "fruit-raspberry","fruit-loganberry","fruit-tayberry"
    ) for i, v in enumerate([250, 180, 120, 60, 0])},

    # Group 2 — phosphate
    **{(slug, "phosphate", i): v for slug in (
        "fruit-blackberry","fruit-vine"
    ) for i, v in enumerate([110, 70, 40, 40, 0])},

    # Group 2 — potash
    **{(slug, "potash", i): v for slug in (
        "fruit-blackberry","fruit-vine"
    ) for i, v in enumerate([220, 150, 80, 0, 0])},

    # All crops — magnesium
    **{(slug, "magnesium", i): v for slug in (
        "fruit-blackcurrant","fruit-redcurrant","fruit-gooseberry",
        "fruit-raspberry","fruit-loganberry","fruit-tayberry",
        "fruit-blackberry","fruit-vine"
    ) for i, v in enumerate([100, 65, 50, 0, 0])},
}
```

### 3f. Strawberry nitrogen — Table 7.8

Nitrogen for soil-grown strawberries is SNS-index based. Table 7.8 uses three soil groups:
`"light-sand"` (light sand and shallow soils), `"deep-silt"` (deep silty soils), and
`"other-mineral"` (all remaining mineral soils including clays). SNS Index 0–5.
Index 5 means "5 and over".

Strawberries use the same SNS assessment system as Section 6 vegetables (`calculate_veg_sns()`).

```python
FRUIT_STRAWBERRY_NITROGEN: dict[tuple[str, str, int], float] = {
    # Main season
    ("fruit-strawberry-main", "light-sand",  0): 60,
    ("fruit-strawberry-main", "light-sand",  1): 50,
    ("fruit-strawberry-main", "light-sand",  2): 40,
    ("fruit-strawberry-main", "light-sand",  3): 30,
    ("fruit-strawberry-main", "light-sand",  4): 20,
    ("fruit-strawberry-main", "light-sand",  5):  0,

    ("fruit-strawberry-main", "deep-silt",   0):  0,
    ("fruit-strawberry-main", "deep-silt",   1):  0,
    ("fruit-strawberry-main", "deep-silt",   2):  0,
    ("fruit-strawberry-main", "deep-silt",   3):  0,
    ("fruit-strawberry-main", "deep-silt",   4):  0,
    ("fruit-strawberry-main", "deep-silt",   5):  0,

    ("fruit-strawberry-main", "other-mineral",0): 40,
    ("fruit-strawberry-main", "other-mineral",1): 40,
    ("fruit-strawberry-main", "other-mineral",2): 30,
    ("fruit-strawberry-main", "other-mineral",3): 20,
    ("fruit-strawberry-main", "other-mineral",4):  0,
    ("fruit-strawberry-main", "other-mineral",5):  0,

    # Everbearers
    ("fruit-strawberry-ever", "light-sand",  0): 80,
    ("fruit-strawberry-ever", "light-sand",  1): 70,
    ("fruit-strawberry-ever", "light-sand",  2): 60,
    ("fruit-strawberry-ever", "light-sand",  3): 40,
    ("fruit-strawberry-ever", "light-sand",  4): 20,
    ("fruit-strawberry-ever", "light-sand",  5):  0,

    ("fruit-strawberry-ever", "deep-silt",   0): 40,
    ("fruit-strawberry-ever", "deep-silt",   1): 30,
    ("fruit-strawberry-ever", "deep-silt",   2): 30,
    ("fruit-strawberry-ever", "deep-silt",   3): 20,
    ("fruit-strawberry-ever", "deep-silt",   4):  0,
    ("fruit-strawberry-ever", "deep-silt",   5):  0,

    ("fruit-strawberry-ever", "other-mineral",0): 60,
    ("fruit-strawberry-ever", "other-mineral",1): 50,
    ("fruit-strawberry-ever", "other-mineral",2): 40,
    ("fruit-strawberry-ever", "other-mineral",3): 20,
    ("fruit-strawberry-ever", "other-mineral",4):  0,
    ("fruit-strawberry-ever", "other-mineral",5):  0,
}
```

**Note on clay mapping:** Table 7.8 does not list clay as a separate category. When
`soil_category == "clay"`, map to `"other-mineral"` for strawberry nitrogen lookup.

### 3g. Strawberry P/K/Mg — Table 7.9

```python
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
```

Note: the K:Mg ratio constraint (should be no greater than 3:1 based on soil mg/litre K and Mg)
should be noted in the engine output.

### 3h. Hops nitrogen — Table 7.17

Hops nitrogen is by soil category. Light sand and shallow soils are not listed in the table;
the engine raises a `ValueError` for this combination and suggests seeking specialist advice.

```python
FRUIT_HOPS_NITROGEN: dict[str, float] = {
    "deep-silt":    180,
    "clay":         200,
    "other-mineral":220,
    # "light-sand" not given in RB209 Table 7.17; raise ValueError
}
```

### 3i. Hops P/K/Mg — Table 7.17

Hops use an extended index range (0–5). Index 5 means "5 and over".

```python
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
```

Note: The K:Mg ratio (soil mg/litre K:Mg) must not exceed 3:1 for hops. Surface-apply and
incorporate annually. Reduce N by 70 kg/ha where large/frequent organic manure applications
have been used in previous years.

---

## 4. Engine Changes — `rb209/engine.py`

### 4a. New import

```python
from rb209.data.fruit import (
    FRUIT_PREPLANT_PKM,
    FRUIT_TOP_NITROGEN,
    FRUIT_TOP_PKM,
    FRUIT_SOFT_NITROGEN,
    FRUIT_SOFT_PKM,
    FRUIT_STRAWBERRY_NITROGEN,
    FRUIT_STRAWBERRY_PKM,
    FRUIT_HOPS_NITROGEN,
    FRUIT_HOPS_PKM,
)
from rb209.models import FruitSoilCategory, OrchardManagement
```

### 4b. New helper `_is_fruit_crop(crop: str) -> bool`

```python
def _is_fruit_crop(crop: str) -> bool:
    return CROP_INFO.get(crop, {}).get("category") == "fruit"
```

### 4c. New function `recommend_fruit_nitrogen()`

```python
def recommend_fruit_nitrogen(
    crop: str,
    soil_category: str,              # FruitSoilCategory value
    orchard_management: str | None = None,  # OrchardManagement value; required for top fruit
    sns_index: int | None = None,    # Required for strawberry crops
) -> float:
    """Return kg N/ha for a fruit, vine or hop crop.

    Args:
        crop: A fruit crop slug (category == "fruit").
        soil_category: FruitSoilCategory value.
        orchard_management: OrchardManagement value; required for top fruit only.
        sns_index: SNS index 0–5; required for strawberry crops only.

    Returns:
        Nitrogen recommendation in kg N/ha.

    Raises:
        ValueError: If crop is unknown, parameters are missing/invalid, or no
                    table entry exists for the given combination.
    """
```

Logic:
- Validate `crop` is a fruit category crop.
- Validate `soil_category` is a `FruitSoilCategory` value.
- **Pre-planting crops** (`fruit-preplant`, `hops-preplant`): return 0 kg N/ha.
  For `hops-preplant` add note "Potted hop plants benefit from 70–80 kg N/ha applied
  in spring before planting."
- **Top fruit** (`fruit-dessert-apple`, `fruit-culinary-apple`, `fruit-pear`,
  `fruit-cherry`, `fruit-plum`): require `orchard_management`; look up
  `FRUIT_TOP_NITROGEN[(crop, soil_category, orchard_management)]`.
- **Soft fruit and vines** (not strawberry): look up
  `FRUIT_SOFT_NITROGEN[(crop, soil_category)]`.
- **Strawberries** (`fruit-strawberry-main`, `fruit-strawberry-ever`): require
  `sns_index`; map `"clay"` → `"other-mineral"` for table lookup; look up
  `FRUIT_STRAWBERRY_NITROGEN[(crop, mapped_soil, min(sns_index, 5))]`.
- **Hops** (`fruit-hops`): look up `FRUIT_HOPS_NITROGEN[soil_category]`; raise
  `ValueError` if `soil_category == "light-sand"` (not in Table 7.17).

### 4d. New function `recommend_fruit_pkm()`

```python
def recommend_fruit_pkm(
    crop: str,
    p_index: int,
    k_index: int,
    mg_index: int,
) -> tuple[float, float, float]:
    """Return (P2O5, K2O, MgO) kg/ha for a fruit, vine or hop crop.

    Args:
        crop: A fruit crop slug.
        p_index: Soil P index 0–9.
        k_index: Soil K index 0–9.
        mg_index: Soil Mg index 0–9.

    Returns:
        Tuple of (phosphate, potash, magnesium) in kg/ha.
    """
```

Logic:
- Validate indices 0–9.
- **Pre-planting crops**: clamp index to 5; look up `FRUIT_PREPLANT_PKM` using
  `("fruit-vines", nutrient, clamped)` for `fruit-preplant` and
  `("hops", nutrient, clamped)` for `hops-preplant`.
- **Top fruit**: clamp index to 4; look up `FRUIT_TOP_PKM[(nutrient, clamped)]`.
- **Soft fruit and vines** (not strawberry): clamp index to 4; look up
  `FRUIT_SOFT_PKM[(crop, nutrient, clamped)]`.
- **Strawberries**: clamp index to 4; look up `FRUIT_STRAWBERRY_PKM[(nutrient, clamped)]`.
- **Hops**: clamp index to 5; look up `FRUIT_HOPS_PKM[(nutrient, clamped)]`.

### 4e. New function `recommend_fruit_all()`

```python
def recommend_fruit_all(
    crop: str,
    soil_category: str,
    p_index: int,
    k_index: int,
    mg_index: int,
    orchard_management: str | None = None,
    sns_index: int | None = None,
) -> NutrientRecommendation:
    """Return full N/P/K/Mg recommendation for a fruit, vine or hop crop."""
```

Returns a `NutrientRecommendation` dataclass (same as `recommend_all()`). Calls
`recommend_fruit_nitrogen()` and `recommend_fruit_pkm()` internally. Adds crop-specific
advisory notes:

- **Cider apples K note**: "Cider apples respond to Soil K Index 3. Consider applying K
  at Index 3 if growing cider apples."
- **Blackcurrant Ben-series note**: for `fruit-blackcurrant`, "Ben-series varieties typically
  require only 70–120 kg N/ha."
- **Sulphate of potash note**: for `fruit-redcurrant`, `fruit-gooseberry`, `fruit-raspberry`,
  when `k_index` is 0 or 1 and K recommendation > 120 kg/ha, add "Use sulphate of potash
  for this crop."
- **Hops Verticillium note**: for `fruit-hops`, "Where Verticillium wilt risk is present,
  reduce N to 125–165 kg N/ha."
- **Hops organic manure note**: for `fruit-hops`, "Reduce N by 70 kg/ha where large
  frequent organic manure applications have been used in the previous year."
- **Hops N split note**: for `fruit-hops`, "Split N into 2–3 dressings: late March/April,
  May, and late June/early July."
- **Strawberry SNS note**: for strawberry crops, "Nitrogen recommendations are based on
  SNS Index. Use `veg-sns` or `veg-smn` commands to determine SNS Index (Section 6 system)."
- **K:Mg ratio note**: for `fruit-hops` and strawberry crops, "Ensure soil K:Mg ratio
  (mg/litre) does not exceed 3:1 to avoid induced magnesium deficiency."
- **Top fruit N excess warning**: "Excess nitrogen reduces red colour in apples, encourages
  large dark leaves and can reduce storage life. Consider leaf and fruit analysis."

### 4f. Sulphur for fruit crops — `rb209/data/sulfur.py`

Add entries for fruit crops to the existing sulfur data. Section 7 states fruit crops are
"not generally thought to respond to sulphur" but a response is possible on light/low-OM
soils. Return 0 as the default (no recommendation) for all fruit crops; the engine note
should mention that 15–25 kg SO₃/ha may be applied in spring as sulphate where deficiency
is recognised.

```python
# All fruit crops — no routine recommendation; 0 flags as advisory-only
"fruit-preplant":        0,
"hops-preplant":         0,
"fruit-dessert-apple":   0,
"fruit-culinary-apple":  0,
"fruit-pear":            0,
"fruit-cherry":          0,
"fruit-plum":            0,
"fruit-blackcurrant":    0,
"fruit-redcurrant":      0,
"fruit-gooseberry":      0,
"fruit-raspberry":       0,
"fruit-loganberry":      0,
"fruit-tayberry":        0,
"fruit-blackberry":      0,
"fruit-strawberry-main": 0,
"fruit-strawberry-ever": 0,
"fruit-vine":            0,
"fruit-hops":            0,
```

Add a note in the engine output for all fruit crops: "Fruit crops do not routinely require
sulphur. Apply 15–25 kg SO₃/ha as sulphate in spring where deficiency is recognised, on
light sandy or low-OM soils."

---

## 5. CLI Changes — `rb209/cli.py`

### 5a. New `--soil-category` argument

Add `--soil-category` / `-sc` to the `recommend` and `nitrogen` subcommands. Takes a
`FruitSoilCategory` string value. Help text: "Soil category for fruit/vine/hop nitrogen
recommendation (light-sand | deep-silt | clay | other-mineral)."

### 5b. New `--orchard-management` argument

Add `--orchard-management` / `-om` to the `recommend` and `nitrogen` subcommands. Takes an
`OrchardManagement` string value. Required when crop is a top fruit slug. Help text:
"Orchard management system for top fruit nitrogen (grass-strip | overall-grass)."

### 5c. New `fruit-recommend` subcommand

Add a `fruit-recommend` subcommand that calls `recommend_fruit_all()`.

Arguments:
- `crop` (positional): any fruit category slug
- `--soil-category` / `-sc` (required)
- `--p-index` / `-p` (int, required)
- `--k-index` / `-k` (int, required)
- `--mg-index` / `-mg` (int, required)
- `--orchard-management` / `-om` (optional, required for top fruit)
- `--sns-index` / `-sns` (int, optional, required for strawberries)
- `--format` (table | json, default table)

### 5d. New `fruit-nitrogen` subcommand

Add a `fruit-nitrogen` subcommand that calls `recommend_fruit_nitrogen()`.

Arguments:
- `crop` (positional)
- `--soil-category` / `-sc` (required)
- `--orchard-management` / `-om` (optional, for top fruit)
- `--sns-index` / `-sns` (int, optional, for strawberries)

### 5e. Group fruit crops in `list-crops` output

The `list-crops` command should show a `fruit` section listing all 18 fruit slugs alongside
their display names, consistent with how the vegetables section is displayed.

---

## 6. Tests — `tests/test_fruit.py`

Create a new test file covering:

1. **FruitSoilCategory enum** — verify all four values exist and reject invalid strings.

2. **OrchardManagement enum** — verify both values exist.

3. **Pre-planting P/K/Mg** — check `fruit-preplant` and `hops-preplant` at indices 0 and 2:
   - `fruit-preplant`: P Index 0 → 200, P Index 2 → 50, K Index 1 → 100, Mg Index 2 → 85
   - `hops-preplant`: P Index 0 → 250, K Index 2 → 200, Mg Index 0 → 250

4. **Top fruit nitrogen (Table 7.4)** — spot-check at least 6 combinations:
   - Dessert apple, deep silt, grass-strip → 30
   - Dessert apple, deep silt, overall-grass → 70
   - Culinary apple, light-sand, grass-strip → 110
   - Culinary apple, clay, overall-grass → 110
   - Pear, other-mineral, grass-strip → 120
   - Cherry, light-sand, overall-grass → 180

5. **Top fruit P/K/Mg (Table 7.5)** — verify that all top fruit share the same table:
   - P Index 0 → 80, P Index 2 → 20
   - K Index 0 → 220, K Index 2 → 80
   - Mg Index 1 → 65, Mg Index 3 → 0

6. **Soft fruit nitrogen (Table 7.6)** — spot-check at least 6 combinations:
   - Blackcurrant, light-sand → 160
   - Blackcurrant, deep-silt → 110
   - Raspberry, light-sand → 120
   - Raspberry, clay → 80
   - Vine, deep-silt → 0
   - Vine, other-mineral → 40

7. **Soft fruit P/K/Mg (Table 7.7)** — verify group separation:
   - `fruit-blackcurrant`, K Index 0 → 250
   - `fruit-blackcurrant`, K Index 2 → 120
   - `fruit-blackberry`, K Index 0 → 220
   - `fruit-blackberry`, K Index 2 → 80
   - All crops, Mg Index 0 → 100

8. **Strawberry nitrogen (Table 7.8)** — verify SNS-index-based logic:
   - Main season, light-sand, SNS 0 → 60
   - Main season, deep-silt, SNS 0 → 0
   - Main season, other-mineral, SNS 2 → 30
   - Everbearer, light-sand, SNS 1 → 70
   - Everbearer, deep-silt, SNS 2 → 30
   - Clay mapped to other-mineral for strawberries

9. **Strawberry P/K/Mg (Table 7.9)** — verify P Index 0 → 110, K Index 1 → 150.

10. **Hops nitrogen (Table 7.17)** — verify three soil categories:
    - Deep silty → 180
    - Clay → 200
    - Other mineral → 220
    - Light sand → raises `ValueError`

11. **Hops P/K/Mg (Table 7.17)** — verify extended index range:
    - P Index 0 → 250, P Index 5 → 0
    - K Index 0 → 425, K Index 3 → 200, K Index 5 → 0
    - Mg Index 2 → 50

12. **Engine integration** — call `recommend_fruit_all()` for 4 representative crops and
    assert all returned P/K/Mg values match expected:
    - Dessert apple, light-sand, grass-strip, P/K/Mg Index 2
    - Raspberry, other-mineral, P/K/Mg Index 1
    - Strawberry main season, light-sand, SNS 1, P/K/Mg Index 2
    - Hops, clay, P/K/Mg Index 2

13. **Sulphur** — verify all 18 fruit crops return 0 from `recommend_sulfur()`.

14. **Advisory notes** — verify that key notes appear in `recommend_fruit_all()` output for:
    - `fruit-culinary-apple` (cider K note)
    - `fruit-blackcurrant` (Ben-series note)
    - `fruit-hops` (Verticillium note, split-N note)
    - `fruit-strawberry-main` (SNS note, K:Mg ratio note)

15. **Error handling** — confirm `ValueError` is raised for:
    - Unknown crop slug
    - Top fruit without `orchard_management`
    - Strawberry without `sns_index`
    - Hops with `soil_category == "light-sand"`
    - Out-of-range index values

---

## 7. Implementation Order

1. `models.py` — add `FruitSoilCategory` and `OrchardManagement` enums
2. `data/fruit.py` — create new module with all 9 lookup tables (Sections 3a–3i)
3. `data/crops.py` — add 18 fruit/vine/hop crop entries
4. `data/sulfur.py` — add fruit crop SO₃ entries (all 0, advisory note only)
5. `engine.py` — add `_is_fruit_crop()`, `recommend_fruit_nitrogen()`,
   `recommend_fruit_pkm()`, and `recommend_fruit_all()`
6. `cli.py` — add `--soil-category`, `--orchard-management` flags and
   `fruit-recommend`, `fruit-nitrogen` subcommands
7. `tests/test_fruit.py` — full test suite

---

## 8. Out of Scope

The following are documented in Section 7 but are not part of this implementation plan:

- **Leaf analysis tables** (Tables 7.11–7.13) — reference ranges for diagnosing deficiencies;
  no kg/ha recommendation values to compute. Out of scope.
- **Apple fruit analysis tables** (Tables 7.14–7.15) — storage quality diagnostics; no
  fertiliser recommendations to compute. Out of scope.
- **Substrate strawberry nutrient solution** (Table 7.10) — mg/litre ranges for fertigation
  of substrate-grown crops; outside the soil-applied kg/ha model. Out of scope.
- **Fertigation guidance** (young trees, strawberries) — advisory text with no
  programmable rate tables. Out of scope.
- **Micronutrient recommendations** (B, Cu, Fe, Mn, Zn) — qualitative foliar-spray guidance
  only; no kg/ha values to implement. Out of scope.
- **Liming calculations for fruit** — reuses the existing `calculate_lime()` function;
  Section 7 liming guidance (pre-plant 40 cm correction, frequency) should be exposed as
  advisory notes rather than new code.
- **NVZ N-max limits for fruit crops** — not reproduced in the `ref/` source files. Blocked
  pending source data.
