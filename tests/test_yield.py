"""Tests for Phase 3 — yield adjustment factors."""

import json
import pathlib
import subprocess
import sys
import unittest

from rb209.engine import recommend_all, recommend_nitrogen, recommend_phosphorus, recommend_potassium

_REPO_ROOT = pathlib.Path(__file__).parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "rb209", *args],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )


class TestYieldAdjustmentNitrogen(unittest.TestCase):
    def test_winter_wheat_above_baseline(self):
        # base 150 + (10.0 - 8.0) × 20 = 190
        result = recommend_nitrogen("winter-wheat-feed", 2, expected_yield=10.0)
        self.assertEqual(result, 190)

    def test_winter_wheat_below_baseline(self):
        # base 150 + (6.0 - 8.0) × 20 = 110
        result = recommend_nitrogen("winter-wheat-feed", 2, expected_yield=6.0)
        self.assertEqual(result, 110)

    def test_winter_wheat_at_baseline_no_change(self):
        result = recommend_nitrogen("winter-wheat-feed", 2, expected_yield=8.0)
        self.assertEqual(result, 150)

    def test_winter_wheat_capped_at_max_yield(self):
        # yield capped to 13.0: 150 + (13.0 - 8.0) × 20 = 250
        result = recommend_nitrogen("winter-wheat-feed", 2, expected_yield=15.0)
        self.assertEqual(result, 250)

    def test_no_adjustment_when_yield_not_provided(self):
        result = recommend_nitrogen("winter-wheat-feed", 2)
        self.assertEqual(result, 150)

    def test_crop_without_yield_data_raises(self):
        # linseed has no yield adjustment data — must raise, not silently ignore
        with self.assertRaises(ValueError) as ctx:
            recommend_nitrogen("linseed", 2, expected_yield=5.0)
        self.assertIn("linseed", str(ctx.exception))

    def test_result_clamped_to_zero(self):
        # base 40 + (4.0 - 8.0) × 20 = -40 → 0
        result = recommend_nitrogen("winter-wheat-feed", 5, expected_yield=4.0)
        self.assertEqual(result, 0)

    def test_potato_n_not_adjusted(self):
        # potatoes have n_adjust_per_t=0, so yield doesn't change N
        base = recommend_nitrogen("potatoes-maincrop", 2)
        adjusted = recommend_nitrogen("potatoes-maincrop", 2, expected_yield=70.0)
        self.assertEqual(base, adjusted)


class TestYieldAdjustmentPotassium(unittest.TestCase):
    def test_potato_k_above_baseline(self):
        # base 180 + (60 - 50) × 5.8 = 238
        result = recommend_potassium("potatoes-maincrop", 2, expected_yield=60.0)
        self.assertAlmostEqual(result, 238, places=5)

    def test_potato_k_below_baseline(self):
        # base 180 + (40 - 50) × 5.8 = 122
        result = recommend_potassium("potatoes-maincrop", 2, expected_yield=40.0)
        self.assertAlmostEqual(result, 122, places=5)

    def test_potato_k_at_baseline_no_change(self):
        base = recommend_potassium("potatoes-maincrop", 2)
        result = recommend_potassium("potatoes-maincrop", 2, expected_yield=50.0)
        self.assertAlmostEqual(result, base, places=5)

    def test_no_adjustment_when_yield_not_provided(self):
        base = recommend_potassium("potatoes-maincrop", 2)
        self.assertEqual(base, 180)


class TestYieldAdjustmentPhosphorus(unittest.TestCase):
    def test_winter_wheat_p_above_baseline(self):
        # base 60 + (10.0 - 8.0) × 7.0 = 74
        result = recommend_phosphorus("winter-wheat-feed", 2, expected_yield=10.0)
        self.assertAlmostEqual(result, 74, places=5)

    def test_winter_wheat_p_below_baseline(self):
        # base 60 + (6.0 - 8.0) × 7.0 = 46
        result = recommend_phosphorus("winter-wheat-feed", 2, expected_yield=6.0)
        self.assertAlmostEqual(result, 46, places=5)

    def test_no_adjustment_when_yield_not_provided(self):
        result = recommend_phosphorus("winter-wheat-feed", 2)
        self.assertEqual(result, 60)

    def test_crop_without_yield_data_raises(self):
        with self.assertRaises(ValueError) as ctx:
            recommend_phosphorus("linseed", 2, expected_yield=5.0)
        self.assertIn("linseed", str(ctx.exception))


class TestYieldAdjustmentFull(unittest.TestCase):
    def test_recommend_all_with_yield_adjusts_all_nutrients(self):
        # N: 150 + (10-8)×20 = 190
        # P: 60 + (10-8)×7.0 = 74
        # K: 75 + (10-8)×10.5 = 96
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=10.0)
        self.assertEqual(rec.nitrogen, 190)
        self.assertAlmostEqual(rec.phosphorus, 74, places=5)
        self.assertAlmostEqual(rec.potassium, 96, places=5)

    def test_recommend_all_notes_contain_yield_info(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=10.0)
        all_notes = " ".join(rec.notes).lower()
        self.assertIn("yield", all_notes)

    def test_recommend_all_notes_contain_expected_and_baseline_yield(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=10.0)
        # Note should reference the actual yield value
        note_text = " ".join(rec.notes)
        self.assertIn("10.0", note_text)
        self.assertIn("8.0", note_text)

    def test_recommend_all_no_yield_unchanged(self):
        rec_base = recommend_all("winter-wheat-feed", 2, 2, 1)
        rec_yield = recommend_all("winter-wheat-feed", 2, 2, 1, expected_yield=8.0)
        self.assertEqual(rec_base.nitrogen, rec_yield.nitrogen)

    def test_recommend_all_no_yield_note_when_not_provided(self):
        rec = recommend_all("winter-wheat-feed", 2, 2, 1)
        for note in rec.notes:
            self.assertNotIn("baseline", note.lower())

    def test_recommend_all_crop_without_yield_data_raises(self):
        with self.assertRaises(ValueError) as ctx:
            recommend_all("linseed", 2, 2, 1, expected_yield=5.0)
        self.assertIn("linseed", str(ctx.exception))

    def test_error_message_lists_supported_crops(self):
        with self.assertRaises(ValueError) as ctx:
            recommend_nitrogen("spring-barley", 2, expected_yield=5.0)
        msg = str(ctx.exception)
        self.assertIn("spring-barley", msg)
        self.assertIn("winter-wheat-feed", msg)


class TestYieldAdjustmentCLI(unittest.TestCase):
    def test_recommend_with_expected_yield(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
            "--expected-yield", "10",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("190", result.stdout)

    def test_nitrogen_with_expected_yield(self):
        result = _run_cli(
            "nitrogen",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--expected-yield", "10",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("190", result.stdout)

    def test_phosphorus_with_expected_yield(self):
        result = _run_cli(
            "phosphorus",
            "--crop", "winter-wheat-feed",
            "--p-index", "2",
            "--expected-yield", "10",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("74", result.stdout)

    def test_potassium_with_expected_yield(self):
        result = _run_cli(
            "potassium",
            "--crop", "potatoes-maincrop",
            "--k-index", "2",
            "--expected-yield", "60",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("238", result.stdout)

    def test_recommend_json_with_expected_yield(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
            "--expected-yield", "10",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["nitrogen"], 190)

    def test_unsupported_crop_exits_nonzero(self):
        result = _run_cli(
            "nitrogen",
            "--crop", "linseed",
            "--sns-index", "2",
            "--expected-yield", "5",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("linseed", result.stderr)


if __name__ == "__main__":
    unittest.main()
