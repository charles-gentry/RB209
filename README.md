# RB209

A command-line tool for calculating fertiliser recommendations for UK agricultural crops, implementing the RB209 9th edition tables from Defra/AHDB.

- **56 crop types** across arable, grassland, potato, and vegetable categories
- Nitrogen, phosphorus, potassium, magnesium, sulfur, and lime recommendations
- Soil Nitrogen Supply (SNS) index via field assessment (Tables 4.3–4.5) or direct SMN measurement
- **Vegetable SNS** via Tables 6.2–6.4 (11 previous-crop categories, 4 mineral soil columns) using the new `veg-sns` command; SMN conversion via Table 6.6 using `veg-smn`
- **K Index 2 split for vegetables** — `--k-upper-half` flag distinguishes 2- (121–180 mg/l) from 2+ (181–240 mg/l)
- **Higher magnesium rates for vegetables** — 150 kg MgO/ha at Mg Index 0 (vs 90 for arable)
- Grass ley SNS calculation from RB209 Table 4.6 — looks up SNS indices by ley age (1–2yr / 3–5yr), N-intensity, and management regime (cut / grazed / 1-cut-then-grazed) for up to three years after ploughing out, with `combine_sns` to select the higher of field-assessment and grass-ley SNS indices as required by RB209
- Crop history support — `calculate_sns` accepts an optional `grass_history` parameter to automatically combine field-assessment and Table 4.6 results when the previous crop followed a grass ley (e.g. winter wheat after spring barley after a 2-year ley)
- Organic material nutrient calculations (manures, composts, slurries) with timing- and incorporation-adjusted available-N for all major livestock manures and biosolids (RB209 Section 2 Tables 2.3, 2.6, 2.9, 2.12, 2.15)
- Contextual advisory notes — NVZ N-max warnings, potash split advice for potatoes and grass silage, hypomagnesaemia risk on grassland, clover N-fixation inhibition, over-liming trace-element warnings, combine-drill seedbed limit on sandy soils, lime-before-potatoes common scab risk, vegetable seedbed N cap, leeks NVZ closed period, lettuce/rocket nitrate limits, celery top-dressing reminder
- **Nitrogen application timing** — `timing` command returns per-dressing schedule and amounts for all major crop types including all 34 vegetable crops, taking into account the total N rate (single vs split dressings) and soil type; vegetable crops use the RB209 Section 6 seedbed-cap rule (≤100 kg N/ha in seedbed, remainder as top dressing after establishment)
- **Yield-adjusted recommendations** — optional `--expected-yield` flag on `recommend`, `nitrogen`, `phosphorus`, and `potassium` commands scales N, P2O5, and K2O for deviations from the RB209 baseline yield; supported for 19 vegetable crops (RB209 Tables 6.27 + 6.8), winter wheat, winter oats, and potatoes
- **Break-even ratio (BER) adjustment** — optional `--ber` flag on `recommend` and `nitrogen` commands adjusts cereal N recommendations based on the fertiliser cost to grain price ratio (RB209 Tables 4.25–4.26), with linear interpolation between table values
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
| `timing` | Nitrogen application timing and dressing schedule for a crop |
| `sns` | Calculate SNS index from field assessment (Tables 4.3–4.5) |
| `sns-smn` | Calculate SNS index from direct soil mineral N measurement |
| `sns-ley` | Calculate SNS index from grass ley history (Table 4.6) |
| `veg-sns` | Calculate SNS index for vegetable crops (Tables 6.2–6.4) |
| `veg-smn` | Calculate SNS index for vegetable crops from SMN (Table 6.6) |
| `organic` | Calculate nutrients from organic material applications |
| `lime` | Calculate lime requirement to raise soil pH |
| `list-crops` | List all supported crops (use `--category vegetables` to filter) |
| `list-materials` | List all supported organic materials |

See [CLI.md](CLI.md) for the full command reference with all arguments and examples.

## Supported Crops

**Arable** -- winter wheat (feed/milling), spring wheat, winter barley, spring barley, winter oats, spring oats, winter rye, winter/spring oilseed rape, linseed, peas, field beans, sugar beet, forage maize

**Potatoes** -- maincrop, early, seed

**Grassland** -- grazed, silage, hay, grazed with one silage cut

**Vegetables** (34 crops, RB209 Section 6) -- asparagus (establishment / subsequent), Brussels sprouts, storage cabbage, head cabbage (pre/post 31 Dec), collards (pre/post 31 Dec), cauliflower (summer/autumn, winter seedbed, winter top dressing), calabrese, self-blanching celery (seedbed N), peas (market pick), broad beans, dwarf/runner beans (seedbed N), radish, sweetcorn, lettuce (whole head / baby leaf), wild rocket, bulb onions, salad onions, leeks, beetroot, swedes, turnips and parsnips, carrots, bulbs and bulb flowers, coriander, mint (establishment / subsequent), courgettes (seedbed N / top dressing N)

Run `rb209 list-crops --category vegetables` to see all vegetable slugs.

## Requirements

- Python 3.10+
- No external dependencies

## Testing

```bash
python -m unittest discover tests
```

## License

[GPL-3.0-or-later](LICENSE)
