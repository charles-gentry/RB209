# TODO — Features Not Yet Implemented

This file lists features from RB209 Section 6 (and other sections) that are
documented in the reference material but were explicitly excluded from the
current VEG.md implementation plan, or are planned for future work.

---

## Vegetable Crops (Section 6)

### ~~Yield Adjustments for Vegetable Crops~~ ✓ Implemented
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

### Leaf Analysis Tables
- **Source**: RB209 Tables 6.10, 6.13, 6.15, 6.21, 6.23
- **Description**: Reference ranges for leaf nutrient concentrations in
  asparagus, brassicas, celery, alliums, and root vegetables.  These are
  diagnostic reference tables only; no kg/ha values to compute.

### ~~Nitrogen Timing Rules for Vegetable Crops~~ ✓ Implemented
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

### Sodium Recommendations
- **Source**: RB209 Section 6, asparagus and celery notes
- **Description**: Asparagus may require up to 500 kg Na₂O/ha; celery
  responds to sodium on most soils.  Sodium is not currently a supported
  nutrient in the engine.  Requires a general sodium module.

### Micronutrient Guidance
- **Source**: RB209 Table 6.9
- **Description**: Qualitative risk factors for boron, molybdenum, manganese,
  iron and other trace elements in vegetable crops.  Only qualitative
  guidance is given in RB209; no kg/ha values to implement.

### Fertigation Guidance
- **Source**: RB209 Section 6 general notes
- **Description**: Advisory text on applying nutrients through irrigation
  systems.  Advisory only; no quantitative tables to implement.

### Asparagus Year 3+ Variable N Rate
- **Source**: RB209 Table 6.11
- **Description**: From year 3 onward, asparagus N rate (40–80 kg N/ha)
  depends on winter rainfall and cutting intensity.  The current
  `veg-asparagus` slug returns the year-2 benchmark of 120 kg N/ha for
  all indices; the `timing` command adds a note directing users to seek
  FACTS advice for year 3+.  A more complete implementation would accept a
  `year` parameter and a measured winter-rainfall amount to compute the
  year 3+ rate (no fixed per-index table exists in RB209).

### ~~Courgette Top-Dressing Amount~~ ✓ Implemented
- **Source**: RB209 Table 6.26
- **Status**: Implemented.  `veg-courgettes-topdress` crop slug added.
  Returns 75 kg N/ha at SNS 0–3, 0 at SNS 4–6.  P2O5 and K2O are 0
  (applied at seedbed stage); S is 0.

---

## Other Sections (Out of Scope for VEG.md)

### Section 7 — Fruit, Vines, and Hops
- Full nutrient recommendations for top fruit, soft fruit, vines, and hops
  are not implemented.  Reference data is available in `ref/section7_fruit_vines_hops.md`.

### NVZ N-max Limits for Vegetable Crops
- **Source**: Defra NVZ guidance / RB209 Section 6 notes
- **Description**: Whole-farm N-max limits specific to vegetable crop types
  are not populated in `NVZ_NMAX`.  The engine will not issue an N-max
  warning for vegetable crops that exceed typical thresholds.

### Organic Soil Vegetable SNS — Full Field Assessment
- For organic and peat soils, the vegetable SNS tables (6.2–6.4) are
  replaced by an advisory note to consult a FACTS Qualified Adviser.
  A future enhancement could provide a structured SMN-based lookup using
  `smn_to_sns_index_veg()` for these soils as the preferred method.

---

*Last updated: 2026-02-24. See VEG.md for the original implementation plan.*

<!-- Yield adjustment implemented 2026-02-24 -->
