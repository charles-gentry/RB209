# TODO

Items identified from running the test suite (`python -m pytest tests/ -v`).

**Summary:** 16 failed, 95 passed, 7 skipped (118 total).

---

## Bugs / Failures

### 1. Fix wrong `cwd` path in CLI integration tests (16 tests failing)

**File:** `tests/test_cli.py:14`

All 16 CLI integration tests fail with:

```
FileNotFoundError: [Errno 2] No such file or directory: '/home/user/Rb209'
```

The `_run_cli` helper hard-codes `cwd="/home/user/Rb209"` but the actual directory
is `/home/user/RB209` (all-caps). Fix by using a path relative to the test file
(e.g. `pathlib.Path(__file__).parents[1]`) so the tests are not tied to a specific
machine or casing.

---

## Unimplemented Features (Skipped Tests)

### 2. Timing and incorporation adjustment factors for organic materials

**Test:** `test_example_4_2_pig_slurry_adjusted_available_n`

Pig slurry applied in February and incorporated within 6 hours should yield a higher
available-N figure than the flat coefficient currently used.  RB209 Section 2 defines
timing- and incorporation-specific adjustment factors that are not yet implemented.

### 3. Table 4.6 — Grass ley SNS by age, N-intensity and management regime

**Tests:** `test_example_4_4_table_4_6_grass_ley_sns`, `test_example_4_5_table_4_6_grass_ley_sns`

`calculate_sns` has no lookup for grass ley previous crops using Table 4.6, which
maps combinations of (ley age × annual N-input × management regime) to an SNS index.
Examples:
- 3–5 year ley, high N (280 kg/ha/yr), 1 cut silage then grazed → SNS 2 (Example 4.4)
- 2-year grazed ley, high N (300 kg/ha/yr) → SNS 2 (Example 4.5)

### 4. Intermediate grass ley duration category (3-year ley)

**Test:** `test_example_4_4_three_year_ley_category`

The previous-crop catalogue only contains `grass-1-2yr` and `grass-long-term`.
A 3-year ley falls between these categories.  A `grass-3-5yr` (or equivalent)
previous-crop type is needed to match RB209 Table 4.6.

### 5. Subsequent-crop SNS reduction after grass ley

**Test:** `test_example_4_4_subsequent_crop_sns`

After a grass ley, RB209 specifies reduced SNS indices for the next two crops in
sequence (e.g. SNS 2 → 2 → 1).  The engine has no concept of crop sequence; only
the immediate previous crop is considered.

### 6. "Take the higher of two SNS values" logic

**Test:** `test_example_4_5_combined_sns_take_higher`

When both field-assessment (Table 4.5) and grass-ley (Table 4.6) methods apply,
RB209 requires using the higher of the two SNS indices.  This comparison/selection
step is not implemented.

### 7. Crop history / second-previous-crop support in `calculate_sns`

**Test:** `test_example_4_5_crop_history`

`calculate_sns` only accepts a single previous crop.  Example 4.5 requires knowing
the crop that preceded the immediate previous crop (a 2-year ley before spring
barley) to apply Table 4.6 correctly.  The function signature and SNS logic need
extending to accept an optional crop-history chain.
