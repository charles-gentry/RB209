"""Tests for the recommendation engine."""

import unittest

from rb209.engine import (
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

    def test_soil_specific_no_data_raises(self):
        # Organic soil at SNS 0 has no data (dash in Table 4.17)
        with self.assertRaises(ValueError):
            recommend_nitrogen("winter-wheat-feed", 0, soil_type="organic")

    def test_soil_specific_crop_without_table_raises(self):
        # Spring barley has no soil-specific table
        with self.assertRaises(ValueError):
            recommend_nitrogen("spring-barley", 2, soil_type="medium")


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


if __name__ == "__main__":
    unittest.main()
