# TODO

Open items identified from a full code review.

**Test summary:** 0 failed, 149 passed, 0 skipped (149 total).

---

## Open Issues

### ~~1. `recommend_nitrogen` raises instead of falling back to generic table when `soil_type` is provided~~ ✓ Fixed

**Fixed in:** `rb209/engine.py`, `tests/test_engine.py`, `CLI.md`

When `soil_type` is passed for a crop with no soil-specific N table, the engine now
falls back to the generic `NITROGEN_RECOMMENDATIONS` table instead of raising
`ValueError`. The CLI flag `--soil-type` works correctly for all crops.

---

### 2. `format_sns` displays empty "Previous crop" row for Table 4.6 results

**File:** `rb209/formatters.py:88-91`

When the SNS method is `"table-4.6"`, the formatter falls into the `else` branch
and always appends the `previous_crop` field.  But `previous_crop` is an empty
string for Table 4.6 results, producing a blank row:

```
|   Previous crop              |
```

The formatter should either omit the previous-crop row when it is empty, or display
ley-specific fields (ley age, management, year) for Table 4.6 results.

---

### 3. `Crop` and `CropCategory` enums are defined but never used

**File:** `rb209/models.py:15-52`

The `Crop` enum (22 members) and `CropCategory` enum are defined and `Crop` is
imported in `cli.py`, but neither is referenced anywhere in the codebase. The
engine, CLI, and data modules all use plain string values for crop identification.
These enums are dead code — either integrate them into the type signatures
(replacing bare `str` crop parameters) or remove them.

---

### 4. `TARGET_PH` and `MIN_PH_FOR_LIMING` constants are unused

**File:** `rb209/data/lime.py:17-23`

`TARGET_PH` (arable: 6.5, grassland: 6.0) and `MIN_PH_FOR_LIMING = 5.0` are
defined but never imported or referenced anywhere. `calculate_lime` takes
`target_ph` as an explicit argument and performs no land-use-based defaulting
or minimum-pH gating. Either wire these constants into the engine (e.g.
auto-suggest target pH by crop category, warn when pH is below the liming
threshold) or remove them as dead code.

---

### 5. `OrganicNutrients` dataclass lacks a unit field

**File:** `rb209/models.py:132-141`, `rb209/formatters.py:104`

`OrganicNutrients` stores `rate` but not the unit (tonnes/ha vs. m³/ha).
The formatter outputs the application rate as a bare number:

```
|   Application rate          25.0 |
```

There is no way for the user to tell whether the rate is in t/ha or m³/ha.
Adding a `unit` field (populated from `ORGANIC_MATERIAL_INFO[material]["unit"]`)
would allow the formatter to display e.g. `25.0 t/ha` or `30.0 m³/ha`.

---

### 6. `--straw-removed` / `--straw-incorporated` flags should be mutually exclusive

**Files:** `rb209/cli.py:201-204, 237-240`

Both the `recommend` and `potassium` parsers define `--straw-removed`
(`default=True, action="store_true"`) and `--straw-incorporated`
(`action="store_true"`) as independent flags. Passing both simultaneously is
silently accepted, with `--straw-incorporated` winning via the override in
`main()`. Using `parser.add_mutually_exclusive_group()` would prevent
confusing combinations and make the default behaviour explicit.

---

### 7. `pyproject.toml` uses private setuptools build backend

**File:** `pyproject.toml:13`

```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

This references a private/internal setuptools module path. The standard entry
point is `"setuptools.build_meta"`. The private path may break with future
setuptools releases.
