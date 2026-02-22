"""Tests for Phase 4 — break-even ratio (BER) adjustments."""

import json
import pathlib
import subprocess
import sys
import unittest

from rb209.engine import recommend_all, recommend_nitrogen

_REPO_ROOT = pathlib.Path(__file__).parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "rb209", *args],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )


class TestBERAdjustment(unittest.TestCase):
    def test_wheat_ber_5_no_change(self):
        # BER 5.0 is the default — no adjustment.
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=5.0)
        self.assertEqual(result, 150)

    def test_wheat_ber_2_increases_n(self):
        # BER 2.0 → +30 kg/ha
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=2.0)
        self.assertEqual(result, 180)

    def test_wheat_ber_10_decreases_n(self):
        # BER 10.0 → -30 kg/ha
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=10.0)
        self.assertEqual(result, 120)

    def test_barley_ber_3(self):
        # spring-barley at SNS 2 base = 100; BER 3.0 → +15
        result = recommend_nitrogen("spring-barley", 2, ber=3.0)
        self.assertEqual(result, 115)

    def test_non_cereal_ignores_ber(self):
        # sugar-beet not in CROP_BER_GROUP — BER has no effect.
        result = recommend_nitrogen("sugar-beet", 2, ber=2.0)
        self.assertEqual(result, 80)

    def test_ber_none_no_change(self):
        result = recommend_nitrogen("winter-wheat-feed", 2)
        self.assertEqual(result, 150)

    def test_ber_clamped_to_zero(self):
        # winter-wheat-feed at SNS 6 has N = 0; BER 10.0 → -30 → clamped to 0
        result = recommend_nitrogen("winter-wheat-feed", 6, ber=10.0)
        self.assertEqual(result, 0)

    def test_recommend_all_with_ber(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, ber=2.0)
        self.assertEqual(rec.nitrogen, 180)

    def test_recommend_all_ber_note_present(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, ber=2.0)
        all_notes = " ".join(rec.notes).lower()
        self.assertIn("break-even", all_notes)

    def test_recommend_all_ber_note_absent_for_non_cereal(self):
        rec = recommend_all("sugar-beet", 2, 2, 1, ber=2.0)
        all_notes = " ".join(rec.notes).lower()
        self.assertNotIn("break-even", all_notes)

    def test_recommend_all_no_ber_note_when_ber_not_provided(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1)
        all_notes = " ".join(rec.notes).lower()
        self.assertNotIn("break-even", all_notes)


class TestBERInterpolation(unittest.TestCase):
    def test_wheat_ber_4_5_interpolates(self):
        # Between 4.0 (+10) and 5.0 (0): interpolation gives +5
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=4.5)
        self.assertAlmostEqual(result, 155, places=5)

    def test_barley_ber_5_5_interpolates(self):
        # Between 5.0 (0) and 6.0 (-10): interpolation gives -5
        result = recommend_nitrogen("spring-barley", 2, ber=5.5)
        self.assertAlmostEqual(result, 95, places=5)

    def test_wheat_ber_below_minimum_clamps(self):
        # BER 1.0 is below the minimum (2.0); should clamp to +30
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=1.0)
        self.assertEqual(result, 180)

    def test_wheat_ber_above_maximum_clamps(self):
        # BER 12.0 is above the maximum (10.0); should clamp to -30
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=12.0)
        self.assertEqual(result, 120)

    def test_barley_ber_9_interpolates(self):
        # Between 8.0 (-20) and 10.0 (-25): interpolation gives -22.5
        result = recommend_nitrogen("spring-barley", 2, ber=9.0)
        self.assertAlmostEqual(result, 77.5, places=5)

    def test_wheat_ber_exact_table_value_6(self):
        # BER 6.0 is an exact table value → -10
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=6.0)
        self.assertEqual(result, 140)

    def test_wheat_ber_exact_table_value_7(self):
        # BER 7.0 is an exact table value → -15
        result = recommend_nitrogen("winter-wheat-feed", 2, ber=7.0)
        self.assertEqual(result, 135)


class TestBERWithYield(unittest.TestCase):
    def test_ber_and_yield_both_applied(self):
        # Yield: 150 + (10-8)*20 = 190; then BER 2.0: 190 + 30 = 220
        result = recommend_nitrogen(
            "winter-wheat-feed", 2, expected_yield=10.0, ber=2.0
        )
        self.assertEqual(result, 220)

    def test_ber_applied_after_yield(self):
        # Yield: 150 + (10-8)*20 = 190; then BER 10.0: 190 - 30 = 160
        result = recommend_nitrogen(
            "winter-wheat-feed", 2, expected_yield=10.0, ber=10.0
        )
        self.assertEqual(result, 160)


class TestBERAllCrops(unittest.TestCase):
    def test_winter_wheat_milling_ber(self):
        # winter-wheat-milling at SNS 2 = 190; BER 2.0 → +30 = 220
        result = recommend_nitrogen("winter-wheat-milling", 2, ber=2.0)
        self.assertEqual(result, 220)

    def test_spring_wheat_ber(self):
        # spring-wheat at SNS 2 = 100; BER 4.0 → +10 = 110
        result = recommend_nitrogen("spring-wheat", 2, ber=4.0)
        self.assertEqual(result, 110)

    def test_winter_barley_ber(self):
        # winter-barley at SNS 2 = 130; BER 6.0 → -10 = 120
        result = recommend_nitrogen("winter-barley", 2, ber=6.0)
        self.assertEqual(result, 120)


class TestBERCLI(unittest.TestCase):
    def test_nitrogen_with_ber(self):
        result = _run_cli(
            "nitrogen",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--ber", "2.0",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("180", result.stdout)

    def test_recommend_with_ber(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
            "--ber", "2.0",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("180", result.stdout)

    def test_recommend_json_with_ber(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
            "--ber", "2.0",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["nitrogen"], 180)

    def test_recommend_json_ber_note_present(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
            "--ber", "2.0",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        all_notes = " ".join(data["notes"]).lower()
        self.assertIn("break-even", all_notes)

    def test_nitrogen_with_ber_non_cereal(self):
        # BER should have no effect on sugar-beet
        result = _run_cli(
            "nitrogen",
            "--crop", "sugar-beet",
            "--sns-index", "2",
            "--ber", "2.0",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("80", result.stdout)


if __name__ == "__main__":
    unittest.main()
