"""Tests for sodium (Na₂O) recommendations."""

import unittest

from rb209.engine import recommend_all, recommend_sodium


class TestRecommendSodium(unittest.TestCase):
    """Tests for the recommend_sodium() engine function."""

    # ── Sugar beet (Table 4.36) ──────────────────────────────────────

    def test_sugar_beet_k0(self):
        self.assertEqual(recommend_sodium("sugar-beet", k_index=0), 200)

    def test_sugar_beet_k1(self):
        self.assertEqual(recommend_sodium("sugar-beet", k_index=1), 200)

    def test_sugar_beet_k2(self):
        self.assertEqual(recommend_sodium("sugar-beet", k_index=2), 100)

    def test_sugar_beet_k3(self):
        self.assertEqual(recommend_sodium("sugar-beet", k_index=3), 0)

    def test_sugar_beet_k4(self):
        self.assertEqual(recommend_sodium("sugar-beet", k_index=4), 0)

    def test_sugar_beet_k_clamped(self):
        """K Index > 4 should be clamped to 4 (returns 0)."""
        self.assertEqual(recommend_sodium("sugar-beet", k_index=6), 0)

    def test_sugar_beet_requires_k_index(self):
        with self.assertRaises(ValueError):
            recommend_sodium("sugar-beet")

    # ── Asparagus ────────────────────────────────────────────────────

    def test_asparagus_subsequent_years(self):
        self.assertEqual(recommend_sodium("veg-asparagus"), 500)

    def test_asparagus_establishment_zero(self):
        """No sodium in the establishment year."""
        self.assertEqual(recommend_sodium("veg-asparagus-est"), 0)

    # ── Grassland ────────────────────────────────────────────────────

    def test_grass_grazed(self):
        self.assertEqual(recommend_sodium("grass-grazed"), 140)

    def test_grass_silage(self):
        self.assertEqual(recommend_sodium("grass-silage"), 140)

    def test_grass_hay(self):
        self.assertEqual(recommend_sodium("grass-hay"), 140)

    def test_grass_grazed_one_cut(self):
        self.assertEqual(recommend_sodium("grass-grazed-one-cut"), 140)

    # ── No sodium recommendation ─────────────────────────────────────

    def test_wheat_zero(self):
        self.assertEqual(recommend_sodium("winter-wheat-feed"), 0)

    def test_potatoes_zero(self):
        self.assertEqual(recommend_sodium("potatoes-maincrop"), 0)

    def test_celery_zero(self):
        """Celery is responsive but no quantitative rate given — returns 0."""
        self.assertEqual(recommend_sodium("veg-celery-seedbed"), 0)

    def test_veg_carrots_zero(self):
        self.assertEqual(recommend_sodium("veg-carrots"), 0)

    # ── Validation ───────────────────────────────────────────────────

    def test_invalid_crop_raises(self):
        with self.assertRaises(ValueError):
            recommend_sodium("not-a-crop")

    def test_invalid_k_index_raises(self):
        with self.assertRaises(ValueError):
            recommend_sodium("sugar-beet", k_index=10)

    def test_negative_k_index_raises(self):
        with self.assertRaises(ValueError):
            recommend_sodium("sugar-beet", k_index=-1)


class TestRecommendAllSodium(unittest.TestCase):
    """Tests for sodium integration in recommend_all()."""

    def test_sugar_beet_includes_sodium(self):
        rec = recommend_all(
            "sugar-beet", sns_index=2, p_index=2, k_index=0, mg_index=1,
        )
        self.assertEqual(rec.sodium, 200)

    def test_sugar_beet_k3_sodium_zero(self):
        rec = recommend_all(
            "sugar-beet", sns_index=2, p_index=2, k_index=3, mg_index=2,
        )
        self.assertEqual(rec.sodium, 0)

    def test_asparagus_includes_sodium(self):
        rec = recommend_all(
            "veg-asparagus", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        self.assertEqual(rec.sodium, 500)

    def test_grassland_includes_sodium(self):
        rec = recommend_all(
            "grass-grazed", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        self.assertEqual(rec.sodium, 140)

    def test_wheat_sodium_zero(self):
        rec = recommend_all(
            "winter-wheat-feed", sns_index=2, p_index=2, k_index=2,
        )
        self.assertEqual(rec.sodium, 0)

    def test_sugar_beet_sodium_notes(self):
        rec = recommend_all(
            "sugar-beet", sns_index=2, p_index=2, k_index=0, mg_index=1,
        )
        combined = " ".join(rec.notes)
        self.assertIn("sodium", combined.lower())

    def test_asparagus_sodium_notes(self):
        rec = recommend_all(
            "veg-asparagus", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        combined = " ".join(rec.notes)
        self.assertIn("sodium", combined.lower())

    def test_grassland_sodium_notes(self):
        rec = recommend_all(
            "grass-grazed", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        combined = " ".join(rec.notes)
        self.assertIn("sodium", combined.lower())

    def test_celery_advisory_note(self):
        """Celery gets an advisory note even though sodium rate is 0."""
        rec = recommend_all(
            "veg-celery-seedbed", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        self.assertEqual(rec.sodium, 0)
        combined = " ".join(rec.notes)
        self.assertIn("sodium", combined.lower())

    def test_asparagus_est_advisory_note(self):
        """Asparagus establishment gets note about not applying sodium."""
        rec = recommend_all(
            "veg-asparagus-est", sns_index=2, p_index=2, k_index=2, mg_index=2,
        )
        self.assertEqual(rec.sodium, 0)
        combined = " ".join(rec.notes)
        self.assertIn("establishment", combined.lower())


class TestSodiumJSON(unittest.TestCase):
    """Tests for sodium in JSON output."""

    def test_json_includes_sodium_field(self):
        rec = recommend_all(
            "sugar-beet", sns_index=2, p_index=2, k_index=0, mg_index=1,
        )
        import json
        from dataclasses import asdict
        data = asdict(rec)
        self.assertIn("sodium", data)
        self.assertEqual(data["sodium"], 200)

    def test_json_sodium_zero_for_non_sodium_crop(self):
        rec = recommend_all(
            "winter-wheat-feed", sns_index=2, p_index=2, k_index=2,
        )
        from dataclasses import asdict
        data = asdict(rec)
        self.assertEqual(data["sodium"], 0)


if __name__ == "__main__":
    unittest.main()
