"""Tests for the recommendation engine."""

import unittest

from rb209.engine import (
    calculate_lime,
    recommend_all,
    recommend_magnesium,
    recommend_nitrogen,
    recommend_phosphorus,
    recommend_potassium,
    recommend_sulfur,
)


class TestNitrogen(unittest.TestCase):
    def test_winter_wheat_feed_sns0(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 0), 220)

    def test_winter_wheat_feed_sns2(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 2), 150)

    def test_winter_wheat_feed_sns6(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 6), 0)

    def test_winter_wheat_milling_higher_than_feed(self):
        feed = recommend_nitrogen("winter-wheat-feed", 2)
        milling = recommend_nitrogen("winter-wheat-milling", 2)
        self.assertGreater(milling, feed)

    def test_potatoes_maincrop_sns0(self):
        self.assertEqual(recommend_nitrogen("potatoes-maincrop", 0), 270)

    def test_peas_always_zero(self):
        for sns in range(7):
            self.assertEqual(recommend_nitrogen("peas", sns), 0)

    def test_grass_silage_sns0(self):
        self.assertEqual(recommend_nitrogen("grass-silage", 0), 320)

    def test_invalid_crop_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("not-a-crop", 2)

    def test_invalid_sns_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", 7)

    def test_negative_sns_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", -1)

    def test_soil_specific_medium(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 4, soil_type="medium"), 120)

    def test_soil_specific_light(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 4, soil_type="light"), 60)

    def test_soil_specific_heavy(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 4, soil_type="heavy"), 120)

    def test_soil_specific_organic(self):
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 4, soil_type="organic"), 80)

    def test_without_soil_type_uses_generic(self):
        # Existing behavior unchanged when soil_type is omitted
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 0), 220)

    def test_invalid_soil_type_raises(self):
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", 2, soil_type="volcanic")

    def test_soil_specific_no_data_falls_back_to_generic(self):
        # Organic soil at SNS 0 has no data (dash in Table 4.17); falls back to generic
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 0, soil_type="organic"), 220)

    def test_soil_specific_crop_without_table_falls_back_to_generic(self):
        # Spring barley has no soil-specific table; falls back to generic recommendation
        self.assertEqual(recommend_nitrogen("spring-barley", 2, soil_type="medium"), 100)

    def test_bool_true_sns_raises(self):
        # bool is a subclass of int; True == 1 but must be rejected
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", True)

    def test_bool_false_sns_raises(self):
        # False == 0 but must be rejected
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", False)


class TestValidateIndex(unittest.TestCase):
    """Ensure _validate_index rejects bool values across all index parameters."""

    def test_phosphorus_bool_raises(self):
        with self.assertRaises(ValueError):
            recommend_phosphorus("winter-wheat-feed", True)

    def test_potassium_bool_raises(self):
        with self.assertRaises(ValueError):
            recommend_potassium("winter-wheat-feed", True)

    def test_magnesium_bool_raises(self):
        with self.assertRaises(ValueError):
            recommend_magnesium(True)


class TestPhosphorus(unittest.TestCase):
    def test_cereals_p0(self):
        self.assertEqual(recommend_phosphorus("winter-wheat-feed", 0), 110)

    def test_cereals_p4(self):
        self.assertEqual(recommend_phosphorus("winter-wheat-feed", 4), 0)

    def test_potatoes_maincrop_p0(self):
        self.assertEqual(recommend_phosphorus("potatoes-maincrop", 0), 250)

    def test_high_p_index_clamped(self):
        # Index 7 should be clamped to 4 and return 0
        self.assertEqual(recommend_phosphorus("winter-wheat-feed", 7), 0)

    def test_grass_grazed_p0(self):
        self.assertEqual(recommend_phosphorus("grass-grazed", 0), 80)


class TestPotassium(unittest.TestCase):
    def test_cereals_straw_removed_k0(self):
        self.assertEqual(recommend_potassium("winter-wheat-feed", 0, straw_removed=True), 105)

    def test_cereals_straw_incorporated_k0(self):
        self.assertEqual(recommend_potassium("winter-wheat-feed", 0, straw_removed=False), 65)

    def test_sugar_beet_k0(self):
        self.assertEqual(recommend_potassium("sugar-beet", 0), 175)

    def test_potatoes_k0(self):
        self.assertEqual(recommend_potassium("potatoes-maincrop", 0), 300)

    def test_high_k_index_clamped(self):
        self.assertEqual(recommend_potassium("sugar-beet", 8), 0)


class TestMagnesium(unittest.TestCase):
    def test_mg0(self):
        self.assertEqual(recommend_magnesium(0), 90)

    def test_mg1(self):
        self.assertEqual(recommend_magnesium(1), 60)

    def test_mg2(self):
        self.assertEqual(recommend_magnesium(2), 0)

    def test_high_mg_clamped(self):
        self.assertEqual(recommend_magnesium(7), 0)


class TestSulfur(unittest.TestCase):
    def test_osr_highest(self):
        self.assertEqual(recommend_sulfur("winter-oilseed-rape"), 75)

    def test_peas_zero(self):
        self.assertEqual(recommend_sulfur("peas"), 0)

    def test_winter_wheat_feed(self):
        self.assertEqual(recommend_sulfur("winter-wheat-feed"), 30)


class TestRecommendAll(unittest.TestCase):
    def test_returns_all_nutrients(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, 1)
        self.assertEqual(rec.nitrogen, 150)
        self.assertEqual(rec.phosphorus, 60)
        self.assertEqual(rec.potassium, 75)  # straw removed default
        self.assertEqual(rec.magnesium, 60)
        self.assertEqual(rec.sulfur, 30)

    def test_crop_name_populated(self):
        rec = recommend_all("spring-barley", 1, 1, 1)
        self.assertEqual(rec.crop, "Spring Barley")

    def test_straw_note_present(self):
        rec = recommend_all("winter-wheat-feed", 0, 0, 0)
        self.assertTrue(any("straw" in n.lower() for n in rec.notes))


class TestCalculateLime(unittest.TestCase):
    # ── explicit target_ph (existing behaviour) ──────────────────────
    def test_explicit_target_ph(self):
        result = calculate_lime(5.8, 6.5, "medium")
        self.assertAlmostEqual(result.lime_required, 3.9)
        self.assertEqual(result.target_ph, 6.5)

    def test_no_lime_needed(self):
        result = calculate_lime(7.0, 6.5, "medium")
        self.assertEqual(result.lime_required, 0.0)
        self.assertTrue(any("No lime" in n for n in result.notes))

    def test_split_dressing_note(self):
        result = calculate_lime(4.5, 7.5, "heavy")
        self.assertAlmostEqual(result.lime_required, 22.5)
        self.assertTrue(any("split" in n.lower() for n in result.notes))

    # ── land_use auto-defaults (new behaviour) ────────────────────────
    def test_land_use_arable_defaults_to_6_5(self):
        # No target_ph — should derive 6.5 for arable
        result = calculate_lime(5.8, None, "medium", land_use="arable")
        self.assertAlmostEqual(result.target_ph, 6.5)
        self.assertAlmostEqual(result.lime_required, 3.9)

    def test_land_use_grassland_defaults_to_6_0(self):
        result = calculate_lime(5.5, None, "medium", land_use="grassland")
        self.assertAlmostEqual(result.target_ph, 6.0)
        # (6.0 - 5.5) * 5.5 = 2.75, rounded to 1dp via Python = 2.8
        self.assertAlmostEqual(result.lime_required, 2.8)

    def test_explicit_target_ph_overrides_land_use(self):
        # target_ph=5.5 supplied alongside land_use; explicit value wins
        result = calculate_lime(5.0, 5.5, "light", land_use="arable")
        self.assertAlmostEqual(result.target_ph, 5.5)
        self.assertAlmostEqual(result.lime_required, 2.0)

    def test_neither_target_ph_nor_land_use_raises(self):
        with self.assertRaises(ValueError, msg="Should raise when both are None"):
            calculate_lime(5.8, None, "medium")

    def test_invalid_land_use_raises(self):
        with self.assertRaises(ValueError):
            calculate_lime(5.8, None, "medium", land_use="orchard")

    # ── MIN_PH_FOR_LIMING warning ─────────────────────────────────────
    def test_very_acidic_ph_adds_warning_note(self):
        # pH 4.5 is below MIN_PH_FOR_LIMING (5.0)
        result = calculate_lime(4.5, 6.5, "medium")
        self.assertTrue(
            any("very acidic" in n.lower() or "strongly recommended" in n.lower()
                for n in result.notes)
        )

    def test_ph_at_threshold_no_warning(self):
        # pH exactly at 5.0 should NOT trigger the warning
        result = calculate_lime(5.0, 6.5, "medium")
        self.assertFalse(
            any("very acidic" in n.lower() for n in result.notes)
        )

    def test_ph_above_threshold_no_warning(self):
        result = calculate_lime(5.5, 6.5, "medium")
        self.assertFalse(
            any("very acidic" in n.lower() for n in result.notes)
        )

    def test_very_acidic_with_land_use_auto_default(self):
        # Combined: land_use auto-default + very-acidic warning
        result = calculate_lime(4.2, None, "light", land_use="arable")
        self.assertAlmostEqual(result.target_ph, 6.5)
        self.assertTrue(
            any("very acidic" in n.lower() or "strongly recommended" in n.lower()
                for n in result.notes)
        )


class TestNVZWarnings(unittest.TestCase):
    def test_nvz_warning_when_n_exceeds_limit(self):
        # N = 220, threshold = 220 — at limit, not over; no warning
        rec = recommend_all("winter-wheat-feed", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 220)
        self.assertFalse(any("NVZ" in n or "N-max" in n for n in rec.notes))

    def test_nvz_warning_when_n_exceeds_limit_soil_specific(self):
        # N = 250 (medium soil-specific), threshold = 220 — warning present
        rec = recommend_all(
            "winter-wheat-feed", sns_index=0, p_index=2, k_index=2, soil_type="medium"
        )
        self.assertEqual(rec.nitrogen, 250)
        self.assertTrue(any("N-max" in n for n in rec.notes))

    def test_nvz_no_warning_when_under_limit(self):
        # N = 120 < 220 — no NVZ note
        rec = recommend_all("winter-wheat-feed", sns_index=3, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 120)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_no_warning_for_crop_without_limit(self):
        # linseed has no NVZ_NMAX entry — no warning expected
        rec = recommend_all("linseed", sns_index=0, p_index=2, k_index=2)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_no_warning_sugar_beet_at_limit(self):
        # sugar-beet NVZ limit is 120; recommendation at SNS 0 is also 120 → no warning
        rec = recommend_all("sugar-beet", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 120)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_warning_text_contains_values(self):
        # Warning text should contain recommendation (250) and limit (220) as integers
        rec = recommend_all(
            "winter-wheat-feed", sns_index=0, p_index=2, k_index=2, soil_type="medium"
        )
        nvz_notes = [n for n in rec.notes if "N-max" in n]
        self.assertTrue(len(nvz_notes) > 0)
        note = nvz_notes[0]
        self.assertIn("250", note)
        self.assertIn("220", note)

    def test_nvz_spring_wheat_limit_180(self):
        # spring-wheat SNS 0 = 160 kg/ha < 180 limit — no warning
        rec = recommend_all("spring-wheat", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 160)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_spring_barley_warning_at_sns0(self):
        # spring-barley SNS 0 = 160 kg/ha > 150 limit — warning expected
        rec = recommend_all("spring-barley", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 160)
        self.assertTrue(any("N-max" in n for n in rec.notes))

    def test_nvz_spring_barley_no_warning_at_sns1(self):
        # spring-barley SNS 1 = 120 kg/ha < 150 limit — no warning
        rec = recommend_all("spring-barley", sns_index=1, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 120)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_milling_wheat_limit_260(self):
        # winter-wheat-milling SNS 0 = 260 kg/ha, limit 260 — at limit, no warning
        rec = recommend_all("winter-wheat-milling", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 260)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_forage_maize_limit_150(self):
        # forage-maize SNS 0 = 150, limit 150 — at limit, no warning
        rec = recommend_all("forage-maize", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 150)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_veg_group1_carrots_limit_180(self):
        # veg-carrots SNS 0 = 100 kg/ha < 180 limit — no warning
        rec = recommend_all("veg-carrots", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 100)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_veg_group2_sweetcorn_limit_280(self):
        # veg-sweetcorn SNS 0 = 220 kg/ha < 280 limit — no warning
        rec = recommend_all("veg-sweetcorn", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 220)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_veg_group3_brussels_sprouts_limit_370(self):
        # veg-brussels-sprouts SNS 0 = 330 kg/ha < 370 limit — no warning
        rec = recommend_all("veg-brussels-sprouts", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 330)
        self.assertFalse(any("N-max" in n for n in rec.notes))

    def test_nvz_grass_silage_limit_340(self):
        # grass-silage SNS 0 = 320 kg/ha < 340 limit — no warning
        rec = recommend_all("grass-silage", sns_index=0, p_index=2, k_index=2)
        self.assertEqual(rec.nitrogen, 320)
        self.assertFalse(any("N-max" in n for n in rec.notes))


class TestPotashSplitWarnings(unittest.TestCase):
    # 1.2 Potatoes split warnings
    def test_potash_split_note_for_potatoes_above_300(self):
        # K2O = 300 at k_index=0; threshold is >300 so no note
        rec = recommend_all("potatoes-maincrop", 2, 2, 0)
        self.assertEqual(rec.potassium, 300)
        self.assertFalse(any("split" in n.lower() for n in rec.notes))

    def test_potash_split_note_not_present_at_300(self):
        # Same: K2O = 300 exactly; assert no "split" note
        rec = recommend_all("potatoes-maincrop", 2, 2, 0)
        self.assertFalse(any("split" in n.lower() for n in rec.notes))

    def test_potash_split_note_not_for_cereals(self):
        # Cereals never get a potash split note regardless of K level
        rec = recommend_all("winter-wheat-feed", 2, 2, 0)
        self.assertEqual(rec.potassium, 105)
        self.assertFalse(
            any("autumn/winter" in n and "spring" in n for n in rec.notes)
        )

    def test_potash_no_split_for_low_k(self):
        # potatoes-early at k_index=2 → K2O = 150; no split note
        rec = recommend_all("potatoes-early", 2, 2, 2)
        self.assertEqual(rec.potassium, 150)
        self.assertFalse(any("autumn/winter" in n for n in rec.notes))

    # 1.3 Grass silage luxury uptake warnings
    def test_grass_silage_potash_split_note_at_k0(self):
        # K2O = 150 > 90 → luxury uptake note
        rec = recommend_all("grass-silage", 2, 2, 0)
        self.assertEqual(rec.potassium, 150)
        self.assertTrue(any("luxury uptake" in n for n in rec.notes))

    def test_grass_silage_no_potash_note_at_k2(self):
        # K2O = 60 ≤ 90 → no luxury uptake note
        rec = recommend_all("grass-silage", 2, 2, 2)
        self.assertEqual(rec.potassium, 60)
        self.assertFalse(any("luxury uptake" in n for n in rec.notes))

    def test_potash_luxury_note_not_for_grazed_grass(self):
        # grass-grazed at k_index=0 → K2O = 60; no luxury-uptake note
        rec = recommend_all("grass-grazed", 2, 2, 0)
        self.assertEqual(rec.potassium, 60)
        self.assertFalse(any("luxury uptake" in n for n in rec.notes))


class TestCalculateLimePotato(unittest.TestCase):
    """Tests for 1.4 lime-before-potatoes warning."""

    def test_lime_potato_scab_warning(self):
        result = calculate_lime(5.5, 6.5, "medium", crop="potatoes-maincrop")
        self.assertGreater(result.lime_required, 0)
        self.assertTrue(any("common scab" in n for n in result.notes))

    def test_lime_no_potato_warning_when_no_lime_needed(self):
        result = calculate_lime(7.0, 6.5, "medium", crop="potatoes-maincrop")
        self.assertEqual(result.lime_required, 0.0)
        self.assertFalse(any("common scab" in n for n in result.notes))

    def test_lime_no_potato_warning_for_cereals(self):
        result = calculate_lime(5.5, 6.5, "medium", crop="winter-wheat-feed")
        self.assertFalse(any("common scab" in n for n in result.notes))

    def test_lime_no_potato_warning_when_no_crop(self):
        result = calculate_lime(5.5, 6.5, "medium")
        self.assertFalse(any("common scab" in n for n in result.notes))


class TestCalculateLimeOverliming(unittest.TestCase):
    """Tests for 1.5 over-liming trace element warnings."""

    def test_overlime_grassland_ph7_warning(self):
        result = calculate_lime(6.5, 7.5, "medium", land_use="grassland")
        self.assertTrue(any("copper, cobalt" in n for n in result.notes))

    def test_overlime_no_warning_arable_ph7(self):
        result = calculate_lime(6.5, 7.5, "medium", land_use="arable")
        self.assertFalse(any("copper, cobalt" in n for n in result.notes))

    def test_overlime_mn_warning_above_7_5(self):
        result = calculate_lime(7.0, 8.0, "medium")
        self.assertTrue(any("Manganese" in n for n in result.notes))

    def test_overlime_sandy_mn_warning_above_6_5(self):
        result = calculate_lime(6.0, 7.0, "light")
        combined = " ".join(result.notes)
        self.assertIn("sandy", combined)
        self.assertIn("manganese", combined.lower())

    def test_overlime_organic_mn_warning_above_6_0(self):
        result = calculate_lime(5.5, 6.5, "organic")
        combined = " ".join(result.notes)
        self.assertTrue("organic" in combined.lower() or "peaty" in combined.lower())
        self.assertIn("manganese", combined.lower())

    def test_no_overlime_warning_when_no_lime_needed(self):
        result = calculate_lime(7.0, 6.5, "medium")
        self.assertEqual(result.lime_required, 0.0)
        # No over-liming notes (lime_needed path not reached)
        self.assertFalse(any("copper" in n or "Manganese" in n or "sandy" in n
                              for n in result.notes))


class TestHypomagnesaemiaWarning(unittest.TestCase):
    def test_hypomagnesaemia_warning_grass_grazed_mg0(self):
        # k_index=0 → K2O = 60 > 0; mg_index=0; grassland → warning
        rec = recommend_all("grass-grazed", 2, 2, 0, mg_index=0)
        self.assertGreater(rec.potassium, 0)
        self.assertTrue(any("hypomagnesaemia" in n for n in rec.notes))

    def test_no_hypomagnesaemia_warning_mg2(self):
        rec = recommend_all("grass-grazed", 2, 2, 0, mg_index=2)
        self.assertFalse(any("hypomagnesaemia" in n for n in rec.notes))

    def test_no_hypomagnesaemia_warning_arable(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 0, mg_index=0)
        self.assertFalse(any("hypomagnesaemia" in n for n in rec.notes))

    def test_no_hypomagnesaemia_warning_k_zero(self):
        # k_index=3 → K2O = 0; condition k > 0 is False
        rec = recommend_all("grass-grazed", 2, 2, 3, mg_index=0)
        self.assertEqual(rec.potassium, 0)
        self.assertFalse(any("hypomagnesaemia" in n for n in rec.notes))


class TestCloverWarning(unittest.TestCase):
    def test_clover_warning_grass_grazed_with_n(self):
        # sns_index=2 → N = 180 > 0; clover_risk → warning
        rec = recommend_all("grass-grazed", 2, 2, 2)
        self.assertGreater(rec.nitrogen, 0)
        self.assertTrue(any("clover" in n for n in rec.notes))

    def test_clover_warning_not_shown_when_n_zero(self):
        # sns_index=6 → N = 0; no clover warning
        rec = recommend_all("grass-grazed", 6, 2, 2)
        self.assertEqual(rec.nitrogen, 0)
        self.assertFalse(any("clover" in n for n in rec.notes))

    def test_clover_warning_not_shown_for_arable(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 2)
        self.assertFalse(any("clover" in n for n in rec.notes))


class TestCombineDrillWarning(unittest.TestCase):
    def test_combine_drill_warning_light_soil_high_nk(self):
        # N=180 (light soil), K=105 (k_index=0 straw removed), total=285 > 150
        rec = recommend_all("winter-wheat-feed", 0, 2, 0, soil_type="light")
        self.assertEqual(rec.nitrogen, 180)
        self.assertEqual(rec.potassium, 105)
        self.assertTrue(any("combine-drill" in n for n in rec.notes))

    def test_no_combine_drill_warning_medium_soil(self):
        rec = recommend_all("winter-wheat-feed", 0, 2, 0, soil_type="medium")
        self.assertFalse(any("combine-drill" in n for n in rec.notes))

    def test_no_combine_drill_warning_low_nk(self):
        # N=60 (light, sns=4), K=0 (k_index=3); total=60 ≤ 150
        rec = recommend_all("winter-wheat-feed", 4, 2, 3, soil_type="light")
        self.assertEqual(rec.potassium, 0)
        self.assertFalse(any("combine-drill" in n for n in rec.notes))

    def test_no_combine_drill_warning_grassland(self):
        # grass-silage is not arable → no combine-drill warning
        rec = recommend_all("grass-silage", 0, 2, 0, soil_type="light")
        self.assertFalse(any("combine-drill" in n for n in rec.notes))


if __name__ == "__main__":
    unittest.main()
