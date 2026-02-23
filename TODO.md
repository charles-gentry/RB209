# TODO — Features Not Yet Implemented

This file lists features from RB209 Section 6 (and other sections) that are
documented in the reference material but were explicitly excluded from the
current VEG.md implementation plan, or are planned for future work.

---

## Vegetable Crops (Section 6)

### Yield Adjustments for Vegetable Crops
- **Source**: RB209 Table 6.27
- **Description**: Per-crop dry-matter, harvest index, and mineralisation
  parameters needed to scale N/P/K recommendations by expected yield.
  The methodology requires additional crop-specific data not yet integrated
  into `yield_adjustments.py`.
- **Affected module**: `rb209/data/yield_adjustments.py`

### Leaf Analysis Tables
- **Source**: RB209 Tables 6.10, 6.13, 6.15, 6.21, 6.23
- **Description**: Reference ranges for leaf nutrient concentrations in
  asparagus, brassicas, celery, alliums, and root vegetables.  These are
  diagnostic reference tables only; no kg/ha values to compute.

### Nitrogen Timing Rules for Vegetable Crops
- **Source**: RB209 Section 6, per-crop notes
- **Description**: The current implementation captures seedbed/top-dressing
  splits via separate crop slugs (e.g. `veg-cauliflower-winter-seedbed` vs
  `veg-cauliflower-winter-topdress`).  A dedicated vegetable timing module
  in `timing.py` would provide structured split-schedule output via the
  `timing` command, consistent with arable crops.

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
  all indices.  A more complete implementation would accept a `year`
  parameter and a measured winter-rainfall amount to compute the
  year 3+ rate.

### Courgette Top-Dressing Amount
- **Source**: RB209 Table 6.26
- **Description**: In addition to the seedbed N (captured by
  `veg-courgettes-seedbed`), up to 75 kg N/ha top dressing may be required.
  A `veg-courgettes-topdress` slug with its own recommendation table has
  not been added.

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

*Last updated: 2026-02-23. See VEG.md for the original implementation plan.*
