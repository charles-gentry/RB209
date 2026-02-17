"""Tests based on RB209 worked examples 4.1–4.5.

Each test method corresponds to a step in one of the five worked examples
from Section 4 of the RB209 9th edition.  Tests assert the published RB209
values as the source of truth.  Where the code's current data tables differ,
the test will fail — highlighting a data correction needed.

Features not yet implemented (SMN method, Table 4.6 grass ley management,
timing/incorporation adjustment factors, crop history) are marked with
@unittest.skip.
"""

import unittest

from rb209.engine import (
    calculate_organic,
    calculate_smn_sns,
    calculate_sns,
    recommend_nitrogen,
    sns_value_to_index,
)
from rb209.models import (
    NResidueCategory,
    PREVIOUS_CROP_N_CATEGORY,
    PreviousCrop,
)


class TestRB209Examples(unittest.TestCase):
    """Test class covering RB209 worked examples 4.1 through 4.5."""

    # ── Example 4.1 ─────────────────────────────────────────────────
    # Spring barley (feed) on a light sand soil following sugar beet.
    # Annual rainfall 650 mm (medium).  No organic manures.
    # Table 4.4: SNS Index 0.
    # Table 4.22: spring barley recommendation = 160 kg N/ha.

    def test_example_4_1_sugar_beet_n_residue_is_low(self):
        """Sugar beet is classified as LOW N-residue for SNS purposes."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.SUGAR_BEET],
            NResidueCategory.LOW,
        )

    def test_example_4_1_sns_index(self):
        """Light sand soil, sugar beet previous crop, medium rainfall -> SNS 0."""
        result = calculate_sns("sugar-beet", "light", "medium")
        self.assertEqual(result.sns_index, 0)

    def test_example_4_1_sns_method(self):
        """Field assessment method is used for the SNS calculation."""
        result = calculate_sns("sugar-beet", "light", "medium")
        self.assertEqual(result.method, "field-assessment")

    def test_example_4_1_nitrogen_recommendation(self):
        """Spring barley at SNS 0 -> 160 kg N/ha (Table 4.22)."""
        self.assertEqual(recommend_nitrogen("spring-barley", 0), 160)

    # ── Example 4.2 ─────────────────────────────────────────────────
    # Sugar beet on medium soil after winter wheat.
    # 30 m3/ha pig slurry (4% DM) applied February, incorporated < 6 h.
    # Dry winter — excess winter rainfall 100 mm (low).
    # Table 4.3: SNS Index 1.
    # Table 4.35: sugar beet recommendation = 120 kg N/ha.
    # Pig slurry provides 65 kg/ha available N.
    # Net fertiliser N = 120 – 65 = 55 kg N/ha.

    def test_example_4_2_cereals_n_residue_is_low(self):
        """Winter wheat (cereals) is classified as LOW N-residue."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.CEREALS],
            NResidueCategory.LOW,
        )

    def test_example_4_2_sns_index(self):
        """Medium soil, cereals previous crop, low rainfall -> SNS 1 (Table 4.3)."""
        result = calculate_sns("cereals", "medium", "low")
        self.assertEqual(result.sns_index, 1)

    def test_example_4_2_nitrogen_recommendation(self):
        """Sugar beet at SNS 1 -> 120 kg N/ha (Table 4.35)."""
        self.assertEqual(recommend_nitrogen("sugar-beet", 1), 120)

    def test_example_4_2_pig_slurry_available_n(self):
        """30 m3/ha pig slurry (4% DM) applied Feb, incorporated < 6 h -> 65 kg/ha available N."""
        result = calculate_organic("pig-slurry", 30)
        self.assertAlmostEqual(result.available_n, 65.0)

    def test_example_4_2_pig_slurry_total_n(self):
        """30 m3/ha pig slurry (4% DM) -> 108 kg/ha total N."""
        result = calculate_organic("pig-slurry", 30)
        self.assertAlmostEqual(result.total_n, 108.0)

    def test_example_4_2_net_nitrogen(self):
        """Net fertiliser N = sugar beet rec (120) – slurry available N (65) = 55."""
        n_rec = recommend_nitrogen("sugar-beet", 1)
        organic = calculate_organic("pig-slurry", 30)
        net = n_rec - organic.available_n
        self.assertAlmostEqual(net, 55.0)

    def test_example_4_2_pig_slurry_adjusted_available_n(self):
        """Pig slurry applied Feb, incorporated < 6 h should yield higher
        available N than a winter surface application.
        Table 2.12 (RB209 Section 2): spring + incorporated-6h = 60% of
        total N; winter + surface-applied = 35% of total N.
        """
        # Spring application incorporated within 6 hours (Table 2.12, 4% DM):
        # 60% × 3.6 kg N/m³ × 30 m³/ha = 64.8 kg N/ha
        spring_inc = calculate_organic(
            "pig-slurry", 30, timing="spring", incorporated=True
        )
        self.assertAlmostEqual(spring_inc.available_n, 64.8, places=1)

        # Winter surface-applied, medium soil (Table 2.12, 4% DM):
        # 35% × 3.6 kg N/m³ × 30 m³/ha = 37.8 kg N/ha
        winter_surf = calculate_organic(
            "pig-slurry", 30, timing="winter", soil_type="medium", incorporated=False
        )
        self.assertAlmostEqual(winter_surf.available_n, 37.8, places=1)

        # Incorporating promptly in spring delivers more available N than
        # leaving material on the surface over winter.
        self.assertGreater(spring_inc.available_n, winter_surf.available_n)

    # ── Example 4.3 ─────────────────────────────────────────────────
    # Winter wheat on medium soil after potatoes (received FYM).
    # SMN (0–90 cm) = 115 kg N/ha, crop N = 25 kg N/ha.
    # SNS = 115 + 25 = 140 kg N/ha -> Table 4.10 -> SNS Index 4.
    # Table 4.17: winter wheat recommendation = 120 kg N/ha (medium soil).

    def test_example_4_3_potatoes_n_residue_is_medium(self):
        """Potatoes are classified as MEDIUM N-residue."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.POTATOES],
            NResidueCategory.MEDIUM,
        )

    def test_example_4_3_nitrogen_at_sns4(self):
        """Winter wheat (feed) at SNS 4 -> 120 kg N/ha (Table 4.17, medium soil)."""
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 4), 120)

    def test_example_4_3_smn_method(self):
        """SMN = 115, crop N = 25, total SNS = 140 kg N/ha."""
        result = calculate_smn_sns(smn=115, crop_n=25)
        self.assertEqual(result.sns_index, 4)
        self.assertEqual(result.method, "smn")
        self.assertEqual(result.smn, 115)
        self.assertEqual(result.crop_n, 25)
        self.assertEqual(result.sns_value, 140)

    def test_example_4_3_table_4_10(self):
        """SNS value of 140 kg N/ha should convert to SNS Index 4."""
        self.assertEqual(sns_value_to_index(140), 4)

    def test_example_4_3_soil_specific_nitrogen(self):
        """Winter wheat at SNS 4 on medium soil -> 120 kg N/ha (Table 4.17)."""
        self.assertEqual(
            recommend_nitrogen("winter-wheat-feed", 4, soil_type="medium"), 120
        )

    # ── Example 4.4 ─────────────────────────────────────────────────
    # Winter barley after 3-year pure grass ley.
    # High N management (280 kg/ha/yr + slurry), 1 cut silage then grazed.
    # Medium soil, moderate rainfall.
    # Table 4.6: '3–5 year leys, high N, 1 cut then grazed' -> SNS Index 2.
    # Next two crops: SNS 2 then SNS 1.

    def test_example_4_4_nitrogen_at_sns2(self):
        """Winter barley at SNS 2 -> 130 kg N/ha."""
        self.assertEqual(recommend_nitrogen("winter-barley", 2), 130)

    @unittest.skip(
        "Table 4.6 (grass ley SNS by age/N-intensity/regime) not implemented"
    )
    def test_example_4_4_table_4_6_grass_ley_sns(self):
        """3-year grass ley, high N (280 kg/ha/yr), 1 cut silage + grazed,
        medium soil, moderate rainfall -> SNS 2 per Table 4.6.
        """

    @unittest.skip("3-year grass ley category not available as previous crop")
    def test_example_4_4_three_year_ley_category(self):
        """The code only has grass-1-2yr and grass-long-term.
        A 3-year ley falls between these categories.
        """

    @unittest.skip(
        "Subsequent crop SNS reduction (SNS 2 -> 2 -> 1) not implemented"
    )
    def test_example_4_4_subsequent_crop_sns(self):
        """The SNS Indices for the next two crops following the winter barley
        are Index 2 and Index 1, respectively.
        """

    # ── Example 4.5 ─────────────────────────────────────────────────
    # Winter wheat after spring barley that followed a 2-year grazed ley.
    # High N (300 kg/ha/yr).  Deep clay (heavy), high rainfall.
    # Table 4.5: cereals, heavy, high -> SNS 1.
    # Table 4.6: 2-year grazed ley, high N -> SNS 2.
    # Use the higher of the two: SNS 2.

    def test_example_4_5_table_4_5_sns(self):
        """Cereals (spring barley), heavy soil, high rainfall -> SNS 1 (Table 4.5)."""
        result = calculate_sns("cereals", "heavy", "high")
        self.assertEqual(result.sns_index, 1)

    def test_example_4_5_cereals_n_residue_is_low(self):
        """Spring barley is a cereal — LOW N-residue category."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.CEREALS],
            NResidueCategory.LOW,
        )

    def test_example_4_5_nitrogen_at_final_sns2(self):
        """Winter wheat (feed) at the final SNS 2 -> 150 kg N/ha."""
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 2), 150)

    def test_example_4_5_nitrogen_at_table_4_5_sns1(self):
        """Winter wheat (feed) at Table 4.5 SNS 1 -> 180 kg N/ha.
        This would be the recommendation if only Table 4.5 were used.
        """
        self.assertEqual(recommend_nitrogen("winter-wheat-feed", 1), 180)

    @unittest.skip("Table 4.6 (grass ley SNS) not implemented")
    def test_example_4_5_table_4_6_grass_ley_sns(self):
        """2-year grazed ley, high N (300 kg/ha/yr) -> SNS 2 per Table 4.6."""

    @unittest.skip(
        "'Take higher of two SNS values' logic not implemented"
    )
    def test_example_4_5_combined_sns_take_higher(self):
        """Final SNS = max(Table 4.5 result, Table 4.6 result) = max(1, 2) = 2."""

    @unittest.skip(
        "Second-previous-crop (crop history) not supported by calculate_sns"
    )
    def test_example_4_5_crop_history(self):
        """calculate_sns only considers the immediate previous crop.
        Example 4.5 requires considering the grass ley that preceded
        the spring barley.
        """


if __name__ == "__main__":
    unittest.main()
