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
| `--straw-removed` | No | flag | -- | true | Straw removed from field (cereals only; mutually exclusive with `--straw-incorporated`) |
| `--straw-incorporated` | No | flag | -- | false | Straw incorporated (cereals only; mutually exclusive with `--straw-removed`) |
| `--soil-type` | No | string | `light`, `medium`, `heavy`, `organic` | -- | Soil type for soil-specific N recommendation. When provided for a crop that has no soil-specific data, falls back to the generic recommendation table. |
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
- For cereal crops with `has_straw_option`, passing `--straw-incorporated` sets `straw_removed=false`, reducing the K recommendation. Default is straw removed. `--straw-removed` and `--straw-incorporated` are mutually exclusive; passing both is an error.
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
| `--soil-type` | No | string | `light`, `medium`, `heavy`, `organic` | -- | Soil type for soil-specific N recommendation. When provided for a crop that has no soil-specific data, falls back to the generic recommendation table. |
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
| `--straw-removed` | No | flag | -- | true | Straw removed (cereals only; mutually exclusive with `--straw-incorporated`) |
| `--straw-incorporated` | No | flag | -- | false | Straw incorporated (cereals only; mutually exclusive with `--straw-removed`) |
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
- For cereals, straw management changes the K recommendation. When straw is removed, more K fertiliser is needed. `--straw-removed` and `--straw-incorporated` are mutually exclusive flags; passing both is an error.
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

Calculate the Soil Nitrogen Supply (SNS) index for a field using the field assessment method. Optionally, supply grass ley history flags to perform a combined assessment (field-assessment + Table 4.6) in a single command.

**Usage:**

```
rb209 sns --previous-crop CROP --soil-type TYPE --rainfall LEVEL [--ley-age AGE --ley-n-intensity LEVEL --ley-management REGIME] [--ley-year N] [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--previous-crop` | Yes | string | `cereals`, `oilseed-rape`, `potatoes`, `sugar-beet`, `peas-beans`, `linseed`, `forage-maize`, `set-aside`, `grass-1-2yr`, `grass-3-5yr`, `grass-long-term`, `vegetables`, `fallow` | -- | Previous crop grown in this field |
| `--soil-type` | Yes | string | `light`, `medium`, `heavy`, `organic` | -- | Soil texture category |
| `--rainfall` | Yes | string | `low`, `medium`, `high` | -- | Excess winter rainfall category |
| `--ley-age` | No | string | `1-2yr`, `3-5yr` | -- | Grass ley duration for combined assessment (requires `--ley-n-intensity` and `--ley-management`) |
| `--ley-n-intensity` | No | string | `low`, `high` | -- | N management intensity of the grass ley |
| `--ley-management` | No | string | `cut`, `grazed`, `1-cut-then-grazed` | -- | Ley management regime |
| `--ley-year` | No | int | `1`, `2`, `3` | `2` | Year after ploughing out the ley |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (field assessment only):**

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

**Example (combined assessment with grass ley history):**

```
$ rb209 sns --previous-crop cereals --soil-type heavy --rainfall high \
    --ley-age 1-2yr --ley-n-intensity high --ley-management grazed --ley-year 2
```

This performs both the field assessment (cereals, heavy, high → SNS 1) and the Table 4.6 lookup (1–2yr ley, high N, grazed, year 2 → SNS 2) and returns the higher value (SNS 2) with `method="combined"`.

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
| `method` | string | `"field-assessment"` or `"combined"` (when ley flags are used) |
| `notes` | string[] | Includes the N-residue category of the previous crop; when combined, also includes Table 4.6 details and which value was selected |

**Notes:**
- The SNS index is derived from a three-way lookup: previous crop determines an N-residue category (low/medium/high/very-high), which combines with soil type and rainfall to produce the index. See [Previous Crops and N-Residue Categories](#previous-crops-and-n-residue-categories) for the mapping.
- Use the resulting `sns_index` value as the `--sns-index` argument to `recommend` or `nitrogen`.
- **Combined assessment:** When `--ley-age` is provided, `--ley-n-intensity` and `--ley-management` are also required. The command performs both the field-assessment and Table 4.6 lookups and returns the higher SNS index, as required by RB209. The `--ley-year` defaults to 2 (the crop is typically the second crop after the ley was ploughed out). Organic soils are not supported for the grass ley component (Table 4.6 does not cover them).

---

### sns-ley

Calculate the Soil Nitrogen Supply (SNS) index from grass ley history using RB209 Table 4.6. Use this when the field has been in grass within the past three years, then compare the result with the field-assessment `sns` result and take the higher of the two indices.

**Usage:**

```
rb209 sns-ley --ley-age AGE --n-intensity LEVEL --management REGIME --soil-type TYPE --rainfall LEVEL [--year N] [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--ley-age` | Yes | string | `1-2yr`, `3-5yr` | -- | Duration of the grass ley |
| `--n-intensity` | Yes | string | `low`, `high` | -- | N management intensity (low: <250 kg N/ha/yr; high: >250, clover-rich, or lucerne) |
| `--management` | Yes | string | `cut`, `grazed`, `1-cut-then-grazed` | -- | Ley management regime |
| `--soil-type` | Yes | string | `light`, `medium`, `heavy` | -- | Soil type (organic soils not covered by Table 4.6) |
| `--rainfall` | Yes | string | `low`, `medium`, `high` | -- | Excess winter rainfall category |
| `--year` | No | int | `1`, `2`, `3` | `1` | Year after ploughing out the ley |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 sns-ley --ley-age 3-5yr --n-intensity high --management 1-cut-then-grazed --soil-type medium --rainfall medium
+------------------------------+
| Soil Nitrogen Supply (SNS)   |
+------------------------------+
|   SNS Index               2  |
|   Soil type          medium  |
|   Rainfall           medium  |
|   Method          table-4.6  |
+------------------------------+
| Table 4.6: 3-5yr ley, high N |
| , 1-cut-then-grazed manageme |
| nt, medium soil, medium rain |
| fall — year 1 after ploughin |
| g.                           |
+------------------------------+
```

**Example (JSON):**

```json
{
  "sns_index": 2,
  "previous_crop": "",
  "soil_type": "medium",
  "rainfall": "medium",
  "method": "table-4.6",
  "smn": null,
  "crop_n": null,
  "sns_value": null,
  "notes": [
    "Table 4.6: 3-5yr ley, high N, 1-cut-then-grazed management, medium soil, medium rainfall — year 1 after ploughing."
  ]
}
```

**JSON schema:**

The JSON output uses the same `SNSResult` schema as the `sns` and `sns-smn` commands. For Table 4.6 results, `method` is `"table-4.6"`, `previous_crop` is empty, and `smn`/`crop_n`/`sns_value` are `null`.

| Field | Type | Description |
|-------|------|-------------|
| `sns_index` | int | Calculated SNS index from Table 4.6 |
| `previous_crop` | string | Empty string (not applicable for Table 4.6) |
| `soil_type` | string | Soil type as provided |
| `rainfall` | string | Rainfall category as provided |
| `method` | string | Always `"table-4.6"` |
| `smn` | null | Not applicable |
| `crop_n` | null | Not applicable |
| `sns_value` | null | Not applicable |
| `notes` | string[] | Describes the Table 4.6 lookup parameters |

**Notes:**
- Organic soils are not covered by Table 4.6 and are rejected at argument parsing.
- The `--year` parameter represents how many years since the ley was ploughed out. Year 1 = first crop after ploughing, Year 2 = second crop, Year 3 = third crop. SNS indices generally decrease over the three years.
- RB209 requires comparing this result with the field-assessment SNS (from the `sns` command) and using the higher of the two indices.

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
|   Application rate        25.0 t/ha |
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
|   Application rate        30.0 m3/ha |
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
  "unit": "t",
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
| `unit` | string | Rate unit: `"t"` (tonnes/ha for solids) or `"m3"` (cubic metres/ha for slurries) |
| `total_n` | float | Total nitrogen (kg/ha) |
| `available_n` | float | Crop-available nitrogen in year 1 (kg/ha) |
| `p2o5` | float | Phosphorus as P2O5 (kg/ha) |
| `k2o` | float | Potassium as K2O (kg/ha) |
| `mgo` | float | Magnesium as MgO (kg/ha) |
| `so3` | float | Sulfur as SO3 (kg/ha) |

**Notes:**
- `total_n` is the total nitrogen in the application. `available_n` is the portion available to the crop in year 1 (typically 5–15 % of total N for farmyard manures and composts, higher for slurries and poultry manures).
- Solid materials (FYM, compost, cake, litter) use t/ha. Slurries use m3/ha. See [Organic Materials](#organic-materials) for units per material.
- Nutrient values are calculated as `per_unit_content × rate`, rounded to 1 decimal place.
- **Timing-adjusted available-N** is supported for all major livestock manures and biosolids using the RB209 Section 2 percentage factors. When `--timing` is omitted, the flat default available-N coefficient from the RB209 typical-values tables is used. Timing seasons: `autumn` = Aug–Oct, `winter` = Nov–Jan, `spring` = Feb–Apr, `summer` = grassland use only. The `--soil-type` argument selects the correct soil column — `light` maps to the sandy/shallow category; all other soil types map to medium/heavy. Incorporating promptly (`--incorporated`) increases retained nitrogen for most materials; summer + incorporated is not applicable (N/A in RB209) for any material. Supported materials and their RB209 table references:

  | Material | RB209 Table | Incorporation window |
  |----------|-------------|----------------------|
  | `cattle-fym`, `pig-fym`, `sheep-fym`, `horse-fym` | Table 2.3 | 24 h |
  | `poultry-litter` | Table 2.6 (40 % DM) | 24 h |
  | `layer-manure` | Table 2.6 (20 % DM) | 24 h |
  | `cattle-slurry` | Table 2.9 (6 % DM) | 6 h |
  | `pig-slurry` | Table 2.12 (4 % DM) | 6 h |
  | `biosolids-cake` | Table 2.15 (digested cake) | 24 h |

  Composts (`green-compost`, `green-food-compost`) and `paper-crumble` do not have timing tables in RB209; for these materials the `--timing` flag is not supported and the flat default coefficient is always used.

---

### lime

Calculate lime requirement to raise soil pH.

**Usage:**

```
rb209 lime --current-ph PH (--target-ph PH | --land-use arable|grassland) --soil-type TYPE [--format FORMAT]
```

Either `--target-ph` or `--land-use` must be supplied.  When `--land-use` is given without `--target-ph`, the RB209 default target pH for that land use is used automatically (arable: 6.5, grassland: 6.0).

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--current-ph` | Yes | float | `3.0` to `9.0` | -- | Current soil pH |
| `--target-ph` | No* | float | `4.0` to `8.5` | -- | Target soil pH. Required when `--land-use` is omitted. |
| `--land-use` | No* | string | `arable`, `grassland` | -- | Land use for automatic target pH selection (arable → 6.5, grassland → 6.0). Required when `--target-ph` is omitted. |
| `--soil-type` | Yes | string | `light`, `medium`, `heavy`, `organic` | -- | Soil texture category |
| `--format` | No | string | `table`, `json` | `table` | Output format |

\* One of `--target-ph` or `--land-use` must be provided.

**Example (explicit target pH):**

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

**Example (auto target pH via land use -- arable):**

```
$ rb209 lime --current-ph 5.8 --land-use arable --soil-type medium
+--------------------------------+
| Lime Requirement               |
+--------------------------------+
|   Current pH                 5.8 |
|   Target pH                  6.5 |
|   Soil type               medium |
|   Lime required   3.9 t CaCO3/ha |
+--------------------------------+
```

**Example (auto target pH via land use -- grassland):**

```
$ rb209 lime --current-ph 5.5 --land-use grassland --soil-type medium
+--------------------------------+
| Lime Requirement               |
+--------------------------------+
|   Current pH                 5.5 |
|   Target pH                  6.0 |
|   Soil type               medium |
|   Lime required   2.8 t CaCO3/ha |
+--------------------------------+
```

**Example (very acidic soil -- pH below 5.0):**

```
$ rb209 lime --current-ph 4.5 --land-use arable --soil-type medium
+----------------------------------+
| Lime Requirement                 |
+----------------------------------+
|   Current pH                 4.5 |
|   Target pH                  6.5 |
|   Soil type               medium |
|   Lime required   11.0 t CaCO3/ha |
+----------------------------------+
| Soil pH (4.5) is below 5.0. Soil |
|  is very acidic — liming is stro |
| ngly recommended.                |
| Total lime required (11.0 t/ha)  |
|  exceeds single application maxi |
| mum (7.5 t/ha). Apply in split d |
| ressings over successive years.  |
+----------------------------------+
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
| Soil pH (4.5) is below 5.0. Soil |
|  is very acidic — liming is stro |
| ngly recommended.                |
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
| `target_ph` | float | Target soil pH (explicit or derived from `land_use`) |
| `soil_type` | string | Soil type as provided |
| `lime_required` | float | Lime requirement (t CaCO3/ha) |
| `notes` | string[] | Advisory notes (e.g. very acidic soil warning, split dressing advice) |

**Notes:**
- If `current_ph >= target_ph`, lime required is 0 and a note explains no lime is needed.
- Lime requirement = (target_ph - current_ph) * soil_factor. Soil factors: light=4.0, medium=5.5, heavy=7.5, organic=11.0 t CaCO3/ha per pH unit.
- If lime required exceeds 7.5 t/ha, the tool advises splitting applications over successive years.
- When current pH is below **5.0**, a warning note is added: soil is very acidic and liming is strongly recommended.

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

Used by `sns`, `sns-ley`, `lime`, and accepted by those commands via `--soil-type`. Note that `sns-ley` only accepts `light`, `medium`, and `heavy` (organic soils are not covered by Table 4.6).

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
| `grass-3-5yr` | high |
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

A higher SNS index means more nitrogen is already available in the soil, so less fertiliser nitrogen is needed. The `sns` command performs this lookup using Tables 4.3–4.5.

**Grass ley history (Table 4.6):** When a field has been in grass within the past three years, RB209 requires also consulting Table 4.6 and using the **higher** of the two SNS indices. The Python API exposes `calculate_grass_ley_sns(ley_age, n_intensity, management, soil_type, rainfall, year=1)` for this purpose — it returns an `SNSResult` with `method="table-4.6"`. Parameters:

| Parameter | Values | Description |
|-----------|--------|-------------|
| `ley_age` | `"1-2yr"`, `"3-5yr"` | Duration of the grass ley |
| `n_intensity` | `"low"`, `"high"` | Annual N inputs: low = <250 kg N/ha; high = >250 kg N/ha, clover-rich, or lucerne |
| `management` | `"cut"`, `"grazed"`, `"1-cut-then-grazed"` | Ley management regime |
| `soil_type` | `"light"`, `"medium"`, `"heavy"` | Soil type (organic soils not covered by Table 4.6) |
| `rainfall` | `"low"`, `"medium"`, `"high"` | Rainfall category |
| `year` | `1`, `2`, `3` | Year after ploughing out the ley (default 1) |

This calculation is also available as the [`sns-ley`](#sns-ley) CLI subcommand. Compare the result with the `sns` command output and take the higher index.

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

**Target pH defaults:** RB209 specifies standard target pH values by land use. Instead of looking these up manually, you can pass `--land-use` to the `lime` command and the correct target pH is applied automatically:

| Land use | RB209 target pH |
|----------|----------------|
| `arable` | 6.5 |
| `grassland` | 6.0 |

**Very acidic soils:** When the current pH is below 5.0, the tool adds a warning note that the soil is very acidic and liming is strongly recommended. Soils at this pH may also require split applications.

The maximum single application is 7.5 t/ha. If the calculated requirement exceeds this, the tool advises applying lime in split dressings over successive years.

### Organic Material Nutrients

Organic materials (manures, slurries, composts) supply multiple nutrients. The `organic` command reports both **total nitrogen** and **available nitrogen** (crop-available in year 1). Available N is typically 5–15 % of total N for farmyard manures, and higher (25–60 %) for slurries and poultry manures.

By default, `available_n` is calculated from the flat per-unit coefficient in the RB209 typical-values tables. For all major livestock manures and biosolids, the more accurate approach from RB209 Section 2 is available via the `--timing`, `--incorporated`, and `--soil-type` flags. The available-N fraction varies by material, timing, soil category, and whether the material is incorporated. For example, cattle slurry ranges from 5 % (autumn, sandy, surface-applied) to 40 % (spring, any soil, incorporated within 6 hours), and pig slurry from 10 % to 60 %. See the [`organic` command](#organic) for the full list of supported materials and their RB209 table references.

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
