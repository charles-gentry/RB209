"""Magnesium (MgO) recommendation tables.

Values are kg MgO/ha by soil Mg index.
Based on RB209 9th edition.
"""

# mg_index -> kg MgO/ha
MAGNESIUM_RECOMMENDATIONS: dict[int, float] = {
    0: 90,
    1: 60,
    2: 0,
    3: 0,
    4: 0,
}

# Vegetable crops use higher Mg rates (Section 6, p.16).
VEG_MAGNESIUM_RECOMMENDATIONS: dict[int, float] = {
    0: 150,
    1: 100,
    2: 0,
    3: 0,
    4: 0,
}
