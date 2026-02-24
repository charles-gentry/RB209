"""Yield adjustment factors for N, P2O5, and K2O.

Each entry maps a crop to its adjustment parameters:
  "baseline_yield": t/ha (default assumed yield from RB209 table)
  "n_adjust_per_t": kg fertiliser N/ha per tonne above/below baseline
  "p_adjust_per_t": kg P2O5/ha per tonne (offtake-based, Table 6.8)
  "k_adjust_per_t": kg K2O/ha per tonne (offtake-based, Table 6.8)
  "max_yield": optional cap on yield adjustment

Sources:
  Arable/potato crops: RB209 Section 4 Table 4.12 (cereals),
                       Section 5 p.8 (potatoes).
  Vegetable crops:     RB209 Section 6 Table 6.27 (baseline yield, N uptake);
                       Section 6 Table 6.8 (P2O5 and K2O offtake per tonne).

For vegetable crops the N adjustment per tonne is derived as:
  n_adjust_per_t = (N_uptake / baseline_yield) / fertiliser_recovery
where fertiliser_recovery = 0.60 (60 % as stated in RB209 Section 6).
This is a linear approximation, valid for small deviations from the
baseline yield as noted in RB209 ("for small changes in yield, e.g. if
yield increases by 10 %, nitrogen uptake increases by the same amount").

Crops explicitly excluded by Table 6.27 footnote (insufficient data):
  asparagus, celery, peas/beans, sweetcorn, courgettes, bulbs.
"""

YIELD_ADJUSTMENTS: dict[str, dict] = {
    # ── Arable cereals (Table 4.12) ──────────────────────────────────
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
    # ── Potatoes (Section 5) ─────────────────────────────────────────
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
    # ── Vegetable brassicas (Tables 6.27 + 6.8) ──────────────────────
    "veg-brussels-sprouts": {
        # T6.27: 20.3 t/ha fresh, 368 kg N/ha; T6.8: sprouts buttons
        "baseline_yield": 20.3,
        "n_adjust_per_t": 30.2,    # 368 / (20.3 × 0.60)
        "p_adjust_per_t": 2.6,     # Table 6.8 sprouts (buttons)
        "k_adjust_per_t": 6.3,
    },
    "veg-cabbage-storage": {
        # T6.27: 110.0 t/ha, 378 kg N/ha; T6.8: cabbage
        "baseline_yield": 110.0,
        "n_adjust_per_t": 5.7,     # 378 / (110.0 × 0.60)
        "p_adjust_per_t": 0.9,     # Table 6.8 cabbage
        "k_adjust_per_t": 3.6,
    },
    "veg-cabbage-head-pre-dec": {
        # T6.27: 60.0 t/ha, 270 kg N/ha; T6.8: cabbage
        "baseline_yield": 60.0,
        "n_adjust_per_t": 7.5,     # 270 / (60.0 × 0.60)
        "p_adjust_per_t": 0.9,
        "k_adjust_per_t": 3.6,
    },
    "veg-cabbage-head-post-dec": {
        # T6.27: 53.0 t/ha, 203 kg N/ha; T6.8: cabbage
        "baseline_yield": 53.0,
        "n_adjust_per_t": 6.4,     # 203 / (53.0 × 0.60)
        "p_adjust_per_t": 0.9,
        "k_adjust_per_t": 3.6,
    },
    "veg-collards-pre-dec": {
        # T6.27 row 1: 20.0 t/ha, 260 kg N/ha; P/K: cabbage proxy
        "baseline_yield": 20.0,
        "n_adjust_per_t": 21.7,    # 260 / (20.0 × 0.60)
        "p_adjust_per_t": 0.9,     # Table 6.8 cabbage (proxy)
        "k_adjust_per_t": 3.6,
    },
    "veg-collards-post-dec": {
        # T6.27 row 2 (dates 15/09–15/01): 30.0 t/ha, 300 kg N/ha; P/K: cabbage proxy
        "baseline_yield": 30.0,
        "n_adjust_per_t": 16.7,    # 300 / (30.0 × 0.60)
        "p_adjust_per_t": 0.9,     # Table 6.8 cabbage (proxy)
        "k_adjust_per_t": 3.6,
    },
    "veg-cauliflower-summer": {
        # T6.27: 30.6 t/ha, 259 kg N/ha; T6.8: cauliflowers
        "baseline_yield": 30.6,
        "n_adjust_per_t": 14.1,    # 259 / (30.6 × 0.60)
        "p_adjust_per_t": 1.4,     # Table 6.8 cauliflowers
        "k_adjust_per_t": 4.8,
    },
    "veg-calabrese": {
        # T6.27: 16.3 t/ha, 226 kg N/ha; T6.8: cauliflowers (proxy for calabrese)
        "baseline_yield": 16.3,
        "n_adjust_per_t": 23.1,    # 226 / (16.3 × 0.60)
        "p_adjust_per_t": 1.4,     # Table 6.8 cauliflowers (proxy)
        "k_adjust_per_t": 4.8,
    },
    # ── Vegetable salads / leafy (Table 6.27 + 6.8) ──────────────────
    "veg-lettuce-whole": {
        # T6.27: lettuce (crisp) 45.5 t/ha, 165 kg N/ha; P/K not in T6.8
        "baseline_yield": 45.5,
        "n_adjust_per_t": 6.0,     # 165 / (45.5 × 0.60)
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 0,
    },
    # ── Radish (Table 6.27 only; T6.8 has no radish entry) ───────────
    "veg-radish": {
        # T6.27: 50.0 t/ha, 100 kg N/ha
        "baseline_yield": 50.0,
        "n_adjust_per_t": 3.3,     # 100 / (50.0 × 0.60)
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 0,
    },
    # ── Alliums (Tables 6.27 + 6.8) ──────────────────────────────────
    "veg-onions-bulb": {
        # T6.27: bulb onions spring 60.5 t/ha, 147 kg N/ha; T6.8: onions (bulbs only)
        "baseline_yield": 60.5,
        "n_adjust_per_t": 4.1,     # 147 / (60.5 × 0.60)
        "p_adjust_per_t": 0.7,     # Table 6.8 onions (bulbs only)
        "k_adjust_per_t": 1.8,
    },
    "veg-onions-salad": {
        # T6.27: salad onions 30.0 t/ha, 114 kg N/ha; T6.8: onions (proxy)
        "baseline_yield": 30.0,
        "n_adjust_per_t": 6.3,     # 114 / (30.0 × 0.60)
        "p_adjust_per_t": 0.7,     # Table 6.8 onions (proxy)
        "k_adjust_per_t": 1.8,
    },
    "veg-leeks": {
        # T6.27: 47.0 t/ha, 279 kg N/ha; P/K not in T6.8
        "baseline_yield": 47.0,
        "n_adjust_per_t": 9.9,     # 279 / (47.0 × 0.60)
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 0,
    },
    # ── Root vegetables (Tables 6.27 + 6.8) ──────────────────────────
    "veg-beetroot": {
        # T6.27: 60.0 t/ha, 270 kg N/ha*; T6.8: beetroot
        "baseline_yield": 60.0,
        "n_adjust_per_t": 7.5,     # 270 / (60.0 × 0.60) — N uptake from KNS 2007
        "p_adjust_per_t": 1.0,     # Table 6.8 beetroot
        "k_adjust_per_t": 4.5,
    },
    "veg-swedes": {
        # T6.27: swede 84.4 t/ha, 222 kg N/ha; T6.8: swedes (roots only)
        "baseline_yield": 84.4,
        "n_adjust_per_t": 4.4,     # 222 / (84.4 × 0.60)
        "p_adjust_per_t": 0.7,     # Table 6.8 swedes (roots only)
        "k_adjust_per_t": 2.4,
    },
    "veg-turnips-parsnips": {
        # T6.27: parsnips and turnips 48.0 t/ha, 241 kg N/ha*; P/K not in T6.8
        "baseline_yield": 48.0,
        "n_adjust_per_t": 8.4,     # 241 / (48.0 × 0.60) — N uptake from KNS 2007
        "p_adjust_per_t": 0,
        "k_adjust_per_t": 0,
    },
    "veg-carrots": {
        # T6.27: 150.0 t/ha, 178 kg N/ha; T6.8: carrots
        "baseline_yield": 150.0,
        "n_adjust_per_t": 2.0,     # 178 / (150.0 × 0.60)
        "p_adjust_per_t": 0.7,     # Table 6.8 carrots
        "k_adjust_per_t": 3.0,
    },
    # ── Herbs (Tables 6.27 + 6.8) ────────────────────────────────────
    "veg-coriander": {
        # T6.27: 48.0 t/ha, 129 kg N/ha; T6.8: coriander
        "baseline_yield": 48.0,
        "n_adjust_per_t": 4.5,     # 129 / (48.0 × 0.60)
        "p_adjust_per_t": 0.8,     # Table 6.8 coriander
        "k_adjust_per_t": 5.5,
    },
    "veg-mint": {
        # T6.27: mint 25.0 t/ha, 153 kg N/ha; T6.8: mint
        "baseline_yield": 25.0,
        "n_adjust_per_t": 10.2,    # 153 / (25.0 × 0.60)
        "p_adjust_per_t": 1.0,     # Table 6.8 mint
        "k_adjust_per_t": 3.9,
    },
}
