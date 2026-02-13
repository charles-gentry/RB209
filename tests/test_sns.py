"""Tests for SNS calculation."""

import unittest

from rb209.engine import calculate_smn_sns, calculate_sns, sns_value_to_index


class TestSNS(unittest.TestCase):
    def test_cereals_light_high_rainfall(self):
        result = calculate_sns("cereals", "light", "high")
        self.assertEqual(result.sns_index, 0)

    def test_cereals_medium_medium_rainfall(self):
        result = calculate_sns("cereals", "medium", "medium")
        self.assertEqual(result.sns_index, 1)

    def test_cereals_heavy_low_rainfall(self):
        result = calculate_sns("cereals", "heavy", "low")
        self.assertEqual(result.sns_index, 2)

    def test_oilseed_rape_medium_medium(self):
        result = calculate_sns("oilseed-rape", "medium", "medium")
        self.assertEqual(result.sns_index, 2)

    def test_peas_beans_heavy_low(self):
        result = calculate_sns("peas-beans", "heavy", "low")
        self.assertEqual(result.sns_index, 4)

    def test_long_term_grass_organic_low(self):
        result = calculate_sns("grass-long-term", "organic", "low")
        self.assertEqual(result.sns_index, 6)

    def test_long_term_grass_light_low(self):
        result = calculate_sns("grass-long-term", "light", "low")
        self.assertEqual(result.sns_index, 4)

    def test_method_is_field_assessment(self):
        result = calculate_sns("cereals", "medium", "medium")
        self.assertEqual(result.method, "field-assessment")

    def test_notes_contain_residue_category(self):
        result = calculate_sns("cereals", "medium", "medium")
        self.assertTrue(any("low" in n.lower() for n in result.notes))

    def test_invalid_previous_crop_raises(self):
        with self.assertRaises(ValueError):
            calculate_sns("bananas", "medium", "medium")

    def test_invalid_soil_type_raises(self):
        with self.assertRaises(ValueError):
            calculate_sns("cereals", "volcanic", "medium")

    def test_invalid_rainfall_raises(self):
        with self.assertRaises(ValueError):
            calculate_sns("cereals", "medium", "extreme")


class TestSNSValueToIndex(unittest.TestCase):
    """Tests for Table 4.10 conversion."""

    def test_zero_is_index_0(self):
        self.assertEqual(sns_value_to_index(0), 0)

    def test_60_is_index_0(self):
        self.assertEqual(sns_value_to_index(60), 0)

    def test_61_is_index_1(self):
        self.assertEqual(sns_value_to_index(61), 1)

    def test_80_is_index_1(self):
        self.assertEqual(sns_value_to_index(80), 1)

    def test_81_is_index_2(self):
        self.assertEqual(sns_value_to_index(81), 2)

    def test_120_is_index_3(self):
        self.assertEqual(sns_value_to_index(120), 3)

    def test_121_is_index_4(self):
        self.assertEqual(sns_value_to_index(121), 4)

    def test_160_is_index_4(self):
        self.assertEqual(sns_value_to_index(160), 4)

    def test_161_is_index_5(self):
        self.assertEqual(sns_value_to_index(161), 5)

    def test_240_is_index_5(self):
        self.assertEqual(sns_value_to_index(240), 5)

    def test_241_is_index_6(self):
        self.assertEqual(sns_value_to_index(241), 6)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            sns_value_to_index(-1)


class TestCalculateSMN(unittest.TestCase):
    """Tests for SMN-based SNS calculation."""

    def test_method_is_smn(self):
        result = calculate_smn_sns(100, 20)
        self.assertEqual(result.method, "smn")

    def test_example_4_3(self):
        result = calculate_smn_sns(115, 25)
        self.assertEqual(result.sns_index, 4)
        self.assertEqual(result.sns_value, 140)

    def test_zero_values(self):
        result = calculate_smn_sns(0, 0)
        self.assertEqual(result.sns_index, 0)
        self.assertEqual(result.sns_value, 0)

    def test_negative_smn_raises(self):
        with self.assertRaises(ValueError):
            calculate_smn_sns(-10, 25)

    def test_negative_crop_n_raises(self):
        with self.assertRaises(ValueError):
            calculate_smn_sns(100, -5)

    def test_field_assessment_fields_empty(self):
        result = calculate_smn_sns(115, 25)
        self.assertEqual(result.previous_crop, "")
        self.assertEqual(result.soil_type, "")
        self.assertEqual(result.rainfall, "")


if __name__ == "__main__":
    unittest.main()
