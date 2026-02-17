# RB209 CLI Reference

RB209 is a command-line tool for calculating fertiliser recommendations for UK agricultural crops. It implements the recommendation tables from the RB209 9th edition (Defra/AHDB Nutrient Management Guide) covering nitrogen, phosphorus, potassium, magnesium, sulfur, lime, and organic materials.

The tool supports 22 crop types across arable, grassland, and potato categories. All output is available as human-readable ASCII tables (default) or machine-readable JSON.

- **Entry points:** `rb209` (if installed) or `python -m rb209`
- **Python:** 3.10+
- **Dependencies:** None (pure Python, standard library only)
- **License:** GPL-3.0-or-later

## Installation

From the repository root:

```bash
pip install .
```

After installation, the `rb209` command is available. Alternatively, run directly as a Python module:

```bash
python -m rb209 --version
```

## Quick Start

A typical workflow has two steps: (1) determine the Soil Nitrogen Supply (SNS) index for your field, then (2) get a full nutrient recommendation using that index.

**Step 1 -- Calculate the SNS index:**

```
$ rb209 sns --previous-crop cereals --soil-type medium --rainfall medium
+----------------------------------+
| Soil Nitrogen Supply (SNS)       |
+----------------------------------+
|   SNS Index                      1 |
|   Previous crop            cereals |
|   Soil type                 medium |
|   Rainfall                  medium |
|   Method          field-assessment |
+----------------------------------+
| Previous crop 'cereals' has low  |
| N residue.                       |
+----------------------------------+
```

**Step 2 -- Get the full recommendation using the SNS index from step 1:**

```
$ rb209 recommend --crop winter-wheat-feed --sns-index 1 --p-index 2 --k-index 1
+--------------------------------------------------+
| Nutrient Recommendations — Winter Wheat (feed)   |
+--------------------------------------------------+
|   Nitrogen (N)        180 kg/ha                  |
|   Phosphorus (P2O5)    60 kg/ha                  |
|   Potassium (K2O)      75 kg/ha                  |
|   Magnesium (MgO)       0 kg/ha                  |
|   Sulfur (SO3)         30 kg/ha                  |
+--------------------------------------------------+
| K recommendation assumes straw removed.          |
| Feed wheat variety. For milling wheat use winter |
| -wheat-milling.                                  |
+--------------------------------------------------+
```

**Get JSON output for programmatic use:**

```
$ rb209 recommend --crop winter-wheat-feed --sns-index 2 --p-index 2 --k-index 1 --format json
{
  "crop": "Winter Wheat (feed)",
  "nitrogen": 150,
  "phosphorus": 60,
  "potassium": 75,
  "magnesium": 0,
  "sulfur": 30,
  "notes": [
    "K recommendation assumes straw removed.",
    "Feed wheat variety. For milling wheat use winter-wheat-milling."
  ]
}
```

## Output Formats

Every command supports the `--format` flag with two options:

| Value | Description |
|-------|-------------|
| `table` | Human-readable ASCII box (default) |
| `json` | Machine-readable JSON object or array |

Use `--format json` when parsing output programmatically. JSON output uses `dataclasses.asdict()` so field names match the Python data model exactly.

## Command Reference

### recommend

Full NPK + S + Mg nutrient recommendation for a crop.

**Usage:**

```
rb209 recommend --crop CROP --sns-index N --p-index N --k-index N [options]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop to get recommendations for |
| `--sns-index` | Yes | int | `0` to `6` | -- | Soil Nitrogen Supply index |
| `--p-index` | Yes | int | `0` to `9` | -- | Soil phosphorus index (clamped to 4) |
| `--k-index` | Yes | int | `0` to `9` | -- | Soil potassium index (clamped to 4) |
| `--mg-index` | No | int | `0` to `9` | `2` | Soil magnesium index (clamped to 4) |
| `--straw-removed` | No | flag | -- | true | Straw removed from field (cereals only) |
| `--straw-incorporated` | No | flag | -- | false | Straw incorporated (cereals only; overrides `--straw-removed`) |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 recommend --crop winter-wheat-feed --sns-index 2 --p-index 2 --k-index 1
+--------------------------------------------------+
| Nutrient Recommendations — Winter Wheat (feed)   |
+--------------------------------------------------+
|   Nitrogen (N)        150 kg/ha                  |
|   Phosphorus (P2O5)    60 kg/ha                  |
|   Potassium (K2O)      75 kg/ha                  |
|   Magnesium (MgO)       0 kg/ha                  |
|   Sulfur (SO3)         30 kg/ha                  |
+--------------------------------------------------+
| K recommendation assumes straw removed.          |
| Feed wheat variety. For milling wheat use winter |
| -wheat-milling.                                  |
+--------------------------------------------------+
```

**Example (JSON):**

```json
{
  "crop": "Winter Wheat (feed)",
  "nitrogen": 150,
  "phosphorus": 60,
  "potassium": 75,
  "magnesium": 0,
  "sulfur": 30,
  "notes": [
    "K recommendation assumes straw removed.",
    "Feed wheat variety. For milling wheat use winter-wheat-milling."
  ]
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `crop` | string | Display name of the crop |
| `nitrogen` | float | Nitrogen recommendation (kg N/ha) |
| `phosphorus` | float | Phosphorus recommendation (kg P2O5/ha) |
| `potassium` | float | Potassium recommendation (kg K2O/ha) |
| `magnesium` | float | Magnesium recommendation (kg MgO/ha) |
| `sulfur` | float | Sulfur recommendation (kg SO3/ha) |
| `notes` | string[] | Advisory notes (may be empty) |

**Notes:**
- For cereal crops with `has_straw_option`, passing `--straw-incorporated` sets `straw_removed=false`, reducing the K recommendation. Default is straw removed.
- The `--mg-index` defaults to 2 (target index). At index 2 or above, MgO recommendation is 0.
- P, K, and Mg indices above 4 are clamped to 4, which returns 0 kg/ha for all three nutrients.

---

### nitrogen

Nitrogen recommendation for a single crop.

**Usage:**

```
rb209 nitrogen --crop CROP --sns-index N [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop type |
| `--sns-index` | Yes | int | `0` to `6` | -- | Soil Nitrogen Supply index |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 nitrogen --crop winter-barley --sns-index 3
+--------------------------------+
| Nitrogen (N) — Winter Barley   |
+--------------------------------+
|   Nitrogen (N)   100 kg/ha     |
+--------------------------------+
```

**Example (JSON):**

```json
{
  "crop": "Winter Barley",
  "nutrient": "Nitrogen (N)",
  "value": 100,
  "unit": "kg/ha"
}
```

**JSON schema (single nutrient):**

| Field | Type | Description |
|-------|------|-------------|
| `crop` | string | Display name of the crop |
| `nutrient` | string | Nutrient name and formula |
| `value` | float | Recommendation in stated unit |
| `unit` | string | Always `"kg/ha"` |

**Notes:**
- N-fixing crops (`peas`, `field-beans`) always return 0 at every SNS index.
- SNS index must be 0-6. Values outside this range produce an error.

---

### phosphorus

Phosphorus recommendation for a single crop.

**Usage:**

```
rb209 phosphorus --crop CROP --p-index N [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop type |
| `--p-index` | Yes | int | `0` to `9` | -- | Soil phosphorus index (clamped to 4) |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 phosphorus --crop winter-wheat-feed --p-index 2
+-------------------------------------------+
| Phosphorus (P2O5) — Winter Wheat (feed)   |
+-------------------------------------------+
|   Phosphorus (P2O5)   60 kg/ha            |
+-------------------------------------------+
```

**Example (JSON):**

```json
{
  "crop": "Winter Wheat (feed)",
  "nutrient": "Phosphorus (P2O5)",
  "value": 60,
  "unit": "kg/ha"
}
```

**Notes:**
- JSON schema is the same as [nitrogen](#nitrogen) (single nutrient format).
- Indices above 4 are clamped to 4 (returns 0 kg/ha).

---

### potassium

Potassium recommendation for a single crop.

**Usage:**

```
rb209 potassium --crop CROP --k-index N [options]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop type |
| `--k-index` | Yes | int | `0` to `9` | -- | Soil potassium index (clamped to 4) |
| `--straw-removed` | No | flag | -- | true | Straw removed (cereals only) |
| `--straw-incorporated` | No | flag | -- | false | Straw incorporated (cereals only; overrides `--straw-removed`) |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (straw removed, default):**

```
$ rb209 potassium --crop winter-wheat-feed --k-index 0
+-----------------------------------------+
| Potassium (K2O) — Winter Wheat (feed)   |
+-----------------------------------------+
|   Potassium (K2O)   105 kg/ha           |
+-----------------------------------------+
```

**Example (straw incorporated):**

```
$ rb209 potassium --crop winter-wheat-feed --k-index 0 --straw-incorporated
+-----------------------------------------+
| Potassium (K2O) — Winter Wheat (feed)   |
+-----------------------------------------+
|   Potassium (K2O)   65 kg/ha            |
+-----------------------------------------+
```

**Notes:**
- JSON schema is the same as [nitrogen](#nitrogen) (single nutrient format).
- For cereals, straw management changes the K recommendation. When straw is removed, more K fertiliser is needed. The `--straw-incorporated` flag overrides the default `--straw-removed`.
- Non-cereal crops ignore the straw flags.
- Indices above 4 are clamped to 4 (returns 0 kg/ha).

---

### sulfur

Sulfur recommendation for a single crop.

**Usage:**

```
rb209 sulfur --crop CROP [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop type |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 sulfur --crop winter-oilseed-rape
+--------------------------------------+
| Sulfur (SO3) — Winter Oilseed Rape   |
+--------------------------------------+
|   Sulfur (SO3)   75 kg/ha            |
+--------------------------------------+
```

**Notes:**
- JSON schema is the same as [nitrogen](#nitrogen) (single nutrient format).
- Sulfur recommendations are crop-specific and do not depend on a soil index.

---

### sns

Calculate the Soil Nitrogen Supply (SNS) index for a field using the field assessment method.

**Usage:**

```
rb209 sns --previous-crop CROP --soil-type TYPE --rainfall LEVEL [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--previous-crop` | Yes | string | `cereals`, `oilseed-rape`, `potatoes`, `sugar-beet`, `peas-beans`, `linseed`, `forage-maize`, `set-aside`, `grass-1-2yr`, `grass-long-term`, `vegetables`, `fallow` | -- | Previous crop grown in this field |
| `--soil-type` | Yes | string | `light`, `medium`, `heavy`, `organic` | -- | Soil texture category |
| `--rainfall` | Yes | string | `low`, `medium`, `high` | -- | Excess winter rainfall category |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 sns --previous-crop cereals --soil-type medium --rainfall medium
+----------------------------------+
| Soil Nitrogen Supply (SNS)       |
+----------------------------------+
|   SNS Index                      1 |
|   Previous crop            cereals |
|   Soil type                 medium |
|   Rainfall                  medium |
|   Method          field-assessment |
+----------------------------------+
| Previous crop 'cereals' has low  |
| N residue.                       |
+----------------------------------+
```

**Example (JSON):**

```json
{
  "sns_index": 1,
  "previous_crop": "cereals",
  "soil_type": "medium",
  "rainfall": "medium",
  "method": "field-assessment",
  "notes": [
    "Previous crop 'cereals' has low N residue."
  ]
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `sns_index` | int | Calculated SNS index (0-6) |
| `previous_crop` | string | Previous crop value as provided |
| `soil_type` | string | Soil type as provided |
| `rainfall` | string | Rainfall category as provided |
| `method` | string | Always `"field-assessment"` |
| `notes` | string[] | Includes the N-residue category of the previous crop |

**Notes:**
- The SNS index is derived from a three-way lookup: previous crop determines an N-residue category (low/medium/high/very-high), which combines with soil type and rainfall to produce the index. See [Previous Crops and N-Residue Categories](#previous-crops-and-n-residue-categories) for the mapping.
- Use the resulting `sns_index` value as the `--sns-index` argument to `recommend` or `nitrogen`.

---

### organic

Calculate nutrients supplied by an organic material application.

**Usage:**

```
rb209 organic --material MATERIAL --rate RATE [--timing SEASON] [--incorporated] [--soil-type TYPE] [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--material` | Yes | string | `cattle-fym`, `pig-fym`, `sheep-fym`, `horse-fym`, `poultry-litter`, `layer-manure`, `cattle-slurry`, `pig-slurry`, `green-compost`, `green-food-compost`, `biosolids-cake`, `paper-crumble` | -- | Organic material type |
| `--rate` | Yes | float | >= 0 | -- | Application rate (t/ha for solids, m3/ha for slurries) |
| `--timing` | No | string | `autumn`, `winter`, `spring`, `summer` | -- | Application season for timing-adjusted available-N (see note below) |
| `--incorporated` | No | flag | -- | false | Material is soil-incorporated promptly after application (within 6 h for slurries) |
| `--soil-type` | No | string | `light`, `medium`, `heavy`, `organic` | medium-heavy | Soil type for timing-adjusted lookup |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (flat default — no timing):**

```
$ rb209 organic --material cattle-fym --rate 25
+----------------------------------+
| Organic Nutrients — Cattle FYM   |
+----------------------------------+
|   Application rate            25.0 |
|   Total N              150.0 kg/ha |
|   Available N (yr 1)    30.0 kg/ha |
|   P2O5                  80.0 kg/ha |
|   K2O                  200.0 kg/ha |
|   MgO                   45.0 kg/ha |
|   SO3                   75.0 kg/ha |
+----------------------------------+
```

**Example (timing-adjusted — pig slurry, spring, incorporated within 6 h):**

```
$ rb209 organic --material pig-slurry --rate 30 --timing spring --incorporated
+------------------------------------+
| Organic Nutrients — Pig Slurry (4% |
|  DM)                               |
+------------------------------------+
|   Application rate              30.0 |
|   Total N               108.0 kg/ha |
|   Available N (yr 1)     64.8 kg/ha |
|   P2O5                   60.0 kg/ha |
|   K2O                    48.0 kg/ha |
|   MgO                    15.0 kg/ha |
|   SO3                    24.0 kg/ha |
+------------------------------------+
```

**Example (JSON):**

```json
{
  "material": "Cattle FYM",
  "rate": 25.0,
  "total_n": 150.0,
  "available_n": 30.0,
  "p2o5": 80.0,
  "k2o": 200.0,
  "mgo": 45.0,
  "so3": 75.0
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `material` | string | Display name of the organic material |
| `rate` | float | Application rate as provided |
| `total_n` | float | Total nitrogen (kg/ha) |
| `available_n` | float | Crop-available nitrogen in year 1 (kg/ha) |
| `p2o5` | float | Phosphorus as P2O5 (kg/ha) |
| `k2o` | float | Potassium as K2O (kg/ha) |
| `mgo` | float | Magnesium as MgO (kg/ha) |
| `so3` | float | Sulfur as SO3 (kg/ha) |

**Notes:**
- `total_n` is the total nitrogen in the application. `available_n` is the portion available to the crop in year 1 (typically 10–30 % of total N for farmyard manures, higher for slurries).
- Solid materials (FYM, compost, cake, litter) use t/ha. Slurries use m3/ha. See [Organic Materials](#organic-materials) for units per material.
- Nutrient values are calculated as `per_unit_content × rate`, rounded to 1 decimal place.
- **Timing-adjusted available-N** is currently supported for `pig-slurry` only, using RB209 Table 2.12 percentage factors. When `--timing` is omitted, the flat default coefficient is used (60 % of total N for pig slurry, reflecting a spring application). Timing seasons: `autumn` = Aug–Oct, `winter` = Nov–Jan, `spring` = Feb–Apr, `summer` = grassland use only. Incorporating slurry promptly (`--incorporated`) increases the retained nitrogen; for pig slurry in spring this raises available N from 50 % to 60 % of total N. The `--soil-type` argument selects the correct column in Table 2.12 — `light` maps to the sandy/shallow category; all other soil types map to medium/heavy.

---

### lime

Calculate lime requirement to raise soil pH.

**Usage:**

```
rb209 lime --current-ph PH --target-ph PH --soil-type TYPE [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--current-ph` | Yes | float | `3.0` to `9.0` | -- | Current soil pH |
| `--target-ph` | Yes | float | `4.0` to `8.5` | -- | Target soil pH |
| `--soil-type` | Yes | string | `light`, `medium`, `heavy`, `organic` | -- | Soil texture category |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 lime --current-ph 5.8 --target-ph 6.5 --soil-type medium
+--------------------------------+
| Lime Requirement               |
+--------------------------------+
|   Current pH                 5.8 |
|   Target pH                  6.5 |
|   Soil type               medium |
|   Lime required   3.9 t CaCO3/ha |
+--------------------------------+
```

**Example (JSON):**

```json
{
  "current_ph": 5.8,
  "target_ph": 6.5,
  "soil_type": "medium",
  "lime_required": 3.9,
  "notes": []
}
```

**Example (split dressing -- large lime requirement):**

```
$ rb209 lime --current-ph 4.5 --target-ph 7.5 --soil-type heavy
+---------------------------------+
| Lime Requirement                |
+---------------------------------+
|   Current pH                  4.5 |
|   Target pH                   7.5 |
|   Soil type                 heavy |
|   Lime required   22.5 t CaCO3/ha |
+---------------------------------+
| Total lime required (22.5 t/ha) |
|  exceeds single application max |
| imum (7.5 t/ha). Apply in split |
|  dressings over successive year |
| s.                              |
+---------------------------------+
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `current_ph` | float | Current soil pH as provided |
| `target_ph` | float | Target soil pH as provided |
| `soil_type` | string | Soil type as provided |
| `lime_required` | float | Lime requirement (t CaCO3/ha) |
| `notes` | string[] | Advisory notes (e.g. split dressing advice) |

**Notes:**
- If `current_ph >= target_ph`, lime required is 0 and a note explains no lime is needed.
- Lime requirement = (target_ph - current_ph) * soil_factor. Soil factors: light=4.0, medium=5.5, heavy=7.5, organic=11.0 t CaCO3/ha per pH unit.
- If lime required exceeds 7.5 t/ha, the tool advises splitting applications over successive years.

---

### list-crops

List available crop types.

**Usage:**

```
rb209 list-crops [--category CATEGORY] [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--category` | No | string | `arable`, `grassland`, `potatoes` | -- | Filter to a single crop category |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table, all crops):**

```
$ rb209 list-crops
Available Crops
===============

  ARABLE
  --------------------------------------------------
    field-beans                    Field Beans
    forage-maize                   Forage Maize
    linseed                        Linseed
    peas                           Peas
    spring-barley                  Spring Barley
    spring-oats                    Spring Oats
    spring-oilseed-rape            Spring Oilseed Rape
    spring-wheat                   Spring Wheat
    sugar-beet                     Sugar Beet
    winter-barley                  Winter Barley
    winter-oats                    Winter Oats
    winter-oilseed-rape            Winter Oilseed Rape
    winter-rye                     Winter Rye
    winter-wheat-feed              Winter Wheat (feed)
    winter-wheat-milling           Winter Wheat (milling)

  GRASSLAND
  --------------------------------------------------
    grass-grazed                   Grass (grazed only)
    grass-grazed-one-cut           Grass (grazed + 1 silage cut)
    grass-hay                      Grass (hay)
    grass-silage                   Grass (silage, multi-cut)

  POTATOES
  --------------------------------------------------
    potatoes-early                 Potatoes (early)
    potatoes-maincrop              Potatoes (maincrop)
    potatoes-seed                  Potatoes (seed)
```

**Example (JSON, filtered to arable):**

```
$ rb209 list-crops --category arable --format json
```

Returns a JSON array of objects, each with `value`, `name`, and `category` fields:

```json
[
  {"value": "field-beans", "name": "Field Beans", "category": "arable"},
  {"value": "forage-maize", "name": "Forage Maize", "category": "arable"},
  ...
]
```

**JSON schema (array element):**

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | CLI argument value to pass to `--crop` |
| `name` | string | Human-readable display name |
| `category` | string | One of `arable`, `grassland`, `potatoes` |

---

### list-materials

List available organic materials.

**Usage:**

```
rb209 list-materials [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 list-materials
Available Organic Materials
===========================

  Value                     Name                                Unit
  --------------------------------------------------------------------
  cattle-fym                Cattle FYM                          t
  pig-fym                   Pig FYM                             t
  sheep-fym                 Sheep FYM                           t
  horse-fym                 Horse FYM                           t
  poultry-litter            Poultry Litter (broiler/turkey)     t
  layer-manure              Layer Manure                        t
  cattle-slurry             Cattle Slurry (6% DM)               m3
  pig-slurry                Pig Slurry (4% DM)                  m3
  green-compost             Green Compost                       t
  green-food-compost        Green/Food Compost                  t
  biosolids-cake            Biosolids Cake (sewage sludge)      t
  paper-crumble             Paper Crumble                       t
```

**JSON schema (array element):**

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | CLI argument value to pass to `--material` |
| `name` | string | Human-readable display name |
| `unit` | string | `t` (tonnes/ha) or `m3` (cubic metres/ha) |

## Valid Values Reference

### Crops

22 crops in 3 categories. Use the **Value** column as the `--crop` argument.

**Arable (15):**

| Value | Display Name | Straw Option |
|-------|-------------|-------------|
| `field-beans` | Field Beans | No |
| `forage-maize` | Forage Maize | No |
| `linseed` | Linseed | No |
| `peas` | Peas | No |
| `spring-barley` | Spring Barley | Yes |
| `spring-oats` | Spring Oats | Yes |
| `spring-oilseed-rape` | Spring Oilseed Rape | No |
| `spring-wheat` | Spring Wheat | Yes |
| `sugar-beet` | Sugar Beet | No |
| `winter-barley` | Winter Barley | Yes |
| `winter-oats` | Winter Oats | Yes |
| `winter-oilseed-rape` | Winter Oilseed Rape | No |
| `winter-rye` | Winter Rye | Yes |
| `winter-wheat-feed` | Winter Wheat (feed) | Yes |
| `winter-wheat-milling` | Winter Wheat (milling) | Yes |

**Grassland (4):**

| Value | Display Name |
|-------|-------------|
| `grass-grazed` | Grass (grazed only) |
| `grass-grazed-one-cut` | Grass (grazed + 1 silage cut) |
| `grass-hay` | Grass (hay) |
| `grass-silage` | Grass (silage, multi-cut) |

**Potatoes (3):**

| Value | Display Name |
|-------|-------------|
| `potatoes-early` | Potatoes (early) |
| `potatoes-maincrop` | Potatoes (maincrop) |
| `potatoes-seed` | Potatoes (seed) |

### Soil Types

| Value | Description |
|-------|-------------|
| `light` | Sandy, shallow soils |
| `medium` | Loamy soils |
| `heavy` | Clay, deep soils |
| `organic` | Peaty, organic soils |

Used by `sns`, `lime`, and accepted by those commands via `--soil-type`.

### Previous Crops and N-Residue Categories

Used by the `sns` command via `--previous-crop`. The previous crop determines an N-residue category, which feeds into the SNS lookup.

| Previous Crop Value | N-Residue Category |
|--------------------|--------------------|
| `cereals` | low |
| `sugar-beet` | low |
| `linseed` | low |
| `forage-maize` | low |
| `set-aside` | low |
| `fallow` | low |
| `oilseed-rape` | medium |
| `potatoes` | medium |
| `peas-beans` | high |
| `vegetables` | high |
| `grass-1-2yr` | high |
| `grass-long-term` | very-high |

### Rainfall Categories

Used by the `sns` command via `--rainfall`.

| Value | Excess Winter Rainfall |
|-------|----------------------|
| `low` | < 150 mm |
| `medium` | 150 -- 250 mm |
| `high` | > 250 mm |

### Organic Materials

Used by the `organic` command via `--material`. Per-unit nutrient content (kg per tonne for solids, kg per m3 for slurries):

| Value | Name | Unit | Total N | Avail N | P2O5 | K2O | MgO | SO3 |
|-------|------|------|---------|---------|------|-----|-----|-----|
| `cattle-fym` | Cattle FYM | t | 6.0 | 1.2 | 3.2 | 8.0 | 1.8 | 3.0 |
| `pig-fym` | Pig FYM | t | 7.0 | 1.4 | 6.0 | 5.0 | 1.5 | 3.0 |
| `sheep-fym` | Sheep FYM | t | 7.0 | 1.4 | 3.2 | 6.0 | 2.0 | 4.0 |
| `horse-fym` | Horse FYM | t | 5.0 | 1.0 | 3.5 | 6.0 | 1.5 | 2.0 |
| `poultry-litter` | Poultry Litter (broiler/turkey) | t | 19.0 | 5.7 | 14.0 | 9.5 | 3.5 | 5.0 |
| `layer-manure` | Layer Manure | t | 16.0 | 4.8 | 13.0 | 8.0 | 3.0 | 5.5 |
| `cattle-slurry` | Cattle Slurry (6% DM) | m3 | 2.6 | 0.8 | 1.2 | 2.5 | 0.5 | 0.8 |
| `pig-slurry` | Pig Slurry (4% DM) | m3 | 3.6 | 2.167 | 2.0 | 1.6 | 0.5 | 0.8 |
| `green-compost` | Green Compost | t | 4.3 | 0.4 | 3.0 | 4.2 | 1.5 | 2.5 |
| `green-food-compost` | Green/Food Compost | t | 8.0 | 0.8 | 4.5 | 6.0 | 2.0 | 4.0 |
| `biosolids-cake` | Biosolids Cake (sewage sludge) | t | 12.5 | 2.5 | 12.0 | 0.5 | 2.0 | 7.0 |
| `paper-crumble` | Paper Crumble | t | 3.0 | 0.3 | 1.5 | 0.5 | 2.5 | 4.0 |

### Nutrient Indices

| Index Type | CLI Argument | Range | Data Range | Clamping |
|-----------|-------------|-------|------------|----------|
| SNS | `--sns-index` | 0 -- 6 | 0 -- 6 | None (strict) |
| Phosphorus | `--p-index` | 0 -- 9 | 0 -- 4 | Values > 4 clamped to 4 |
| Potassium | `--k-index` | 0 -- 9 | 0 -- 4 | Values > 4 clamped to 4 |
| Magnesium | `--mg-index` | 0 -- 9 | 0 -- 4 | Values > 4 clamped to 4 |

At index 4, P/K/Mg recommendations are 0 kg/ha (soil has sufficient nutrients). Index 0 indicates a severely deficient soil with the highest fertiliser requirement.

## Domain Concepts

### What is RB209?

RB209 is the UK government's (Defra/AHDB) standard reference for fertiliser use on agricultural crops, now in its 9th edition. It provides nutrient management recommendations based on soil analysis, crop type, and field history. This CLI implements the core recommendation tables from that publication.

### Soil Nutrient Indices

After soil testing, each nutrient (P, K, Mg) is assigned an index number. A lower index indicates greater deficiency and therefore a higher fertiliser requirement. The index scale is 0-9 in UK soil analysis, but the RB209 recommendation tables only have data for indices 0-4. At index 4 and above, no fertiliser is recommended because the soil already has sufficient nutrients.

### Soil Nitrogen Supply (SNS)

Unlike P, K, and Mg, nitrogen availability is not measured by a single soil test. Instead, the SNS index (0-6) is estimated from field history using three factors:

1. **Previous crop** -- determines how much nitrogen residue is left in the soil (categorised as low, medium, high, or very-high)
2. **Soil type** -- affects how nitrogen is retained or leached
3. **Rainfall** -- excess winter rainfall leaches nitrogen from the soil

A higher SNS index means more nitrogen is already available in the soil, so less fertiliser nitrogen is needed. The `sns` command performs this lookup.

### Straw Management

For cereal crops (wheat, barley, oats, rye), the potassium recommendation depends on whether straw is removed from the field or incorporated back into the soil. Straw contains potassium, so:

- **Straw removed** (default): higher K recommendation to replace exported nutrients
- **Straw incorporated**: lower K recommendation because nutrients are recycled

Non-cereal crops are not affected by the straw flags.

### Index Clamping

The P, K, and Mg index arguments accept values 0-9 to match the full UK soil index scale, but the recommendation lookup tables only contain data for indices 0-4. Any index above 4 is silently clamped to 4 before lookup. Since index 4 returns 0 kg/ha for all three nutrients, passing index 5-9 also returns 0. The SNS index (0-6) is not clamped and rejects out-of-range values with an error.

### Lime Calculation

Lime requirement is calculated as:

```
lime (t CaCO3/ha) = (target_pH - current_pH) * soil_factor
```

Soil factors (tonnes CaCO3/ha per pH unit): light = 4.0, medium = 5.5, heavy = 7.5, organic = 11.0. Heavier and organic soils have greater buffering capacity and need more lime to change pH.

The maximum single application is 7.5 t/ha. If the calculated requirement exceeds this, the tool advises applying lime in split dressings over successive years.

### Organic Material Nutrients

Organic materials (manures, slurries, composts) supply multiple nutrients. The `organic` command reports both **total nitrogen** and **available nitrogen** (crop-available in year 1). Available N is typically 10–30 % of total N for farmyard manures, and higher (35–60 %) for slurries and poultry manures.

By default, `available_n` is calculated from the flat per-unit coefficient in the RB209 typical-values tables. For **pig slurry**, the more accurate approach from RB209 Section 2 (Table 2.12) is available via the `--timing`, `--incorporated`, and `--soil-type` flags: the available-N fraction ranges from 10 % (autumn, sandy soil, surface-applied) to 60 % (spring, any soil, incorporated within 6 hours). See the [`organic` command](#organic) for details.

### Nutrient Units

All nutrient recommendations use UK agricultural conventions:

| Nutrient | Unit | Notes |
|----------|------|-------|
| Nitrogen | kg N/ha | Elemental nitrogen |
| Phosphorus | kg P2O5/ha | Phosphorus pentoxide (oxide form) |
| Potassium | kg K2O/ha | Potassium oxide (oxide form) |
| Magnesium | kg MgO/ha | Magnesium oxide (oxide form) |
| Sulfur | kg SO3/ha | Sulfur trioxide (oxide form) |
| Lime | t CaCO3/ha | Calcium carbonate equivalent |

## Error Handling and Exit Codes

| Exit Code | Meaning | Cause |
|-----------|---------|-------|
| `0` | Success | Command completed normally |
| `1` | Validation error | Invalid index range, unknown material, pH out of range |
| `2` | Argument error | Missing required arguments, invalid choice for enum values |

**Example -- invalid choice (exit code 2):**

```
$ rb209 nitrogen --crop invalid-crop --sns-index 2
rb209 nitrogen: error: argument --crop: invalid choice: 'invalid-crop'
```

Argparse rejects the value before the engine runs.

**Example -- out of range index (exit code 1):**

```
$ rb209 nitrogen --crop winter-wheat-feed --sns-index 9
Error: SNS index must be an integer between 0 and 6, got 9
```

The value is syntactically valid but fails engine validation.

**Example -- missing required arguments (exit code 2):**

```
$ rb209 recommend
rb209 recommend: error: the following arguments are required: --crop, --sns-index, --p-index, --k-index
```
