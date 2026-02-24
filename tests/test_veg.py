"""Tests for vegetable crop support (Section 6 of RB209)."""

import unittest

from rb209.engine import (
    calculate_veg_sns,
    recommend_all,
    recommend_magnesium,
    recommend_nitrogen,
    recommend_phosphorus,
    recommend_potassium,
    recommend_sulfur,
    smn_to_sns_index_veg,
)


class TestVegSNSLookup(unittest.TestCase):
    """Spot-check VEG_SNS_LOOKUP against Tables 6.2–6.4."""

    def test_low_rainfall_cereals_light_sand(self):
        result = calculate_veg_sns("cereals", "light-sand", "low")
        self.assertEqual(result.sns_index, 0)

    def test_low_rainfall_veg_high_n_medium(self):
        result = calculate_veg_sns("veg-high-n", "medium", "low")
        self.assertEqual(result.sns_index, 4)

    def test_low_rainfall_beans_deep_silt(self):
        result = calculate_veg_sns("beans", "deep-silt", "low")
        self.assertEqual(result.sns_index, 3)

    def test_moderate_rainfall_cereals_deep_clay(self):
        result = calculate_veg_sns("cereals", "deep-clay", "moderate")
        self.assertEqual(result.sns_index, 1)

    def test_moderate_rainfall_veg_medium_n_deep_silt(self):
        result = calculate_veg_sns("veg-medium-n", "deep-silt", "moderate")
        self.assertEqual(result.sns_index, 3)

    def test_moderate_rainfall_veg_high_n_deep_clay(self):
        result = calculate_veg_sns("veg-high-n", "deep-clay", "moderate")
        self.assertEqual(result.sns_index, 4)

    def test_high_rainfall_veg_high_n_medium(self):
        result = calculate_veg_sns("veg-high-n", "medium", "high")
        self.assertEqual(result.sns_index, 2)

    def test_high_rainfall_potatoes_deep_silt(self):
        result = calculate_veg_sns("potatoes", "deep-silt", "high")
        self.assertEqual(result.sns_index, 2)

    def test_high_rainfall_uncropped_light_sand(self):
        result = calculate_veg_sns("uncropped", "light-sand", "high")
        self.assertEqual(result.sns_index, 0)

    def test_high_rainfall_veg_low_n_deep_clay(self):
        result = calculate_veg_sns("veg-low-n", "deep-clay", "high")
        self.assertEqual(result.sns_index, 1)

    def test_organic_soil_returns_advisory_index(self):
        result = calculate_veg_sns("cereals", "organic", "moderate")
        self.assertEqual(result.sns_index, 4)
        self.assertTrue(any("FACTS" in n for n in result.notes))

    def test_peat_soil_returns_advisory_index(self):
        result = calculate_veg_sns("cereals", "peat", "low")
        self.assertEqual(result.sns_index, 5)
        self.assertTrue(any("FACTS" in n for n in result.notes))

    def test_invalid_previous_crop_raises(self):
        with self.assertRaises(ValueError):
            calculate_veg_sns("winter-wheat", "medium", "low")

    def test_invalid_soil_type_raises(self):
        with self.assertRaises(ValueError):
            calculate_veg_sns("cereals", "heavy", "low")

    def test_invalid_rainfall_raises(self):
        with self.assertRaises(ValueError):
            calculate_veg_sns("cereals", "medium", "medium")

    def test_method_is_veg_field_assessment(self):
        result = calculate_veg_sns("cereals", "medium", "low")
        self.assertEqual(result.method, "veg-field-assessment")

    def test_result_notes_contain_index(self):
        result = calculate_veg_sns("veg-high-n", "deep-silt", "low")
        self.assertTrue(any("4" in n for n in result.notes))


class TestSMNToSNSIndexVeg(unittest.TestCase):
    """Test smn_to_sns_index_veg() against Table 6.6 boundaries."""

    # Depth 30
    def test_30cm_index0_boundary(self):
        self.assertEqual(smn_to_sns_index_veg(19.9, 30), 0)

    def test_30cm_index1_lower(self):
        self.assertEqual(smn_to_sns_index_veg(20, 30), 1)

    def test_30cm_index1_upper(self):
        self.assertEqual(smn_to_sns_index_veg(27, 30), 1)

    def test_30cm_index2(self):
        self.assertEqual(smn_to_sns_index_veg(28, 30), 2)

    def test_30cm_index3(self):
        self.assertEqual(smn_to_sns_index_veg(34, 30), 3)

    def test_30cm_index4(self):
        self.assertEqual(smn_to_sns_index_veg(41, 30), 4)

    def test_30cm_index5(self):
        self.assertEqual(smn_to_sns_index_veg(54, 30), 5)

    def test_30cm_index6(self):
        self.assertEqual(smn_to_sns_index_veg(81, 30), 6)

    # Depth 60
    def test_60cm_index0(self):
        self.assertEqual(smn_to_sns_index_veg(39.9, 60), 0)

    def test_60cm_index1(self):
        self.assertEqual(smn_to_sns_index_veg(40, 60), 1)

    def test_60cm_index2(self):
        self.assertEqual(smn_to_sns_index_veg(54, 60), 2)

    def test_60cm_index6(self):
        self.assertEqual(smn_to_sns_index_veg(161, 60), 6)

    # Depth 90
    def test_90cm_index0(self):
        self.assertEqual(smn_to_sns_index_veg(59.9, 90), 0)

    def test_90cm_index1(self):
        self.assertEqual(smn_to_sns_index_veg(60, 90), 1)

    def test_90cm_index6(self):
        self.assertEqual(smn_to_sns_index_veg(241, 90), 6)

    def test_invalid_depth_raises(self):
        with self.assertRaises(ValueError):
            smn_to_sns_index_veg(50, 45)

    def test_negative_smn_raises(self):
        with self.assertRaises(ValueError):
            smn_to_sns_index_veg(-1, 30)


class TestNitrogenVeg(unittest.TestCase):
    """One assertion per crop at SNS 0, 2, and 6."""

    def _n(self, crop, sns):
        return recommend_nitrogen(crop, sns)

    def test_asparagus_est(self):
        self.assertEqual(self._n("veg-asparagus-est", 0), 150)
        self.assertEqual(self._n("veg-asparagus-est", 2), 150)
        self.assertEqual(self._n("veg-asparagus-est", 6), 0)

    def test_asparagus(self):
        self.assertEqual(self._n("veg-asparagus", 0), 120)
        self.assertEqual(self._n("veg-asparagus", 6), 120)

    def test_brussels_sprouts(self):
        self.assertEqual(self._n("veg-brussels-sprouts", 0), 330)
        self.assertEqual(self._n("veg-brussels-sprouts", 2), 270)
        self.assertEqual(self._n("veg-brussels-sprouts", 6), 0)

    def test_cabbage_storage(self):
        self.assertEqual(self._n("veg-cabbage-storage", 0), 340)
        self.assertEqual(self._n("veg-cabbage-storage", 6), 0)

    def test_cabbage_head_pre_dec(self):
        self.assertEqual(self._n("veg-cabbage-head-pre-dec", 0), 325)
        self.assertEqual(self._n("veg-cabbage-head-pre-dec", 6), 0)

    def test_cabbage_head_post_dec(self):
        self.assertEqual(self._n("veg-cabbage-head-post-dec", 2), 180)

    def test_collards_pre_dec(self):
        self.assertEqual(self._n("veg-collards-pre-dec", 0), 210)
        self.assertEqual(self._n("veg-collards-pre-dec", 6), 0)

    def test_collards_post_dec(self):
        self.assertEqual(self._n("veg-collards-post-dec", 6), 90)

    def test_cauliflower_summer(self):
        self.assertEqual(self._n("veg-cauliflower-summer", 0), 290)
        self.assertEqual(self._n("veg-cauliflower-summer", 6), 0)

    def test_cauliflower_winter_seedbed(self):
        self.assertEqual(self._n("veg-cauliflower-winter-seedbed", 0), 100)
        self.assertEqual(self._n("veg-cauliflower-winter-seedbed", 6), 0)

    def test_cauliflower_winter_topdress(self):
        self.assertEqual(self._n("veg-cauliflower-winter-topdress", 0), 190)
        self.assertEqual(self._n("veg-cauliflower-winter-topdress", 6), 0)

    def test_calabrese(self):
        self.assertEqual(self._n("veg-calabrese", 0), 235)
        self.assertEqual(self._n("veg-calabrese", 2), 165)

    def test_celery_seedbed(self):
        self.assertEqual(self._n("veg-celery-seedbed", 2), 75)
        self.assertEqual(self._n("veg-celery-seedbed", 6), 0)

    def test_peas_market_zero(self):
        for sns in range(7):
            self.assertEqual(self._n("veg-peas-market", sns), 0)

    def test_beans_broad_zero(self):
        for sns in range(7):
            self.assertEqual(self._n("veg-beans-broad", sns), 0)

    def test_beans_dwarf(self):
        self.assertEqual(self._n("veg-beans-dwarf", 0), 180)
        self.assertEqual(self._n("veg-beans-dwarf", 6), 0)

    def test_radish(self):
        self.assertEqual(self._n("veg-radish", 0), 100)
        self.assertEqual(self._n("veg-radish", 6), 0)

    def test_sweetcorn(self):
        self.assertEqual(self._n("veg-sweetcorn", 0), 220)
        self.assertEqual(self._n("veg-sweetcorn", 6), 0)

    def test_lettuce_whole(self):
        self.assertEqual(self._n("veg-lettuce-whole", 0), 200)
        self.assertEqual(self._n("veg-lettuce-whole", 6), 30)

    def test_lettuce_baby(self):
        self.assertEqual(self._n("veg-lettuce-baby", 0), 60)
        self.assertEqual(self._n("veg-lettuce-baby", 6), 0)

    def test_rocket(self):
        self.assertEqual(self._n("veg-rocket", 2), 100)
        self.assertEqual(self._n("veg-rocket", 6), 0)

    def test_onions_bulb(self):
        self.assertEqual(self._n("veg-onions-bulb", 0), 160)
        self.assertEqual(self._n("veg-onions-bulb", 6), 0)

    def test_onions_salad(self):
        self.assertEqual(self._n("veg-onions-salad", 6), 20)

    def test_leeks(self):
        self.assertEqual(self._n("veg-leeks", 0), 200)
        self.assertEqual(self._n("veg-leeks", 6), 40)

    def test_beetroot(self):
        self.assertEqual(self._n("veg-beetroot", 0), 290)
        self.assertEqual(self._n("veg-beetroot", 6), 60)

    def test_swedes(self):
        self.assertEqual(self._n("veg-swedes", 0), 135)
        self.assertEqual(self._n("veg-swedes", 6), 0)

    def test_turnips_parsnips(self):
        self.assertEqual(self._n("veg-turnips-parsnips", 0), 170)
        self.assertEqual(self._n("veg-turnips-parsnips", 6), 0)

    def test_carrots(self):
        self.assertEqual(self._n("veg-carrots", 0), 100)
        self.assertEqual(self._n("veg-carrots", 6), 0)

    def test_bulbs(self):
        self.assertEqual(self._n("veg-bulbs", 0), 125)
        self.assertEqual(self._n("veg-bulbs", 6), 0)

    def test_coriander(self):
        self.assertEqual(self._n("veg-coriander", 0), 140)
        self.assertEqual(self._n("veg-coriander", 6), 30)

    def test_mint_est(self):
        self.assertEqual(self._n("veg-mint-est", 0), 180)
        self.assertEqual(self._n("veg-mint-est", 6), 70)

    def test_mint(self):
        self.assertEqual(self._n("veg-mint", 0), 180)
        self.assertEqual(self._n("veg-mint", 6), 70)

    def test_courgettes_seedbed(self):
        self.assertEqual(self._n("veg-courgettes-seedbed", 0), 100)
        self.assertEqual(self._n("veg-courgettes-seedbed", 6), 0)


class TestPhosphorusVeg(unittest.TestCase):
    """Spot-check phosphorus for 5 representative crops across P index 0–4."""

    def test_asparagus_est(self):
        self.assertEqual(recommend_phosphorus("veg-asparagus-est", 0), 175)
        self.assertEqual(recommend_phosphorus("veg-asparagus-est", 4), 75)

    def test_brussels_sprouts(self):
        self.assertEqual(recommend_phosphorus("veg-brussels-sprouts", 0), 200)
        self.assertEqual(recommend_phosphorus("veg-brussels-sprouts", 4), 0)

    def test_celery(self):
        self.assertEqual(recommend_phosphorus("veg-celery-seedbed", 0), 250)
        self.assertEqual(recommend_phosphorus("veg-celery-seedbed", 2), 150)
        self.assertEqual(recommend_phosphorus("veg-celery-seedbed", 4), 50)

    def test_lettuce_whole(self):
        self.assertEqual(recommend_phosphorus("veg-lettuce-whole", 0), 250)
        self.assertEqual(recommend_phosphorus("veg-lettuce-whole", 3), 100)
        self.assertEqual(recommend_phosphorus("veg-lettuce-whole", 4), 0)

    def test_carrots(self):
        self.assertEqual(recommend_phosphorus("veg-carrots", 0), 200)
        self.assertEqual(recommend_phosphorus("veg-carrots", 2), 100)
        self.assertEqual(recommend_phosphorus("veg-carrots", 4), 0)

    def test_coriander(self):
        self.assertEqual(recommend_phosphorus("veg-coriander", 0), 175)
        self.assertEqual(recommend_phosphorus("veg-coriander", 2), 75)

    def test_peas_market(self):
        self.assertEqual(recommend_phosphorus("veg-peas-market", 0), 185)
        self.assertEqual(recommend_phosphorus("veg-peas-market", 3), 35)
        self.assertEqual(recommend_phosphorus("veg-peas-market", 4), 0)

    def test_p_index_clamped_above_4(self):
        # Index 9 should clamp to 4
        self.assertEqual(
            recommend_phosphorus("veg-brussels-sprouts", 9),
            recommend_phosphorus("veg-brussels-sprouts", 4),
        )


class TestPotassiumVeg(unittest.TestCase):
    """Test K index 0, 2- (default), 2+ (k_upper_half), and 3 for 5 crops."""

    def test_brussels_sprouts_k_index_2_lower(self):
        self.assertEqual(recommend_potassium("veg-brussels-sprouts", 2), 200)

    def test_brussels_sprouts_k_index_2_upper(self):
        self.assertEqual(recommend_potassium("veg-brussels-sprouts", 2, k_upper_half=True), 150)

    def test_brussels_sprouts_k_index_0(self):
        self.assertEqual(recommend_potassium("veg-brussels-sprouts", 0), 300)

    def test_brussels_sprouts_k_index_3(self):
        self.assertEqual(recommend_potassium("veg-brussels-sprouts", 3), 60)

    def test_celery_k_index_2_lower(self):
        self.assertEqual(recommend_potassium("veg-celery-seedbed", 2), 350)

    def test_celery_k_index_2_upper(self):
        self.assertEqual(recommend_potassium("veg-celery-seedbed", 2, k_upper_half=True), 300)

    def test_lettuce_whole_k_index_2_lower(self):
        self.assertEqual(recommend_potassium("veg-lettuce-whole", 2), 150)

    def test_lettuce_whole_k_index_2_upper(self):
        self.assertEqual(recommend_potassium("veg-lettuce-whole", 2, k_upper_half=True), 100)

    def test_onions_bulb_k_index_0(self):
        self.assertEqual(recommend_potassium("veg-onions-bulb", 0), 275)

    def test_onions_bulb_k_index_2_lower(self):
        self.assertEqual(recommend_potassium("veg-onions-bulb", 2), 175)

    def test_onions_bulb_k_index_2_upper(self):
        self.assertEqual(recommend_potassium("veg-onions-bulb", 2, k_upper_half=True), 125)

    def test_asparagus_est_no_split(self):
        # asparagus-est has no documented 2+/2- split — k_upper_half uses 2- value
        self.assertEqual(recommend_potassium("veg-asparagus-est", 2), 200)
        self.assertEqual(recommend_potassium("veg-asparagus-est", 2, k_upper_half=True), 200)

    def test_coriander_k_index_2_upper(self):
        self.assertEqual(recommend_potassium("veg-coriander", 2, k_upper_half=True), 165)

    def test_k_index_clamped_above_4(self):
        self.assertEqual(
            recommend_potassium("veg-lettuce-whole", 9),
            recommend_potassium("veg-lettuce-whole", 4),
        )


class TestMagnesiumVeg(unittest.TestCase):
    """Vegetable crops must return 150/100 at Mg index 0/1, not arable 90/60."""

    def test_veg_mg_index_0(self):
        self.assertEqual(recommend_magnesium(0, crop="veg-brussels-sprouts"), 150)

    def test_veg_mg_index_1(self):
        self.assertEqual(recommend_magnesium(1, crop="veg-carrots"), 100)

    def test_veg_mg_index_2_is_zero(self):
        self.assertEqual(recommend_magnesium(2, crop="veg-leeks"), 0)

    def test_arable_mg_index_0_unchanged(self):
        self.assertEqual(recommend_magnesium(0, crop="winter-wheat-feed"), 90)

    def test_arable_mg_index_1_unchanged(self):
        self.assertEqual(recommend_magnesium(1, crop="winter-wheat-feed"), 60)

    def test_no_crop_returns_arable_rates(self):
        self.assertEqual(recommend_magnesium(0), 90)
        self.assertEqual(recommend_magnesium(1), 60)


class TestSulfurVeg(unittest.TestCase):
    """Brassicas 50, other veg 25, N-fixing 0."""

    def test_brassica_brussels(self):
        self.assertEqual(recommend_sulfur("veg-brussels-sprouts"), 50)

    def test_brassica_cauliflower(self):
        self.assertEqual(recommend_sulfur("veg-cauliflower-summer"), 50)

    def test_brassica_swedes(self):
        self.assertEqual(recommend_sulfur("veg-swedes"), 50)

    def test_brassica_turnips(self):
        self.assertEqual(recommend_sulfur("veg-turnips-parsnips"), 50)

    def test_other_veg_lettuce(self):
        self.assertEqual(recommend_sulfur("veg-lettuce-whole"), 25)

    def test_other_veg_onions(self):
        self.assertEqual(recommend_sulfur("veg-onions-bulb"), 25)

    def test_other_veg_leeks(self):
        self.assertEqual(recommend_sulfur("veg-leeks"), 25)

    def test_other_veg_carrots(self):
        self.assertEqual(recommend_sulfur("veg-carrots"), 25)

    def test_n_fixing_peas(self):
        self.assertEqual(recommend_sulfur("veg-peas-market"), 0)

    def test_n_fixing_beans_broad(self):
        self.assertEqual(recommend_sulfur("veg-beans-broad"), 0)

    def test_n_fixing_beans_dwarf(self):
        self.assertEqual(recommend_sulfur("veg-beans-dwarf"), 0)


class TestEngineIntegrationVeg(unittest.TestCase):
    """Integration tests: recommend_all() for 6 representative vegetable crops."""

    def test_brussels_sprouts_sns1_p2_k1(self):
        rec = recommend_all("veg-brussels-sprouts", sns_index=1, p_index=2, k_index=1)
        self.assertEqual(rec.nitrogen, 300)
        self.assertEqual(rec.phosphorus, 100)
        self.assertEqual(rec.potassium, 250)
        self.assertEqual(rec.magnesium, 0)   # Mg index defaults to 2
        self.assertEqual(rec.sulfur, 50)

    def test_carrots_sns2_p1_k2_mg0(self):
        rec = recommend_all("veg-carrots", sns_index=2, p_index=1, k_index=2, mg_index=0)
        self.assertEqual(rec.nitrogen, 40)
        self.assertEqual(rec.phosphorus, 150)
        self.assertEqual(rec.potassium, 175)
        self.assertEqual(rec.magnesium, 150)  # vegetable Mg rate at index 0
        self.assertEqual(rec.sulfur, 25)

    def test_peas_market_zero_n(self):
        rec = recommend_all("veg-peas-market", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 0)
        self.assertTrue(any("N-fixing" in n for n in rec.notes))

    def test_leeks_nvz_note(self):
        rec = recommend_all("veg-leeks", sns_index=0, p_index=2, k_index=2)
        self.assertTrue(any("NVZ" in n for n in rec.notes))

    def test_celery_topdress_note(self):
        rec = recommend_all("veg-celery-seedbed", sns_index=0, p_index=2, k_index=1)
        self.assertTrue(any("top dressing" in n for n in rec.notes))

    def test_lettuce_whole_nitrate_note(self):
        rec = recommend_all("veg-lettuce-whole", sns_index=1, p_index=2, k_index=1)
        self.assertTrue(any("nitrate" in n.lower() for n in rec.notes))

    def test_asparagus_year2_note(self):
        rec = recommend_all("veg-asparagus", sns_index=1, p_index=2, k_index=1)
        self.assertTrue(any("Year 2" in n for n in rec.notes))

    def test_k2_upper_half_note_when_k_index_2(self):
        rec = recommend_all("veg-beetroot", sns_index=1, p_index=2, k_index=2)
        self.assertTrue(any("2+" in n or "2-" in n for n in rec.notes))

    def test_k2_upper_half_flag_changes_potassium(self):
        rec_lower = recommend_all("veg-beetroot", sns_index=1, p_index=2, k_index=2)
        rec_upper = recommend_all("veg-beetroot", sns_index=1, p_index=2, k_index=2, k_upper_half=True)
        self.assertGreater(rec_lower.potassium, rec_upper.potassium)


class TestAdvisoryNotesVeg(unittest.TestCase):
    """Verify specific advisory note content."""

    def test_lettuce_whole_nitrate_warning(self):
        rec = recommend_all("veg-lettuce-whole", sns_index=0, p_index=1, k_index=1)
        self.assertTrue(any("nitrate" in n.lower() for n in rec.notes))

    def test_leeks_nvz_closed_period(self):
        rec = recommend_all("veg-leeks", sns_index=2, p_index=2, k_index=2)
        self.assertTrue(any("NVZ" in n for n in rec.notes))

    def test_celery_topdress_reminder(self):
        rec = recommend_all("veg-celery-seedbed", sns_index=1, p_index=1, k_index=1)
        self.assertTrue(any("top dressing" in n for n in rec.notes))

    def test_asparagus_year_timing_note(self):
        rec = recommend_all("veg-asparagus", sns_index=0, p_index=1, k_index=1)
        self.assertTrue(any("Year 2" in n for n in rec.notes))

    def test_seedbed_cap_radish(self):
        rec = recommend_all("veg-radish", sns_index=0, p_index=1, k_index=1)
        self.assertTrue(any("100 kg N/ha in the seedbed" in n for n in rec.notes))

    def test_seedbed_cap_carrots(self):
        rec = recommend_all("veg-carrots", sns_index=0, p_index=1, k_index=1)
        self.assertTrue(any("100 kg N/ha in the seedbed" in n for n in rec.notes))


class TestErrorHandlingVeg(unittest.TestCase):
    """Error handling consistent with existing test patterns."""

    def test_unknown_veg_crop_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("veg-unknown-crop", 0)

    def test_sns_index_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("veg-carrots", 7)

    def test_negative_sns_index_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("veg-leeks", -1)

    def test_p_index_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            recommend_phosphorus("veg-carrots", 10)

    def test_k_index_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            recommend_potassium("veg-carrots", 10)


class TestCourgettesTopdress(unittest.TestCase):
    """Tests for the veg-courgettes-topdress crop slug."""

    def test_n_sns0(self):
        self.assertEqual(recommend_nitrogen("veg-courgettes-topdress", 0), 75)

    def test_n_sns3(self):
        self.assertEqual(recommend_nitrogen("veg-courgettes-topdress", 3), 75)

    def test_n_sns4_zero(self):
        self.assertEqual(recommend_nitrogen("veg-courgettes-topdress", 4), 0)

    def test_n_sns6_zero(self):
        self.assertEqual(recommend_nitrogen("veg-courgettes-topdress", 6), 0)

    def test_p_all_zero(self):
        for idx in range(5):
            self.assertEqual(recommend_phosphorus("veg-courgettes-topdress", idx), 0)

    def test_k_all_zero(self):
        for idx in range(5):
            self.assertEqual(recommend_potassium("veg-courgettes-topdress", idx), 0)

    def test_sulfur_zero(self):
        self.assertEqual(recommend_sulfur("veg-courgettes-topdress"), 0)

    def test_recommend_all_n_only(self):
        rec = recommend_all("veg-courgettes-topdress", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 75)
        self.assertEqual(rec.phosphorus, 0)
        self.assertEqual(rec.potassium, 0)


class TestVegNitrogenTiming(unittest.TestCase):
    """Nitrogen timing rules for vegetable crops."""

    def setUp(self):
        from rb209.engine import nitrogen_timing as _nt
        self._nt = _nt

    # ── Asparagus establishment ──────────────────────────────────────────────

    def test_asparagus_est_three_splits(self):
        r = self._nt("veg-asparagus-est", 150)
        self.assertEqual(len(r.splits), 3)

    def test_asparagus_est_equal_thirds(self):
        r = self._nt("veg-asparagus-est", 150)
        self.assertEqual(r.splits[0].amount, 50)
        self.assertEqual(r.splits[1].amount, 50)
        self.assertEqual(r.splits[2].amount, 50)

    def test_asparagus_est_amounts_sum_to_total(self):
        for total in [90, 120, 150]:
            r = self._nt("veg-asparagus-est", total)
            self.assertEqual(sum(s.amount for s in r.splits), total)

    def test_asparagus_est_timing_labels(self):
        r = self._nt("veg-asparagus-est", 90)
        self.assertIn("Before sowing", r.splits[0].timing)
        self.assertIn("established", r.splits[1].timing)
        self.assertIn("August", r.splits[2].timing)

    # ── Asparagus subsequent years ───────────────────────────────────────────

    def test_asparagus_single_dressing(self):
        r = self._nt("veg-asparagus", 120)
        self.assertEqual(len(r.splits), 1)
        self.assertEqual(r.splits[0].amount, 120)
        self.assertIn("February", r.splits[0].timing)

    def test_asparagus_year3_note(self):
        r = self._nt("veg-asparagus", 120)
        self.assertTrue(any("year 3" in n.lower() or "Year 3" in n for n in r.notes))

    # ── Seedbed-cap brassicas ────────────────────────────────────────────────

    def test_brussels_low_n_single_dressing(self):
        r = self._nt("veg-brussels-sprouts", 80)
        self.assertEqual(len(r.splits), 1)
        self.assertEqual(r.splits[0].amount, 80)

    def test_brussels_100_single_dressing(self):
        r = self._nt("veg-brussels-sprouts", 100)
        self.assertEqual(len(r.splits), 1)

    def test_brussels_high_n_two_splits(self):
        r = self._nt("veg-brussels-sprouts", 270)
        self.assertEqual(len(r.splits), 2)

    def test_brussels_high_n_seedbed_capped_at_100(self):
        r = self._nt("veg-brussels-sprouts", 270)
        self.assertEqual(r.splits[0].amount, 100)

    def test_brussels_high_n_topdress_is_remainder(self):
        r = self._nt("veg-brussels-sprouts", 270)
        self.assertEqual(r.splits[1].amount, 170)

    def test_brussels_amounts_sum_to_total(self):
        for total in [80, 100, 200, 330]:
            r = self._nt("veg-brussels-sprouts", total)
            self.assertEqual(sum(s.amount for s in r.splits), total)

    def test_fixed_amount_total_less_than_cap(self):
        # When total N < 100, the seedbed cap should not produce a negative topdress.
        r = self._nt("veg-sweetcorn", 75)
        self.assertEqual(len(r.splits), 1)
        self.assertEqual(r.splits[0].amount, 75)

    def test_seedbed_cap_exact_100(self):
        r = self._nt("veg-carrots", 100)
        self.assertEqual(len(r.splits), 1)
        self.assertEqual(r.splits[0].amount, 100)

    def test_seedbed_cap_101(self):
        # 101 kg/ha should produce 100 seedbed + 1 topdress.
        r = self._nt("veg-beetroot", 101)
        self.assertEqual(len(r.splits), 2)
        self.assertEqual(r.splits[0].amount, 100)
        self.assertEqual(r.splits[1].amount, 1)

    # ── Cauliflower winter split slugs ───────────────────────────────────────

    def test_cauliflower_winter_seedbed_single(self):
        r = self._nt("veg-cauliflower-winter-seedbed", 100)
        self.assertEqual(len(r.splits), 1)
        self.assertIn("seedbed", r.splits[0].timing.lower())

    def test_cauliflower_winter_topdress_single(self):
        r = self._nt("veg-cauliflower-winter-topdress", 190)
        self.assertEqual(len(r.splits), 1)
        self.assertIn("top dressing", r.splits[0].timing.lower())

    # ── Celery ───────────────────────────────────────────────────────────────

    def test_celery_seedbed_has_topdress_note(self):
        r = self._nt("veg-celery-seedbed", 75)
        self.assertTrue(any("top" in n.lower() for n in r.notes))

    # ── Bulbs ────────────────────────────────────────────────────────────────

    def test_bulbs_single_before_emergence(self):
        r = self._nt("veg-bulbs", 125)
        self.assertEqual(len(r.splits), 1)
        self.assertIn("emergence", r.splits[0].timing.lower())

    # ── Onions ───────────────────────────────────────────────────────────────

    def test_onions_bulb_low_n_single(self):
        r = self._nt("veg-onions-bulb", 90)
        self.assertEqual(len(r.splits), 1)

    def test_onions_bulb_high_n_two_splits(self):
        r = self._nt("veg-onions-bulb", 160)
        self.assertEqual(len(r.splits), 2)
        self.assertEqual(r.splits[0].amount, 100)

    def test_onions_salad_single(self):
        r = self._nt("veg-onions-salad", 130)
        self.assertEqual(len(r.splits), 1)

    # ── Leeks ────────────────────────────────────────────────────────────────

    def test_leeks_high_n_nvz_note(self):
        r = self._nt("veg-leeks", 200)
        self.assertTrue(any("NVZ" in n for n in r.notes))

    def test_leeks_low_n_single(self):
        r = self._nt("veg-leeks", 80)
        self.assertEqual(len(r.splits), 1)

    # ── Lettuce/rocket ───────────────────────────────────────────────────────

    def test_lettuce_single_with_nitrate_note(self):
        r = self._nt("veg-lettuce-whole", 200)
        self.assertEqual(len(r.splits), 1)
        self.assertTrue(any("nitrate" in n.lower() for n in r.notes))

    def test_rocket_single_with_nitrate_note(self):
        r = self._nt("veg-rocket", 100)
        self.assertEqual(len(r.splits), 1)
        self.assertTrue(any("nitrate" in n.lower() for n in r.notes))

    # ── N-fixing crops ───────────────────────────────────────────────────────

    def test_peas_timing_not_applicable(self):
        r = self._nt("veg-peas-market", 0)
        self.assertIn("not applicable", r.splits[0].timing.lower())

    def test_beans_broad_timing_not_applicable(self):
        r = self._nt("veg-beans-broad", 0)
        self.assertIn("not applicable", r.splits[0].timing.lower())


if __name__ == "__main__":
    unittest.main()
