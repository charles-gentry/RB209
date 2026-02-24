# TODO — Features Not Yet Implemented

This file lists features from RB209 that are documented in the reference
material but not yet implemented, along with recently completed items for
reference.  See VEG.md for the original implementation plan.

---

## Vegetable Crops (Section 6) — Pending

The core Section 6 vegetable implementation is complete (all 34 crop slugs,
full N/P/K/Mg/S tables, SNS/SMN commands, yield adjustments, timing rules,
advisory notes, and `--k-upper-half` flag).  The items below are genuinely
blocked by missing regulatory/reference data or are qualitative-only guidance
with no quantitative values to implement.

### Asparagus Year 3+ Variable N Rate
- **Source**: RB209 Table 6.11
- **Status**: Blocked — no fixed per-SNS-index table exists in RB209.
- **Description**: From year 3 onward, asparagus N rate (40–80 kg N/ha)
  depends on winter rainfall and cutting intensity.  The current
  `veg-asparagus` slug returns the year-2 benchmark of 120 kg N/ha for
  all indices; the `timing` command adds a note directing users to seek
  FACTS advice for year 3+.  A more complete implementation would accept a
  `year` parameter and a measured winter-rainfall amount to compute the
  year 3+ rate — but no fixed per-index table exists in RB209 to back this.

### NVZ N-max Limits for Vegetable Crops
- **Source**: Defra Nitrate Pollution Prevention Regulations 2015, Schedule 8
- **Status**: Blocked — Schedule 8 limits for vegetable crop groups are not
  reproduced in any `ref/` source file.  Section 6 of the reference material
  only mentions NVZ closed-period rules (for leeks); it does not tabulate
  whole-farm N-max values by vegetable type.  When the Schedule 8 values are
  available they should be added to `NVZ_NMAX` in `rb209/data/nitrogen.py`.
- **Description**: Whole-farm N-max limits specific to vegetable crop types
  are not populated in `NVZ_NMAX`.  The engine will not issue an N-max
  warning for vegetable crops that exceed typical thresholds.

### Sodium Recommendations
- **Source**: RB209 Section 6, asparagus and celery notes
- **Status**: Blocked — requires a general sodium module (new nutrient type).
- **Description**: Asparagus may require up to 500 kg Na₂O/ha; celery
  responds to sodium on most soils.  Sodium is not currently a supported
  nutrient in the engine.  Requires adding Na₂O to the nutrient model before
  crop-specific recommendations can be exposed.

### Leaf Analysis Tables
- **Source**: RB209 Tables 6.10, 6.13, 6.15, 6.21, 6.23
- **Status**: Out of scope — diagnostic reference tables only; no kg/ha
  values to compute.
- **Description**: Reference ranges for leaf nutrient concentrations in
  asparagus, brassicas, celery, alliums, and root vegetables.

### Micronutrient Guidance
- **Source**: RB209 Table 6.9
- **Status**: Out of scope — qualitative guidance only; no kg/ha values.
- **Description**: Qualitative risk factors for boron, molybdenum, manganese,
  iron and other trace elements in vegetable crops.

### Fertigation Guidance
- **Source**: RB209 Section 6 general notes
- **Status**: Out of scope — advisory text only; no quantitative tables.
- **Description**: Advisory text on applying nutrients through irrigation
  systems.

---

## Other Sections — Pending

### Section 7 — Fruit, Vines, and Hops
- **Status**: Out of scope for the current implementation cycle.
- Reference data is available in `ref/section7_fruit_vines_hops.md`.

---

## Recently Completed

### ~~Organic Soil Vegetable SNS — Full Field Assessment~~ ✓
- **Source**: RB209 Tables 6.2–6.4
- **Status**: Implemented.  `calculate_veg_sns()` now provides a full field
  assessment for organic and peat soils:
  - A `VEG_SNS_ORGANIC_ADVISORY` lookup table in `rb209/data/sns.py` records
    the advisory ranges verbatim from Tables 6.2–6.4: SNS Index 3–6 for
    organic soils and SNS Index 4–6 for peat soils.
  - The engine returns a representative mid-range index (4 for organic,
    5 for peat) with `method="veg-field-assessment-advisory"` to distinguish
    it from a calculated mineral-soil lookup.
  - Three structured advisory notes are generated: (1) the specific range
    from Tables 6.2–6.4, (2) a recommendation to use the `veg-smn` command
    with a soil mineral nitrogen measurement for a site-specific index, and
    (3) a reminder to consult a FACTS Qualified Adviser.
  - Existing behaviour (advisory index, FACTS note) is preserved; the method
    string and note wording are improved.

### ~~Yield Adjustments for Vegetable Crops~~ ✓
- **Source**: RB209 Table 6.27 (N baseline and uptake), Table 6.8 (P2O5/K2O offtake)
- **Status**: Implemented in `rb209/data/yield_adjustments.py`.  19 vegetable
  crop slugs added with `baseline_yield`, `n_adjust_per_t`, `p_adjust_per_t`,
  and `k_adjust_per_t` parameters.  The N adjustment per tonne is derived from
  `N_uptake / (baseline_yield × 0.60)` (linear approximation for small yield
  changes, 60 % fertiliser recovery as per RB209 Section 6).  P2O5 and K2O
  adjustments use the per-tonne offtake values from Table 6.8; where no
  Table 6.8 entry exists those adjustments are 0.  Crops explicitly excluded
  by the Table 6.27 footnote (insufficient data) remain out of scope:
  asparagus, celery, peas/beans, sweetcorn, courgettes, and bulbs.

### ~~Nitrogen Timing Rules for Vegetable Crops~~ ✓
- **Source**: RB209 Section 6, per-crop notes
- **Status**: Implemented in `rb209/data/timing.py`.  Timing rules cover:
  - Asparagus establishment (three equal split dressings)
  - Asparagus year 2 (single dressing by end-Feb/early-Mar)
  - All seedbed-cap crops: ≤100 kg N/ha in seedbed; remainder as top
    dressing after establishment (`fixed_amount` engine support added)
  - Cauliflower winter split slugs (separate seedbed / top-dressing rules)
  - Self-blanching celery (seedbed only; top-dressing note)
  - Bulbs (single top dressing before emergence)
  - Onions (bulb onions: seedbed cap; salad onions: single at sowing)
  - Leeks (seedbed cap with NVZ closed-period note)
  - Lettuce / rocket (single at transplanting with nitrate note)
  - Mint (single in spring)
  - N-fixing crops (peas, broad beans — not applicable note)

### ~~Courgette Top-Dressing Amount~~ ✓
- **Source**: RB209 Table 6.26
- **Status**: Implemented.  `veg-courgettes-topdress` crop slug added.
  Returns 75 kg N/ha at SNS 0–3, 0 at SNS 4–6.  P2O5 and K2O are 0
  (applied at seedbed stage); S is 0.

### ~~Section 6 Core Implementation~~ ✓
- **Status**: Fully implemented across 11 implementation steps in VEG.md.
  All 34 vegetable crop slugs are registered in `CROP_INFO` with full
  N/P/K/Mg/S recommendation tables, SNS field-assessment and SMN-measurement
  commands, K Index 2 split (`--k-upper-half`), advisory notes, and
  471-test coverage.

---

*Last updated: 2026-02-24 (organic soil veg SNS completed).*
