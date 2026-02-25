# TODO — Features Not Yet Implemented

This file lists features from RB209 that are documented in the reference
material but not yet implemented.

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

## Fruit, Vines, and Hops (Section 7) — Pending

The core Section 7 fruit implementation is complete (all 18 crop slugs,
full N/P/K/Mg recommendations, soil categories, pre-planting tables,
orchard management options, strawberry SNS, and hops).

### NVZ N-max Limits for Fruit Crops
- **Source**: Defra Nitrate Pollution Prevention Regulations 2015, Schedule 8
- **Status**: Blocked — Schedule 8 limits for fruit crop groups are not
  reproduced in the `ref/` source files.
- **Description**: Whole-farm N-max limits specific to fruit crop types
  are not populated in `NVZ_NMAX`.

### Leaf and Fruit Analysis Tables
- **Source**: RB209 Tables 7.11–7.15
- **Status**: Out of scope — diagnostic reference tables only; no kg/ha
  values to compute.

### Substrate Strawberry Nutrient Solution
- **Source**: RB209 Table 7.10
- **Status**: Out of scope — mg/litre ranges for fertigation of
  substrate-grown crops; outside the soil-applied kg/ha model.

### Micronutrient Recommendations
- **Source**: RB209 Section 7
- **Status**: Out of scope — qualitative foliar-spray guidance only; no
  kg/ha values to implement.

---

*Last updated: 2026-02-25.*
