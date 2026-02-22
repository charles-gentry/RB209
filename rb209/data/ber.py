"""Break-even ratio (BER) adjustments for cereal N recommendations.

BER = cost of fertiliser N (£/kg) ÷ grain value (£/kg).
Default BER is 5.0.  Tables 4.25 and 4.26 provide adjustments.

BER_ADJUSTMENTS[(crop_group, ber)] -> kg N/ha adjustment from the default.

Source: RB209 Section 4 Tables 4.25 (wheat) and 4.26 (barley).
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
