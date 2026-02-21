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


if __name__ == "__main__":
    unittest.main()
