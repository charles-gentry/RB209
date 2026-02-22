# TODO

Open items identified from a full code review.

**Test summary:** 0 failed, 309 passed, 0 skipped (309 total).

---

## Open Issues

### ~~1. `recommend_nitrogen` raises instead of falling back to generic table when `soil_type` is provided~~ ✓ Fixed

**Fixed in:** `rb209/engine.py`, `tests/test_engine.py`, `CLI.md`

When `soil_type` is passed for a crop with no soil-specific N table, the engine now
falls back to the generic `NITROGEN_RECOMMENDATIONS` table instead of raising
`ValueError`. The CLI flag `--soil-type` works correctly for all crops.

---

### ~~2. `format_sns` displays empty "Previous crop" row for Table 4.6 results~~ ✓ Fixed

**Fixed in:** `rb209/formatters.py`, `CLI.md`

The formatter now only appends the `previous_crop` row when it is non-empty.
Table 4.6 results (method `"table-4.6"`) no longer show a blank "Previous crop"
row; the ley details are already captured in the notes section.

---

### 3. `Crop` and `CropCategory` enums are defined but never used

**File:** `rb209/models.py:15-52`

The `Crop` enum (22 members) and `CropCategory` enum are defined and `Crop` is
imported in `cli.py`, but neither is referenced anywhere in the codebase. The
engine, CLI, and data modules all use plain string values for crop identification.
These enums are dead code — either integrate them into the type signatures
(replacing bare `str` crop parameters) or remove them.

---

### ~~4. `TARGET_PH` and `MIN_PH_FOR_LIMING` constants are unused~~ ✓ Fixed

**Fixed in:** `rb209/engine.py`, `rb209/cli.py`, `tests/test_engine.py`, `tests/test_cli.py`, `CLI.md`

`TARGET_PH` and `MIN_PH_FOR_LIMING` are now imported and used in
`calculate_lime`. The `target_ph` argument is now optional (defaults to
`None`); when `land_use` is supplied instead, the RB209 default target pH is
applied automatically (arable: 6.5, grassland: 6.0). A warning note is
appended to the result whenever `current_ph < MIN_PH_FOR_LIMING` (5.0). The
CLI `lime` subcommand gains a new optional `--land-use` flag and `--target-ph`
is no longer required.

---

### ~~5. `OrganicNutrients` dataclass lacks a unit field~~ ✓ Fixed

**Fixed in:** `rb209/models.py`, `rb209/engine.py`, `rb209/formatters.py`, `CLI.md`

Added a `unit` field to `OrganicNutrients` (populated from
`ORGANIC_MATERIAL_INFO[material]["unit"]`). The formatter now displays the
application rate with its unit, e.g. `25.0 t/ha` or `30.0 m³/ha`. The JSON
output also includes the `unit` field.

---

### ~~6. `--straw-removed` / `--straw-incorporated` flags should be mutually exclusive~~ ✓ Fixed

**Fixed in:** `rb209/cli.py`, `CLI.md`

Both the `recommend` and `potassium` parsers now use
`parser.add_mutually_exclusive_group()` with `--straw-incorporated` mapped to
`dest="straw_removed"` via `action="store_false"`. Passing both flags
simultaneously now produces an argparse error (exit code 2). The manual override
in `main()` has been removed.

---

### 7. `pyproject.toml` uses private setuptools build backend

**File:** `pyproject.toml:13`

```toml
build-backend = "setuptools.backends._legacy:_Backend"
```

This references a private/internal setuptools module path. The standard entry
point is `"setuptools.build_meta"`. The private path may break with future
setuptools releases.
