"""Yield adjustment factors for N, P2O5, and K2O.

Each entry maps a crop to its adjustment parameters:
  "baseline_yield": t/ha (default assumed yield)
  "n_adjust_per_t": kg N/ha per tonne above/below baseline
  "p_adjust_per_t": kg P2O5/ha per tonne (offtake-based)
  "k_adjust_per_t": kg K2O/ha per tonne (offtake-based)
  "max_yield": optional cap on yield adjustment

Source: RB209 Section 4 Table 4.12 (cereals), Section 5 p.8 (potatoes).
"""

YIELD_ADJUSTMENTS: dict[str, dict] = {
    "winter-wheat-feed": {
        "baseline_yield": 8.0,
        "n_adjust_per_t": 20,      # 10 kg per 0.5 t = 20 per t
        "p_adjust_per_t": 7.0,     # Table 4.12 grain+straw
        "k_adjust_per_t": 10.5,
        "max_yield": 13.0,
    },
    "winter-wheat-milling": {
        "baseline_yield": 8.0,
        "n_adjust_per_t": 20,
        "p_adjust_per_t": 7.0,
        "k_adjust_per_t": 10.5,
        "max_yield": 13.0,
    },
    "winter-oats": {
        "baseline_yield": 6.0,
        "n_adjust_per_t": 20,      # Table 4.19
        "p_adjust_per_t": 7.0,
        "k_adjust_per_t": 12.0,
    },
    "potatoes-maincrop": {
        "baseline_yield": 50.0,
        "n_adjust_per_t": 0,       # No N yield adjustment for potatoes
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 5.8,     # K2O at target index
    },
    "potatoes-early": {
        "baseline_yield": 30.0,
        "n_adjust_per_t": 0,
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 5.8,
    },
    # Additional crops to be populated from RB209 Table 4.12
}
