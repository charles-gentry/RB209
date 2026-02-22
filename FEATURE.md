# FEATURE.md — Implementation Plan

Full implementation plan for features and contextual advisory notes that RB209
describes but that the tool does not yet surface (or surfaces only partially).
Organised into four phases by dependency order and priority.  Each feature
specifies the files to change, the implementation steps, and the tests to write.

**Baseline:** 166 tests passing, 0 failures.

---

## Phase 1 — Contextual Warnings (notes-only, no new CLI flags)

These features add advisory notes to existing outputs without changing function
signatures, data tables, or CLI arguments.  They are low-risk and can land
independently of each other.

---

### 1.1 NVZ N-max Warnings

**Priority:** High | **Complexity:** Low | **RB209 Source:** S4 Table 4.17/4.18 footnotes

The RB209 recommendation tables flag values that exceed the NVZ whole-farm
N-max limit (e.g. 220 kg N/ha for most arable crops).  Add a warning note when
the computed N recommendation exceeds the NVZ threshold for the crop type.

#### Data

Add to `rb209/data/nitrogen.py`:

```python
# NVZ whole-farm N-max limits by crop group (kg N/ha).
# Source: RB209 Table 4.17 footnote "a", Defra NVZ guidance.
NVZ_NMAX: dict[str, float] = {
    "winter-wheat-feed": 220,
    "winter-wheat-milling": 220,
    "spring-wheat": 220,
    "winter-barley": 220,
    "spring-barley": 220,
    "winter-oats": 220,
    "spring-oats": 220,
    "winter-rye": 220,
    "winter-oilseed-rape": 250,
    "spring-oilseed-rape": 250,
    "grass-grazed": 300,
    "grass-silage": 300,
    "grass-hay": 300,
    "grass-grazed-one-cut": 300,
    "potatoes-maincrop": 270,
    "potatoes-early": 270,
    "potatoes-seed": 270,
}
```

#### Files to modify

| File | Change |
|------|--------|
| `rb209/data/nitrogen.py` | Add `NVZ_NMAX` dict |
| `rb209/engine.py` | Import `NVZ_NMAX`; in `recommend_all()`, after computing `n`, compare against `NVZ_NMAX.get(crop)` and append a warning note when exceeded |
| `tests/test_engine.py` | New `TestNVZWarnings` class |

#### Implementation steps

1. Add the `NVZ_NMAX` dict to `rb209/data/nitrogen.py`.
2. In `engine.py`, import `NVZ_NMAX`.
3. In `recommend_all()`, after `n = recommend_nitrogen(...)`, check
   `if crop in NVZ_NMAX and n > NVZ_NMAX[crop]` and append:
   `"N recommendation ({n} kg/ha) exceeds the NVZ N-max limit ({limit} kg/ha) for this crop type. The N-max applies as a whole-farm average."`
4. Add tests (see below).

#### Tests — `tests/test_engine.py::TestNVZWarnings`

```
test_nvz_warning_when_n_exceeds_limit
    recommend_all("winter-wheat-feed", sns_index=0, p_index=2, k_index=2)
    → N = 220.  Threshold = 220.  No warning (at limit, not over).

test_nvz_warning_when_n_exceeds_limit_soil_specific
    recommend_all("winter-wheat-feed", sns_index=0, p_index=2, k_index=2, soil_type="medium")
    → N = 250 (soil-specific).  Threshold = 220.  Warning present.

test_nvz_no_warning_when_under_limit
    recommend_all("winter-wheat-feed", sns_index=3, p_index=2, k_index=2)
    → N = 120.  No NVZ note.

test_nvz_no_warning_for_crop_without_limit
    recommend_all("sugar-beet", sns_index=0, p_index=2, k_index=2)
    → sugar-beet not in NVZ_NMAX.  No NVZ note.

test_nvz_warning_text_contains_values
    Assert the note contains both the recommendation and the limit as integers.
```

---

### 1.2 Potash Split Warning for Potatoes

**Priority:** Medium | **Complexity:** Low | **RB209 Source:** S5 p.9

When potash recommendation for any potato crop exceeds 300 kg K₂O/ha, advise
splitting: half in late autumn/winter, half in spring.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | In `recommend_all()`, after computing `k`, check if crop is a potato type and `k > 300` |
| `tests/test_engine.py` | New `TestPotashSplitWarnings` class |

#### Implementation steps

1. In `recommend_all()`, after `k = recommend_potassium(...)`:
   ```python
   if crop.startswith("potatoes-") and k > 300:
       notes.append(
           f"K2O recommendation ({k:.0f} kg/ha) exceeds 300 kg/ha. "
           "Apply half in late autumn/winter and half in spring."
       )
   ```
2. Add tests.

#### Tests — `tests/test_engine.py::TestPotashSplitWarnings`

```
test_potash_split_note_for_potatoes_above_300
    Use k_index=0 for potatoes-maincrop (K2O = 300).
    → At 300, no note (threshold is ">300", not ">=300").
    Verify no "split" note.

test_potash_split_note_not_present_at_300
    potatoes-maincrop at k_index=0 → K2O = 300 exactly.
    Assert "split" not in notes.

test_potash_split_note_not_for_cereals
    winter-wheat-feed at k_index=0 → K2O = 105.
    Assert no potash split note even if hypothetically high.

test_potash_no_split_for_low_k
    potatoes-early at k_index=2 → K2O = 150.
    No split note.
```

> Note: With current data tables, no potato K2O value exceeds 300 (the maximum
> is 300 for maincrop at K index 0).  The logic is still worth adding for
> correctness when yield adjustments (Phase 3) raise the effective K2O value.

---

### 1.3 Potash Split Warning for Grass Silage

**Priority:** Medium | **Complexity:** Low | **RB209 Source:** S3 Table 3.3 footnotes

Spring potash for first-cut silage should be limited to 80–90 kg K₂O/ha to
minimise luxury uptake.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | In `recommend_all()`, check grass-silage K2O > 90 |
| `tests/test_engine.py` | New tests in `TestPotashSplitWarnings` |

#### Implementation steps

1. In `recommend_all()`, after computing `k`:
   ```python
   if crop == "grass-silage" and k > 90:
       notes.append(
           f"Limit spring K2O application for 1st cut to 80-90 kg/ha "
           "to minimise luxury uptake. Apply balance in previous autumn."
       )
   ```
2. Add tests.

#### Tests

```
test_grass_silage_potash_split_note_at_k0
    grass-silage at k_index=0 → K2O = 150.
    Assert "luxury uptake" in notes.

test_grass_silage_no_potash_note_at_k2
    grass-silage at k_index=2 → K2O = 60.
    Assert "luxury uptake" not in notes.

test_potash_luxury_note_not_for_grazed_grass
    grass-grazed at k_index=0 → K2O = 60.
    No luxury-uptake note.
```

---

### 1.4 Lime-Before-Potatoes Warning

**Priority:** Medium | **Complexity:** Low | **RB209 Source:** S5 p.11

Warn in lime output when the crop context is potatoes or when the user could
benefit from the advisory.  Since `calculate_lime()` does not currently know
the crop, this feature adds an optional `crop` parameter.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | Add optional `crop: str | None = None` param to `calculate_lime()` |
| `rb209/cli.py` | Add optional `--crop` to the `lime` subcommand; pass to `calculate_lime()` |
| `tests/test_engine.py` | New tests in `TestCalculateLime` |
| `tests/test_cli.py` | New CLI integration test |

#### Implementation steps

1. Add `crop: str | None = None` to `calculate_lime()` signature.
2. After computing `lime_needed`, if `crop` starts with `"potatoes-"` and
   `lime_needed > 0`:
   ```python
   notes.append(
       "Avoid liming immediately before potatoes — increases common scab "
       "risk and manganese deficiency risk."
   )
   ```
3. Add `--crop` argument to `lime` subcommand in CLI (optional, no default).
4. Pass `crop` through from handler.

#### Tests

```
test_lime_potato_scab_warning
    calculate_lime(5.5, 6.5, "medium", crop="potatoes-maincrop")
    → lime > 0.  Assert "common scab" in notes.

test_lime_no_potato_warning_when_no_lime_needed
    calculate_lime(7.0, 6.5, "medium", crop="potatoes-maincrop")
    → lime = 0.  Assert "common scab" not in notes.

test_lime_no_potato_warning_for_cereals
    calculate_lime(5.5, 6.5, "medium", crop="winter-wheat-feed")
    → Assert "common scab" not in notes.

test_lime_no_potato_warning_when_no_crop
    calculate_lime(5.5, 6.5, "medium")
    → Assert "common scab" not in notes.

CLI test:
test_lime_with_crop_potato_shows_scab_warning
    _run_cli("lime", "--current-ph", "5.5", "--target-ph", "6.5",
             "--soil-type", "medium", "--crop", "potatoes-maincrop")
    → assert "common scab" in stdout.lower()
```

---

### 1.5 Over-Liming Trace Element Warnings

**Priority:** Low | **Complexity:** Low | **RB209 Source:** S1 p.14, S3 p.18

When the target pH is high enough to risk inducing trace element deficiencies,
add a warning note.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | Add checks after computing lime in `calculate_lime()` |
| `tests/test_engine.py` | New tests in `TestCalculateLime` |

#### Implementation steps

1. In `calculate_lime()`, after computing `lime_needed`, add the following
   checks (only when `lime_needed > 0`):
   - If `target_ph > 7.0` and `land_use == "grassland"`:
     `"Avoid liming grassland above pH 7.0 — may induce copper, cobalt and selenium deficiencies."`
   - If `target_ph > 7.5`:
     `"Manganese deficiency risk increases above pH 7.5."`
   - If `soil_type == "light"` and `target_ph > 6.5`:
     `"On sandy soils, manganese deficiency is more likely above pH 6.5."`
   - If `soil_type == "organic"` and `target_ph > 6.0`:
     `"On organic/peaty soils, manganese deficiency is more likely above pH 6.0."`
2. Add tests.

#### Tests

```
test_overlime_grassland_ph7_warning
    calculate_lime(6.5, 7.5, "medium", land_use="grassland")
    → Assert "copper, cobalt" in notes.

test_overlime_no_warning_arable_ph7
    calculate_lime(6.5, 7.5, "medium", land_use="arable")
    → "copper, cobalt" not in notes (only applies to grassland).

test_overlime_mn_warning_above_7_5
    calculate_lime(7.0, 8.0, "medium")
    → Assert "Manganese" in notes.

test_overlime_sandy_mn_warning_above_6_5
    calculate_lime(6.0, 7.0, "light")
    → Assert "sandy" and "manganese" in notes.

test_overlime_organic_mn_warning_above_6_0
    calculate_lime(5.5, 6.5, "organic")
    → Assert "organic" or "peaty" and "manganese" in notes.

test_no_overlime_warning_when_no_lime_needed
    calculate_lime(7.0, 6.5, "medium")
    → lime = 0, no over-liming notes.
```

---

### 1.6 Hypomagnesaemia Warning for Grassland Potash

**Priority:** Low | **Complexity:** Low | **RB209 Source:** S3 p.10

Warn when applying potash to grassland at Mg Index 0.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | In `recommend_all()`, check grassland + mg_index == 0 |
| `tests/test_engine.py` | New tests |

#### Implementation steps

1. In `recommend_all()`, after computing all nutrients:
   ```python
   if info["category"] == "grassland" and mg_index == 0 and k > 0:
       notes.append(
           "Mg Index 0 on grassland: risk of hypomagnesaemia (grass staggers). "
           "Avoid applying potash in spring. Apply 50-100 kg MgO/ha every 3-4 years."
       )
   ```
2. Add tests.

#### Tests

```
test_hypomagnesaemia_warning_grass_grazed_mg0
    recommend_all("grass-grazed", 2, 2, 0, mg_index=0)
    → k > 0.  Assert "hypomagnesaemia" in notes.

test_no_hypomagnesaemia_warning_mg2
    recommend_all("grass-grazed", 2, 2, 0, mg_index=2)
    → Assert "hypomagnesaemia" not in notes.

test_no_hypomagnesaemia_warning_arable
    recommend_all("winter-wheat-feed", 2, 2, 0, mg_index=0)
    → Assert "hypomagnesaemia" not in notes.

test_no_hypomagnesaemia_warning_k_zero
    recommend_all("grass-grazed", 2, 2, 3, mg_index=0)
    → k = 0.  Assert "hypomagnesaemia" not in notes.
```

---

### 1.7 Clover Sward N-Fixation Inhibition Warning

**Priority:** Low | **Complexity:** Low | **RB209 Source:** S3 p.16

Warn that applying mineral N to grass/clover swards inhibits clover N fixation.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/data/crops.py` | Add `"clover_risk"` key to grassland entries |
| `rb209/engine.py` | In `recommend_all()`, check for clover_risk flag and N > 0 |
| `tests/test_engine.py` | New tests |

#### Implementation steps

1. In `CROP_INFO`, add `"clover_risk": True` to all grassland entries.
2. In `recommend_all()`:
   ```python
   if info.get("clover_risk") and n > 0:
       notes.append(
           "Mineral N inhibits clover N fixation. If the sward contains "
           "significant clover, reduce or omit N applications."
       )
   ```
3. Add tests.

#### Tests

```
test_clover_warning_grass_grazed_with_n
    recommend_all("grass-grazed", 2, 2, 2)
    → N > 0.  Assert "clover" in notes.

test_clover_warning_not_shown_when_n_zero
    recommend_all("grass-grazed", 6, 2, 2)
    → N = 0.  Assert "clover" not in notes.

test_clover_warning_not_shown_for_arable
    recommend_all("winter-wheat-feed", 2, 2, 2)
    → Assert "clover" not in notes.
```

---

### 1.8 Organic Application Condition Warnings

**Priority:** Low | **Complexity:** Low | **RB209 Source:** S1 p.6

Warn about soil condition restrictions for organic material application.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | In `calculate_organic()`, append a standard advisory note |
| `tests/test_organic.py` | New test |

#### Implementation steps

1. In `calculate_organic()`, after computing the result, append:
   ```python
   # This would require adding a notes field to OrganicNutrients — see below.
   ```
   **Alternative:** Since `OrganicNutrients` has no `notes` field, add a
   `notes: list[str]` field (default empty) to the dataclass, then populate it.

2. If adding notes to `OrganicNutrients`:
   - Update `rb209/models.py`: add `notes: list[str] = field(default_factory=list)`
   - Update `rb209/formatters.py`: pass `result.notes` to `_box()` in
     `format_organic()`
   - In `calculate_organic()`, build notes list and include:
     `"Do not apply organic materials to soils that are waterlogged, frozen hard, snow-covered, or deeply cracked."`

#### Tests

```
test_organic_condition_warning_present
    result = calculate_organic("cattle-fym", 25)
    → Assert "waterlogged" in result.notes or similar.

test_organic_notes_field_exists
    result = calculate_organic("cattle-fym", 25)
    → Assert hasattr(result, "notes") and isinstance(result.notes, list).
```

---

### 1.9 Seedbed N+K₂O Combine-Drill Limit

**Priority:** Low | **Complexity:** Low | **RB209 Source:** S4 p.21

When combined N + K₂O exceeds 150 kg/ha for sandy (light) soils, warn about
seedling damage risk.

#### Files to modify

| File | Change |
|------|--------|
| `rb209/engine.py` | In `recommend_all()`, check if soil_type == "light" and N + K > 150 |
| `tests/test_engine.py` | New tests |

#### Implementation steps

1. In `recommend_all()`:
   ```python
   if soil_type == "light" and (n + k) > 150 and info["category"] == "arable":
       notes.append(
           f"On sandy soils, do not combine-drill more than 150 kg/ha of N + K2O "
           f"(current total: {n + k:.0f} kg/ha). Risk of seedling damage."
       )
   ```
2. Add tests.

#### Tests

```
test_combine_drill_warning_light_soil_high_nk
    recommend_all("winter-wheat-feed", 0, 2, 0, soil_type="light")
    → N = 180, K = 105, total = 285.  Assert "combine-drill" in notes.

test_no_combine_drill_warning_medium_soil
    recommend_all("winter-wheat-feed", 0, 2, 0, soil_type="medium")
    → Assert "combine-drill" not in notes.

test_no_combine_drill_warning_low_nk
    recommend_all("winter-wheat-feed", 4, 2, 3, soil_type="light")
    → N = 60, K = 0.  Assert "combine-drill" not in notes.

test_no_combine_drill_warning_grassland
    recommend_all("grass-silage", 0, 2, 0, soil_type="light")
    → Not arable.  Assert "combine-drill" not in notes.
```

---

## Phase 2 — Nitrogen Timing and Split Dressings ✓ IMPLEMENTED

The highest-impact feature from FEATURE.md.  Adds a new `nitrogen_timing()`
engine function and `timing` subcommand that, given a crop and total N, returns
split-dressing advice.

**Priority:** High | **Complexity:** Medium | **RB209 Source:** S3 pp.14–15,
S4 pp.26–31, S5 p.23

**Status:** Complete — 86 new tests passing (252 total).

---

### 2.1 Data Table — N Timing Rules

#### New file: `rb209/data/timing.py`

Define per-crop timing rules as structured data.  Each rule is a dict describing
the conditions and the resulting split schedule.

```python
"""Nitrogen application timing and split dressing rules.

Each entry in NITROGEN_TIMING_RULES is a list of rule dicts for a given crop.
Rules are evaluated in order; the first matching rule is used.

Rule dict keys:
  "condition":  callable(total_n: float, soil_type: str | None) -> bool
  "splits":     list of dicts with keys "fraction", "timing", "notes"
                or callable(total_n) -> list[dict]
  "notes":      list[str]  — additional advisory notes
"""
```

**Crops with timing data:**

| Crop | Timing rules (from FEATURE.md §1) |
|------|----------------------------------|
| `winter-wheat-feed`, `winter-wheat-milling` | §1.1 — one/two dressings; >120 split 50/50 |
| `winter-barley` | §1.2 — <100 single; 100-200 two splits; >=200 three splits |
| `spring-wheat` | §1.3 — conditional on drilling date and soil type |
| `spring-barley` | §1.4 — <100 single; >=100 two splits |
| `winter-rye` | §1.6 — same as wheat; lodging adjustment |
| `potatoes-*` | §1.7 — seedbed vs emergence split by soil type |
| `grass-silage` | §1.8 — per-cut splits, SNS adjustment |
| `grass-grazed` | §1.9 — monthly rotation schedule |
| `grass-hay` | §1.10 — single application per cut |

#### Data structure example (winter barley)

```python
NITROGEN_TIMING_RULES["winter-barley"] = [
    {
        "max_n": 99,
        "splits": [
            {"amount": "all", "timing": "GS30-31", "note": "Single dressing at GS30-31."},
        ],
    },
    {
        "min_n": 100, "max_n": 199,
        "splits": [
            {"fraction": 0.5, "timing": "Late tillering (mid-Feb/early Mar)"},
            {"fraction": 0.5, "timing": "GS30-31"},
        ],
    },
    {
        "min_n": 200,
        "splits": [
            {"fraction": 0.4, "timing": "Late tillering (mid-Feb/early Mar)"},
            {"fraction": 0.4, "timing": "GS30-31"},
            {"fraction": 0.2, "timing": "GS32"},
        ],
        "notes": ["Consider reducing by 25 kg N/ha if lodging risk is high."],
    },
]
```

---

### 2.2 New Data Model — `NitrogenTimingResult`

#### File: `rb209/models.py`

```python
@dataclass
class NitrogenSplit:
    """A single nitrogen dressing within a split schedule."""
    amount: float          # kg N/ha
    timing: str            # e.g. "GS30-31", "Mid-Feb to early Mar"
    note: str = ""

@dataclass
class NitrogenTimingResult:
    """Nitrogen split dressing advice for a crop."""
    crop: str
    total_n: float         # kg N/ha
    splits: list[NitrogenSplit]
    notes: list[str] = field(default_factory=list)
```

---

### 2.3 Engine Function — `nitrogen_timing()`

#### File: `rb209/engine.py`

```python
def nitrogen_timing(
    crop: str,
    total_n: float,
    soil_type: str | None = None,
) -> NitrogenTimingResult:
    """Return nitrogen split dressing advice for a given crop and total N.

    Args:
        crop: Crop value string.
        total_n: Total nitrogen recommendation (kg N/ha).
        soil_type: Optional soil type (affects timing for some crops).

    Returns:
        NitrogenTimingResult with split schedule and advisory notes.
    """
```

Implementation:
1. Validate crop.
2. Look up `NITROGEN_TIMING_RULES[crop]`.
3. Iterate rules; find first where `total_n` matches the `min_n`/`max_n` range.
4. Compute split amounts from fractions × `total_n` (round to nearest integer).
5. Build and return `NitrogenTimingResult`.
6. If no rules exist for the crop, return a single split with the full amount
   and a note: `"No specific timing guidance for {crop}. Apply as a single dressing."`

---

### 2.4 Formatter — `format_timing()`

#### File: `rb209/formatters.py`

Add `format_timing(result: NitrogenTimingResult, fmt: str = "table") -> str`.

Table format: a box showing each split as a row with "Dressing N" → "X kg/ha at
{timing}".  Notes appended below.

JSON format: `dataclasses.asdict(result)`.

---

### 2.5 CLI Subcommand — `timing`

#### File: `rb209/cli.py`

New subcommand `timing`:
```
rb209 timing --crop winter-barley --total-n 180 [--soil-type medium]
```

Arguments:
- `--crop` (required): crop choice
- `--total-n` (required, float): total N recommendation in kg/ha
- `--soil-type` (optional): for soil-dependent timing rules
- `--format` (optional): table or json

Handler calls `nitrogen_timing()` and prints via `format_timing()`.

---

### 2.6 Integration with `recommend` and `nitrogen` Commands

After computing the N recommendation, both `_handle_recommend` and
`_handle_nitrogen` should append a note referencing the `timing` command:

```python
if total_n > 0:
    notes.append(
        f"Run 'rb209 timing --crop {crop} --total-n {total_n:.0f}' for "
        "application timing and split dressing guidance."
    )
```

This avoids changing the existing output structure while directing users to
the new feature.

---

### 2.7 Tests — `tests/test_timing.py` (new file)

```
class TestNitrogenTimingWinterBarley:
    test_under_100_single_dressing
        nitrogen_timing("winter-barley", 80) → 1 split, amount=80, timing contains "GS30"

    test_100_to_200_two_splits
        nitrogen_timing("winter-barley", 180) → 2 splits
        splits[0].amount = 90, splits[1].amount = 90

    test_200_plus_three_splits
        nitrogen_timing("winter-barley", 200) → 3 splits
        splits: 80 / 80 / 40.  "lodging" in notes.

class TestNitrogenTimingWinterWheat:
    test_under_120_single_dressing
        nitrogen_timing("winter-wheat-feed", 100) → 1 split

    test_over_120_two_splits
        nitrogen_timing("winter-wheat-feed", 180) → 2 splits, 90/90

    test_milling_wheat_protein_note
        nitrogen_timing("winter-wheat-milling", 190)
        → "protein" in notes (GS32-GS39 timing note)

class TestNitrogenTimingSpringBarley:
    test_under_100_single_dressing
        nitrogen_timing("spring-barley", 80) → 1 split

    test_100_plus_two_splits
        nitrogen_timing("spring-barley", 120) → 2 splits, first = 40

class TestNitrogenTimingPotatoes:
    test_light_soil_split
        nitrogen_timing("potatoes-maincrop", 270, soil_type="light")
        → 2 splits: 2/3 seedbed, 1/3 post-emergence

    test_non_light_soil_single
        nitrogen_timing("potatoes-maincrop", 270, soil_type="medium")
        → 1 split in seedbed

class TestNitrogenTimingGrassSilage:
    test_high_first_cut_split
        nitrogen_timing("grass-silage", 320)
        → multiple splits across cuts

class TestNitrogenTimingNoRules:
    test_crop_without_rules_returns_single
        nitrogen_timing("linseed", 70)
        → 1 split, "No specific timing guidance" in notes

class TestNitrogenTimingEdgeCases:
    test_zero_n
        nitrogen_timing("winter-barley", 0) → 0 or 1 split with amount=0

    test_invalid_crop_raises
        nitrogen_timing("banana", 100) → ValueError

    test_negative_n_raises
        nitrogen_timing("winter-barley", -10) → ValueError
```

#### CLI integration tests — `tests/test_cli.py`

```
test_timing_basic
    _run_cli("timing", "--crop", "winter-barley", "--total-n", "180")
    → returncode 0, output contains "90" (split amount)

test_timing_json
    _run_cli("timing", "--crop", "winter-barley", "--total-n", "180", "--format", "json")
    → valid JSON with "splits" key

test_timing_missing_total_n
    _run_cli("timing", "--crop", "winter-barley")
    → returncode != 0
```

---

## Phase 3 — Yield Adjustments

Add an optional `--expected-yield` parameter that adjusts N, P, and K
recommendations based on RB209 yield correction factors.

**Priority:** Medium | **Complexity:** Medium | **RB209 Source:** S4 p.26, S5 p.8

---

### 3.1 Data Table — Yield Adjustment Factors

#### New file: `rb209/data/yield_adjustments.py`

```python
"""Yield adjustment factors for N, P2O5, and K2O.

Each entry maps a crop to its adjustment parameters:
  "baseline_yield": t/ha (default assumed yield)
  "n_adjust_per_t": kg N/ha per tonne above/below baseline
  "p_adjust_per_t": kg P2O5/ha per tonne (offtake-based)
  "k_adjust_per_t": kg K2O/ha per tonne (offtake-based)
  "max_yield": optional cap on yield adjustment
"""

YIELD_ADJUSTMENTS: dict[str, dict] = {
    "winter-wheat-feed": {
        "baseline_yield": 8.0,
        "n_adjust_per_t": 20,      # 10 kg per 0.5 t = 20 per t
        "p_adjust_per_t": 7.0,     # Table 4.12 grain+straw
        "k_adjust_per_t": 10.5,
        "max_yield": 13.0,
    },
    "winter-wheat-milling": {
        "baseline_yield": 8.0,
        "n_adjust_per_t": 20,
        "p_adjust_per_t": 7.0,
        "k_adjust_per_t": 10.5,
        "max_yield": 13.0,
    },
    "winter-oats": {
        "baseline_yield": 6.0,
        "n_adjust_per_t": 20,      # Table 4.19
        "p_adjust_per_t": 7.0,
        "k_adjust_per_t": 12.0,
    },
    "potatoes-maincrop": {
        "baseline_yield": 50.0,
        "n_adjust_per_t": 0,       # No N yield adjustment for potatoes
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 5.8,     # K2O at target index
    },
    "potatoes-early": {
        "baseline_yield": 30.0,
        "n_adjust_per_t": 0,
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 5.8,
    },
    # Additional crops to be populated from RB209 Table 4.12
}
```

---

### 3.2 Engine Changes

#### File: `rb209/engine.py`

Modify `recommend_nitrogen()`, `recommend_phosphorus()`, `recommend_potassium()`
to accept an optional `expected_yield: float | None = None` parameter.

When `expected_yield` is provided:
1. Look up adjustment factors from `YIELD_ADJUSTMENTS[crop]`.
2. Compute delta = `(expected_yield - baseline_yield) × adjust_per_t`.
3. Add delta to the base recommendation.
4. Clamp result to `max(0, result)`.

Also modify `recommend_all()` to pass `expected_yield` through to each function
and add notes about the adjustment.

---

### 3.3 CLI Changes

#### File: `rb209/cli.py`

Add `--expected-yield` (optional, float, metavar="t/ha") to the `recommend`,
`nitrogen`, `phosphorus`, and `potassium` subcommands.

---

### 3.4 Tests — `tests/test_yield.py` (new file)

```
class TestYieldAdjustmentNitrogen:
    test_winter_wheat_above_baseline
        recommend_nitrogen("winter-wheat-feed", 2, expected_yield=10.0)
        → base 150 + (10.0 - 8.0) × 20 = 190

    test_winter_wheat_below_baseline
        recommend_nitrogen("winter-wheat-feed", 2, expected_yield=6.0)
        → base 150 + (6.0 - 8.0) × 20 = 110

    test_winter_wheat_at_baseline_no_change
        recommend_nitrogen("winter-wheat-feed", 2, expected_yield=8.0)
        → 150

    test_winter_wheat_capped_at_max_yield
        recommend_nitrogen("winter-wheat-feed", 2, expected_yield=15.0)
        → yield capped to 13.0: 150 + (13.0 - 8.0) × 20 = 250

    test_no_adjustment_when_yield_not_provided
        recommend_nitrogen("winter-wheat-feed", 2)
        → 150 (unchanged)

    test_crop_without_yield_data_returns_base
        recommend_nitrogen("linseed", 2, expected_yield=5.0)
        → 40 (no yield adjustment data for linseed)

    test_result_clamped_to_zero
        recommend_nitrogen("winter-wheat-feed", 5, expected_yield=4.0)
        → base 40 + (4.0 - 8.0) × 20 = -40 → clamped to 0

class TestYieldAdjustmentPotassium:
    test_potato_k_above_baseline
        recommend_potassium("potatoes-maincrop", 2, expected_yield=60.0)
        → base 180 + (60 - 50) × 5.8 = 238

    test_potato_k_below_baseline
        recommend_potassium("potatoes-maincrop", 2, expected_yield=40.0)
        → base 180 + (40 - 50) × 5.8 = 122

class TestYieldAdjustmentFull:
    test_recommend_all_with_yield_adjusts_all_nutrients
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=10.0)
        → rec.nitrogen == 190 (adjusted)
        → rec.phosphorus adjusted by (10-8)×7.0
        → rec.potassium adjusted by (10-8)×10.5

    test_recommend_all_notes_contain_yield_info
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=10.0)
        → "yield" in some note (documents the adjustment)
```

#### CLI integration tests

```
test_recommend_with_expected_yield
    _run_cli("recommend", "--crop", "winter-wheat-feed", "--sns-index", "2",
             "--p-index", "2", "--k-index", "1", "--expected-yield", "10")
    → returncode 0, "190" in stdout (adjusted N)

test_nitrogen_with_expected_yield
    _run_cli("nitrogen", "--crop", "winter-wheat-feed", "--sns-index", "2",
             "--expected-yield", "10")
    → "190" in stdout
```

---

## Phase 4 — Economic Break-Even Ratio

Add an optional `--ber` parameter for wheat and barley N recommendations.

**Priority:** Low | **Complexity:** Medium | **RB209 Source:** S4 Tables 4.25–4.26

---

### 4.1 Data Table — BER Adjustments

#### New file: `rb209/data/ber.py`

```python
"""Break-even ratio (BER) adjustments for cereal N recommendations.

BER = cost of fertiliser N (£/kg) ÷ grain value (£/kg).
Default BER is 5.0.  Tables 4.25 and 4.26 provide adjustments.

BER_ADJUSTMENTS[(crop_group, ber)] -> kg N/ha adjustment from the default.
"""

BER_ADJUSTMENTS: dict[tuple[str, float], float] = {
    # Wheat (Table 4.25)
    ("wheat", 2.0): +30,
    ("wheat", 3.0): +20,
    ("wheat", 4.0): +10,
    ("wheat", 5.0): 0,       # default
    ("wheat", 6.0): -10,
    ("wheat", 7.0): -15,
    ("wheat", 8.0): -20,
    ("wheat", 10.0): -30,
    # Barley (Table 4.26)
    ("barley", 2.0): +25,
    ("barley", 3.0): +15,
    ("barley", 4.0): +10,
    ("barley", 5.0): 0,
    ("barley", 6.0): -10,
    ("barley", 7.0): -15,
    ("barley", 8.0): -20,
    ("barley", 10.0): -25,
}

# Map crops to BER groups
CROP_BER_GROUP: dict[str, str] = {
    "winter-wheat-feed": "wheat",
    "winter-wheat-milling": "wheat",
    "spring-wheat": "wheat",
    "winter-barley": "barley",
    "spring-barley": "barley",
}
```

---

### 4.2 Engine Changes

#### File: `rb209/engine.py`

Add optional `ber: float | None = None` to `recommend_nitrogen()` and
`recommend_all()`.

When `ber` is provided:
1. Look up `CROP_BER_GROUP[crop]` — if not present, ignore BER.
2. Find the nearest BER key in `BER_ADJUSTMENTS` and interpolate.
3. Add the adjustment to the base N.
4. Clamp to `max(0, result)`.

---

### 4.3 CLI Changes

Add `--ber` (optional, float) to `recommend` and `nitrogen` subcommands.
Help text: `"Break-even ratio (fertiliser N cost £/kg ÷ grain value £/kg). Default: 5.0."`

---

### 4.4 Tests — `tests/test_ber.py` (new file)

```
class TestBERAdjustment:
    test_wheat_ber_5_no_change
        recommend_nitrogen("winter-wheat-feed", 2, ber=5.0) → 150

    test_wheat_ber_2_increases_n
        recommend_nitrogen("winter-wheat-feed", 2, ber=2.0) → 150 + 30 = 180

    test_wheat_ber_10_decreases_n
        recommend_nitrogen("winter-wheat-feed", 2, ber=10.0) → 150 - 30 = 120

    test_barley_ber_3
        recommend_nitrogen("spring-barley", 2, ber=3.0) → 100 + 15 = 115

    test_non_cereal_ignores_ber
        recommend_nitrogen("sugar-beet", 2, ber=2.0) → 80 (unchanged)

    test_ber_none_no_change
        recommend_nitrogen("winter-wheat-feed", 2) → 150

    test_ber_clamped_to_zero
        recommend_nitrogen("winter-wheat-feed", 6, ber=10.0) → max(0, 0 - 30) = 0

    test_recommend_all_with_ber
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, ber=2.0)
        → rec.nitrogen == 180

    test_recommend_all_ber_note_present
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, ber=2.0)
        → "break-even" in some note
```

#### CLI integration tests

```
test_nitrogen_with_ber
    _run_cli("nitrogen", "--crop", "winter-wheat-feed", "--sns-index", "2", "--ber", "2.0")
    → "180" in stdout

test_recommend_with_ber
    _run_cli("recommend", "--crop", "winter-wheat-feed", "--sns-index", "2",
             "--p-index", "2", "--k-index", "1", "--ber", "2.0")
    → "180" in stdout
```

---

## Implementation Order and Dependencies

```
Phase 1 (warnings)
  ├── 1.1 NVZ warnings            ← standalone
  ├── 1.2 Potash split (potatoes)  ← standalone
  ├── 1.3 Potash split (silage)    ← standalone
  ├── 1.4 Lime-before-potatoes     ← standalone (adds crop param to calculate_lime)
  ├── 1.5 Over-liming warnings     ← standalone
  ├── 1.6 Hypomagnesaemia          ← standalone
  ├── 1.7 Clover N-fixation        ← standalone
  ├── 1.8 Organic conditions       ← requires adding notes to OrganicNutrients
  └── 1.9 Combine-drill limit      ← standalone

Phase 2 (N timing)                 ← depends on nothing in Phase 1
  ├── 2.1 Data: timing rules
  ├── 2.2 Model: NitrogenTimingResult
  ├── 2.3 Engine: nitrogen_timing()
  ├── 2.4 Formatter: format_timing()
  ├── 2.5 CLI: timing subcommand
  └── 2.6 Integration notes in recommend/nitrogen

Phase 3 (yield adjustments)        ← depends on nothing in Phase 1 or 2
  ├── 3.1 Data: yield adjustment factors
  ├── 3.2 Engine: expected_yield param
  ├── 3.3 CLI: --expected-yield flag
  └── 3.4 Tests

Phase 4 (BER)                      ← depends on nothing above
  ├── 4.1 Data: BER adjustment tables
  ├── 4.2 Engine: ber param
  ├── 4.3 CLI: --ber flag
  └── 4.4 Tests
```

All four phases are independent of each other and can be developed in any
order or in parallel.  Within each phase, steps should be done in the listed
order (data → model → engine → formatter → CLI → tests).

---

## Test Summary

| Phase | New test file | New test class | Est. test count |
|-------|--------------|----------------|-----------------|
| 1.1 | `test_engine.py` | `TestNVZWarnings` | 5 |
| 1.2 | `test_engine.py` | `TestPotashSplitWarnings` | 4 |
| 1.3 | `test_engine.py` | (in `TestPotashSplitWarnings`) | 3 |
| 1.4 | `test_engine.py`, `test_cli.py` | (in `TestCalculateLime`) | 5 |
| 1.5 | `test_engine.py` | (in `TestCalculateLime`) | 6 |
| 1.6 | `test_engine.py` | `TestHypomagnesaemiaWarning` | 4 |
| 1.7 | `test_engine.py` | `TestCloverWarning` | 3 |
| 1.8 | `test_organic.py` | (new tests) | 2 |
| 1.9 | `test_engine.py` | `TestCombineDrillWarning` | 4 |
| 2 | `test_timing.py` (new) | 7 classes | ~20 |
| 2 | `test_cli.py` | (timing integration) | 3 |
| 3 | `test_yield.py` (new) | 3 classes | ~12 |
| 3 | `test_cli.py` | (yield integration) | 2 |
| 4 | `test_ber.py` (new) | 1 class | ~9 |
| 4 | `test_cli.py` | (BER integration) | 2 |
| **Total** | | | **~84 new tests** |

Combined with the existing 166 tests, the full suite should reach ~250 tests.

---

## Features Intentionally Deferred

These features from the original FEATURE.md are deferred because they require
subjective judgement, complex data entry, or regulatory data that changes
independently of the RB209 tables:

| Feature | Reason for deferral |
|---------|-------------------|
| Potato variety group / season length N ranges (S5 Table 5.10) | High complexity; requires user to know determinacy group (1–4) and growing season length; lookup table is large |
| Manure history SNS adjustment (S4 p.11) | Guidance is qualitative ("increase by 1–2 levels depending on type, rate and frequency"); cannot be reliably automated without extensive user input |
| NVZ closed-period date enforcement | Dates change by regulation and region; better handled by an external compliance layer |
| Detailed grazed grass monthly split schedule (Table 3.9) | Requires target DM yield class input and monthly rotation tracking; better as a dedicated planning tool |
| Sodium deficiency in grassland (S3) | Requires herbage analysis data not typically available at recommendation time |
| Cover crop / crop failure SNS adjustments (S4) | Qualitative guidance ("increase the SNS Index") — add as advisory notes in a future pass |
