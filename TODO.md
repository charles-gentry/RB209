# TODO

Items identified from the test suite and a full code review.

**Test summary:** 0 failed, 114 passed, 4 skipped (118 total).

---

## Bugs / Failures

~~### 1. Fix wrong `cwd` path in CLI integration tests (16 tests failing)~~

**Fixed** in `tests/test_cli.py`. The `_run_cli` helper hard-coded
`cwd="/home/user/Rb209"` (wrong casing), causing all 16 CLI integration tests to
fail with `FileNotFoundError`. Replaced with
`_REPO_ROOT = pathlib.Path(__file__).parents[1]` so the path is derived from the
test file's location and is machine/casing agnostic.

---

## Unimplemented Features (Skipped Tests)

~~### 2. Timing and incorporation adjustment factors for organic materials~~

**Fixed.**  `calculate_organic()` now accepts optional `timing`, `incorporated`,
and `soil_type` parameters.  When `timing` is supplied, available-N is derived from
the RB209 Table 2.12 percentage factors instead of the flat default coefficient.
A lookup table (`ORGANIC_N_TIMING_FACTORS`) keyed on material, timing season,
soil category, and incorporation flag is stored in `rb209/data/organic.py`.
Test `test_example_4_2_pig_slurry_adjusted_available_n` has been implemented and
now passes: spring + incorporated-6h gives 64.8 kg N/ha (60 % of total N) vs.
37.8 kg N/ha for winter surface-applied (35 % of total N).

~~### 3. Table 4.6 — Grass ley SNS by age, N-intensity and management regime~~

**Fixed.**  A new `calculate_grass_ley_sns()` engine function looks up SNS indices
from RB209 Table 4.6 (SNS Indices following ploughing out of grass leys).  It accepts
`ley_age` (`"1-2yr"` / `"3-5yr"`), `n_intensity` (`"low"` / `"high"`), `management`
(`"cut"` / `"grazed"` / `"1-cut-then-grazed"`), `soil_type`, `rainfall`, and `year`
(1–3 years after ploughing).  The full Table 4.6 dataset — four soil categories × three
management rows × three years — is stored in `GRASS_LEY_SNS_LOOKUP` in
`rb209/data/sns.py`.  The function returns an `SNSResult` with `method="table-4.6"`.

Tests now passing:
- `test_example_4_4_table_4_6_grass_ley_sns`: 3–5yr ley, high N, 1-cut-then-grazed,
  medium soil, moderate rainfall → Year 1 = SNS 2 (Example 4.4)
- `test_example_4_5_table_4_6_grass_ley_sns`: 1–2yr ley, high N, grazed, heavy soil,
  high rainfall → Year 2 = SNS 2 (Example 4.5 — winter wheat is 2nd crop after the ley)

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

---

## Code Review Findings

Issues identified from a full code review (not covered by the test-suite items above).

### 8. `recommend_nitrogen` raises instead of falling back to generic table when `soil_type` is provided

**Files:** `rb209/engine.py:285-299`

When `soil_type` is passed to `recommend_nitrogen()` for a crop that only has generic
N data (anything other than `winter-wheat-feed`), the function raises `ValueError`
instead of falling back to the generic recommendation table.  This also breaks the
`recommend` CLI subcommand:

```
$ rb209 recommend --crop spring-barley --sns-index 1 --p-index 1 --k-index 1 --soil-type medium
Error: No soil-specific nitrogen data for crop 'spring-barley' at SNS 1 on medium soil
```

The `--soil-type` flag is documented as optional, and the user may reasonably pass it
for other purposes (e.g. to note their soil type for reporting).  When soil-specific N
data is absent, the engine should fall back to `NITROGEN_RECOMMENDATIONS` rather than
erroring.

~~### 9. No CLI subcommand for `calculate_grass_ley_sns` (Table 4.6)~~

**Fixed.**  A new `sns-ley` CLI subcommand has been added to `rb209/cli.py`.  It
accepts `--ley-age` (`1-2yr` / `3-5yr`), `--n-intensity` (`low` / `high`),
`--management` (`cut` / `grazed` / `1-cut-then-grazed`), `--soil-type`
(`light` / `medium` / `heavy`), `--rainfall` (`low` / `medium` / `high`), and
`--year` (`1` / `2` / `3`, default 1).  Organic soils are excluded at the
argument-parsing level since Table 4.6 does not cover them.  Output supports
both `--format table` (default) and `--format json`.

### 10. `format_sns` displays empty "Previous crop" row for Table 4.6 results

**File:** `rb209/formatters.py:81-94`

When the SNS method is `"table-4.6"`, the formatter falls into the `else` branch
and displays `previous_crop`, `soil_type`, and `rainfall`.  But `previous_crop`
is an empty string for Table 4.6 results, producing a blank row:

```
|   Previous crop              |
```

The formatter should either omit the previous-crop row when it is empty, or display
ley-specific fields (ley age, management, year) for Table 4.6 results.

~~### 11. Timing/incorporation factors only implemented for pig slurry~~

**Fixed.**  `ORGANIC_N_TIMING_FACTORS` now contains entries for all major
livestock manures and biosolids covered by RB209 Section 2:

| Material(s) | RB209 Table | DM basis |
|---|---|---|
| `cattle-fym`, `pig-fym`, `sheep-fym`, `horse-fym` | Table 2.3 | all FYM (fresh values) |
| `poultry-litter` | Table 2.6 | 40 % DM |
| `layer-manure` | Table 2.6 | 20 % DM |
| `cattle-slurry` | Table 2.9 | 6 % DM |
| `pig-slurry` | Table 2.12 | 4 % DM (unchanged) |
| `biosolids-cake` | Table 2.15 | digested cake, 25 % DM |

Composts (`green-compost`, `green-food-compost`) and `paper-crumble` have
no timing table in RB209 and remain flat-coefficient only.  Passing `timing=`
for these materials still raises `ValueError`.  The docstring in `engine.py`
and the notes in CLI.md and README.md have been updated accordingly.

### 12. `Crop` and `CropCategory` enums are defined but never used

**File:** `rb209/models.py:15-52`

The `Crop` enum (22 members) and `CropCategory` enum are defined and `Crop` is
imported in `cli.py`, but neither is referenced anywhere in the codebase.  The
engine, CLI, and data modules all use plain string values for crop identification.
These enums are dead code — either integrate them into the type signatures
(replacing bare `str` crop parameters) or remove them.

### 13. `TARGET_PH` and `MIN_PH_FOR_LIMING` constants are unused

**File:** `rb209/data/lime.py:17-23`

`TARGET_PH` (arable: 6.5, grassland: 6.0) and `MIN_PH_FOR_LIMING = 5.0` are
defined but never imported or referenced anywhere.  `calculate_lime` takes
`target_ph` as an explicit argument and performs no land-use-based defaulting
or minimum-pH gating.  Either wire these constants into the engine (e.g.
auto-suggest target pH by crop category, warn when pH is below the liming
threshold) or remove them as dead code.

### 14. `OrganicNutrients` dataclass lacks a unit field

**File:** `rb209/models.py:130-139`, `rb209/formatters.py:104`

`OrganicNutrients` stores `rate` but not the unit (tonnes/ha vs. m³/ha).
The formatter outputs the application rate as a bare number:

```
|   Application rate          25.0 |
```

There is no way for the user to tell whether the rate is in t/ha or m³/ha.
Adding a `unit` field (populated from `ORGANIC_MATERIAL_INFO[material]["unit"]`)
would allow the formatter to display e.g. `25.0 t/ha` or `30.0 m³/ha`.

### 15. `--straw-removed` / `--straw-incorporated` flags should be mutually exclusive

**Files:** `rb209/cli.py:169-172, 206-209, 322-324`

Both the `recommend` and `potassium` parsers define `--straw-removed`
(`default=True, action="store_true"`) and `--straw-incorporated`
(`action="store_true"`) as independent flags.  Passing both simultaneously is
silently accepted, with `--straw-incorporated` winning via the override in
`main()`.  Using `parser.add_mutually_exclusive_group()` would prevent
confusing combinations and make the default behaviour explicit.

### 16. `pyproject.toml` uses private setuptools build backend

**File:** `pyproject.toml:13`

```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

This references a private/internal setuptools module path.  The standard entry
point is `"setuptools.build_meta"`.  The private path may break with future
setuptools releases.

### 17. `_validate_index` accepts `bool` values due to Python `bool` subclassing `int`

**File:** `rb209/engine.py:42`

`_validate_index` checks `not isinstance(value, int)`, but Python `bool` is a
subclass of `int` (`isinstance(True, int)` is `True`).  This means
`recommend_nitrogen("winter-wheat-feed", True)` silently succeeds and returns
the SNS index 1 recommendation (180 kg/ha) rather than rejecting the input.
Adding `isinstance(value, bool)` as an early rejection would prevent this.
