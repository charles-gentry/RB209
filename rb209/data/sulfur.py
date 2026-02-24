"""Sulfur (SO3) recommendation tables.

Values are kg SO3/ha for crops likely to respond to sulfur.
Based on RB209 9th edition. Recommendations are for S-responsive
situations (most of England and Wales now considered responsive).
"""

# crop_value -> kg SO3/ha (for responsive situations)
SULFUR_RECOMMENDATIONS: dict[str, float] = {
    # Cereals
    "winter-wheat-feed": 30,
    "winter-wheat-milling": 40,
    "spring-wheat": 25,
    "winter-barley": 30,
    "spring-barley": 25,
    "winter-oats": 25,
    "spring-oats": 20,
    "winter-rye": 25,

    # Oilseeds - high S demand
    "winter-oilseed-rape": 75,
    "spring-oilseed-rape": 50,
    "linseed": 25,

    # Pulses
    "peas": 0,
    "field-beans": 0,

    # Root/forage
    "sugar-beet": 35,
    "forage-maize": 25,

    # Potatoes
    "potatoes-maincrop": 35,
    "potatoes-early": 30,
    "potatoes-seed": 25,

    # Grassland
    "grass-grazed": 30,
    "grass-silage": 40,
    "grass-hay": 30,
    "grass-grazed-one-cut": 35,

    # Vegetable crops — Brassicas: 50 kg SO3/ha (Section 6)
    "veg-brussels-sprouts":           50,
    "veg-cabbage-storage":            50,
    "veg-cabbage-head-pre-dec":       50,
    "veg-cabbage-head-post-dec":      50,
    "veg-collards-pre-dec":           50,
    "veg-collards-post-dec":          50,
    "veg-cauliflower-summer":         50,
    "veg-cauliflower-winter-seedbed": 50,
    "veg-cauliflower-winter-topdress": 50,
    "veg-calabrese":                  50,
    "veg-swedes":                     50,  # swedes are brassicas
    "veg-turnips-parsnips":           50,  # turnips are brassicas

    # Vegetable crops — other: 25 kg SO3/ha
    "veg-asparagus-est":      25,
    "veg-asparagus":          25,
    "veg-celery-seedbed":     25,
    "veg-radish":             25,
    "veg-sweetcorn":          25,
    "veg-lettuce-whole":      25,
    "veg-lettuce-baby":       25,
    "veg-rocket":             25,
    "veg-onions-bulb":        25,
    "veg-onions-salad":       25,
    "veg-leeks":              25,
    "veg-beetroot":           25,
    "veg-carrots":            25,
    "veg-bulbs":              25,
    "veg-coriander":          25,
    "veg-mint-est":           25,
    "veg-mint":               25,
    "veg-courgettes-seedbed":   25,
    "veg-courgettes-topdress":   0,  # S applied at seedbed; none at topdress

    # N-fixing vegetable crops — no S response documented
    "veg-peas-market":  0,
    "veg-beans-broad":  0,
    "veg-beans-dwarf":  0,
}
