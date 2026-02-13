"""Soil Nitrogen Supply (SNS) lookup tables.

SNS is determined by previous crop N-residue category, soil type,
and excess winter rainfall.
Based on RB209 9th edition field assessment method.
"""

# (n_residue_category, soil_type, rainfall) -> SNS index
# n_residue_category: "low", "medium", "high", "very-high"
# soil_type: "light", "medium", "heavy", "organic"
# rainfall: "low", "medium", "high"

SNS_LOOKUP: dict[tuple[str, str, str], int] = {
    # LOW N residue (cereals, sugar beet, linseed, forage maize, set-aside, fallow)
    ("low", "light", "low"): 1,
    ("low", "light", "medium"): 0,
    ("low", "light", "high"): 0,
    ("low", "medium", "low"): 1,
    ("low", "medium", "medium"): 1,
    ("low", "medium", "high"): 1,
    ("low", "heavy", "low"): 2,
    ("low", "heavy", "medium"): 2,
    ("low", "heavy", "high"): 1,
    ("low", "organic", "low"): 3,
    ("low", "organic", "medium"): 2,
    ("low", "organic", "high"): 2,

    # MEDIUM N residue (oilseed rape, potatoes)
    ("medium", "light", "low"): 2,
    ("medium", "light", "medium"): 1,
    ("medium", "light", "high"): 1,
    ("medium", "medium", "low"): 3,
    ("medium", "medium", "medium"): 2,
    ("medium", "medium", "high"): 2,
    ("medium", "heavy", "low"): 3,
    ("medium", "heavy", "medium"): 3,
    ("medium", "heavy", "high"): 2,
    ("medium", "organic", "low"): 4,
    ("medium", "organic", "medium"): 3,
    ("medium", "organic", "high"): 3,

    # HIGH N residue (peas/beans, vegetables, 1-2 yr grass)
    ("high", "light", "low"): 3,
    ("high", "light", "medium"): 2,
    ("high", "light", "high"): 1,
    ("high", "medium", "low"): 4,
    ("high", "medium", "medium"): 3,
    ("high", "medium", "high"): 2,
    ("high", "heavy", "low"): 4,
    ("high", "heavy", "medium"): 3,
    ("high", "heavy", "high"): 3,
    ("high", "organic", "low"): 5,
    ("high", "organic", "medium"): 4,
    ("high", "organic", "high"): 3,

    # VERY HIGH N residue (long-term grass 5+ years, lucerne)
    ("very-high", "light", "low"): 4,
    ("very-high", "light", "medium"): 3,
    ("very-high", "light", "high"): 2,
    ("very-high", "medium", "low"): 5,
    ("very-high", "medium", "medium"): 4,
    ("very-high", "medium", "high"): 3,
    ("very-high", "heavy", "low"): 5,
    ("very-high", "heavy", "medium"): 4,
    ("very-high", "heavy", "high"): 4,
    ("very-high", "organic", "low"): 6,
    ("very-high", "organic", "medium"): 5,
    ("very-high", "organic", "high"): 4,
}

# Table 4.10: SNS value (kg N/ha) to SNS index.
# Each tuple is (upper_bound_inclusive, sns_index).
# Evaluated in order; first match wins.
SNS_VALUE_TO_INDEX: list[tuple[float, int]] = [
    (60, 0),
    (80, 1),
    (100, 2),
    (120, 3),
    (160, 4),
    (240, 5),
    (float("inf"), 6),
]
