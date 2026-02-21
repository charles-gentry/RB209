"""Tests based on RB209 worked examples.

Each test method corresponds to a step in one of the worked examples
from the RB209 9th edition.  Tests assert the published RB209 values as the
source of truth.  Where the code's current data tables differ, the test will
fail — highlighting a data correction needed.

Covered examples:
  Section 2 (Organic Materials): Examples 2.2–2.5
  Section 4 (Arable Crops):     Examples 4.1–4.5
  Section 5 (Potatoes):         Examples 5.3–5.4
"""

import unittest

from rb209.engine import (
    calculate_grass_ley_sns,
    calculate_organic,
    calculate_smn_sns,
    calculate_sns,
    combine_sns,
    recommend_nitrogen,
    recommend_phosphorus,
    recommend_potassium,
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

    def test_example_4_4_table_4_6_grass_ley_sns(self):
        """3-year grass ley, high N (280 kg/ha/yr), 1 cut silage + grazed,
        medium soil, moderate rainfall -> SNS 2 per Table 4.6.
        """
        result = calculate_grass_ley_sns(
            ley_age="3-5yr",
            n_intensity="high",
            management="1-cut-then-grazed",
            soil_type="medium",
            rainfall="medium",
            year=1,
        )
        self.assertEqual(result.sns_index, 2)
        self.assertEqual(result.method, "table-4.6")

    def test_example_4_4_three_year_ley_category(self):
        """A 3-year ley maps to grass-3-5yr with HIGH N-residue category.

        RB209 reserves VERY HIGH for long-term grass (5+ years).
        A 3–5 year ley has the same HIGH category as a 1–2 year ley
        for field-assessment purposes.
        """
        self.assertEqual(
            PreviousCrop.GRASS_3_5_YEAR.value, "grass-3-5yr"
        )
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.GRASS_3_5_YEAR],
            NResidueCategory.HIGH,
        )
        # Field assessment with grass-3-5yr produces a valid SNS result
        result = calculate_sns("grass-3-5yr", "medium", "medium")
        self.assertEqual(result.sns_index, 3)
        self.assertEqual(result.previous_crop, "grass-3-5yr")

    def test_example_4_4_subsequent_crop_sns(self):
        """The SNS Indices for the next two crops following the winter barley
        are Index 2 and Index 1, respectively.

        Year 1 (winter barley) = SNS 2 (tested above).
        Year 2 (next crop)     = SNS 2.
        Year 3 (crop after)    = SNS 1.
        """
        year2 = calculate_grass_ley_sns(
            ley_age="3-5yr",
            n_intensity="high",
            management="1-cut-then-grazed",
            soil_type="medium",
            rainfall="medium",
            year=2,
        )
        self.assertEqual(year2.sns_index, 2)

        year3 = calculate_grass_ley_sns(
            ley_age="3-5yr",
            n_intensity="high",
            management="1-cut-then-grazed",
            soil_type="medium",
            rainfall="medium",
            year=3,
        )
        self.assertEqual(year3.sns_index, 1)

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

    def test_example_4_5_table_4_6_grass_ley_sns(self):
        """2-year grazed ley, high N (300 kg/ha/yr), heavy soil, high rainfall.
        Winter wheat is the second crop after the ley (spring barley was Year 1).
        Table 4.6 Year 2 SNS -> 2.
        """
        result = calculate_grass_ley_sns(
            ley_age="1-2yr",
            n_intensity="high",
            management="grazed",
            soil_type="heavy",
            rainfall="high",
            year=2,
        )
        self.assertEqual(result.sns_index, 2)
        self.assertEqual(result.method, "table-4.6")

    def test_example_4_5_combined_sns_take_higher(self):
        """Final SNS = max(Table 4.5 result, Table 4.6 result) = max(1, 2) = 2."""
        field_sns = calculate_sns("cereals", "heavy", "high")  # SNS 1
        ley_sns = calculate_grass_ley_sns(
            ley_age="1-2yr",
            n_intensity="high",
            management="grazed",
            soil_type="heavy",
            rainfall="high",
            year=2,
        )  # SNS 2
        combined = combine_sns(field_sns, ley_sns)
        self.assertEqual(combined.sns_index, 2)

    def test_example_4_5_crop_history(self):
        """calculate_sns with grass_history combines field assessment (SNS 1)
        with Table 4.6 year 2 (SNS 2) and returns the higher (SNS 2).

        Example 4.5: winter wheat after spring barley (cereals) that followed
        a 2-year grazed ley with high N (300 kg/ha/yr).  Heavy soil, high
        rainfall.
        """
        result = calculate_sns(
            "cereals",
            "heavy",
            "high",
            grass_history={
                "ley_age": "1-2yr",
                "n_intensity": "high",
                "management": "grazed",
                "year": 2,
            },
        )
        self.assertEqual(result.sns_index, 2)
        self.assertEqual(result.method, "combined")


class TestSection2OrganicExamples(unittest.TestCase):
    """Tests based on RB209 Section 2 worked examples 2.2–2.5.

    These examples demonstrate how to calculate the nutrient value of
    organic material applications and determine net fertiliser requirements.
    """

    # ── Example 2.2 ─────────────────────────────────────────────────
    # 30 m³/ha of cattle slurry (6% DM), surface-applied in early spring
    # before first-cut silage.  Soil at P Index 2 and K Index 2-.
    # Total N: 2.6 kg/m³ × 30 = 78 kg/ha.
    # Crop-available N: 35% of total = 0.9 kg/m³ → 27 kg/ha.
    # P2O5: 1.2 kg/m³ × 30 = 36 kg/ha.
    # K2O: 2.5 kg/m³ × 30 = 75 kg/ha.
    # Silage N requirement: 120 kg/ha.
    # Net fertiliser N: 120 – 27 = 93 kg/ha.

    def test_example_2_2_cattle_slurry_total_n(self):
        """30 m³/ha cattle slurry (6% DM) -> 78 kg/ha total N."""
        result = calculate_organic("cattle-slurry", 30)
        self.assertAlmostEqual(result.total_n, 78.0)

    def test_example_2_2_cattle_slurry_p2o5(self):
        """30 m³/ha cattle slurry -> 36 kg/ha P2O5 (1.2 × 30)."""
        result = calculate_organic("cattle-slurry", 30)
        self.assertAlmostEqual(result.p2o5, 36.0)

    def test_example_2_2_cattle_slurry_k2o(self):
        """30 m³/ha cattle slurry -> 75 kg/ha K2O (2.5 × 30)."""
        result = calculate_organic("cattle-slurry", 30)
        self.assertAlmostEqual(result.k2o, 75.0)

    def test_example_2_2_cattle_slurry_spring_available_n(self):
        """Cattle slurry, spring, surface-applied -> 35% of total N available.

        Table 2.9: spring, medium/heavy soil, not incorporated = 35%.
        0.35 × 2.6 × 30 = 27.3 kg/ha (reference rounds to 27).
        """
        result = calculate_organic(
            "cattle-slurry", 30, timing="spring", incorporated=False
        )
        self.assertAlmostEqual(result.available_n, 27.3, places=0)

    def test_example_2_2_net_fertiliser_n_for_silage(self):
        """First-cut silage needs 120 kg N/ha; slurry provides ~27 -> net ~93."""
        organic = calculate_organic(
            "cattle-slurry", 30, timing="spring", incorporated=False
        )
        silage_n_requirement = 120  # from example Stage 4
        net = silage_n_requirement - organic.available_n
        self.assertAlmostEqual(net, 92.7, places=0)

    # ── Example 2.3 ─────────────────────────────────────────────────
    # 35 t/ha of pig FYM applied in autumn to a clay soil before drilling
    # oilseed rape (3.5 t/ha seed yield, straw not removed).
    # FYM is not rapidly incorporated.
    # SNS Index 1, P Index 2, K Index 2-.
    # Total N: 7.0 kg/t × 35 = 245 kg/ha.
    # Available N: 10% of total (autumn, medium/heavy, not incorporated)
    #   = 0.7 kg/t × 35 = 24.5 kg/ha (reference says 25).
    # P2O5: 6.0 kg/t × 35 = 210 kg/ha.
    # K2O: 8.0 kg/t × 35 = 280 kg/ha (Table 2.4).
    # OSR N rec at SNS 1 = 220 kg N/ha.
    # Net fertiliser N = 220 – 25 = 195 kg N/ha.

    def test_example_2_3_pig_fym_total_n(self):
        """35 t/ha pig FYM -> 245 kg/ha total N (7.0 × 35)."""
        result = calculate_organic("pig-fym", 35)
        self.assertAlmostEqual(result.total_n, 245.0)

    def test_example_2_3_pig_fym_available_n_autumn(self):
        """Pig FYM, autumn, clay (heavy) soil, not incorporated -> 10% avail.

        Table 2.3: autumn, medium/heavy, surface-applied = 10%.
        0.10 × 7.0 × 35 = 24.5 kg/ha.
        """
        result = calculate_organic(
            "pig-fym", 35, timing="autumn", soil_type="heavy", incorporated=False
        )
        self.assertAlmostEqual(result.available_n, 24.5)

    def test_example_2_3_pig_fym_p2o5(self):
        """35 t/ha pig FYM -> 210 kg/ha P2O5 (6.0 × 35, Table 2.4)."""
        result = calculate_organic("pig-fym", 35)
        self.assertAlmostEqual(result.p2o5, 210.0)

    def test_example_2_3_pig_fym_k2o(self):
        """35 t/ha pig FYM -> 280 kg/ha K2O (8.0 × 35, Table 2.4)."""
        result = calculate_organic("pig-fym", 35)
        self.assertAlmostEqual(result.k2o, 280.0)

    def test_example_2_3_osr_phosphorus_at_p2(self):
        """Oilseed rape at P Index 2 -> 50 kg P2O5/ha (Section 4)."""
        self.assertEqual(recommend_phosphorus("winter-oilseed-rape", 2), 50)

    def test_example_2_3_net_fertiliser_n(self):
        """OSR N rec (220) – FYM available N (~25) = ~195 kg N/ha.

        The FYM provides 24.5 kg/ha available N.  The reference rounds to 25
        and arrives at 195 kg/ha net.  We verify the organic calculation step.
        """
        organic = calculate_organic(
            "pig-fym", 35, timing="autumn", soil_type="heavy", incorporated=False
        )
        # Reference: N rec = 220, available N ≈ 25, net = 195
        osr_n_rec = 220
        net = osr_n_rec - organic.available_n
        self.assertAlmostEqual(net, 195.5, places=0)

    # ── Example 2.4 ─────────────────────────────────────────────────
    # 20 t/ha of digested cake (biosolids) applied in autumn before
    # oilseed rape on medium soil, incorporated by ploughing within 24 h.
    # SNS Index 1, P Index 2, K Index 2-.
    # Total N: 11 kg/t × 20 = 220 kg/ha (Table 2.14).
    # Available N: 15% of total (autumn, medium/heavy, incorporated)
    #   = 1.65 kg/t × 20 = 33 kg/ha.
    # P2O5: 11 kg/t × 20 = 220 kg/ha (Table 2.16).
    # K2O: 0.6 kg/t × 20 = 12 kg/ha.
    # OSR N rec at SNS 1 = 220 kg/ha.
    # Net fertiliser N = 220 – 33 = 187 kg/ha.

    def test_example_2_4_biosolids_total_n(self):
        """20 t/ha biosolids digested cake -> 220 kg/ha total N (11 × 20).

        Table 2.14: digested cake total N = 11 kg N/t.
        """
        result = calculate_organic("biosolids-cake", 20)
        self.assertAlmostEqual(result.total_n, 220.0)

    def test_example_2_4_biosolids_available_n_autumn_incorporated(self):
        """Biosolids, autumn, medium soil, incorporated -> 15% of total N.

        Table 2.15: autumn, medium/heavy, incorporated = 15%.
        0.15 × 11 × 20 = 33 kg/ha.
        """
        result = calculate_organic(
            "biosolids-cake", 20,
            timing="autumn", soil_type="medium", incorporated=True,
        )
        self.assertAlmostEqual(result.available_n, 33.0)

    def test_example_2_4_biosolids_p2o5(self):
        """20 t/ha biosolids -> 220 kg/ha P2O5 (11 × 20, Table 2.16)."""
        result = calculate_organic("biosolids-cake", 20)
        self.assertAlmostEqual(result.p2o5, 220.0)

    def test_example_2_4_biosolids_k2o(self):
        """20 t/ha biosolids -> 12 kg/ha K2O (0.6 × 20, Table 2.16)."""
        result = calculate_organic("biosolids-cake", 20)
        self.assertAlmostEqual(result.k2o, 12.0)

    def test_example_2_4_net_fertiliser_n(self):
        """OSR N rec (220) – biosolids available N (33) = 187 kg N/ha."""
        organic = calculate_organic(
            "biosolids-cake", 20,
            timing="autumn", soil_type="medium", incorporated=True,
        )
        osr_n_rec = 220
        net = osr_n_rec - organic.available_n
        self.assertAlmostEqual(net, 187.0)

    # ── Example 2.5 ─────────────────────────────────────────────────
    # 30 t/ha of green compost applied in autumn to a sandy soil before
    # drilling winter barley (8 t/ha grain yield, straw baled).
    # P Index 2, K Index 2-.
    # Total N: 7.5 kg/t × 30 = 225 kg/ha (Table 2.17).
    # Available N: NIL (green compost N availability is negligible).
    # P2O5: 3.0 kg/t × 30 = 90 kg/ha.
    # K2O: 6.8 kg/t × 30 = 204 kg/ha.

    def test_example_2_5_green_compost_total_n(self):
        """30 t/ha green compost -> 225 kg/ha total N (7.5 × 30, Table 2.17)."""
        result = calculate_organic("green-compost", 30)
        self.assertAlmostEqual(result.total_n, 225.0)

    def test_example_2_5_green_compost_available_n_negligible(self):
        """Green compost available N is negligible (reference says NIL)."""
        result = calculate_organic("green-compost", 30)
        self.assertLess(result.available_n, 15.0)

    def test_example_2_5_green_compost_p2o5(self):
        """30 t/ha green compost -> 90 kg/ha P2O5 (3.0 × 30, Table 2.17)."""
        result = calculate_organic("green-compost", 30)
        self.assertAlmostEqual(result.p2o5, 90.0)

    def test_example_2_5_green_compost_k2o(self):
        """30 t/ha green compost -> 204 kg/ha K2O (6.8 × 30, Table 2.17)."""
        result = calculate_organic("green-compost", 30)
        self.assertAlmostEqual(result.k2o, 204.0)


class TestSection5PotatoExamples(unittest.TestCase):
    """Tests based on RB209 Section 5 worked examples 5.3–5.4.

    These examples demonstrate how to calculate nitrogen requirements for
    potato crops using SNS assessment and organic manure adjustments.
    The potato section uses Tables 5.4–5.6 for SNS, which correspond to
    the arable Tables 4.3–4.5 but may differ for some crop/soil/rainfall
    combinations.
    """

    # ── Example 5.3 ─────────────────────────────────────────────────
    # Maris Piper potatoes on medium soil near Cambridge (low rainfall).
    # Previous crop: winter barley (a cereal).
    # Table 5.4: cereals, medium soil, low rainfall -> SNS Index 1.
    # Variety group 3, growing season >120 days.
    # N recommendation: 180 kg N/ha (range 150–210, Table 5.10).
    # No organic manures applied.

    def test_example_5_3_sns_index(self):
        """Cereals, medium soil, low rainfall -> SNS 1 (Table 5.4).

        Table 5.4 for potatoes should give the same result as Table 4.3
        for this combination.
        """
        result = calculate_sns("cereals", "medium", "low")
        self.assertEqual(result.sns_index, 1)

    def test_example_5_3_cereals_n_residue_is_low(self):
        """Winter barley is a cereal — LOW N-residue category."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.CEREALS],
            NResidueCategory.LOW,
        )

    # ── Example 5.4 ─────────────────────────────────────────────────
    # Estima potatoes in Somerset (high rainfall), medium soil.
    # Previous crop: oilseed rape.
    # Table 5.6: oilseed rape, medium soil, high rainfall -> SNS Index 1.
    # Variety group 1, growing season 60–90 days.
    # N recommendation: 185 kg N/ha (160–210 range), adjusted to 200.
    # 40 t/ha cattle FYM applied in winter, ploughed in one week later.
    # Crop-available N from FYM = 24 kg/ha.
    # Manufactured N = 200 – 24 = 176 kg N/ha.

    def test_example_5_4_oilseed_rape_n_residue_is_medium(self):
        """Oilseed rape is classified as MEDIUM N-residue."""
        self.assertEqual(
            PREVIOUS_CROP_N_CATEGORY[PreviousCrop.OILSEED_RAPE],
            NResidueCategory.MEDIUM,
        )

    def test_example_5_4_cattle_fym_available_n_winter_incorporated(self):
        """40 t/ha cattle FYM, winter, medium soil, ploughed in -> 24 kg/ha.

        Table 2.3: winter, medium/heavy, incorporated = 10%.
        0.10 × 6.0 × 40 = 24.0 kg/ha.
        """
        result = calculate_organic(
            "cattle-fym", 40,
            timing="winter", soil_type="medium", incorporated=True,
        )
        self.assertAlmostEqual(result.available_n, 24.0)

    def test_example_5_4_cattle_fym_total_n(self):
        """40 t/ha cattle FYM -> 240 kg/ha total N (6.0 × 40)."""
        result = calculate_organic("cattle-fym", 40)
        self.assertAlmostEqual(result.total_n, 240.0)

    def test_example_5_4_net_fertiliser_n(self):
        """Adjusted N rec (200) – FYM available N (24) = 176 kg N/ha.

        The reference adjusts the base recommendation of 185 up to 200
        due to a cold spring, then subtracts the FYM contribution.
        """
        organic = calculate_organic(
            "cattle-fym", 40,
            timing="winter", soil_type="medium", incorporated=True,
        )
        adjusted_n_rec = 200  # Example's adjusted figure
        net = adjusted_n_rec - organic.available_n
        self.assertAlmostEqual(net, 176.0)


if __name__ == "__main__":
    unittest.main()
