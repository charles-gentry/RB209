"""Tests for Phase 2 — Nitrogen Timing and Split Dressings."""

import unittest

from rb209.engine import nitrogen_timing
from rb209.models import NitrogenTimingResult, NitrogenSplit


class TestNitrogenTimingWinterBarley(unittest.TestCase):
    def test_under_100_single_dressing(self):
        result = nitrogen_timing("winter-barley", 80)
        self.assertIsInstance(result, NitrogenTimingResult)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 80)
        self.assertIn("GS30", result.splits[0].timing)

    def test_99_single_dressing(self):
        result = nitrogen_timing("winter-barley", 99)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 99)

    def test_100_to_200_two_splits(self):
        result = nitrogen_timing("winter-barley", 180)
        self.assertEqual(len(result.splits), 2)
        self.assertEqual(result.splits[0].amount, 90)
        self.assertEqual(result.splits[1].amount, 90)

    def test_100_two_splits(self):
        result = nitrogen_timing("winter-barley", 100)
        self.assertEqual(len(result.splits), 2)
        self.assertEqual(result.splits[0].amount, 50)
        self.assertEqual(result.splits[1].amount, 50)

    def test_199_two_splits(self):
        result = nitrogen_timing("winter-barley", 199)
        self.assertEqual(len(result.splits), 2)

    def test_200_plus_three_splits(self):
        result = nitrogen_timing("winter-barley", 200)
        self.assertEqual(len(result.splits), 3)
        self.assertEqual(result.splits[0].amount, 80)
        self.assertEqual(result.splits[1].amount, 80)
        self.assertEqual(result.splits[2].amount, 40)
        # "lodging" must appear in notes
        all_notes = " ".join(result.notes)
        self.assertIn("lodging", all_notes.lower())

    def test_high_n_three_splits(self):
        result = nitrogen_timing("winter-barley", 250)
        self.assertEqual(len(result.splits), 3)
        # fractions 0.4/0.4/0.2 of 250 = 100/100/50
        self.assertEqual(result.splits[0].amount, 100)
        self.assertEqual(result.splits[1].amount, 100)
        self.assertEqual(result.splits[2].amount, 50)


class TestNitrogenTimingWinterWheat(unittest.TestCase):
    def test_under_120_single_dressing(self):
        result = nitrogen_timing("winter-wheat-feed", 100)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 100)

    def test_120_single_dressing(self):
        result = nitrogen_timing("winter-wheat-feed", 120)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 120)

    def test_over_120_two_splits(self):
        result = nitrogen_timing("winter-wheat-feed", 180)
        self.assertEqual(len(result.splits), 2)
        self.assertEqual(result.splits[0].amount, 90)
        self.assertEqual(result.splits[1].amount, 90)

    def test_milling_wheat_protein_note(self):
        result = nitrogen_timing("winter-wheat-milling", 190)
        self.assertIsInstance(result, NitrogenTimingResult)
        self.assertEqual(len(result.splits), 2)
        all_notes = " ".join(result.notes)
        self.assertIn("protein", all_notes.lower())

    def test_milling_wheat_single_also_has_protein_note(self):
        result = nitrogen_timing("winter-wheat-milling", 100)
        self.assertEqual(len(result.splits), 1)
        all_notes = " ".join(result.notes)
        self.assertIn("protein", all_notes.lower())

    def test_feed_wheat_no_protein_note(self):
        result = nitrogen_timing("winter-wheat-feed", 180)
        all_notes = " ".join(result.notes).lower()
        self.assertNotIn("protein", all_notes)


class TestNitrogenTimingSpringBarley(unittest.TestCase):
    def test_under_100_single_dressing(self):
        result = nitrogen_timing("spring-barley", 80)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 80)

    def test_100_plus_two_splits(self):
        result = nitrogen_timing("spring-barley", 120)
        self.assertEqual(len(result.splits), 2)
        # first fraction = 1/3, so round(1/3 * 120) = 40
        self.assertEqual(result.splits[0].amount, 40)

    def test_spring_barley_100_two_splits(self):
        result = nitrogen_timing("spring-barley", 100)
        self.assertEqual(len(result.splits), 2)


class TestNitrogenTimingPotatoes(unittest.TestCase):
    def test_light_soil_two_splits(self):
        result = nitrogen_timing("potatoes-maincrop", 270, soil_type="light")
        self.assertEqual(len(result.splits), 2)
        # 2/3 seedbed, 1/3 post-emergence
        self.assertEqual(result.splits[0].amount, 180)
        self.assertEqual(result.splits[1].amount, 90)

    def test_light_soil_split_amounts_sum_to_total(self):
        result = nitrogen_timing("potatoes-maincrop", 270, soil_type="light")
        total = sum(s.amount for s in result.splits)
        self.assertEqual(total, 270)

    def test_non_light_soil_single_dressing(self):
        result = nitrogen_timing("potatoes-maincrop", 270, soil_type="medium")
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 270)

    def test_heavy_soil_single_dressing(self):
        result = nitrogen_timing("potatoes-maincrop", 180, soil_type="heavy")
        self.assertEqual(len(result.splits), 1)

    def test_no_soil_type_single_dressing(self):
        result = nitrogen_timing("potatoes-maincrop", 270)
        self.assertEqual(len(result.splits), 1)

    def test_potatoes_early_light_soil_split(self):
        result = nitrogen_timing("potatoes-early", 200, soil_type="light")
        self.assertEqual(len(result.splits), 2)

    def test_potatoes_seed_light_soil_split(self):
        result = nitrogen_timing("potatoes-seed", 150, soil_type="light")
        self.assertEqual(len(result.splits), 2)


class TestNitrogenTimingGrassSilage(unittest.TestCase):
    def test_high_n_multiple_splits(self):
        result = nitrogen_timing("grass-silage", 320)
        self.assertGreater(len(result.splits), 1)

    def test_very_high_n_four_cuts(self):
        result = nitrogen_timing("grass-silage", 320)
        self.assertEqual(len(result.splits), 4)

    def test_medium_n_three_cuts(self):
        result = nitrogen_timing("grass-silage", 200)
        self.assertGreater(len(result.splits), 1)

    def test_low_n_single_cut(self):
        result = nitrogen_timing("grass-silage", 60)
        self.assertEqual(len(result.splits), 1)


class TestNitrogenTimingGrassGrazed(unittest.TestCase):
    def test_low_n_two_splits(self):
        result = nitrogen_timing("grass-grazed", 80)
        self.assertEqual(len(result.splits), 2)

    def test_high_n_multiple_splits(self):
        result = nitrogen_timing("grass-grazed", 250)
        self.assertGreater(len(result.splits), 2)


class TestNitrogenTimingGrassHay(unittest.TestCase):
    def test_single_application(self):
        result = nitrogen_timing("grass-hay", 140)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 140)


class TestNitrogenTimingWinterRye(unittest.TestCase):
    def test_high_n_two_splits(self):
        result = nitrogen_timing("winter-rye", 150)
        self.assertEqual(len(result.splits), 2)

    def test_lodging_note_always_present(self):
        result = nitrogen_timing("winter-rye", 80)
        all_notes = " ".join(result.notes).lower()
        self.assertIn("lodging", all_notes)


class TestNitrogenTimingNoRules(unittest.TestCase):
    def test_crop_without_rules_returns_single(self):
        result = nitrogen_timing("linseed", 70)
        self.assertEqual(len(result.splits), 1)
        self.assertEqual(result.splits[0].amount, 70)
        all_notes = " ".join(result.notes)
        self.assertIn("No specific timing guidance", all_notes)

    def test_sugar_beet_no_rules_single(self):
        result = nitrogen_timing("sugar-beet", 80)
        self.assertEqual(len(result.splits), 1)
        all_notes = " ".join(result.notes)
        self.assertIn("No specific timing guidance", all_notes)


class TestNitrogenTimingEdgeCases(unittest.TestCase):
    def test_zero_n_returns_split_with_zero(self):
        result = nitrogen_timing("winter-barley", 0)
        # Should return at least 1 split
        self.assertGreaterEqual(len(result.splits), 1)
        # The first split should have amount 0
        self.assertEqual(result.splits[0].amount, 0)

    def test_invalid_crop_raises(self):
        with self.assertRaises(ValueError):
            nitrogen_timing("banana", 100)

    def test_negative_n_raises(self):
        with self.assertRaises(ValueError):
            nitrogen_timing("winter-barley", -10)

    def test_invalid_soil_type_raises(self):
        with self.assertRaises(ValueError):
            nitrogen_timing("potatoes-maincrop", 200, soil_type="volcanic")

    def test_result_is_nitrogenitimingresult(self):
        result = nitrogen_timing("winter-wheat-feed", 150)
        self.assertIsInstance(result, NitrogenTimingResult)

    def test_splits_are_nitrogensplit_instances(self):
        result = nitrogen_timing("winter-barley", 180)
        for split in result.splits:
            self.assertIsInstance(split, NitrogenSplit)

    def test_crop_name_in_result(self):
        result = nitrogen_timing("winter-barley", 180)
        self.assertIn("Barley", result.crop)

    def test_total_n_preserved(self):
        result = nitrogen_timing("winter-wheat-feed", 150)
        self.assertEqual(result.total_n, 150)

    def test_split_amounts_sum_to_total_n(self):
        for crop, n in [
            ("winter-barley", 180),
            ("winter-barley", 200),
            ("winter-wheat-feed", 180),
            ("spring-barley", 120),
            ("potatoes-maincrop", 270),
        ]:
            with self.subTest(crop=crop, n=n):
                result = nitrogen_timing(crop, n)
                total = sum(s.amount for s in result.splits)
                self.assertEqual(total, round(n), msg=f"Split sum mismatch for {crop} @ {n}")


if __name__ == "__main__":
    unittest.main()
