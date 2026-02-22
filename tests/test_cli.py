"""Integration tests for the CLI."""

import json
import pathlib
import subprocess
import sys
import unittest

_REPO_ROOT = pathlib.Path(__file__).parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "rb209", *args],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )


class TestCLIRecommend(unittest.TestCase):
    def test_recommend_basic(self):
        result = _run_cli(
            "recommend",
            "--crop", "winter-wheat-feed",
            "--sns-index", "2",
            "--p-index", "2",
            "--k-index", "1",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Nitrogen", result.stdout)
        self.assertIn("150", result.stdout)

    def test_recommend_json(self):
        result = _run_cli(
            "recommend",
            "--crop", "spring-barley",
            "--sns-index", "1",
            "--p-index", "1",
            "--k-index", "1",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["nitrogen"], 120)
        self.assertIn("phosphorus", data)


class TestCLINitrogen(unittest.TestCase):
    def test_nitrogen_basic(self):
        result = _run_cli("nitrogen", "--crop", "winter-barley", "--sns-index", "3")
        self.assertEqual(result.returncode, 0)
        self.assertIn("100", result.stdout)


class TestCLISNS(unittest.TestCase):
    def test_sns_basic(self):
        result = _run_cli(
            "sns",
            "--previous-crop", "cereals",
            "--soil-type", "medium",
            "--rainfall", "medium",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("1", result.stdout)

    def test_sns_json(self):
        result = _run_cli(
            "sns",
            "--previous-crop", "oilseed-rape",
            "--soil-type", "heavy",
            "--rainfall", "low",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["sns_index"], 3)


class TestCLIOrganic(unittest.TestCase):
    def test_organic_basic(self):
        result = _run_cli("organic", "--material", "cattle-fym", "--rate", "25")
        self.assertEqual(result.returncode, 0)
        self.assertIn("150.0", result.stdout)

    def test_organic_json(self):
        result = _run_cli(
            "organic", "--material", "pig-slurry", "--rate", "30", "--format", "json"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertAlmostEqual(data["total_n"], 108.0)


class TestCLILime(unittest.TestCase):
    def test_lime_basic(self):
        result = _run_cli(
            "lime",
            "--current-ph", "5.8",
            "--target-ph", "6.5",
            "--soil-type", "medium",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("3.9", result.stdout)

    def test_land_use_arable_auto_target(self):
        # --land-use arable should default target pH to 6.5
        result = _run_cli(
            "lime",
            "--current-ph", "5.8",
            "--land-use", "arable",
            "--soil-type", "medium",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("6.5", result.stdout)
        self.assertIn("3.9", result.stdout)

    def test_land_use_grassland_auto_target(self):
        # --land-use grassland should default target pH to 6.0
        result = _run_cli(
            "lime",
            "--current-ph", "5.5",
            "--land-use", "grassland",
            "--soil-type", "medium",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("6.0", result.stdout)

    def test_no_target_ph_no_land_use_errors(self):
        result = _run_cli(
            "lime",
            "--current-ph", "5.8",
            "--soil-type", "medium",
        )
        self.assertEqual(result.returncode, 2)

    def test_very_acidic_soil_warning(self):
        # pH below 5.0 should produce a warning note
        result = _run_cli(
            "lime",
            "--current-ph", "4.5",
            "--target-ph", "6.5",
            "--soil-type", "medium",
        )
        self.assertEqual(result.returncode, 0)
        # "very acidic" appears on a single line within the box
        self.assertIn("very acidic", result.stdout.lower())

    def test_land_use_json_target_ph_field(self):
        import json
        result = _run_cli(
            "lime",
            "--current-ph", "5.0",
            "--land-use", "arable",
            "--soil-type", "light",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertAlmostEqual(data["target_ph"], 6.5)


class TestCLIListCrops(unittest.TestCase):
    def test_list_all_crops(self):
        result = _run_cli("list-crops")
        self.assertEqual(result.returncode, 0)
        self.assertIn("winter-wheat-feed", result.stdout)
        self.assertIn("grass-silage", result.stdout)
        self.assertIn("potatoes-maincrop", result.stdout)

    def test_list_crops_arable_only(self):
        result = _run_cli("list-crops", "--category", "arable")
        self.assertEqual(result.returncode, 0)
        self.assertIn("winter-wheat-feed", result.stdout)
        self.assertNotIn("grass-silage", result.stdout)

    def test_list_crops_json(self):
        result = _run_cli("list-crops", "--format", "json")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


class TestCLIListMaterials(unittest.TestCase):
    def test_list_materials(self):
        result = _run_cli("list-materials")
        self.assertEqual(result.returncode, 0)
        self.assertIn("cattle-fym", result.stdout)
        self.assertIn("pig-slurry", result.stdout)


class TestCLIErrors(unittest.TestCase):
    def test_invalid_crop_exits_nonzero(self):
        result = _run_cli("nitrogen", "--crop", "banana", "--sns-index", "2")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_args_exits_nonzero(self):
        result = _run_cli("nitrogen", "--crop", "winter-wheat-feed")
        self.assertNotEqual(result.returncode, 0)

    def test_no_command_shows_help(self):
        result = _run_cli()
        self.assertEqual(result.returncode, 0)
        self.assertIn("rb209", result.stdout.lower() + result.stderr.lower())


class TestCLIVersion(unittest.TestCase):
    def test_version(self):
        result = _run_cli("--version")
        self.assertIn("0.1.0", result.stdout)


class TestCLITiming(unittest.TestCase):
    def test_timing_basic(self):
        result = _run_cli(
            "timing",
            "--crop", "winter-barley",
            "--total-n", "180",
        )
        self.assertEqual(result.returncode, 0)
        # Two splits of 90 kg/ha each
        self.assertIn("90", result.stdout)

    def test_timing_json(self):
        result = _run_cli(
            "timing",
            "--crop", "winter-barley",
            "--total-n", "180",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("splits", data)
        self.assertIsInstance(data["splits"], list)
        self.assertEqual(len(data["splits"]), 2)

    def test_timing_missing_total_n(self):
        result = _run_cli("timing", "--crop", "winter-barley")
        self.assertNotEqual(result.returncode, 0)

    def test_timing_invalid_crop(self):
        result = _run_cli("timing", "--crop", "banana", "--total-n", "100")
        self.assertNotEqual(result.returncode, 0)

    def test_timing_potatoes_light_soil(self):
        result = _run_cli(
            "timing",
            "--crop", "potatoes-maincrop",
            "--total-n", "270",
            "--soil-type", "light",
        )
        self.assertEqual(result.returncode, 0)
        # 2/3 of 270 = 180
        self.assertIn("180", result.stdout)

    def test_timing_json_total_n_field(self):
        result = _run_cli(
            "timing",
            "--crop", "winter-wheat-feed",
            "--total-n", "150",
            "--format", "json",
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertAlmostEqual(data["total_n"], 150.0)

    def test_timing_no_rules_crop_returns_single(self):
        result = _run_cli(
            "timing",
            "--crop", "linseed",
            "--total-n", "70",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("70", result.stdout)


class TestCLILimeCrop(unittest.TestCase):
    def test_lime_with_crop_potato_shows_scab_warning(self):
        result = _run_cli(
            "lime",
            "--current-ph", "5.5",
            "--target-ph", "6.5",
            "--soil-type", "medium",
            "--crop", "potatoes-maincrop",
        )
        self.assertEqual(result.returncode, 0)
        # The formatter may wrap "common scab" across lines; check both words present
        stdout_lower = result.stdout.lower()
        self.assertIn("common", stdout_lower)
        self.assertIn("scab", stdout_lower)


if __name__ == "__main__":
    unittest.main()
