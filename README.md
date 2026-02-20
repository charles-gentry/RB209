# RB209

A command-line tool for calculating fertiliser recommendations for UK agricultural crops, implementing the RB209 9th edition tables from Defra/AHDB.

- 22 crop types across arable, grassland, and potato categories
- Nitrogen, phosphorus, potassium, magnesium, sulfur, and lime recommendations
- Soil Nitrogen Supply (SNS) index via field assessment (Tables 4.3–4.5) or direct SMN measurement
- Grass ley SNS calculation from RB209 Table 4.6 — looks up SNS indices by ley age (1–2yr / 3–5yr), N-intensity, and management regime (cut / grazed / 1-cut-then-grazed) for up to three years after ploughing out, with `combine_sns` to select the higher of field-assessment and grass-ley SNS indices as required by RB209
- Crop history support — `calculate_sns` accepts an optional `grass_history` parameter to automatically combine field-assessment and Table 4.6 results when the previous crop followed a grass ley (e.g. winter wheat after spring barley after a 2-year ley)
- Organic material nutrient calculations (manures, composts, slurries) with timing- and incorporation-adjusted available-N for all major livestock manures and biosolids (RB209 Section 2 Tables 2.3, 2.6, 2.9, 2.12, 2.15)
- Human-readable ASCII tables or machine-readable JSON output
- Pure Python -- no external dependencies

## Installation

```bash
pip install .
```

Or run directly without installing:

```bash
python -m rb209 --version
```

## Quick Start

A typical workflow has two steps: calculate the Soil Nitrogen Supply (SNS) index for your field, then get a full nutrient recommendation using that index.

**Step 1 -- Calculate the SNS index:**

```
$ rb209 sns --previous-crop cereals --soil-type medium --rainfall medium
+----------------------------------+
| Soil Nitrogen Supply (SNS)       |
+----------------------------------+
|   SNS Index                    1 |
|   Previous crop          cereals |
|   Soil type               medium |
|   Rainfall                medium |
|   Method        field-assessment |
+----------------------------------+
| Previous crop 'cereals' has low  |
| N residue.                       |
+----------------------------------+
```

**Step 2 -- Get the full recommendation:**

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

Add `--format json` to any command for machine-readable output:

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

## Commands

| Command | Description |
|---------|-------------|
| `recommend` | Full NPK + sulfur + magnesium recommendation for a crop |
| `nitrogen` | Nitrogen recommendation only |
| `phosphorus` | Phosphorus recommendation only |
| `potassium` | Potassium recommendation only (with straw management options) |
| `sulfur` | Sulfur recommendation only |
| `sns` | Calculate SNS index from field assessment (Tables 4.3–4.5) |
| `sns-smn` | Calculate SNS index from direct soil mineral N measurement |
| `sns-ley` | Calculate SNS index from grass ley history (Table 4.6) |
| `organic` | Calculate nutrients from organic material applications |
| `lime` | Calculate lime requirement to raise soil pH |
| `list-crops` | List all supported crops |
| `list-materials` | List all supported organic materials |

See [CLI.md](CLI.md) for the full command reference with all arguments and examples.

## Supported Crops

**Arable** -- winter wheat (feed/milling), spring wheat, winter barley, spring barley, winter oats, spring oats, winter rye, winter/spring oilseed rape, linseed, peas, field beans, sugar beet, forage maize

**Potatoes** -- maincrop, early, seed

**Grassland** -- grazed, silage, hay, grazed with one silage cut

## Requirements

- Python 3.10+
- No external dependencies

## Testing

```bash
python -m pytest tests/
```

## License

[GPL-3.0-or-later](LICENSE)
