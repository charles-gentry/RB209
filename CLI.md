# RB209 CLI Reference

RB209 is a command-line tool for calculating fertiliser recommendations for UK agricultural crops. It implements the recommendation tables from the RB209 9th edition (Defra/AHDB Nutrient Management Guide) covering nitrogen, phosphorus, potassium, magnesium, sulfur, lime, organic materials, and nitrogen application timing.

The tool supports 56 crop types across arable, grassland, potato, and vegetable categories. All output is available as human-readable ASCII tables (default) or machine-readable JSON.

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
| `--expected-yield` | No | float | any positive value | -- | Expected yield (t/ha). When provided and the crop has yield adjustment data (see [Yield-Adjusted Crops](#yield-adjusted-crops)), adjusts N, P2O5, and K2O recommendations based on the difference from the RB209 baseline yield. An error is raised if the crop does not support yield adjustment. |
| `--ber` | No | float | any positive value | -- | Break-even ratio (fertiliser N cost £/kg ÷ grain value £/kg). Default: 5.0. Only affects wheat and barley N recommendations. Values between table entries are linearly interpolated. |
| `--k-upper-half` / `-ku` | No | flag | -- | false | Use the K Index 2+ rate (181–240 mg/l) for vegetable crops at K Index 2. By default the lower 2- rate (121–180 mg/l) is used. Has no effect for non-vegetable crops or K indices other than 2. |
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
- The `notes` array in the output may include contextual advisory notes beyond the basic crop note. See [Contextual Advisory Notes](#contextual-advisory-notes) for the full list of notes that can appear.
- The `--ber` option adjusts the N recommendation for wheat and barley crops based on the economic break-even ratio (BER = fertiliser N cost £/kg ÷ grain value £/kg). The default BER is 5.0 (no adjustment). Lower BER values (cheap fertiliser relative to grain) increase the N recommendation; higher BER values decrease it. BER values between the table entries (2, 3, 4, 5, 6, 7, 8, 10) are linearly interpolated. For non-cereal crops, `--ber` is accepted but has no effect.
- The `--expected-yield` option adjusts N, P2O5, and K2O recommendations when the expected fresh yield differs from the RB209 baseline. See [Yield-Adjusted Crops](#yield-adjusted-crops) for the list of supported crops. An error is raised if the crop does not appear in that list.

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
| `--expected-yield` | No | float | any positive value | -- | Expected yield (t/ha) for yield-adjusted N recommendation. See [Yield-Adjusted Crops](#yield-adjusted-crops). |
| `--ber` | No | float | any positive value | -- | Break-even ratio (fertiliser N cost £/kg ÷ grain value £/kg). Default: 5.0. Only affects wheat and barley. |
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
| `--expected-yield` | No | float | any positive value | -- | Expected yield (t/ha) for yield-adjusted P2O5 recommendation. See [Yield-Adjusted Crops](#yield-adjusted-crops). |
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
| `--expected-yield` | No | float | any positive value | -- | Expected yield (t/ha) for yield-adjusted K2O recommendation. See [Yield-Adjusted Crops](#yield-adjusted-crops). |
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

### veg-sns

Calculate the Soil Nitrogen Supply (SNS) index for vegetable crops using the RB209 Section 6 field assessment tables (Tables 6.2–6.4). These tables differ from the arable Tables 4.3–4.5 in both the previous-crop categories (11 vs 4) and the soil-type columns (4 mineral columns vs 3).

**Usage:**

```
rb209 veg-sns --previous-crop CROP --soil-type TYPE --rainfall LEVEL [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--previous-crop` | Yes | string | `beans`, `cereals`, `forage-cut`, `oilseed-rape`, `peas`, `potatoes`, `sugar-beet`, `uncropped`, `veg-low-n`, `veg-medium-n`, `veg-high-n` | -- | Previous crop category for vegetable SNS (Section 6) |
| `--soil-type` | Yes | string | `light-sand`, `medium`, `deep-clay`, `deep-silt`, `organic`, `peat` | -- | Vegetable soil type column from Tables 6.2–6.4. Organic and peat soils return an advisory index with a note to consult a FACTS Qualified Adviser. |
| `--rainfall` | Yes | string | `low`, `moderate`, `high` | -- | Rainfall category: `low` (<600 mm / <150 mm EWR), `moderate` (600–700 mm), `high` (>700 mm / >250 mm EWR) |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 veg-sns --previous-crop cereals --soil-type medium --rainfall moderate
+--------------------------------------+
| Soil Nitrogen Supply (SNS)           |
+--------------------------------------+
|   SNS Index                          1 |
|   Previous crop                cereals |
|   Soil type                     medium |
|   Rainfall                    moderate |
|   Method          veg-field-assessment |
+--------------------------------------+
| Previous crop 'cereals' on medium so |
| il with moderate rainfall gives SNS  |
| Index 1 (Tables 6.2–6.4).            |
+--------------------------------------+
```

**Example (JSON):**

```json
{
  "sns_index": 1,
  "previous_crop": "cereals",
  "soil_type": "medium",
  "rainfall": "moderate",
  "method": "veg-field-assessment",
  "smn": null,
  "crop_n": null,
  "sns_value": null,
  "notes": [
    "Previous crop 'cereals' on medium soil with moderate rainfall gives SNS Index 1 (Tables 6.2–6.4)."
  ]
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `sns_index` | int | Calculated SNS index (0–6) |
| `previous_crop` | string | Previous crop value as provided |
| `soil_type` | string | Soil type as provided |
| `rainfall` | string | Rainfall category as provided |
| `method` | string | Always `"veg-field-assessment"` for mineral soils; `"veg-field-assessment"` with advisory note for organic/peat soils |
| `smn` | null | Not applicable for field-assessment method |
| `crop_n` | null | Not applicable |
| `sns_value` | null | Not applicable |
| `notes` | string[] | Describes the table lookup; for organic/peat soils, advises consulting a FACTS Qualified Adviser |

**Notes:**
- The vegetable SNS lookup uses different previous-crop categories from the arable `sns` command. See [Vegetable Previous Crops](#vegetable-previous-crops) for the full list.
- Rainfall bands differ from arable: `low` maps to Table 6.2, `moderate` to Table 6.3, `high` to Table 6.4.
- For **organic** soils, SNS Index 4 is returned with a note that organic soils typically have SNS 3–6 and a FACTS Qualified Adviser should be consulted.
- For **peat** soils, SNS Index 5 is returned with a similar advisory note.
- Use the resulting `sns_index` as the `--sns-index` argument to `recommend` or `nitrogen`.

---

### veg-smn

Calculate the Soil Nitrogen Supply (SNS) index for vegetable crops from a direct Soil Mineral Nitrogen (SMN) measurement, using RB209 Table 6.6. The thresholds differ from the arable Table 4.10 used by `sns-smn`.

**Usage:**

```
rb209 veg-smn --smn VALUE --depth DEPTH [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--smn` | Yes | float | >= 0 | -- | Soil Mineral Nitrogen (kg N/ha) measured to the specified depth |
| `--depth` | Yes | int | `30`, `60`, `90` | -- | Sampling depth in cm |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table):**

```
$ rb209 veg-smn --smn 45 --depth 60
+------------------------------+
| Soil Nitrogen Supply (SNS)   |
+------------------------------+
|   SNS Index         1        |
|   Soil type                  |
|   Rainfall                   |
|   Method      veg-smn        |
+------------------------------+
| SMN (45.0 kg N/ha to 60 cm d |
| epth) gives SNS Index 1 (Tab |
| le 6.6).                     |
+------------------------------+
```

**Example (JSON):**

```json
{
  "sns_index": 1,
  "previous_crop": "",
  "soil_type": "",
  "rainfall": "",
  "method": "veg-smn",
  "smn": 45.0,
  "crop_n": null,
  "sns_value": null,
  "notes": [
    "SMN (45.0 kg N/ha to 60 cm depth) gives SNS Index 1 (Table 6.6)."
  ]
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `sns_index` | int | Calculated SNS index (0–6) |
| `previous_crop` | string | Empty string (not applicable) |
| `soil_type` | string | Empty string (not applicable) |
| `rainfall` | string | Empty string (not applicable) |
| `method` | string | Always `"veg-smn"` |
| `smn` | float | SMN value as provided (kg N/ha) |
| `crop_n` | null | Not applicable |
| `sns_value` | null | Not applicable |
| `notes` | string[] | Describes the SMN value, depth, and resulting index |

**SMN thresholds (Table 6.6):**

| SNS Index | 0–30 cm (kg N/ha) | 0–60 cm (kg N/ha) | 0–90 cm (kg N/ha) |
|-----------|-------------------|-------------------|-------------------|
| 0 | ≤ 19.9 | ≤ 39.9 | ≤ 59.9 |
| 1 | 20 – 27 | 40 – 53 | 60 – 80 |
| 2 | 27.1 – 33 | 53.1 – 67 | 80.1 – 100 |
| 3 | 33.1 – 40 | 67.1 – 80 | 100.1 – 120 |
| 4 | 40.1 – 53 | 80.1 – 107 | 120.1 – 160 |
| 5 | 53.1 – 80 | 107.1 – 160 | 160.1 – 240 |
| 6 | > 80 | > 160 | > 240 |

**Notes:**
- Only 30, 60, or 90 cm sampling depth is supported. Other values produce an error.
- Use the resulting `sns_index` as the `--sns-index` argument to `recommend` or `nitrogen`.
- For the arable equivalent (Table 4.10 thresholds), use the `sns-smn` command instead.

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
  "so3": 75.0,
  "notes": [
    "Do not apply organic materials to soils that are waterlogged, frozen hard, snow-covered, or deeply cracked."
  ]
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
| `notes` | string[] | Advisory notes — always includes a soil condition warning |

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
| `--crop` | No | string | See [Crops](#crops) | -- | Optional crop type. When a potato crop is specified and lime is required, a warning about common scab and Mn deficiency risk is added. |
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
- When `--crop` is a potato type (`potatoes-maincrop`, `potatoes-early`, `potatoes-seed`) and lime is required (> 0), a note warns that liming immediately before potatoes increases common scab and Mn deficiency risk.
- Over-liming trace element notes: grassland raised above pH 7.0 risks Cu/Co/Se deficiency; any soil above pH 7.5 risks Mn deficiency; light (sandy) soils above pH 6.5 risk Mn deficiency; organic/peaty soils above pH 6.0 risk Mn deficiency. These notes are only added when lime is actually needed. See [Contextual Advisory Notes](#contextual-advisory-notes).

---

### timing

Nitrogen application timing and split dressing advice for a crop.

Given the total nitrogen recommendation (from `nitrogen` or `recommend`), the `timing` command returns a per-dressing schedule — how much N to apply and when — based on the crop type, total N rate, and optionally soil type.

**Usage:**

```
rb209 timing --crop CROP --total-n RATE [--soil-type TYPE] [--format FORMAT]
```

**Arguments:**

| Argument | Required | Type | Valid Values | Default | Description |
|----------|----------|------|--------------|---------|-------------|
| `--crop` | Yes | string | See [Crops](#crops) | -- | Crop type |
| `--total-n` | Yes | float | >= 0 | -- | Total nitrogen recommendation (kg N/ha) |
| `--soil-type` | No | string | `light`, `medium`, `heavy`, `organic` | -- | Soil type — affects timing for some crops (e.g. potatoes on light soils receive a split dressing) |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (winter barley, split schedule):**

```
$ rb209 timing --crop winter-barley --total-n 180
```

Returns two equal dressings of 90 kg/ha: one at late tillering and one at GS30-31.

**Example (potatoes, light soil — split by soil type):**

```
$ rb209 timing --crop potatoes-maincrop --total-n 270 --soil-type light
```

Returns two dressings: 180 kg/ha in the seedbed and 90 kg/ha post-emergence.

**Example (JSON):**

```
$ rb209 timing --crop winter-wheat-feed --total-n 150 --format json
```

```json
{
  "crop": "Winter Wheat (feed)",
  "total_n": 150.0,
  "splits": [
    {
      "amount": 75.0,
      "timing": "GS25-GS30 (February-March)",
      "note": ""
    },
    {
      "amount": 75.0,
      "timing": "GS31-GS32 (late March-April)",
      "note": ""
    }
  ],
  "notes": []
}
```

**JSON schema:**

| Field | Type | Description |
|-------|------|-------------|
| `crop` | string | Display name of the crop |
| `total_n` | float | Total N as provided (kg/ha) |
| `splits` | array | Ordered list of dressing objects |
| `splits[].amount` | float | N to apply at this dressing (kg/ha) |
| `splits[].timing` | string | When to apply (growth stage or calendar period) |
| `splits[].note` | string | Optional dressing-specific note |
| `notes` | string[] | General advisory notes (e.g. lodging risk, protein dressing) |

**Notes:**
- Split amounts are computed from per-crop fractions specified in RB209 Section 3 (grassland) and Section 4 (arable). The last dressing is adjusted so the amounts always sum exactly to `total_n` (rounded to the nearest integer).
- Crops without specific timing guidance (`peas`, `field-beans`, `sugar-beet`, `forage-maize`, `linseed`, `oilseed-rape`) return a single dressing with a note that no specific timing data is available.
- The `recommend` command adds a note directing you to the `timing` command whenever a crop has a timing schedule defined.

**Timing schedules by crop:**

| Crop | Rule | Source |
|------|------|--------|
| `winter-wheat-feed` | ≤120 kg/ha: single at GS25-GS30; >120: 50/50 at GS25-GS30 + GS31-GS32 | RB209 S4 |
| `winter-wheat-milling` | Same splits; protein dressing note (GS32-GS39) always added | RB209 S4 |
| `spring-wheat` | ≤100: single at drilling; >100: 50/50 at drilling + GS30-GS31 | RB209 S4 |
| `winter-barley` | <100: single at GS30-31; 100–199: 50/50; ≥200: 40/40/20 with lodging note | RB209 S4 |
| `spring-barley` | <100: single at drilling; ≥100: 33/67 at drilling + GS25-GS30 | RB209 S4 |
| `winter-rye` | Same splits as `winter-wheat-feed`; lodging risk note always added | RB209 S4 |
| `potatoes-maincrop/early/seed` | Light soil: 2/3 seedbed + 1/3 post-emergence; other: all in seedbed | RB209 S5 |
| `grass-silage` | ≤80: single before 1st cut; 81–180: 2 dressings; 181–280: 3; ≥281: 4 per cut | RB209 S3 |
| `grass-grazed` | ≤100: 2 rotations; 101–200: 3 rotations; ≥201: 5 rotations | RB209 S3 |
| `grass-grazed-one-cut` | ≤120: 2 dressings (spring + after cut); >120: 3 dressings | RB209 S3 |
| `grass-hay` | Single application (early February to mid-March) | RB209 S3 |
| `veg-asparagus-est` | Three equal dressings: pre-sowing, mid-June/July (established), end-August | RB209 S6 |
| `veg-asparagus` | Single dressing by end-February – early March (year-2 benchmark) | RB209 S6 |
| Most brassicas, roots, sweetcorn, beans-dwarf, radish, coriander, courgettes | ≤100: single in seedbed; >100: 100 kg seedbed + remainder after establishment | RB209 S6 |
| `veg-cauliflower-winter-seedbed` | Single seedbed application; note directs to separate topdress slug | RB209 S6 |
| `veg-cauliflower-winter-topdress` | Single top dressing after establishment | RB209 S6 |
| `veg-celery-seedbed` | Single at transplanting; note reminds of required 75–150 kg N/ha topdress | RB209 S6 |
| `veg-bulbs` | Single top dressing just before crop emergence | RB209 S6 |
| `veg-onions-bulb` | ≤100: single at sowing; >100: 100 kg seedbed + remainder after establishment | RB209 S6 |
| `veg-onions-salad` | Single application before or at sowing | RB209 S6 |
| `veg-leeks` | ≤100: single at transplanting; >100: seedbed cap + topdress with NVZ note | RB209 S6 |
| `veg-lettuce-whole`, `veg-lettuce-baby`, `veg-rocket` | Single at transplanting with nitrate accumulation note | RB209 S6 |
| `veg-mint-est`, `veg-mint` | Single application in spring as growth begins | RB209 S6 |
| `veg-peas-market`, `veg-beans-broad` | Not applicable — N-fixing crops | RB209 S6 |

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
| `--category` | No | string | `arable`, `grassland`, `potatoes`, `vegetables` | -- | Filter to a single crop category |
| `--format` | No | string | `table`, `json` | `table` | Output format |

**Example (table, all crops — arable/grassland/potatoes shown; vegetable section truncated):**

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

  VEGETABLES
  --------------------------------------------------
    veg-asparagus                  Asparagus (subsequent years)
    veg-asparagus-est              Asparagus (establishment year)
    veg-beans-broad                Broad Beans
    ... (34 vegetable crops total — use --category vegetables to list all)
```

**Example (table, filtered to vegetables):**

```
$ rb209 list-crops --category vegetables
Available Crops
===============

  VEGETABLES
  --------------------------------------------------
    veg-asparagus                  Asparagus (subsequent years)
    veg-asparagus-est              Asparagus (establishment year)
    veg-beans-broad                Broad Beans
    veg-beans-dwarf                Dwarf/Runner Beans (seedbed N)
    veg-beetroot                   Beetroot
    veg-brussels-sprouts           Brussels Sprouts
    veg-bulbs                      Bulbs and Bulb Flowers
    veg-cabbage-head-post-dec      Head Cabbage (post-31 Dec)
    veg-cabbage-head-pre-dec       Head Cabbage (pre-31 Dec)
    veg-cabbage-storage            Storage Cabbage
    veg-calabrese                  Calabrese
    veg-carrots                    Carrots
    veg-cauliflower-summer         Cauliflower (summer/autumn)
    veg-cauliflower-winter-seedbed Cauliflower (winter — seedbed N)
    veg-cauliflower-winter-topdress Cauliflower (winter — top dressing N)
    veg-celery-seedbed             Self-blanching Celery (seedbed N)
    veg-collards-post-dec          Collards (post-31 Dec)
    veg-collards-pre-dec           Collards (pre-31 Dec)
    veg-coriander                  Coriander
    veg-courgettes-seedbed         Courgettes (seedbed N)
    veg-courgettes-topdress        Courgettes (top dressing N)
    veg-leeks                      Leeks
    veg-lettuce-baby               Lettuce (baby leaf)
    veg-lettuce-whole              Lettuce (whole head)
    veg-mint                       Mint (subsequent years)
    veg-mint-est                   Mint (establishment year)
    veg-onions-bulb                Bulb Onions
    veg-onions-salad               Salad Onions
    veg-peas-market                Peas (market pick)
    veg-radish                     Radish
    veg-rocket                     Wild Rocket
    veg-swedes                     Swedes
    veg-sweetcorn                  Sweetcorn
    veg-turnips-parsnips           Turnips and Parsnips
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
| `category` | string | One of `arable`, `grassland`, `potatoes`, `vegetables` |

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

56 crops in 4 categories. Use the **Value** column as the `--crop` argument.

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

**Vegetables (34) — RB209 Section 6:**

| Value | Display Name | Notes |
|-------|-------------|-------|
| `veg-asparagus-est` | Asparagus (establishment year) | Year 1 only; `timing` gives 3-way split |
| `veg-asparagus` | Asparagus (subsequent years) | Year 2 benchmark (120 kg N/ha); see TODO.md for year 3+ |
| `veg-brussels-sprouts` | Brussels Sprouts | |
| `veg-cabbage-storage` | Storage Cabbage | |
| `veg-cabbage-head-pre-dec` | Head Cabbage (pre-31 Dec) | |
| `veg-cabbage-head-post-dec` | Head Cabbage (post-31 Dec) | |
| `veg-collards-pre-dec` | Collards (pre-31 Dec) | |
| `veg-collards-post-dec` | Collards (post-31 Dec) | |
| `veg-cauliflower-summer` | Cauliflower (summer/autumn) | |
| `veg-cauliflower-winter-seedbed` | Cauliflower (winter — seedbed N) | |
| `veg-cauliflower-winter-topdress` | Cauliflower (winter — top dressing N) | |
| `veg-calabrese` | Calabrese | |
| `veg-celery-seedbed` | Self-blanching Celery (seedbed N) | `timing` adds top-dressing reminder |
| `veg-peas-market` | Peas (market pick) | N = 0 at all indices (N-fixing) |
| `veg-beans-broad` | Broad Beans | N = 0 at all indices (N-fixing) |
| `veg-beans-dwarf` | Dwarf/Runner Beans (seedbed N) | Seedbed N cap applies; not N-fixing |
| `veg-radish` | Radish | |
| `veg-sweetcorn` | Sweetcorn | |
| `veg-lettuce-whole` | Lettuce (whole head) | Nitrate note added |
| `veg-lettuce-baby` | Lettuce (baby leaf) | Nitrate note added |
| `veg-rocket` | Wild Rocket | Nitrate note added |
| `veg-onions-bulb` | Bulb Onions | |
| `veg-onions-salad` | Salad Onions | |
| `veg-leeks` | Leeks | NVZ closed-period note added |
| `veg-beetroot` | Beetroot | |
| `veg-swedes` | Swedes | |
| `veg-turnips-parsnips` | Turnips and Parsnips | |
| `veg-carrots` | Carrots | |
| `veg-bulbs` | Bulbs and Bulb Flowers | |
| `veg-coriander` | Coriander | |
| `veg-mint-est` | Mint (establishment year) | |
| `veg-mint` | Mint (subsequent years) | |
| `veg-courgettes-seedbed` | Courgettes (seedbed N) | Use with `veg-courgettes-topdress` |
| `veg-courgettes-topdress` | Courgettes (top dressing N) | N only (75 kg/ha at SNS 0–3); P2O5, K2O applied at seedbed |

### Soil Types

| Value | Description |
|-------|-------------|
| `light` | Sandy, shallow soils |
| `medium` | Loamy soils |
| `heavy` | Clay, deep soils |
| `organic` | Peaty, organic soils |

Used by `sns`, `sns-ley`, `lime`, and accepted by those commands via `--soil-type`. Note that `sns-ley` only accepts `light`, `medium`, and `heavy` (organic soils are not covered by Table 4.6).

### Vegetable Soil Types

Used by the `veg-sns` command via `--soil-type`. These correspond to the four mineral soil columns in Tables 6.2–6.4, plus advisory values for organic and peat soils.

| Value | Description |
|-------|-------------|
| `light-sand` | Light sandy or shallow soils |
| `medium` | Medium loamy soils |
| `deep-clay` | Deep clay soils |
| `deep-silt` | Deep silty soils |
| `organic` | Organic soils — SNS Index 4 returned with advisory note |
| `peat` | Peat soils — SNS Index 5 returned with advisory note |

### Vegetable Previous Crops

Used by the `veg-sns` command via `--previous-crop`. These 11 categories are specific to Section 6 of RB209 and differ from the arable previous-crop categories used by `sns`.

| Value | Previous Crop Category |
|-------|----------------------|
| `beans` | Beans |
| `cereals` | Cereals |
| `forage-cut` | Forage (cut, e.g. silage) |
| `oilseed-rape` | Oilseed Rape |
| `peas` | Peas |
| `potatoes` | Potatoes |
| `sugar-beet` | Sugar Beet |
| `uncropped` | Uncropped / bare fallow |
| `veg-low-n` | Vegetables — low N residue (e.g. root crops) |
| `veg-medium-n` | Vegetables — medium N residue |
| `veg-high-n` | Vegetables — high N residue (e.g. leafy brassicas) |

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

### Yield-Adjusted Crops

Crops that support `--expected-yield` on the `recommend`, `nitrogen`, `phosphorus`, and `potassium` commands. When `--expected-yield` is supplied for any other crop, the command exits with an error listing the supported crops.

N adjustment uses the formula `Δkg/ha = (expected_yield − baseline) × n_adjust_per_t`. For vegetable crops, `n_adjust_per_t` is derived from RB209 Table 6.27 as `N_uptake / (baseline_yield × 0.60)` (60 % fertiliser recovery). P2O5 and K2O adjustments use per-tonne offtake values from Table 6.8; crops without Table 6.8 data have `p_adjust_per_t = k_adjust_per_t = 0`. All recommendations are clamped to ≥ 0 kg/ha.

**Arable/potato crops (Table 4.12 / Section 5):**

| Crop | Baseline yield (t/ha) | N adj (kg/t) | P2O5 adj (kg/t) | K2O adj (kg/t) |
|------|-----------------------|--------------|-----------------|----------------|
| `winter-wheat-feed` | 8.0 | 20.0 | 7.0 | 10.5 |
| `winter-wheat-milling` | 8.0 | 20.0 | 7.0 | 10.5 |
| `winter-oats` | 6.0 | 20.0 | 7.0 | 12.0 |
| `potatoes-maincrop` | 50.0 | 0 | 0 | 5.8 |
| `potatoes-early` | 30.0 | 0 | 0 | 5.8 |

**Vegetable crops (Table 6.27 + Table 6.8):**

| Crop | Baseline yield (t/ha) | N adj (kg/t) | P2O5 adj (kg/t) | K2O adj (kg/t) |
|------|-----------------------|--------------|-----------------|----------------|
| `veg-brussels-sprouts` | 20.3 | 30.2 | 2.6 | 6.3 |
| `veg-cabbage-storage` | 110.0 | 5.7 | 0.9 | 3.6 |
| `veg-cabbage-head-pre-dec` | 60.0 | 7.5 | 0.9 | 3.6 |
| `veg-cabbage-head-post-dec` | 53.0 | 6.4 | 0.9 | 3.6 |
| `veg-collards-pre-dec` | 20.0 | 21.7 | 0.9 | 3.6 |
| `veg-collards-post-dec` | 30.0 | 16.7 | 0.9 | 3.6 |
| `veg-cauliflower-summer` | 30.6 | 14.1 | 1.4 | 4.8 |
| `veg-calabrese` | 16.3 | 23.1 | 1.4 | 4.8 |
| `veg-lettuce-whole` | 45.5 | 6.0 | 0 | 0 |
| `veg-radish` | 50.0 | 3.3 | 0 | 0 |
| `veg-onions-bulb` | 60.5 | 4.1 | 0.7 | 1.8 |
| `veg-onions-salad` | 30.0 | 6.3 | 0.7 | 1.8 |
| `veg-leeks` | 47.0 | 9.9 | 0 | 0 |
| `veg-beetroot` | 60.0 | 7.5 | 1.0 | 4.5 |
| `veg-swedes` | 84.4 | 4.4 | 0.7 | 2.4 |
| `veg-turnips-parsnips` | 48.0 | 8.4 | 0 | 0 |
| `veg-carrots` | 150.0 | 2.0 | 0.7 | 3.0 |
| `veg-coriander` | 48.0 | 4.5 | 0.8 | 5.5 |
| `veg-mint` | 25.0 | 10.2 | 1.0 | 3.9 |

Crops not listed (asparagus, celery, peas/beans, sweetcorn, courgettes, bulbs, lettuce baby, rocket, mint establishment) are excluded because RB209 Table 6.27 explicitly states insufficient data to derive these parameters.

---

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

### Break-Even Ratio (BER)

The break-even ratio (BER) is the ratio of fertiliser nitrogen cost (£/kg N) to grain value (£/kg). It captures the economic trade-off between the cost of applying more nitrogen and the value of the extra grain produced. RB209 Tables 4.25 (wheat) and 4.26 (barley) provide N adjustments relative to a default BER of 5.0:

| BER | Wheat adjustment | Barley adjustment |
|-----|-----------------|-------------------|
| 2.0 | +30 kg/ha | +25 kg/ha |
| 3.0 | +20 kg/ha | +15 kg/ha |
| 4.0 | +10 kg/ha | +10 kg/ha |
| 5.0 | 0 (default) | 0 (default) |
| 6.0 | -10 kg/ha | -10 kg/ha |
| 7.0 | -15 kg/ha | -15 kg/ha |
| 8.0 | -20 kg/ha | -20 kg/ha |
| 10.0 | -30 kg/ha | -25 kg/ha |

When `--ber` is passed to `recommend` or `nitrogen`, the adjustment for the crop's BER group (wheat or barley) is linearly interpolated from the table above and added to the N recommendation. Values outside the 2.0–10.0 range are clamped to the nearest boundary. Non-cereal crops are not affected.

### Straw Management

For cereal crops (wheat, barley, oats, rye), the potassium recommendation depends on whether straw is removed from the field or incorporated back into the soil. Straw contains potassium, so:

- **Straw removed** (default): higher K recommendation to replace exported nutrients
- **Straw incorporated**: lower K recommendation because nutrients are recycled

Non-cereal crops are not affected by the straw flags.

### Index Clamping

The P, K, and Mg index arguments accept values 0-9 to match the full UK soil index scale, but the recommendation lookup tables only contain data for indices 0-4. Any index above 4 is silently clamped to 4 before lookup. Since index 4 returns 0 kg/ha for all three nutrients, passing index 5-9 also returns 0. The SNS index (0-6) is not clamped and rejects out-of-range values with an error.

### Contextual Advisory Notes

Several commands add contextual advisory notes to their output alongside the numeric recommendations. Notes are always included in the `notes` array in JSON output and are rendered in the box footer in table output.

**`recommend` command notes:**

| Trigger | Note content |
|---------|-------------|
| N recommendation exceeds NVZ N-max limit for crop (e.g. 220 kg/ha for cereals, 250 for OSR) | NVZ N-max warning with exact recommendation and limit values |
| Potato crop with K2O > 300 kg/ha | Split potash application advice (autumn/winter + spring) |
| `grass-silage` with K2O > 90 kg/ha | Limit spring K2O to 80–90 kg/ha to minimise luxury uptake |
| Grassland crop with Mg Index 0 and K2O > 0 | Hypomagnesaemia (grass staggers) risk; avoid spring potash |
| Grassland crop with `clover_risk` flag and N > 0 | Mineral N inhibits clover N fixation |
| Arable crop on `light` soil with N + K2O > 150 kg/ha | Combine-drill seedbed limit warning |
| `--ber` provided and crop is wheat or barley | N adjusted for break-even ratio with adjustment from default BER 5.0 |
| N > 0 and crop has a timing schedule defined | Directs user to `rb209 timing` for N application timing guidance |
| Any vegetable crop at K Index 2 | Explains K Index 2 split (2- vs 2+) and suggests `--k-upper-half` flag when soil K is in the upper half (181–240 mg/l) |
| `veg-celery-seedbed` crop | Reminds user to apply a top-dressing N application in addition to the seedbed N |
| `veg-asparagus` (subsequent years) | Notes that year 3+ N rate (40–80 kg/ha) varies by winter rainfall and cutting intensity; current rate is the year-2 benchmark |
| `veg-lettuce-whole`, `veg-lettuce-baby`, `veg-rocket` | Notes legal nitrate limits for lettuce and rocket under food safety legislation |
| `veg-leeks` crop | Notes the NVZ closed period for autumn/winter N applications |
| Vegetable crops with seedbed N cap (most vegetable slugs) | Notes the 100 kg N/ha maximum for seedbed N on light soils |

**`lime` command notes (when lime is required):**

| Trigger | Note content |
|---------|-------------|
| `--crop` is a potato type | Common scab and Mn deficiency risk from liming before potatoes |
| Target pH > 7.0 and `land_use="grassland"` | Cu, Co, Se deficiency risk above pH 7.0 on grassland |
| Target pH > 7.5 | Mn deficiency risk above pH 7.5 |
| `soil_type="light"` and target pH > 6.5 | Mn deficiency more likely above pH 6.5 on sandy soils |
| `soil_type="organic"` and target pH > 6.0 | Mn deficiency more likely above pH 6.0 on organic/peaty soils |

**`organic` command notes:**

Every `organic` result includes a fixed note reminding users not to apply organic materials to waterlogged, frozen, snow-covered, or deeply cracked soils.

---

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

**Over-liming and trace element risks:** When lime is required, the tool checks the target pH for trace-element deficiency risks. See [Contextual Advisory Notes](#contextual-advisory-notes) for the full set of conditions and the associated note text. Pass `--crop` with a potato type to also trigger the common scab warning.

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
