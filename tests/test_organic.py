"""Tests for organic material calculations."""

import unittest

from rb209.engine import calculate_organic


class TestOrganic(unittest.TestCase):
    def test_cattle_fym_25t(self):
        result = calculate_organic("cattle-fym", 25)
        self.assertEqual(result.material, "Cattle FYM")
        self.assertEqual(result.rate, 25)
        self.assertAlmostEqual(result.total_n, 150.0)
        self.assertAlmostEqual(result.available_n, 30.0)
        self.assertAlmostEqual(result.p2o5, 80.0)
        self.assertAlmostEqual(result.k2o, 200.0)
        self.assertAlmostEqual(result.mgo, 45.0)
        self.assertAlmostEqual(result.so3, 75.0)

    def test_pig_slurry_30m3(self):
        result = calculate_organic("pig-slurry", 30)
        self.assertAlmostEqual(result.total_n, 108.0)
        self.assertAlmostEqual(result.available_n, 65.0)

    def test_poultry_litter_10t(self):
        result = calculate_organic("poultry-litter", 10)
        self.assertAlmostEqual(result.total_n, 190.0)
        self.assertAlmostEqual(result.available_n, 57.0)
        self.assertAlmostEqual(result.p2o5, 140.0)

    def test_zero_rate_returns_zeros(self):
        result = calculate_organic("cattle-fym", 0)
        self.assertEqual(result.total_n, 0)
        self.assertEqual(result.available_n, 0)
        self.assertEqual(result.p2o5, 0)
        self.assertEqual(result.k2o, 0)

    def test_negative_rate_raises(self):
        with self.assertRaises(ValueError):
            calculate_organic("cattle-fym", -5)

    def test_invalid_material_raises(self):
        with self.assertRaises(ValueError):
            calculate_organic("moon-dust", 10)

    def test_green_compost_low_available_n(self):
        result = calculate_organic("green-compost", 20)
        # Green compost has low N availability
        self.assertAlmostEqual(result.available_n, 8.0)
        self.assertGreater(result.total_n, result.available_n)

    def test_organic_notes_field_exists(self):
        result = calculate_organic("cattle-fym", 25)
        self.assertTrue(hasattr(result, "notes"))
        self.assertIsInstance(result.notes, list)

    def test_organic_condition_warning_present(self):
        result = calculate_organic("cattle-fym", 25)
        combined = " ".join(result.notes)
        self.assertIn("waterlogged", combined)


if __name__ == "__main__":
    unittest.main()
