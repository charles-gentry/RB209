"""Recommendation engine — core logic for RB209 fertiliser calculations."""

from rb209.models import (
    FruitSoilCategory,
    LimeRecommendation,
    NResidueCategory,
    NitrogenSplit,
    NitrogenTimingResult,
    NutrientRecommendation,
    OrchardManagement,
    OrganicMaterial,
    OrganicNutrients,
    PREVIOUS_CROP_N_CATEGORY,
    PreviousCrop,
    Rainfall,
    SNSResult,
    SoilType,
    VegPreviousCrop,
    VegSoilType,
)
from rb209.data.crops import CROP_INFO
from rb209.data.lime import LIME_FACTORS, MAX_SINGLE_APPLICATION, MIN_PH_FOR_LIMING, TARGET_PH
from rb209.data.magnesium import MAGNESIUM_RECOMMENDATIONS, VEG_MAGNESIUM_RECOMMENDATIONS
from rb209.data.nitrogen import (
    NITROGEN_RECOMMENDATIONS,
    NITROGEN_SOIL_SPECIFIC,
    NITROGEN_VEG_RECOMMENDATIONS,
    NVZ_NMAX,
)
from rb209.data.organic import (
    ORGANIC_MATERIAL_INFO,
    ORGANIC_N_TIMING_FACTORS,
    TIMING_SOIL_CATEGORY,
)
from rb209.data.phosphorus import PHOSPHORUS_RECOMMENDATIONS, PHOSPHORUS_VEG_RECOMMENDATIONS
from rb209.data.potassium import (
    POTASSIUM_RECOMMENDATIONS,
    POTASSIUM_STRAW_INCORPORATED,
    POTASSIUM_STRAW_REMOVED,
    POTASSIUM_VEG_RECOMMENDATIONS,
    POTASSIUM_VEG_K2_UPPER,
)
from rb209.data.sns import (
    GRASS_LEY_SNS_LOOKUP,
    SNS_LOOKUP,
    SNS_VALUE_TO_INDEX,
    VEG_SNS_LOOKUP,
    VEG_SMN_SNS_THRESHOLDS,
    VEG_SNS_ORGANIC_ADVISORY,
)
from rb209.data.sodium import (
    SODIUM_FLAT_RATES,
    SODIUM_GRASSLAND_CROPS,
    SODIUM_GRASSLAND_RATE,
    SODIUM_NOTES,
    SODIUM_RECOMMENDATIONS,
)
from rb209.data.fruit import (
    FRUIT_PREPLANT_PKM,
    FRUIT_TOP_NITROGEN,
    FRUIT_TOP_PKM,
    FRUIT_SOFT_NITROGEN,
    FRUIT_SOFT_PKM,
    FRUIT_STRAWBERRY_NITROGEN,
    FRUIT_STRAWBERRY_PKM,
    FRUIT_HOPS_NITROGEN,
    FRUIT_HOPS_PKM,
)
from rb209.data.sulfur import SULFUR_RECOMMENDATIONS
from rb209.data.timing import NITROGEN_TIMING_RULES
from rb209.data.ber import BER_ADJUSTMENTS, CROP_BER_GROUP
from rb209.data.yield_adjustments import YIELD_ADJUSTMENTS


def _validate_crop(crop: str) -> None:
    if crop not in CROP_INFO:
        valid = ", ".join(sorted(CROP_INFO))
        raise ValueError(f"Unknown crop '{crop}'. Valid crops: {valid}")


def _validate_index(name: str, value: int, min_val: int = 0, max_val: int = 6) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < min_val or value > max_val:
        raise ValueError(
            f"{name} must be an integer between {min_val} and {max_val}, got {value!r}"
        )


def _clamp_index(value: int, max_key: int) -> int:
    """Clamp an index to the maximum key in the lookup table."""
    return min(value, max_key)


# ── SNS ─────────────────────────────────────────────────────────────

def calculate_sns(
    previous_crop: str,
    soil_type: str,
    rainfall: str,
    *,
    grass_history: dict | None = None,
) -> SNSResult:
    """Calculate Soil Nitrogen Supply index using the field assessment method.

    When ``grass_history`` is provided, the function also calculates an SNS
    index from Table 4.6 (grass ley history) and returns the higher of the two
    indices, as required by RB209.  This covers the common scenario where the
    current crop's previous crop was an arable crop that itself followed a
    grass ley (e.g. winter wheat after spring barley after a 2-year ley).

    Args:
        previous_crop: Previous crop value (e.g. "cereals", "oilseed-rape").
        soil_type: Soil type ("light", "medium", "heavy", "organic").
        rainfall: Excess winter rainfall category ("low", "medium", "high").
        grass_history: Optional dict with grass ley parameters for Table 4.6
            combined assessment.  Keys: ``ley_age`` ("1-2yr" / "3-5yr"),
            ``n_intensity`` ("low" / "high"), ``management`` ("cut" /
            "grazed" / "1-cut-then-grazed"), and optionally ``year``
            (1/2/3, default 2).

    Returns:
        SNSResult with the calculated SNS index.  When grass_history is used,
        method is "combined" and notes describe both assessments.
    """
    # Validate enums
    try:
        prev = PreviousCrop(previous_crop)
    except ValueError:
        valid = ", ".join(p.value for p in PreviousCrop)
        raise ValueError(
            f"Unknown previous crop '{previous_crop}'. Valid options: {valid}"
        )
    try:
        SoilType(soil_type)
    except ValueError:
        valid = ", ".join(s.value for s in SoilType)
        raise ValueError(f"Unknown soil type '{soil_type}'. Valid options: {valid}")
    try:
        Rainfall(rainfall)
    except ValueError:
        valid = ", ".join(r.value for r in Rainfall)
        raise ValueError(
            f"Unknown rainfall category '{rainfall}'. Valid options: {valid}"
        )

    n_cat = PREVIOUS_CROP_N_CATEGORY[prev]
    key = (n_cat.value, soil_type, rainfall)
    sns_index = SNS_LOOKUP[key]

    field_notes = [
        f"Previous crop '{previous_crop}' has {n_cat.value} N residue.",
    ]

    if grass_history is not None:
        ley_result = calculate_grass_ley_sns(
            ley_age=grass_history["ley_age"],
            n_intensity=grass_history["n_intensity"],
            management=grass_history["management"],
            soil_type=soil_type,
            rainfall=rainfall,
            year=grass_history.get("year", 2),
        )
        best_index = max(sns_index, ley_result.sns_index)
        notes = field_notes + ley_result.notes
        notes.append(
            f"Combined: field-assessment SNS {sns_index}, "
            f"Table 4.6 SNS {ley_result.sns_index} — "
            f"using higher value (SNS {best_index})."
        )
        return SNSResult(
            sns_index=best_index,
            previous_crop=previous_crop,
            soil_type=soil_type,
            rainfall=rainfall,
            method="combined",
            notes=notes,
        )

    return SNSResult(
        sns_index=sns_index,
        previous_crop=previous_crop,
        soil_type=soil_type,
        rainfall=rainfall,
        method="field-assessment",
        notes=field_notes,
    )


def sns_value_to_index(sns_value: float) -> int:
    """Convert an SNS value in kg N/ha to an SNS index using Table 4.10.

    Args:
        sns_value: Soil Nitrogen Supply in kg N/ha (must be >= 0).

    Returns:
        SNS index (0-6).
    """
    if sns_value < 0:
        raise ValueError(f"SNS value must be non-negative, got {sns_value}")
    for upper_bound, index in SNS_VALUE_TO_INDEX:
        if sns_value <= upper_bound:
            return index
    return 6


def calculate_smn_sns(smn: float, crop_n: float) -> SNSResult:
    """Calculate Soil Nitrogen Supply index from SMN measurement.

    Uses measured Soil Mineral Nitrogen (0-90 cm depth) and estimated
    crop nitrogen at the time of sampling to determine total SNS,
    then converts to an SNS index via Table 4.10.

    Args:
        smn: Soil Mineral Nitrogen measured in the lab (kg N/ha, 0-90 cm).
        crop_n: Estimated nitrogen in the crop at sampling time (kg N/ha).

    Returns:
        SNSResult with method="smn" and the calculated SNS index.
    """
    if smn < 0:
        raise ValueError(f"SMN must be non-negative, got {smn}")
    if crop_n < 0:
        raise ValueError(f"Crop N must be non-negative, got {crop_n}")

    total_sns = smn + crop_n
    sns_index = sns_value_to_index(total_sns)

    notes = [
        f"SMN (0-90 cm) = {smn:.0f} kg N/ha.",
        f"Crop N = {crop_n:.0f} kg N/ha.",
        f"Total SNS = {total_sns:.0f} kg N/ha (Table 4.10 -> Index {sns_index}).",
    ]

    return SNSResult(
        sns_index=sns_index,
        method="smn",
        smn=smn,
        crop_n=crop_n,
        sns_value=total_sns,
        notes=notes,
    )


def calculate_grass_ley_sns(
    ley_age: str,
    n_intensity: str,
    management: str,
    soil_type: str,
    rainfall: str,
    year: int = 1,
) -> SNSResult:
    """Calculate Soil Nitrogen Supply index from Table 4.6 (grass ley history).

    Use this when the field has been in grass within the past three years.
    The result should be compared with the Table 4.3/4.4/4.5 field-assessment
    result and the higher of the two SNS indices used.

    Args:
        ley_age: Duration of the grass ley: "1-2yr" or "3-5yr".
        n_intensity: N management of the ley: "low" (average annual inputs
            <250 kg N/ha) or "high" (>250 kg N/ha, clover-rich, or lucerne).
        management: Ley management regime: "cut" (2+ cuts annually, little/no
            manure), "grazed", or "1-cut-then-grazed".
        soil_type: Soil type: "light", "medium", or "heavy".
            Note: organic soils are not covered by Table 4.6.
        rainfall: Rainfall category: "low", "medium", or "high".
        year: Year after ploughing out the ley (1, 2, or 3). Defaults to 1.

    Returns:
        SNSResult with sns_index from Table 4.6 and method="table-4.6".
    """
    valid_ages = ("1-2yr", "3-5yr")
    if ley_age not in valid_ages:
        raise ValueError(f"ley_age must be one of {valid_ages}, got '{ley_age}'")

    valid_intensities = ("low", "high")
    if n_intensity not in valid_intensities:
        raise ValueError(
            f"n_intensity must be one of {valid_intensities}, got '{n_intensity}'"
        )

    valid_managements = ("cut", "grazed", "1-cut-then-grazed")
    if management not in valid_managements:
        raise ValueError(
            f"management must be one of {valid_managements}, got '{management}'"
        )

    try:
        SoilType(soil_type)
    except ValueError:
        valid = ", ".join(s.value for s in SoilType)
        raise ValueError(f"Unknown soil type '{soil_type}'. Valid options: {valid}")

    if soil_type == "organic":
        raise ValueError(
            "Table 4.6 does not cover organic soils. "
            "Use the SMN measurement method for these soils."
        )

    try:
        Rainfall(rainfall)
    except ValueError:
        valid = ", ".join(r.value for r in Rainfall)
        raise ValueError(
            f"Unknown rainfall category '{rainfall}'. Valid options: {valid}"
        )

    if year not in (1, 2, 3):
        raise ValueError(f"year must be 1, 2, or 3, got {year}")

    # Map soil_type + rainfall to Table 4.6 soil category
    if soil_type == "light":
        soil_cat = "light"
    elif soil_type == "medium":
        soil_cat = "medium"
    else:  # heavy
        soil_cat = "heavy-low" if rainfall == "low" else "heavy-medium-high"

    # Determine Table 4.6 ley management row
    if ley_age == "3-5yr" and n_intensity == "high" and management == "grazed":
        ley_row = "high-n-grazed-35yr"
    elif (
        (n_intensity == "high" and management == "grazed")
        or (ley_age == "3-5yr" and n_intensity == "low" and management == "grazed")
        or (ley_age == "3-5yr" and n_intensity == "high" and management == "1-cut-then-grazed")
    ):
        ley_row = "high-n-grazed-or-mixed"
    else:
        ley_row = "low-n-or-cut"

    year1, year2, year3 = GRASS_LEY_SNS_LOOKUP[(soil_cat, ley_row)]
    sns_index = (year1, year2, year3)[year - 1]

    notes = [
        f"Table 4.6: {ley_age} ley, {n_intensity} N, {management} management, "
        f"{soil_type} soil, {rainfall} rainfall — year {year} after ploughing.",
    ]

    return SNSResult(
        sns_index=sns_index,
        soil_type=soil_type,
        rainfall=rainfall,
        method="table-4.6",
        notes=notes,
    )


def calculate_veg_sns(
    previous_crop: str,
    soil_type: str,
    rainfall: str,
) -> SNSResult:
    """Calculate Soil Nitrogen Supply index for vegetable crops (Section 6).

    Uses Tables 6.2–6.4 which have 11 previous-crop categories and four
    mineral soil columns.  Organic and peat soils return advisory indices
    with a note to consult a FACTS Qualified Adviser.

    Args:
        previous_crop: VegPreviousCrop value (e.g. "cereals", "veg-high-n").
        soil_type: VegSoilType value ("light-sand", "medium", "deep-clay",
            "deep-silt", "organic", or "peat").
        rainfall: Rainfall category — "low" (<600 mm / <150 mm EWR),
            "moderate" (600–700 mm), or "high" (>700 mm / >250 mm EWR).

    Returns:
        SNSResult with method="veg-field-assessment" and the calculated index.
    """
    try:
        VegPreviousCrop(previous_crop)
    except ValueError:
        valid = ", ".join(p.value for p in VegPreviousCrop)
        raise ValueError(
            f"Unknown vegetable previous crop '{previous_crop}'. Valid options: {valid}"
        )
    try:
        VegSoilType(soil_type)
    except ValueError:
        valid = ", ".join(s.value for s in VegSoilType)
        raise ValueError(
            f"Unknown vegetable soil type '{soil_type}'. Valid options: {valid}"
        )
    valid_rainfalls = ("low", "moderate", "high")
    if rainfall not in valid_rainfalls:
        raise ValueError(
            f"Unknown rainfall '{rainfall}'. Valid options: {', '.join(valid_rainfalls)}"
        )

    notes: list[str] = []

    # Advisory-only soil types — Tables 6.2–6.4 give only a range for these
    # soils because their high N mineralisation potential cannot be
    # characterised by previous crop and rainfall alone.
    if soil_type in VEG_SNS_ORGANIC_ADVISORY:
        min_idx, rep_idx, max_idx = VEG_SNS_ORGANIC_ADVISORY[soil_type]
        soil_label = "organic" if soil_type == "organic" else "peat"
        notes.append(
            f"RB209 Tables 6.2–6.4 do not provide a crop- or rainfall-specific "
            f"SNS index for {soil_label} soils. All crops fall in SNS Index "
            f"{min_idx}–{max_idx} depending on site conditions."
        )
        notes.append(
            f"SNS Index {rep_idx} is returned as a representative mid-range "
            f"estimate. Use the 'veg-smn' command with a soil mineral nitrogen "
            f"(SMN) measurement for a precise, site-specific index."
        )
        notes.append(
            "Consult a FACTS Qualified Adviser before applying nitrogen on "
            f"{soil_label} soils."
        )
        return SNSResult(
            sns_index=rep_idx,
            previous_crop=previous_crop,
            soil_type=soil_type,
            rainfall=rainfall,
            method="veg-field-assessment-advisory",
            notes=notes,
        )

    key = (previous_crop, soil_type, rainfall)
    if key not in VEG_SNS_LOOKUP:
        raise ValueError(
            f"No vegetable SNS data for previous_crop='{previous_crop}', "
            f"soil_type='{soil_type}', rainfall='{rainfall}'."
        )
    sns_index = VEG_SNS_LOOKUP[key]

    notes.append(
        f"Previous crop '{previous_crop}' on {soil_type} soil with {rainfall} rainfall "
        f"gives SNS Index {sns_index} (Tables 6.2–6.4)."
    )

    return SNSResult(
        sns_index=sns_index,
        previous_crop=previous_crop,
        soil_type=soil_type,
        rainfall=rainfall,
        method="veg-field-assessment",
        notes=notes,
    )


def smn_to_sns_index_veg(smn: float, depth_cm: int) -> int:
    """Convert SMN (kg N/ha) to SNS index for vegetable crops using Table 6.6.

    Table 6.6 thresholds differ from the arable Table 4.10 used by
    ``sns_value_to_index()``.

    Args:
        smn: Soil mineral nitrogen measured to depth_cm (kg N/ha, must be >= 0).
        depth_cm: Sampling depth — 30, 60, or 90 cm.

    Returns:
        SNS index (0–6).

    Raises:
        ValueError: If depth_cm is not 30, 60, or 90, or if smn is negative.
    """
    if smn < 0:
        raise ValueError(f"SMN must be non-negative, got {smn}")
    if depth_cm not in VEG_SMN_SNS_THRESHOLDS:
        raise ValueError(
            f"depth_cm must be 30, 60, or 90, got {depth_cm}"
        )
    for upper_bound, index in VEG_SMN_SNS_THRESHOLDS[depth_cm]:
        if smn <= upper_bound:
            return index
    return 6


def combine_sns(*results: SNSResult) -> SNSResult:
    """Return the SNS result with the highest index.

    When both a field-assessment (Table 4.3/4.4/4.5) and a grass-ley
    (Table 4.6) SNS index are available, RB209 requires using the higher
    of the two values.  This function accepts two or more SNSResult objects
    and returns the one with the largest ``sns_index``.  If there is a tie,
    the first result with that index is returned.

    Args:
        *results: Two or more SNSResult objects to compare.

    Returns:
        The SNSResult with the highest sns_index.
    """
    if len(results) < 2:
        raise ValueError("combine_sns requires at least two SNSResult objects")
    return max(results, key=lambda r: r.sns_index)


# ── BER interpolation ──────────────────────────────────────────────

def _interpolate_ber(group: str, ber: float) -> float:
    """Linearly interpolate a BER adjustment for the given crop group.

    Extrapolates (clamped) at the table boundaries.
    """
    # Collect all BER values for this group, sorted.
    points = sorted(
        (b, adj) for (g, b), adj in BER_ADJUSTMENTS.items() if g == group
    )
    if not points:
        return 0.0

    # Clamp to table boundaries.
    if ber <= points[0][0]:
        return points[0][1]
    if ber >= points[-1][0]:
        return points[-1][1]

    # Find the two surrounding points and interpolate.
    for i in range(len(points) - 1):
        b_lo, adj_lo = points[i]
        b_hi, adj_hi = points[i + 1]
        if b_lo <= ber <= b_hi:
            frac = (ber - b_lo) / (b_hi - b_lo)
            return adj_lo + frac * (adj_hi - adj_lo)

    return 0.0  # pragma: no cover


# ── Nitrogen ────────────────────────────────────────────────────────

def recommend_nitrogen(
    crop: str,
    sns_index: int,
    soil_type: str | None = None,
    expected_yield: float | None = None,
    ber: float | None = None,
) -> float:
    """Return nitrogen recommendation in kg N/ha.

    Args:
        crop: Crop value string.
        sns_index: Soil Nitrogen Supply index (0-6).
        soil_type: Optional soil type for soil-specific recommendations.
            When provided, uses Table 4.17 (and similar) soil-specific data.
            When omitted, uses the generic recommendation table.
        expected_yield: Optional expected yield in t/ha. When provided and the
            crop has yield adjustment data, adjusts the recommendation based on
            the difference from the baseline yield.
        ber: Optional break-even ratio (fertiliser N cost £/kg ÷ grain value
            £/kg). Default is 5.0 (no adjustment). Only applies to wheat and
            barley crops.
    """
    _validate_crop(crop)
    _validate_index("SNS index", sns_index, 0, 6)

    if soil_type is not None:
        try:
            SoilType(soil_type)
        except ValueError:
            valid = ", ".join(s.value for s in SoilType)
            raise ValueError(
                f"Unknown soil type '{soil_type}'. Valid options: {valid}"
            )
        soil_key = (crop, sns_index, soil_type)
        if soil_key in NITROGEN_SOIL_SPECIFIC:
            base = NITROGEN_SOIL_SPECIFIC[soil_key]
        else:
            # No soil-specific table for this crop; fall back to generic or veg table.
            key = (crop, sns_index)
            if key in NITROGEN_RECOMMENDATIONS:
                base = NITROGEN_RECOMMENDATIONS[key]
            elif key in NITROGEN_VEG_RECOMMENDATIONS:
                base = NITROGEN_VEG_RECOMMENDATIONS[key]
            else:
                raise ValueError(f"No nitrogen data for crop '{crop}' at SNS {sns_index}")
    else:
        key = (crop, sns_index)
        if key in NITROGEN_RECOMMENDATIONS:
            base = NITROGEN_RECOMMENDATIONS[key]
        elif key in NITROGEN_VEG_RECOMMENDATIONS:
            base = NITROGEN_VEG_RECOMMENDATIONS[key]
        else:
            raise ValueError(f"No nitrogen data for crop '{crop}' at SNS {sns_index}")

    if expected_yield is not None:
        if crop not in YIELD_ADJUSTMENTS:
            valid = ", ".join(sorted(YIELD_ADJUSTMENTS))
            raise ValueError(
                f"No yield adjustment data for crop '{crop}'. "
                f"Supported crops: {valid}"
            )
        adj = YIELD_ADJUSTMENTS[crop]
        capped_yield = min(expected_yield, adj["max_yield"]) if "max_yield" in adj else expected_yield
        delta = (capped_yield - adj["baseline_yield"]) * adj["n_adjust_per_t"]
        base = max(0.0, base + delta)

    if ber is not None:
        group = CROP_BER_GROUP.get(crop)
        if group is not None:
            ber_adj = _interpolate_ber(group, ber)
            base = max(0.0, base + ber_adj)

    return base


# ── Phosphorus ──────────────────────────────────────────────────────

def recommend_phosphorus(
    crop: str,
    p_index: int,
    expected_yield: float | None = None,
) -> float:
    """Return phosphorus recommendation in kg P2O5/ha.

    Args:
        crop: Crop value string.
        p_index: Soil P index (0-9, clamped to max available key).
        expected_yield: Optional expected yield in t/ha. When provided and the
            crop has yield adjustment data, adjusts the recommendation based on
            the difference from the baseline yield.
    """
    _validate_crop(crop)
    _validate_index("P index", p_index, 0, 9)

    clamped = _clamp_index(p_index, 4)
    key = (crop, clamped)
    if key in PHOSPHORUS_RECOMMENDATIONS:
        base = PHOSPHORUS_RECOMMENDATIONS[key]
    elif key in PHOSPHORUS_VEG_RECOMMENDATIONS:
        base = PHOSPHORUS_VEG_RECOMMENDATIONS[key]
    else:
        raise ValueError(f"No phosphorus data for crop '{crop}'")

    if expected_yield is not None:
        if crop not in YIELD_ADJUSTMENTS:
            valid = ", ".join(sorted(YIELD_ADJUSTMENTS))
            raise ValueError(
                f"No yield adjustment data for crop '{crop}'. "
                f"Supported crops: {valid}"
            )
        adj = YIELD_ADJUSTMENTS[crop]
        capped_yield = min(expected_yield, adj["max_yield"]) if "max_yield" in adj else expected_yield
        delta = (capped_yield - adj["baseline_yield"]) * adj["p_adjust_per_t"]
        base = max(0.0, base + delta)

    return base


# ── Potassium ───────────────────────────────────────────────────────

def recommend_potassium(
    crop: str,
    k_index: int,
    straw_removed: bool = True,
    expected_yield: float | None = None,
    k_upper_half: bool = False,
) -> float:
    """Return potassium recommendation in kg K2O/ha.

    Args:
        crop: Crop value string.
        k_index: Soil K index (0-9, clamped to max available key).
        straw_removed: For cereals only — True if straw is removed.
        expected_yield: Optional expected yield in t/ha. When provided and the
            crop has yield adjustment data, adjusts the recommendation based on
            the difference from the baseline yield.
        k_upper_half: For vegetable crops at K Index 2 — True if soil K is in
            the upper half (181–240 mg/l, i.e. 2+), False for 2- (121–180 mg/l).
    """
    _validate_crop(crop)
    _validate_index("K index", k_index, 0, 9)

    clamped = _clamp_index(k_index, 4)
    key = (crop, clamped)

    # K Index 2 upper-half (2+) override for vegetable crops
    if clamped == 2 and k_upper_half and crop in POTASSIUM_VEG_K2_UPPER:
        base = POTASSIUM_VEG_K2_UPPER[crop]
    # Check if this is a cereal with straw option
    elif CROP_INFO[crop].get("has_straw_option"):
        table = POTASSIUM_STRAW_REMOVED if straw_removed else POTASSIUM_STRAW_INCORPORATED
        if key in table:
            base = table[key]
        elif key in POTASSIUM_RECOMMENDATIONS:
            base = POTASSIUM_RECOMMENDATIONS[key]
        else:
            raise ValueError(f"No potassium data for crop '{crop}'")
    elif key in POTASSIUM_RECOMMENDATIONS:
        base = POTASSIUM_RECOMMENDATIONS[key]
    elif key in POTASSIUM_VEG_RECOMMENDATIONS:
        base = POTASSIUM_VEG_RECOMMENDATIONS[key]
    else:
        raise ValueError(f"No potassium data for crop '{crop}'")

    if expected_yield is not None:
        if crop not in YIELD_ADJUSTMENTS:
            valid = ", ".join(sorted(YIELD_ADJUSTMENTS))
            raise ValueError(
                f"No yield adjustment data for crop '{crop}'. "
                f"Supported crops: {valid}"
            )
        adj = YIELD_ADJUSTMENTS[crop]
        capped_yield = min(expected_yield, adj["max_yield"]) if "max_yield" in adj else expected_yield
        delta = (capped_yield - adj["baseline_yield"]) * adj["k_adjust_per_t"]
        base = max(0.0, base + delta)

    return base


# ── Magnesium ───────────────────────────────────────────────────────

def recommend_magnesium(mg_index: int, crop: str | None = None) -> float:
    """Return magnesium recommendation in kg MgO/ha.

    Args:
        mg_index: Soil Mg index (0-9, clamped to max available key).
        crop: Optional crop value string. When provided and the crop is a
            vegetable, uses the higher vegetable Mg rates (150/100 at index 0/1)
            instead of the arable rates (90/60).
    """
    _validate_index("Mg index", mg_index, 0, 9)
    clamped = _clamp_index(mg_index, 4)
    if crop and CROP_INFO.get(crop, {}).get("category") == "vegetables":
        return VEG_MAGNESIUM_RECOMMENDATIONS[clamped]
    return MAGNESIUM_RECOMMENDATIONS[clamped]


# ── Sulfur ──────────────────────────────────────────────────────────

def recommend_sulfur(crop: str) -> float:
    """Return sulfur recommendation in kg SO3/ha for responsive situations.

    Args:
        crop: Crop value string.
    """
    _validate_crop(crop)
    if crop not in SULFUR_RECOMMENDATIONS:
        raise ValueError(f"No sulfur data for crop '{crop}'")
    return SULFUR_RECOMMENDATIONS[crop]


# ── Sodium ─────────────────────────────────────────────────────────

def recommend_sodium(crop: str, k_index: int | None = None) -> float:
    """Return sodium recommendation in kg Na₂O/ha.

    Sodium is only recommended for certain crops:
      - Sugar beet: rate depends on K Index (Table 4.36).
      - Asparagus (subsequent years): flat rate of 500 kg Na₂O/ha.
      - Grassland: 140 kg Na₂O/ha for herbage mineral balance.

    For all other crops, returns 0.

    Args:
        crop: Crop value string.
        k_index: Soil K index (required for sugar beet; ignored for
            other crops).

    Returns:
        Sodium recommendation in kg Na₂O/ha.
    """
    _validate_crop(crop)

    # Sugar beet: index-dependent recommendation
    if crop in {c for (c, _) in SODIUM_RECOMMENDATIONS}:
        if k_index is None:
            raise ValueError(
                f"k_index is required for sodium recommendation for '{crop}'"
            )
        _validate_index("K index", k_index, 0, 9)
        clamped = _clamp_index(k_index, 4)
        key = (crop, clamped)
        return SODIUM_RECOMMENDATIONS.get(key, 0.0)

    # Asparagus (subsequent years): flat rate
    if crop in SODIUM_FLAT_RATES:
        return SODIUM_FLAT_RATES[crop]

    # Grassland: flat rate for herbage mineral balance
    if crop in SODIUM_GRASSLAND_CROPS:
        return SODIUM_GRASSLAND_RATE

    return 0.0


# ── Full recommendation ────────────────────────────────────────────

def recommend_all(
    crop: str,
    sns_index: int,
    p_index: int,
    k_index: int,
    mg_index: int = 2,
    straw_removed: bool = True,
    soil_type: str | None = None,
    expected_yield: float | None = None,
    ber: float | None = None,
    k_upper_half: bool = False,
) -> NutrientRecommendation:
    """Return a full nutrient recommendation for a crop.

    Args:
        crop: Crop value string.
        sns_index: Soil Nitrogen Supply index (0-6).
        p_index: Soil P index (0-9).
        k_index: Soil K index (0-9).
        mg_index: Soil Mg index (0-9). Defaults to 2 (target).
        straw_removed: For cereals — True if straw removed.
        soil_type: Optional soil type for soil-specific N recommendations.
        expected_yield: Optional expected yield in t/ha for yield-adjusted
            recommendations.
        ber: Optional break-even ratio for cereal N adjustment.
        k_upper_half: For vegetable crops at K Index 2 — True if soil K is in
            the upper half (181–240 mg/l, i.e. 2+), False for 2- (121–180 mg/l).
    """
    _validate_crop(crop)

    n = recommend_nitrogen(crop, sns_index, soil_type, expected_yield=expected_yield, ber=ber)
    p = recommend_phosphorus(crop, p_index, expected_yield=expected_yield)
    k = recommend_potassium(crop, k_index, straw_removed, expected_yield=expected_yield, k_upper_half=k_upper_half)
    mg = recommend_magnesium(mg_index, crop=crop)
    s = recommend_sulfur(crop)
    na = recommend_sodium(crop, k_index=k_index)

    notes: list[str] = []
    info = CROP_INFO[crop]

    if info.get("has_straw_option"):
        mode = "removed" if straw_removed else "incorporated"
        notes.append(f"K recommendation assumes straw {mode}.")

    if info.get("notes"):
        notes.append(info["notes"])

    if n == 0 and crop in ("peas", "field-beans", "veg-peas-market", "veg-beans-broad"):
        notes.append("N-fixing crop: no fertiliser nitrogen required.")

    # Vegetable-specific advisory notes
    _VEG_SEEDBED_CAP_CROPS = {
        "veg-beans-dwarf", "veg-radish", "veg-sweetcorn", "veg-beetroot",
        "veg-swedes", "veg-turnips-parsnips", "veg-carrots", "veg-coriander",
    }
    if crop in _VEG_SEEDBED_CAP_CROPS and n > 0:
        notes.append(
            "Apply no more than 100 kg N/ha in the seedbed. "
            "Apply remainder after establishment."
        )

    if crop == "veg-asparagus":
        notes.append(
            "Year 2: apply 120 kg N/ha by end-Feb/early-Mar. "
            "Year 3+: rate depends on winter rainfall (40–80 kg N/ha); seek FACTS advice."
        )

    if crop == "veg-celery-seedbed":
        notes.append(
            "Apply 75–150 kg N/ha top dressing 4–6 weeks after planting."
        )

    if crop in ("veg-lettuce-whole", "veg-lettuce-baby", "veg-rocket"):
        notes.append(
            "Reduce N for late-season crops to comply with EU/UK tissue-nitrate limits."
        )

    if crop == "veg-leeks":
        notes.append(
            "Do not apply fertiliser N during the NVZ closed period "
            "without written FACTS Qualified Adviser recommendation."
        )

    if info["category"] == "vegetables" and k_index == 2:
        notes.append(
            "K Index 2 is split into 2- (121–180 mg/l) and 2+ (181–240 mg/l). "
            "Use --k-upper-half flag if soil K is in the upper half."
        )

    # 1.1 NVZ N-max warning
    if crop in NVZ_NMAX and n > NVZ_NMAX[crop]:
        limit = NVZ_NMAX[crop]
        notes.append(
            f"N recommendation ({n:.0f} kg/ha) exceeds the NVZ N-max limit "
            f"({limit:.0f} kg/ha) for this crop type. "
            "The N-max applies as a whole-farm average."
        )

    # 1.2 Potash split warning for potatoes
    if crop.startswith("potatoes-") and k > 300:
        notes.append(
            f"K2O recommendation ({k:.0f} kg/ha) exceeds 300 kg/ha. "
            "Apply half in late autumn/winter and half in spring."
        )

    # 1.3 Potash split warning for grass silage
    if crop == "grass-silage" and k > 90:
        notes.append(
            "Limit spring K2O application for 1st cut to 80-90 kg/ha "
            "to minimise luxury uptake. Apply balance in previous autumn."
        )

    # 1.6 Hypomagnesaemia warning for grassland at Mg Index 0
    if info["category"] == "grassland" and mg_index == 0 and k > 0:
        notes.append(
            "Mg Index 0 on grassland: risk of hypomagnesaemia (grass staggers). "
            "Avoid applying potash in spring. Apply 50-100 kg MgO/ha every 3-4 years."
        )

    # 1.7 Clover N-fixation inhibition warning
    if info.get("clover_risk") and n > 0:
        notes.append(
            "Mineral N inhibits clover N fixation. If the sward contains "
            "significant clover, reduce or omit N applications."
        )

    # 1.9 Seedbed N+K2O combine-drill limit for light soils
    if soil_type == "light" and (n + k) > 150 and info["category"] == "arable":
        notes.append(
            f"On sandy soils, do not combine-drill more than 150 kg/ha of N + K2O "
            f"(current total: {n + k:.0f} kg/ha). Risk of seedling damage."
        )

    # 3.2 Yield adjustment note
    if expected_yield is not None and crop in YIELD_ADJUSTMENTS:
        adj = YIELD_ADJUSTMENTS[crop]
        capped_yield = min(expected_yield, adj["max_yield"]) if "max_yield" in adj else expected_yield
        notes.append(
            f"Recommendations adjusted for expected yield of {capped_yield:.1f} t/ha "
            f"(baseline: {adj['baseline_yield']:.1f} t/ha)."
        )

    # 4.2 BER adjustment note
    if ber is not None and crop in CROP_BER_GROUP:
        ber_adj = _interpolate_ber(CROP_BER_GROUP[crop], ber)
        notes.append(
            f"N adjusted for break-even ratio {ber:.1f} "
            f"({ber_adj:+.0f} kg/ha from default BER 5.0)."
        )

    # 2.6 Timing hint — direct users to the timing subcommand
    if n > 0 and crop in NITROGEN_TIMING_RULES:
        notes.append(
            f"Run 'rb209 timing --crop {crop} --total-n {n:.0f}' for "
            "N application timing guidance."
        )

    # Sodium advisory notes
    if na > 0 and crop in SODIUM_NOTES:
        notes.extend(SODIUM_NOTES[crop])
    elif na > 0 and info["category"] == "grassland" and "grassland" in SODIUM_NOTES:
        notes.extend(SODIUM_NOTES["grassland"])
    elif na == 0 and crop in SODIUM_NOTES:
        # Advisory-only crops (e.g. asparagus establishment, celery)
        notes.extend(SODIUM_NOTES[crop])

    return NutrientRecommendation(
        crop=info["name"],
        nitrogen=n,
        phosphorus=p,
        potassium=k,
        magnesium=mg,
        sulfur=s,
        sodium=na,
        notes=notes,
    )


# ── Fruit, Vines and Hops (Section 7) ─────────────────────────────

_TOP_FRUIT_SLUGS = frozenset({
    "fruit-dessert-apple", "fruit-culinary-apple",
    "fruit-pear", "fruit-cherry", "fruit-plum",
})
_STRAWBERRY_SLUGS = frozenset({"fruit-strawberry-main", "fruit-strawberry-ever"})
_SOFT_FRUIT_SLUGS = frozenset({
    "fruit-blackcurrant", "fruit-redcurrant", "fruit-gooseberry",
    "fruit-raspberry", "fruit-loganberry", "fruit-tayberry",
    "fruit-blackberry", "fruit-vine",
})
_PREPLANT_SLUGS = frozenset({"fruit-preplant", "hops-preplant"})


def _is_fruit_crop(crop: str) -> bool:
    return CROP_INFO.get(crop, {}).get("category") == "fruit"


def recommend_fruit_nitrogen(
    crop: str,
    soil_category: str,
    orchard_management: str | None = None,
    sns_index: int | None = None,
) -> float:
    """Return kg N/ha for a fruit, vine or hop crop.

    Args:
        crop: A fruit crop slug (category == "fruit").
        soil_category: FruitSoilCategory value.
        orchard_management: OrchardManagement value; required for top fruit only.
        sns_index: SNS index 0–5; required for strawberry crops only.

    Returns:
        Nitrogen recommendation in kg N/ha.

    Raises:
        ValueError: If crop is unknown, parameters are missing/invalid, or no
                    table entry exists for the given combination.
    """
    if crop not in CROP_INFO:
        raise ValueError(f"Unknown crop '{crop}'.")
    if not _is_fruit_crop(crop):
        raise ValueError(f"Crop '{crop}' is not a fruit category crop.")

    try:
        FruitSoilCategory(soil_category)
    except ValueError:
        valid = ", ".join(c.value for c in FruitSoilCategory)
        raise ValueError(
            f"Unknown soil category '{soil_category}'. Valid options: {valid}"
        )

    if crop in _PREPLANT_SLUGS:
        return 0.0

    if crop in _TOP_FRUIT_SLUGS:
        if orchard_management is None:
            raise ValueError(
                f"orchard_management is required for top fruit crop '{crop}'. "
                "Use 'grass-strip' or 'overall-grass'."
            )
        try:
            OrchardManagement(orchard_management)
        except ValueError:
            valid = ", ".join(m.value for m in OrchardManagement)
            raise ValueError(
                f"Unknown orchard management '{orchard_management}'. "
                f"Valid options: {valid}"
            )
        key = (crop, soil_category, orchard_management)
        if key not in FRUIT_TOP_NITROGEN:
            raise ValueError(
                f"No nitrogen data for top fruit combination: "
                f"crop={crop}, soil={soil_category}, management={orchard_management}"
            )
        return FRUIT_TOP_NITROGEN[key]

    if crop in _STRAWBERRY_SLUGS:
        if sns_index is None:
            raise ValueError(
                f"sns_index is required for strawberry crop '{crop}'."
            )
        if isinstance(sns_index, bool) or not isinstance(sns_index, int) or sns_index < 0:
            raise ValueError(
                f"sns_index must be a non-negative integer, got {sns_index!r}"
            )
        # Map clay → other-mineral for Table 7.8
        mapped_soil = "other-mineral" if soil_category == "clay" else soil_category
        clamped_sns = min(sns_index, 5)
        key = (crop, mapped_soil, clamped_sns)
        if key not in FRUIT_STRAWBERRY_NITROGEN:
            raise ValueError(
                f"No nitrogen data for strawberry combination: "
                f"crop={crop}, soil={mapped_soil}, sns_index={clamped_sns}"
            )
        return FRUIT_STRAWBERRY_NITROGEN[key]

    if crop == "fruit-hops":
        if soil_category == "light-sand":
            raise ValueError(
                "Hops nitrogen is not given for light sand soils in Table 7.17. "
                "Seek specialist advice."
            )
        if soil_category not in FRUIT_HOPS_NITROGEN:
            raise ValueError(
                f"No hops nitrogen data for soil category '{soil_category}'."
            )
        return FRUIT_HOPS_NITROGEN[soil_category]

    if crop in _SOFT_FRUIT_SLUGS:
        key = (crop, soil_category)
        if key not in FRUIT_SOFT_NITROGEN:
            raise ValueError(
                f"No nitrogen data for soft fruit combination: "
                f"crop={crop}, soil={soil_category}"
            )
        return FRUIT_SOFT_NITROGEN[key]

    raise ValueError(f"No nitrogen recommendation logic for fruit crop '{crop}'.")


def recommend_fruit_pkm(
    crop: str,
    p_index: int,
    k_index: int,
    mg_index: int,
) -> tuple[float, float, float]:
    """Return (P2O5, K2O, MgO) kg/ha for a fruit, vine or hop crop.

    Args:
        crop: A fruit crop slug.
        p_index: Soil P index 0–9.
        k_index: Soil K index 0–9.
        mg_index: Soil Mg index 0–9.

    Returns:
        Tuple of (phosphate, potash, magnesium) in kg/ha.
    """
    if crop not in CROP_INFO:
        raise ValueError(f"Unknown crop '{crop}'.")
    if not _is_fruit_crop(crop):
        raise ValueError(f"Crop '{crop}' is not a fruit category crop.")

    _validate_index("P index", p_index, 0, 9)
    _validate_index("K index", k_index, 0, 9)
    _validate_index("Mg index", mg_index, 0, 9)

    if crop == "fruit-preplant":
        cp = _clamp_index(p_index, 5)
        ck = _clamp_index(k_index, 5)
        cm = _clamp_index(mg_index, 5)
        return (
            FRUIT_PREPLANT_PKM[("fruit-vines", "phosphate", cp)],
            FRUIT_PREPLANT_PKM[("fruit-vines", "potash", ck)],
            FRUIT_PREPLANT_PKM[("fruit-vines", "magnesium", cm)],
        )

    if crop == "hops-preplant":
        cp = _clamp_index(p_index, 5)
        ck = _clamp_index(k_index, 5)
        cm = _clamp_index(mg_index, 5)
        return (
            FRUIT_PREPLANT_PKM[("hops", "phosphate", cp)],
            FRUIT_PREPLANT_PKM[("hops", "potash", ck)],
            FRUIT_PREPLANT_PKM[("hops", "magnesium", cm)],
        )

    if crop in _TOP_FRUIT_SLUGS:
        cp = _clamp_index(p_index, 4)
        ck = _clamp_index(k_index, 4)
        cm = _clamp_index(mg_index, 4)
        return (
            FRUIT_TOP_PKM[("phosphate", cp)],
            FRUIT_TOP_PKM[("potash", ck)],
            FRUIT_TOP_PKM[("magnesium", cm)],
        )

    if crop in _SOFT_FRUIT_SLUGS:
        cp = _clamp_index(p_index, 4)
        ck = _clamp_index(k_index, 4)
        cm = _clamp_index(mg_index, 4)
        return (
            FRUIT_SOFT_PKM[(crop, "phosphate", cp)],
            FRUIT_SOFT_PKM[(crop, "potash", ck)],
            FRUIT_SOFT_PKM[(crop, "magnesium", cm)],
        )

    if crop in _STRAWBERRY_SLUGS:
        cp = _clamp_index(p_index, 4)
        ck = _clamp_index(k_index, 4)
        cm = _clamp_index(mg_index, 4)
        return (
            FRUIT_STRAWBERRY_PKM[("phosphate", cp)],
            FRUIT_STRAWBERRY_PKM[("potash", ck)],
            FRUIT_STRAWBERRY_PKM[("magnesium", cm)],
        )

    if crop == "fruit-hops":
        cp = _clamp_index(p_index, 5)
        ck = _clamp_index(k_index, 5)
        cm = _clamp_index(mg_index, 5)
        return (
            FRUIT_HOPS_PKM[("phosphate", cp)],
            FRUIT_HOPS_PKM[("potash", ck)],
            FRUIT_HOPS_PKM[("magnesium", cm)],
        )

    raise ValueError(f"No P/K/Mg recommendation logic for fruit crop '{crop}'.")


def recommend_fruit_all(
    crop: str,
    soil_category: str,
    p_index: int,
    k_index: int,
    mg_index: int,
    orchard_management: str | None = None,
    sns_index: int | None = None,
) -> NutrientRecommendation:
    """Return full N/P/K/Mg recommendation for a fruit, vine or hop crop.

    Args:
        crop: A fruit crop slug (category == "fruit").
        soil_category: FruitSoilCategory value.
        p_index: Soil P index 0–9.
        k_index: Soil K index 0–9.
        mg_index: Soil Mg index 0–9.
        orchard_management: OrchardManagement value; required for top fruit.
        sns_index: SNS index 0–5; required for strawberry crops.

    Returns:
        NutrientRecommendation with N, P, K, Mg, S and advisory notes.
    """
    n = recommend_fruit_nitrogen(
        crop, soil_category,
        orchard_management=orchard_management,
        sns_index=sns_index,
    )
    p, k, mg = recommend_fruit_pkm(crop, p_index, k_index, mg_index)
    s = SULFUR_RECOMMENDATIONS.get(crop, 0.0)

    notes: list[str] = []
    info = CROP_INFO[crop]
    if info.get("notes"):
        notes.append(info["notes"])

    # Fruit sulphur advisory
    notes.append(
        "Fruit crops do not routinely require sulphur. Apply 15–25 kg SO\u2083/ha "
        "as sulphate in spring where deficiency is recognised, on light sandy or "
        "low-OM soils."
    )

    # Top fruit N excess warning
    if crop in _TOP_FRUIT_SLUGS:
        notes.append(
            "Excess nitrogen reduces red colour in apples, encourages large dark "
            "leaves and can reduce storage life. Consider leaf and fruit analysis."
        )

    # Cider apple K note
    if crop == "fruit-culinary-apple":
        notes.append(
            "Cider apples respond to Soil K Index 3. Consider applying K at "
            "Index 3 if growing cider apples."
        )

    # Blackcurrant Ben-series note
    if crop == "fruit-blackcurrant":
        notes.append("Ben-series varieties typically require only 70–120 kg N/ha.")

    # Sulphate of potash note for raspberries/redcurrants/gooseberries
    _SOP_CROPS = {"fruit-redcurrant", "fruit-gooseberry", "fruit-raspberry"}
    if crop in _SOP_CROPS and k_index in (0, 1) and k > 120:
        notes.append("Use sulphate of potash for this crop.")

    # Hops notes
    if crop == "fruit-hops":
        notes.append(
            "Where Verticillium wilt risk is present, reduce N to 125–165 kg N/ha."
        )
        notes.append(
            "Reduce N by 70 kg/ha where large frequent organic manure applications "
            "have been used in the previous year."
        )
        notes.append(
            "Split N into 2–3 dressings: late March/April, May, and late "
            "June/early July."
        )
        notes.append(
            "Ensure soil K:Mg ratio (mg/litre) does not exceed 3:1 to avoid "
            "induced magnesium deficiency."
        )

    # Strawberry notes
    if crop in _STRAWBERRY_SLUGS:
        notes.append(
            "Nitrogen recommendations are based on SNS Index. Use `veg-sns` or "
            "`veg-smn` commands to determine SNS Index (Section 6 system)."
        )
        notes.append(
            "Ensure soil K:Mg ratio (mg/litre) does not exceed 3:1 to avoid "
            "induced magnesium deficiency."
        )

    return NutrientRecommendation(
        crop=info["name"],
        nitrogen=n,
        phosphorus=p,
        potassium=k,
        magnesium=mg,
        sulfur=s,
        sodium=0.0,
        notes=notes,
    )


# ── Nitrogen timing ───────────────────────────────────────────────

def nitrogen_timing(
    crop: str,
    total_n: float,
    soil_type: str | None = None,
) -> NitrogenTimingResult:
    """Return nitrogen split dressing advice for a given crop and total N.

    Args:
        crop: Crop value string.
        total_n: Total nitrogen recommendation (kg N/ha). Must be >= 0.
        soil_type: Optional soil type (affects timing for some crops, e.g.
            potatoes on light soils receive a split application).

    Returns:
        NitrogenTimingResult with split schedule and advisory notes.

    Raises:
        ValueError: If crop is unknown or total_n is negative.
    """
    _validate_crop(crop)

    if total_n < 0:
        raise ValueError(f"total_n must be non-negative, got {total_n}")

    if soil_type is not None:
        try:
            SoilType(soil_type)
        except ValueError:
            valid = ", ".join(s.value for s in SoilType)
            raise ValueError(
                f"Unknown soil type '{soil_type}'. Valid options: {valid}"
            )

    crop_name = CROP_INFO[crop]["name"]
    rules = NITROGEN_TIMING_RULES.get(crop)

    if rules is None:
        # No timing data for this crop — return a single full dressing with advisory.
        split = NitrogenSplit(
            amount=round(total_n),
            timing="As a single dressing at the optimum time for the crop.",
        )
        return NitrogenTimingResult(
            crop=crop_name,
            total_n=total_n,
            splits=[split],
            notes=[
                f"No specific timing guidance for {crop}. "
                "Apply as a single dressing."
            ],
        )

    # Find first matching rule.
    matched_rule: dict | None = None
    for rule in rules:
        min_n = rule.get("min_n", 0)
        max_n = rule.get("max_n", float("inf"))
        if total_n < min_n or total_n > max_n:
            continue
        soil_cond = rule.get("soil_condition")
        if soil_cond is not None and not soil_cond(soil_type):
            continue
        matched_rule = rule
        break

    if matched_rule is None:
        # Fallback: apply all in one dressing (should not normally occur).
        split = NitrogenSplit(
            amount=round(total_n),
            timing="As a single dressing at the optimum time for the crop.",
        )
        return NitrogenTimingResult(
            crop=crop_name,
            total_n=total_n,
            splits=[split],
            notes=[],
        )

    rule_splits = matched_rule["splits"]
    notes: list[str] = list(matched_rule.get("notes", []))

    # Compute dressing amounts from fractions or fixed amounts.
    amounts: list[int] = []
    for i, s in enumerate(rule_splits):
        if i < len(rule_splits) - 1:
            if "fixed_amount" in s:
                # Absolute cap: use min(fixed_amount, remaining N) so the last
                # split is never negative even when total_n < fixed_amount.
                remaining = round(total_n) - sum(amounts)
                amounts.append(max(0, min(int(s["fixed_amount"]), remaining)))
            else:
                amounts.append(round(s["fraction"] * total_n))
        else:
            # Last split gets the remainder to preserve the total.
            amounts.append(round(total_n) - sum(amounts))

    splits = [
        NitrogenSplit(amount=float(amt), timing=s["timing"])
        for amt, s in zip(amounts, rule_splits)
    ]

    return NitrogenTimingResult(
        crop=crop_name,
        total_n=total_n,
        splits=splits,
        notes=notes,
    )


# ── Organic materials ──────────────────────────────────────────────

def calculate_organic(
    material: str,
    rate: float,
    timing: str | None = None,
    incorporated: bool = False,
    soil_type: str | None = None,
) -> OrganicNutrients:
    """Calculate nutrients supplied by an organic material application.

    Args:
        material: Organic material value string.
        rate: Application rate in t/ha (FYM/compost) or m3/ha (slurry).
        timing: Optional application timing season for N adjustment.
            One of "autumn" (Aug–Oct), "winter" (Nov–Jan),
            "spring" (Feb–Apr), or "summer" (grassland).
            When provided, available_n is derived from the RB209 timing
            and incorporation factor tables (Section 2) instead of the
            flat default coefficient.
        incorporated: Whether the material is soil-incorporated promptly
            after application (within 6 h for liquids, 24 h for solids).
            Only meaningful when *timing* is also supplied.
        soil_type: Soil type string ("light", "medium", "heavy", "organic").
            Used with *timing* to select the correct soil category in the
            factor tables.  Defaults to "medium_heavy" when omitted.
    """
    try:
        OrganicMaterial(material)
    except ValueError:
        valid = ", ".join(m.value for m in OrganicMaterial)
        raise ValueError(
            f"Unknown organic material '{material}'. Valid options: {valid}"
        )

    if rate < 0:
        raise ValueError("Application rate must be non-negative")

    info = ORGANIC_MATERIAL_INFO[material]
    total_n = round(info["total_n"] * rate, 1)

    if timing is not None:
        timing_table = ORGANIC_N_TIMING_FACTORS.get(material)
        if timing_table is None:
            raise ValueError(
                f"No timing/incorporation factors available for '{material}'. "
                "Use the flat available_n coefficient instead."
            )
        soil_cat = TIMING_SOIL_CATEGORY.get(soil_type or "", "medium_heavy")
        key = (timing, soil_cat, incorporated)
        if key not in timing_table:
            raise ValueError(
                f"No timing factor for material='{material}', timing='{timing}', "
                f"soil_category='{soil_cat}', incorporated={incorporated}. "
                "Check that the combination is defined in the relevant RB209 Section 2 table."
            )
        n_factor = timing_table[key]
        available_n = round(n_factor * info["total_n"] * rate, 1)
    else:
        available_n = round(info["available_n"] * rate, 1)

    # 1.8 Organic application condition warning
    organic_notes = [
        "Do not apply organic materials to soils that are waterlogged, frozen hard, "
        "snow-covered, or deeply cracked."
    ]

    return OrganicNutrients(
        material=info["name"],
        rate=rate,
        unit=info["unit"],
        total_n=total_n,
        available_n=available_n,
        p2o5=round(info["p2o5"] * rate, 1),
        k2o=round(info["k2o"] * rate, 1),
        mgo=round(info["mgo"] * rate, 1),
        so3=round(info["so3"] * rate, 1),
        notes=organic_notes,
    )


# ── Lime ────────────────────────────────────────────────────────────

def calculate_lime(
    current_ph: float,
    target_ph: float | None,
    soil_type: str,
    land_use: str | None = None,
    crop: str | None = None,
) -> LimeRecommendation:
    """Calculate lime requirement.

    ``target_ph`` may be omitted (``None``) when ``land_use`` is supplied;
    the RB209 default target pH is then used automatically (arable: 6.5,
    grassland: 6.0).  Passing an explicit ``target_ph`` always takes
    precedence over the ``land_use`` default.

    When the current pH is below the RB209 minimum liming threshold
    (``MIN_PH_FOR_LIMING = 5.0``), an advisory note is included in the result
    to flag the severity.

    Args:
        current_ph: Current soil pH.
        target_ph: Target soil pH, or ``None`` to derive from ``land_use``.
        soil_type: Soil type ("light", "medium", "heavy", "organic").
        land_use: Land use category for automatic target pH selection:
            "arable" (default target 6.5) or "grassland" (default target 6.0).
            Required when ``target_ph`` is ``None``; ignored otherwise.
        crop: Optional crop value string. When a potato crop is specified and
            lime is required, a warning about common scab risk is added.
    """
    try:
        SoilType(soil_type)
    except ValueError:
        valid = ", ".join(s.value for s in SoilType)
        raise ValueError(f"Unknown soil type '{soil_type}'. Valid options: {valid}")

    if target_ph is None:
        valid_land_uses = tuple(TARGET_PH.keys())
        if land_use is None:
            raise ValueError(
                "Either target_ph or land_use must be provided. "
                f"Valid land_use values: {', '.join(valid_land_uses)}"
            )
        if land_use not in TARGET_PH:
            raise ValueError(
                f"Unknown land_use '{land_use}'. "
                f"Valid options: {', '.join(valid_land_uses)}"
            )
        target_ph = TARGET_PH[land_use]

    if not (3.0 <= current_ph <= 9.0):
        raise ValueError(f"Current pH must be between 3.0 and 9.0, got {current_ph}")
    if not (4.0 <= target_ph <= 8.5):
        raise ValueError(f"Target pH must be between 4.0 and 8.5, got {target_ph}")

    notes: list[str] = []

    if current_ph < MIN_PH_FOR_LIMING:
        notes.append(
            f"Soil pH ({current_ph}) is below {MIN_PH_FOR_LIMING}. "
            "Soil is very acidic — liming is strongly recommended."
        )

    if current_ph >= target_ph:
        notes.append("Soil pH is already at or above target. No lime required.")
        return LimeRecommendation(
            current_ph=current_ph,
            target_ph=target_ph,
            soil_type=soil_type,
            lime_required=0.0,
            notes=notes,
        )

    ph_deficit = target_ph - current_ph
    factor = LIME_FACTORS[soil_type]
    lime_needed = round(ph_deficit * factor, 1)

    if lime_needed > MAX_SINGLE_APPLICATION:
        notes.append(
            f"Total lime required ({lime_needed} t/ha) exceeds single application "
            f"maximum ({MAX_SINGLE_APPLICATION} t/ha). Apply in split dressings "
            f"over successive years."
        )

    # 1.4 Lime-before-potatoes warning
    if crop is not None and crop.startswith("potatoes-"):
        notes.append(
            "Avoid liming immediately before potatoes — increases common scab "
            "risk and manganese deficiency risk."
        )

    # 1.5 Over-liming trace element warnings
    if target_ph > 7.0 and land_use == "grassland":
        notes.append(
            "Avoid liming grassland above pH 7.0 — may induce copper, cobalt "
            "and selenium deficiencies."
        )
    if target_ph > 7.5:
        notes.append(
            "Manganese deficiency risk increases above pH 7.5."
        )
    if soil_type == "light" and target_ph > 6.5:
        notes.append(
            "On sandy soils, manganese deficiency is more likely above pH 6.5."
        )
    if soil_type == "organic" and target_ph > 6.0:
        notes.append(
            "On organic/peaty soils, manganese deficiency is more likely above pH 6.0."
        )

    return LimeRecommendation(
        current_ph=current_ph,
        target_ph=target_ph,
        soil_type=soil_type,
        lime_required=lime_needed,
        notes=notes,
    )
