"""Recommendation engine — core logic for RB209 fertiliser calculations."""

from rb209.models import (
    Crop,
    LimeRecommendation,
    NResidueCategory,
    NutrientRecommendation,
    OrganicMaterial,
    OrganicNutrients,
    PREVIOUS_CROP_N_CATEGORY,
    PreviousCrop,
    Rainfall,
    SNSResult,
    SoilType,
)
from rb209.data.crops import CROP_INFO
from rb209.data.lime import LIME_FACTORS, MAX_SINGLE_APPLICATION
from rb209.data.magnesium import MAGNESIUM_RECOMMENDATIONS
from rb209.data.nitrogen import NITROGEN_RECOMMENDATIONS, NITROGEN_SOIL_SPECIFIC
from rb209.data.organic import ORGANIC_MATERIAL_INFO
from rb209.data.phosphorus import PHOSPHORUS_RECOMMENDATIONS
from rb209.data.potassium import (
    POTASSIUM_RECOMMENDATIONS,
    POTASSIUM_STRAW_INCORPORATED,
    POTASSIUM_STRAW_REMOVED,
)
from rb209.data.sns import SNS_LOOKUP, SNS_VALUE_TO_INDEX
from rb209.data.sulfur import SULFUR_RECOMMENDATIONS


def _validate_crop(crop: str) -> None:
    if crop not in CROP_INFO:
        valid = ", ".join(sorted(CROP_INFO))
        raise ValueError(f"Unknown crop '{crop}'. Valid crops: {valid}")


def _validate_index(name: str, value: int, min_val: int = 0, max_val: int = 6) -> None:
    if not isinstance(value, int) or value < min_val or value > max_val:
        raise ValueError(
            f"{name} must be an integer between {min_val} and {max_val}, got {value}"
        )


def _clamp_index(value: int, max_key: int) -> int:
    """Clamp an index to the maximum key in the lookup table."""
    return min(value, max_key)


# ── SNS ─────────────────────────────────────────────────────────────

def calculate_sns(
    previous_crop: str,
    soil_type: str,
    rainfall: str,
) -> SNSResult:
    """Calculate Soil Nitrogen Supply index using the field assessment method.

    Args:
        previous_crop: Previous crop value (e.g. "cereals", "oilseed-rape").
        soil_type: Soil type ("light", "medium", "heavy", "organic").
        rainfall: Excess winter rainfall category ("low", "medium", "high").

    Returns:
        SNSResult with the calculated SNS index.
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

    notes = [
        f"Previous crop '{previous_crop}' has {n_cat.value} N residue.",
    ]

    return SNSResult(
        sns_index=sns_index,
        previous_crop=previous_crop,
        soil_type=soil_type,
        rainfall=rainfall,
        method="field-assessment",
        notes=notes,
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


# ── Nitrogen ────────────────────────────────────────────────────────

def recommend_nitrogen(
    crop: str, sns_index: int, soil_type: str | None = None
) -> float:
    """Return nitrogen recommendation in kg N/ha.

    Args:
        crop: Crop value string.
        sns_index: Soil Nitrogen Supply index (0-6).
        soil_type: Optional soil type for soil-specific recommendations.
            When provided, uses Table 4.17 (and similar) soil-specific data.
            When omitted, uses the generic recommendation table.
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
            return NITROGEN_SOIL_SPECIFIC[soil_key]
        raise ValueError(
            f"No soil-specific nitrogen data for crop '{crop}' "
            f"at SNS {sns_index} on {soil_type} soil"
        )

    key = (crop, sns_index)
    if key not in NITROGEN_RECOMMENDATIONS:
        raise ValueError(f"No nitrogen data for crop '{crop}' at SNS {sns_index}")
    return NITROGEN_RECOMMENDATIONS[key]


# ── Phosphorus ──────────────────────────────────────────────────────

def recommend_phosphorus(crop: str, p_index: int) -> float:
    """Return phosphorus recommendation in kg P2O5/ha.

    Args:
        crop: Crop value string.
        p_index: Soil P index (0-9, clamped to max available key).
    """
    _validate_crop(crop)
    _validate_index("P index", p_index, 0, 9)

    clamped = _clamp_index(p_index, 4)
    key = (crop, clamped)
    if key not in PHOSPHORUS_RECOMMENDATIONS:
        raise ValueError(f"No phosphorus data for crop '{crop}'")
    return PHOSPHORUS_RECOMMENDATIONS[key]


# ── Potassium ───────────────────────────────────────────────────────

def recommend_potassium(
    crop: str, k_index: int, straw_removed: bool = True
) -> float:
    """Return potassium recommendation in kg K2O/ha.

    Args:
        crop: Crop value string.
        k_index: Soil K index (0-9, clamped to max available key).
        straw_removed: For cereals only — True if straw is removed.
    """
    _validate_crop(crop)
    _validate_index("K index", k_index, 0, 9)

    clamped = _clamp_index(k_index, 4)
    key = (crop, clamped)

    # Check if this is a cereal with straw option
    info = CROP_INFO[crop]
    if info.get("has_straw_option"):
        table = POTASSIUM_STRAW_REMOVED if straw_removed else POTASSIUM_STRAW_INCORPORATED
        if key in table:
            return table[key]

    if key in POTASSIUM_RECOMMENDATIONS:
        return POTASSIUM_RECOMMENDATIONS[key]

    raise ValueError(f"No potassium data for crop '{crop}'")


# ── Magnesium ───────────────────────────────────────────────────────

def recommend_magnesium(mg_index: int) -> float:
    """Return magnesium recommendation in kg MgO/ha.

    Args:
        mg_index: Soil Mg index (0-9, clamped to max available key).
    """
    _validate_index("Mg index", mg_index, 0, 9)
    clamped = _clamp_index(mg_index, 4)
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


# ── Full recommendation ────────────────────────────────────────────

def recommend_all(
    crop: str,
    sns_index: int,
    p_index: int,
    k_index: int,
    mg_index: int = 2,
    straw_removed: bool = True,
    soil_type: str | None = None,
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
    """
    _validate_crop(crop)

    n = recommend_nitrogen(crop, sns_index, soil_type)
    p = recommend_phosphorus(crop, p_index)
    k = recommend_potassium(crop, k_index, straw_removed)
    mg = recommend_magnesium(mg_index)
    s = recommend_sulfur(crop)

    notes: list[str] = []
    info = CROP_INFO[crop]

    if info.get("has_straw_option"):
        mode = "removed" if straw_removed else "incorporated"
        notes.append(f"K recommendation assumes straw {mode}.")

    if info.get("notes"):
        notes.append(info["notes"])

    if n == 0 and crop in ("peas", "field-beans"):
        notes.append("N-fixing crop: no fertiliser nitrogen required.")

    return NutrientRecommendation(
        crop=info["name"],
        nitrogen=n,
        phosphorus=p,
        potassium=k,
        magnesium=mg,
        sulfur=s,
        notes=notes,
    )


# ── Organic materials ──────────────────────────────────────────────

def calculate_organic(material: str, rate: float) -> OrganicNutrients:
    """Calculate nutrients supplied by an organic material application.

    Args:
        material: Organic material value string.
        rate: Application rate in t/ha (FYM/compost) or m3/ha (slurry).
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
    return OrganicNutrients(
        material=info["name"],
        rate=rate,
        total_n=round(info["total_n"] * rate, 1),
        available_n=round(info["available_n"] * rate, 1),
        p2o5=round(info["p2o5"] * rate, 1),
        k2o=round(info["k2o"] * rate, 1),
        mgo=round(info["mgo"] * rate, 1),
        so3=round(info["so3"] * rate, 1),
    )


# ── Lime ────────────────────────────────────────────────────────────

def calculate_lime(
    current_ph: float,
    target_ph: float,
    soil_type: str,
) -> LimeRecommendation:
    """Calculate lime requirement.

    Args:
        current_ph: Current soil pH.
        target_ph: Target soil pH.
        soil_type: Soil type ("light", "medium", "heavy", "organic").
    """
    try:
        SoilType(soil_type)
    except ValueError:
        valid = ", ".join(s.value for s in SoilType)
        raise ValueError(f"Unknown soil type '{soil_type}'. Valid options: {valid}")

    if not (3.0 <= current_ph <= 9.0):
        raise ValueError(f"Current pH must be between 3.0 and 9.0, got {current_ph}")
    if not (4.0 <= target_ph <= 8.5):
        raise ValueError(f"Target pH must be between 4.0 and 8.5, got {target_ph}")

    notes: list[str] = []

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

    return LimeRecommendation(
        current_ph=current_ph,
        target_ph=target_ph,
        soil_type=soil_type,
        lime_required=lime_needed,
        notes=notes,
    )
