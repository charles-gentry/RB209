"""Tests for Section 7 fruit, vine and hop recommendations."""

import unittest

from rb209.models import FruitSoilCategory, OrchardManagement
from rb209.data.fruit import (
    FRUIT_PREPLANT_PKM,
    FRUIT_TOP_NITROGEN,
    FRUIT_TOP_PKM,
    FRUIT_SOFT_NITROGEN,
    FRUIT_SOFT_PKM,
    FRUIT_STRAWBERRY_NITROGEN,
    FRUIT_STRAWBERRY_PKM,
    FRUIT_HOPS_NITROGEN,
    FRUIT_HOPS_PKM,
)
from rb209.engine import (
    recommend_fruit_nitrogen,
    recommend_fruit_pkm,
    recommend_fruit_all,
    recommend_sulfur,
)


class TestFruitSoilCategoryEnum(unittest.TestCase):
    """1. FruitSoilCategory enum."""

    def test_all_values_exist(self):
        self.assertEqual(FruitSoilCategory.LIGHT_SAND.value, "light-sand")
        self.assertEqual(FruitSoilCategory.DEEP_SILT.value, "deep-silt")
        self.assertEqual(FruitSoilCategory.CLAY.value, "clay")
        self.assertEqual(FruitSoilCategory.OTHER.value, "other-mineral")

    def test_invalid_value_raises(self):
        with self.assertRaises(ValueError):
            FruitSoilCategory("bogus-soil")


class TestOrchardManagementEnum(unittest.TestCase):
    """2. OrchardManagement enum."""

    def test_both_values_exist(self):
        self.assertEqual(OrchardManagement.GRASS_STRIP.value, "grass-strip")
        self.assertEqual(OrchardManagement.OVERALL_GRASS.value, "overall-grass")


class TestPreplantPKM(unittest.TestCase):
    """3. Pre-planting P/K/Mg (Table 7.3)."""

    def test_fruit_preplant_p_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-preplant", 0, 0, 0)
        self.assertEqual(p, 200)

    def test_fruit_preplant_p_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-preplant", 2, 0, 0)
        self.assertEqual(p, 50)

    def test_fruit_preplant_k_index_1(self):
        p, k, mg = recommend_fruit_pkm("fruit-preplant", 0, 1, 0)
        self.assertEqual(k, 100)

    def test_fruit_preplant_mg_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-preplant", 0, 0, 2)
        self.assertEqual(mg, 85)

    def test_hops_preplant_p_index_0(self):
        p, k, mg = recommend_fruit_pkm("hops-preplant", 0, 0, 0)
        self.assertEqual(p, 250)

    def test_hops_preplant_k_index_2(self):
        p, k, mg = recommend_fruit_pkm("hops-preplant", 0, 2, 0)
        self.assertEqual(k, 200)

    def test_hops_preplant_mg_index_0(self):
        p, k, mg = recommend_fruit_pkm("hops-preplant", 0, 0, 0)
        self.assertEqual(mg, 250)

    def test_preplant_nitrogen_is_zero(self):
        self.assertEqual(recommend_fruit_nitrogen("fruit-preplant", "light-sand"), 0.0)
        self.assertEqual(recommend_fruit_nitrogen("hops-preplant", "deep-silt"), 0.0)


class TestTopFruitNitrogen(unittest.TestCase):
    """4. Top fruit nitrogen (Table 7.4)."""

    def test_dessert_apple_deep_silt_grass_strip(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-dessert-apple", "deep-silt", orchard_management="grass-strip"),
            30,
        )

    def test_dessert_apple_deep_silt_overall_grass(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-dessert-apple", "deep-silt", orchard_management="overall-grass"),
            70,
        )

    def test_culinary_apple_light_sand_grass_strip(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-culinary-apple", "light-sand", orchard_management="grass-strip"),
            110,
        )

    def test_culinary_apple_clay_overall_grass(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-culinary-apple", "clay", orchard_management="overall-grass"),
            110,
        )

    def test_pear_other_mineral_grass_strip(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-pear", "other-mineral", orchard_management="grass-strip"),
            120,
        )

    def test_cherry_light_sand_overall_grass(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-cherry", "light-sand", orchard_management="overall-grass"),
            180,
        )

    def test_top_fruit_requires_orchard_management(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-dessert-apple", "light-sand")


class TestTopFruitPKM(unittest.TestCase):
    """5. Top fruit P/K/Mg (Table 7.5)."""

    def test_p_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-dessert-apple", 0, 2, 2)
        self.assertEqual(p, 80)

    def test_p_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-pear", 2, 2, 2)
        self.assertEqual(p, 20)

    def test_k_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-cherry", 2, 0, 2)
        self.assertEqual(k, 220)

    def test_k_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-plum", 2, 2, 2)
        self.assertEqual(k, 80)

    def test_mg_index_1(self):
        p, k, mg = recommend_fruit_pkm("fruit-culinary-apple", 2, 2, 1)
        self.assertEqual(mg, 65)

    def test_mg_index_3(self):
        p, k, mg = recommend_fruit_pkm("fruit-dessert-apple", 2, 2, 3)
        self.assertEqual(mg, 0)

    def test_all_top_fruit_share_same_table(self):
        top_fruit = [
            "fruit-dessert-apple", "fruit-culinary-apple",
            "fruit-pear", "fruit-cherry", "fruit-plum",
        ]
        for crop in top_fruit:
            p, k, mg = recommend_fruit_pkm(crop, 1, 1, 1)
            self.assertEqual(p, 40, msg=f"P failed for {crop}")
            self.assertEqual(k, 150, msg=f"K failed for {crop}")
            self.assertEqual(mg, 65, msg=f"Mg failed for {crop}")


class TestSoftFruitNitrogen(unittest.TestCase):
    """6. Soft fruit nitrogen (Table 7.6)."""

    def test_blackcurrant_light_sand(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-blackcurrant", "light-sand"), 160
        )

    def test_blackcurrant_deep_silt(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-blackcurrant", "deep-silt"), 110
        )

    def test_raspberry_light_sand(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-raspberry", "light-sand"), 120
        )

    def test_raspberry_clay(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-raspberry", "clay"), 80
        )

    def test_vine_deep_silt(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-vine", "deep-silt"), 0
        )

    def test_vine_other_mineral(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-vine", "other-mineral"), 40
        )


class TestSoftFruitPKM(unittest.TestCase):
    """7. Soft fruit P/K/Mg (Table 7.7) — group separation."""

    def test_blackcurrant_k_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-blackcurrant", 2, 0, 2)
        self.assertEqual(k, 250)

    def test_blackcurrant_k_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-blackcurrant", 2, 2, 2)
        self.assertEqual(k, 120)

    def test_blackberry_k_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-blackberry", 2, 0, 2)
        self.assertEqual(k, 220)

    def test_blackberry_k_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-blackberry", 2, 2, 2)
        self.assertEqual(k, 80)

    def test_all_crops_mg_index_0(self):
        soft_crops = [
            "fruit-blackcurrant", "fruit-redcurrant", "fruit-gooseberry",
            "fruit-raspberry", "fruit-loganberry", "fruit-tayberry",
            "fruit-blackberry", "fruit-vine",
        ]
        for crop in soft_crops:
            p, k, mg = recommend_fruit_pkm(crop, 2, 2, 0)
            self.assertEqual(mg, 100, msg=f"Mg Index 0 failed for {crop}")


class TestStrawberryNitrogen(unittest.TestCase):
    """8. Strawberry nitrogen (Table 7.8)."""

    def test_main_light_sand_sns_0(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-strawberry-main", "light-sand", sns_index=0),
            60,
        )

    def test_main_deep_silt_sns_0(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-strawberry-main", "deep-silt", sns_index=0),
            0,
        )

    def test_main_other_mineral_sns_2(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-strawberry-main", "other-mineral", sns_index=2),
            30,
        )

    def test_everbearer_light_sand_sns_1(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-strawberry-ever", "light-sand", sns_index=1),
            70,
        )

    def test_everbearer_deep_silt_sns_2(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-strawberry-ever", "deep-silt", sns_index=2),
            30,
        )

    def test_clay_maps_to_other_mineral(self):
        # Clay should give same result as other-mineral for strawberries
        n_clay = recommend_fruit_nitrogen(
            "fruit-strawberry-main", "clay", sns_index=2
        )
        n_other = recommend_fruit_nitrogen(
            "fruit-strawberry-main", "other-mineral", sns_index=2
        )
        self.assertEqual(n_clay, n_other)

    def test_strawberry_requires_sns_index(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-strawberry-main", "light-sand")

    def test_sns_index_clamped_at_5(self):
        # SNS 6 should behave like SNS 5
        n_5 = recommend_fruit_nitrogen("fruit-strawberry-main", "light-sand", sns_index=5)
        n_6 = recommend_fruit_nitrogen("fruit-strawberry-main", "light-sand", sns_index=6)
        self.assertEqual(n_5, n_6)


class TestStrawberryPKM(unittest.TestCase):
    """9. Strawberry P/K/Mg (Table 7.9)."""

    def test_p_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-strawberry-main", 0, 2, 2)
        self.assertEqual(p, 110)

    def test_k_index_1(self):
        p, k, mg = recommend_fruit_pkm("fruit-strawberry-ever", 2, 1, 2)
        self.assertEqual(k, 150)


class TestHopsNitrogen(unittest.TestCase):
    """10. Hops nitrogen (Table 7.17)."""

    def test_deep_silt(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-hops", "deep-silt"), 180
        )

    def test_clay(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-hops", "clay"), 200
        )

    def test_other_mineral(self):
        self.assertEqual(
            recommend_fruit_nitrogen("fruit-hops", "other-mineral"), 220
        )

    def test_light_sand_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-hops", "light-sand")


class TestHopsPKM(unittest.TestCase):
    """11. Hops P/K/Mg (Table 7.17) — extended index range."""

    def test_p_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 0, 3, 2)
        self.assertEqual(p, 250)

    def test_p_index_5(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 5, 3, 2)
        self.assertEqual(p, 0)

    def test_k_index_0(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 2, 0, 2)
        self.assertEqual(k, 425)

    def test_k_index_3(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 2, 3, 2)
        self.assertEqual(k, 200)

    def test_k_index_5(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 2, 5, 2)
        self.assertEqual(k, 0)

    def test_mg_index_2(self):
        p, k, mg = recommend_fruit_pkm("fruit-hops", 2, 3, 2)
        self.assertEqual(mg, 50)

    def test_index_clamped_above_5(self):
        # Index 6 should clamp to 5
        p6, k6, mg6 = recommend_fruit_pkm("fruit-hops", 6, 6, 6)
        p5, k5, mg5 = recommend_fruit_pkm("fruit-hops", 5, 5, 5)
        self.assertEqual(p6, p5)
        self.assertEqual(k6, k5)
        self.assertEqual(mg6, mg5)


class TestEngineIntegration(unittest.TestCase):
    """12. Engine integration — recommend_fruit_all() for representative crops."""

    def test_dessert_apple_light_sand_grass_strip(self):
        rec = recommend_fruit_all(
            "fruit-dessert-apple",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
            orchard_management="grass-strip",
        )
        self.assertEqual(rec.nitrogen, 80)
        self.assertEqual(rec.phosphorus, 20)
        self.assertEqual(rec.potassium, 80)
        self.assertEqual(rec.magnesium, 50)

    def test_raspberry_other_mineral(self):
        rec = recommend_fruit_all(
            "fruit-raspberry",
            soil_category="other-mineral",
            p_index=1, k_index=1, mg_index=1,
        )
        self.assertEqual(rec.nitrogen, 100)
        self.assertEqual(rec.phosphorus, 70)
        self.assertEqual(rec.potassium, 180)
        self.assertEqual(rec.magnesium, 65)

    def test_strawberry_main_light_sand(self):
        rec = recommend_fruit_all(
            "fruit-strawberry-main",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
            sns_index=1,
        )
        self.assertEqual(rec.nitrogen, 50)
        self.assertEqual(rec.phosphorus, 40)
        self.assertEqual(rec.potassium, 80)
        self.assertEqual(rec.magnesium, 50)

    def test_hops_clay(self):
        rec = recommend_fruit_all(
            "fruit-hops",
            soil_category="clay",
            p_index=2, k_index=2, mg_index=2,
        )
        self.assertEqual(rec.nitrogen, 200)
        self.assertEqual(rec.phosphorus, 150)
        self.assertEqual(rec.potassium, 275)
        self.assertEqual(rec.magnesium, 50)


class TestFruitSulphur(unittest.TestCase):
    """13. Sulphur — all 18 fruit crops return 0."""

    _FRUIT_CROPS = [
        "fruit-preplant", "hops-preplant",
        "fruit-dessert-apple", "fruit-culinary-apple",
        "fruit-pear", "fruit-cherry", "fruit-plum",
        "fruit-blackcurrant", "fruit-redcurrant", "fruit-gooseberry",
        "fruit-raspberry", "fruit-loganberry", "fruit-tayberry",
        "fruit-blackberry", "fruit-strawberry-main", "fruit-strawberry-ever",
        "fruit-vine", "fruit-hops",
    ]

    def test_all_fruit_sulfur_zero(self):
        for crop in self._FRUIT_CROPS:
            with self.subTest(crop=crop):
                self.assertEqual(recommend_sulfur(crop), 0)


class TestAdvisoryNotes(unittest.TestCase):
    """14. Advisory notes appear in recommend_fruit_all() output."""

    def test_culinary_apple_cider_k_note(self):
        rec = recommend_fruit_all(
            "fruit-culinary-apple",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
            orchard_management="grass-strip",
        )
        combined = " ".join(rec.notes)
        self.assertIn("cider", combined.lower())

    def test_blackcurrant_ben_series_note(self):
        rec = recommend_fruit_all(
            "fruit-blackcurrant",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
        )
        combined = " ".join(rec.notes)
        self.assertIn("Ben-series", combined)

    def test_hops_verticillium_note(self):
        rec = recommend_fruit_all(
            "fruit-hops",
            soil_category="clay",
            p_index=2, k_index=2, mg_index=2,
        )
        combined = " ".join(rec.notes)
        self.assertIn("Verticillium", combined)

    def test_hops_split_n_note(self):
        rec = recommend_fruit_all(
            "fruit-hops",
            soil_category="clay",
            p_index=2, k_index=2, mg_index=2,
        )
        combined = " ".join(rec.notes)
        self.assertIn("Split N", combined)

    def test_strawberry_sns_note(self):
        rec = recommend_fruit_all(
            "fruit-strawberry-main",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
            sns_index=1,
        )
        combined = " ".join(rec.notes)
        self.assertIn("SNS Index", combined)

    def test_strawberry_kmg_ratio_note(self):
        rec = recommend_fruit_all(
            "fruit-strawberry-main",
            soil_category="light-sand",
            p_index=2, k_index=2, mg_index=2,
            sns_index=1,
        )
        combined = " ".join(rec.notes)
        self.assertIn("K:Mg ratio", combined)


class TestErrorHandling(unittest.TestCase):
    """15. Error handling — ValueError raised for invalid inputs."""

    def test_unknown_crop_slug(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("not-a-crop", "light-sand")

    def test_top_fruit_without_orchard_management(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-dessert-apple", "light-sand")

    def test_strawberry_without_sns_index(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-strawberry-main", "light-sand")

    def test_hops_light_sand_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-hops", "light-sand")

    def test_out_of_range_index_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_pkm("fruit-hops", -1, 0, 0)

    def test_non_fruit_crop_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("winter-wheat-feed", "light-sand")

    def test_invalid_soil_category_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen("fruit-blackcurrant", "bogus-soil")

    def test_invalid_orchard_management_raises(self):
        with self.assertRaises(ValueError):
            recommend_fruit_nitrogen(
                "fruit-dessert-apple", "light-sand",
                orchard_management="bogus-management",
            )


if __name__ == "__main__":
    unittest.main()
