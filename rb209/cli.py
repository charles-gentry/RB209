"""Command-line interface for RB209 fertiliser recommendations."""

import argparse
import sys

from rb209 import __version__
from rb209.data.crops import CROP_INFO
from rb209.data.organic import ORGANIC_MATERIAL_INFO
from rb209.engine import (
    calculate_grass_ley_sns,
    calculate_lime,
    calculate_organic,
    calculate_smn_sns,
    calculate_sns,
    calculate_veg_sns,
    nitrogen_timing,
    recommend_all,
    recommend_fruit_all,
    recommend_fruit_nitrogen,
    recommend_nitrogen,
    recommend_phosphorus,
    recommend_potassium,
    recommend_sodium,
    recommend_sulfur,
    smn_to_sns_index_veg,
)
from rb209.formatters import (
    format_crop_list,
    format_lime,
    format_material_list,
    format_organic,
    format_recommendation,
    format_single_nutrient,
    format_sns,
    format_timing,
)
from rb209.models import (
    FruitSoilCategory,
    OrchardManagement,
    OrganicMaterial,
    PreviousCrop,
    Rainfall,
    SoilType,
    VegPreviousCrop,
    VegSoilType,
)


def _crop_choices() -> list[str]:
    return sorted(CROP_INFO.keys())


def _material_choices() -> list[str]:
    return [m.value for m in OrganicMaterial]


def _add_format_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        dest="output_format",
        help="Output format (default: table)",
    )


# ── Subcommand handlers ────────────────────────────────────────────

def _handle_recommend(args: argparse.Namespace) -> None:
    soil = getattr(args, "soil_type", None)
    expected_yield = getattr(args, "expected_yield", None)
    ber = getattr(args, "ber", None)
    k_upper_half = getattr(args, "k_upper_half", False)
    rec = recommend_all(
        crop=args.crop,
        sns_index=args.sns_index,
        p_index=args.p_index,
        k_index=args.k_index,
        mg_index=args.mg_index,
        straw_removed=args.straw_removed,
        soil_type=soil,
        expected_yield=expected_yield,
        ber=ber,
        k_upper_half=k_upper_half,
    )
    print(format_recommendation(rec, args.output_format))


def _handle_nitrogen(args: argparse.Namespace) -> None:
    soil = getattr(args, "soil_type", None)
    expected_yield = getattr(args, "expected_yield", None)
    ber = getattr(args, "ber", None)
    value = recommend_nitrogen(args.crop, args.sns_index, soil_type=soil, expected_yield=expected_yield, ber=ber)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Nitrogen (N)", "kg/ha", value, args.output_format))


def _handle_phosphorus(args: argparse.Namespace) -> None:
    expected_yield = getattr(args, "expected_yield", None)
    value = recommend_phosphorus(args.crop, args.p_index, expected_yield=expected_yield)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Phosphorus (P2O5)", "kg/ha", value, args.output_format))


def _handle_potassium(args: argparse.Namespace) -> None:
    expected_yield = getattr(args, "expected_yield", None)
    value = recommend_potassium(args.crop, args.k_index, args.straw_removed, expected_yield=expected_yield)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Potassium (K2O)", "kg/ha", value, args.output_format))


def _handle_sulfur(args: argparse.Namespace) -> None:
    value = recommend_sulfur(args.crop)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Sulfur (SO3)", "kg/ha", value, args.output_format))


def _handle_sodium(args: argparse.Namespace) -> None:
    k_index = getattr(args, "k_index", None)
    value = recommend_sodium(args.crop, k_index=k_index)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Sodium (Na2O)", "kg/ha", value, args.output_format))


def _handle_sns(args: argparse.Namespace) -> None:
    grass_history = None
    ley_flags = (args.ley_age, args.ley_n_intensity, args.ley_management)
    if any(f is not None for f in ley_flags):
        if not all(f is not None for f in ley_flags):
            print(
                "Error: --ley-age, --ley-n-intensity, and --ley-management "
                "must all be provided together.",
                file=sys.stderr,
            )
            sys.exit(2)
        grass_history = {
            "ley_age": args.ley_age,
            "n_intensity": args.ley_n_intensity,
            "management": args.ley_management,
            "year": args.ley_year,
        }
    result = calculate_sns(
        args.previous_crop, args.soil_type, args.rainfall,
        grass_history=grass_history,
    )
    print(format_sns(result, args.output_format))


def _handle_sns_smn(args: argparse.Namespace) -> None:
    result = calculate_smn_sns(args.smn, args.crop_n)
    print(format_sns(result, args.output_format))


def _handle_sns_ley(args: argparse.Namespace) -> None:
    result = calculate_grass_ley_sns(
        ley_age=args.ley_age,
        n_intensity=args.n_intensity,
        management=args.management,
        soil_type=args.soil_type,
        rainfall=args.rainfall,
        year=args.year,
    )
    print(format_sns(result, args.output_format))


def _handle_organic(args: argparse.Namespace) -> None:
    result = calculate_organic(
        args.material,
        args.rate,
        timing=args.timing,
        incorporated=args.incorporated,
        soil_type=getattr(args, "soil_type", None),
    )
    print(format_organic(result, args.output_format))


def _handle_lime(args: argparse.Namespace) -> None:
    target_ph = getattr(args, "target_ph", None)
    land_use = getattr(args, "land_use", None)
    crop = getattr(args, "crop", None)
    if target_ph is None and land_use is None:
        print(
            "Error: one of --target-ph or --land-use is required.",
            file=sys.stderr,
        )
        sys.exit(2)
    result = calculate_lime(args.current_ph, target_ph, args.soil_type, land_use=land_use, crop=crop)
    print(format_lime(result, args.output_format))


def _handle_timing(args: argparse.Namespace) -> None:
    soil = getattr(args, "soil_type", None)
    result = nitrogen_timing(args.crop, args.total_n, soil_type=soil)
    print(format_timing(result, args.output_format))


def _handle_veg_sns(args: argparse.Namespace) -> None:
    result = calculate_veg_sns(args.previous_crop, args.soil_type, args.rainfall)
    print(format_sns(result, args.output_format))


def _handle_veg_smn(args: argparse.Namespace) -> None:
    index = smn_to_sns_index_veg(args.smn, args.depth)
    # Build an SNSResult-like object for formatting
    from rb209.models import SNSResult
    result = SNSResult(
        sns_index=index,
        method="veg-smn",
        smn=args.smn,
        notes=[
            f"SMN ({args.smn:.1f} kg N/ha to {args.depth} cm depth) "
            f"gives SNS Index {index} (Table 6.6).",
        ],
    )
    print(format_sns(result, args.output_format))


def _handle_fruit_recommend(args: argparse.Namespace) -> None:
    orchard_management = getattr(args, "orchard_management", None)
    sns_index = getattr(args, "sns_index", None)
    rec = recommend_fruit_all(
        crop=args.crop,
        soil_category=args.soil_category,
        p_index=args.p_index,
        k_index=args.k_index,
        mg_index=args.mg_index,
        orchard_management=orchard_management,
        sns_index=sns_index,
    )
    print(format_recommendation(rec, args.output_format))


def _handle_fruit_nitrogen(args: argparse.Namespace) -> None:
    orchard_management = getattr(args, "orchard_management", None)
    sns_index = getattr(args, "sns_index", None)
    value = recommend_fruit_nitrogen(
        crop=args.crop,
        soil_category=args.soil_category,
        orchard_management=orchard_management,
        sns_index=sns_index,
    )
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Nitrogen (N)", "kg/ha", value, args.output_format))


def _handle_list_crops(args: argparse.Namespace) -> None:
    crops = []
    for value, info in sorted(CROP_INFO.items()):
        if args.category and info["category"] != args.category:
            continue
        crops.append({
            "value": value,
            "name": info["name"],
            "category": info["category"],
        })
    print(format_crop_list(crops, args.output_format))


def _handle_list_materials(args: argparse.Namespace) -> None:
    materials = []
    for value, info in ORGANIC_MATERIAL_INFO.items():
        materials.append({
            "value": value,
            "name": info["name"],
            "unit": info["unit"],
        })
    print(format_material_list(materials, args.output_format))


# ── Parser construction ────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rb209",
        description="RB209 Fertiliser Recommendation Calculator",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── recommend ────────────────────────────────────────────────
    p_rec = subparsers.add_parser(
        "recommend",
        help="Full NPK + S + Mg recommendation for a crop",
    )
    p_rec.add_argument("--crop", required=True, choices=_crop_choices(),
                        help="Crop type")
    p_rec.add_argument("--sns-index", required=True, type=int,
                        metavar="0-6", help="Soil Nitrogen Supply index (0-6)")
    p_rec.add_argument("--p-index", required=True, type=int,
                        metavar="0-9", help="Soil phosphorus index (0-9)")
    p_rec.add_argument("--k-index", required=True, type=int,
                        metavar="0-9", help="Soil potassium index (0-9)")
    p_rec.add_argument("--mg-index", type=int, default=2,
                        metavar="0-9", help="Soil magnesium index (default: 2)")
    straw_group_rec = p_rec.add_mutually_exclusive_group()
    straw_group_rec.add_argument(
        "--straw-removed", dest="straw_removed", action="store_true",
        help="Straw removed from field (cereals, default)",
    )
    straw_group_rec.add_argument(
        "--straw-incorporated", dest="straw_removed", action="store_false",
        help="Straw incorporated into field (cereals)",
    )
    p_rec.set_defaults(straw_removed=True)
    p_rec.add_argument("--soil-type",
                        choices=[s.value for s in SoilType],
                        help="Soil type for soil-specific N recommendations")
    p_rec.add_argument("--expected-yield", type=float, default=None,
                        metavar="t/ha",
                        help="Expected yield (t/ha) for yield-adjusted recommendations")
    p_rec.add_argument("--ber", type=float, default=None,
                        help=(
                            "Break-even ratio (fertiliser N cost £/kg ÷ grain "
                            "value £/kg). Default: 5.0. Only affects wheat and "
                            "barley N recommendations."
                        ))
    p_rec.add_argument("--k-upper-half", "-ku", dest="k_upper_half",
                        action="store_true", default=False,
                        help=(
                            "Use K Index 2+ value (181–240 mg/l) instead of 2- "
                            "for vegetable crops at K Index 2."
                        ))
    _add_format_arg(p_rec)
    p_rec.set_defaults(func=_handle_recommend)

    # ── nitrogen ─────────────────────────────────────────────────
    p_n = subparsers.add_parser("nitrogen", help="Nitrogen recommendation")
    p_n.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_n.add_argument("--sns-index", required=True, type=int,
                      metavar="0-6", help="Soil Nitrogen Supply index (0-6)")
    p_n.add_argument("--soil-type",
                      choices=[s.value for s in SoilType],
                      help="Soil type for soil-specific recommendation")
    p_n.add_argument("--expected-yield", type=float, default=None,
                      metavar="t/ha",
                      help="Expected yield (t/ha) for yield-adjusted N recommendation")
    p_n.add_argument("--ber", type=float, default=None,
                      help=(
                          "Break-even ratio (fertiliser N cost £/kg ÷ grain "
                          "value £/kg). Default: 5.0. Only affects wheat and "
                          "barley N recommendations."
                      ))
    _add_format_arg(p_n)
    p_n.set_defaults(func=_handle_nitrogen)

    # ── phosphorus ───────────────────────────────────────────────
    p_p = subparsers.add_parser("phosphorus", help="Phosphorus recommendation")
    p_p.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_p.add_argument("--p-index", required=True, type=int,
                      metavar="0-9", help="Soil phosphorus index (0-9)")
    p_p.add_argument("--expected-yield", type=float, default=None,
                      metavar="t/ha",
                      help="Expected yield (t/ha) for yield-adjusted P recommendation")
    _add_format_arg(p_p)
    p_p.set_defaults(func=_handle_phosphorus)

    # ── potassium ────────────────────────────────────────────────
    p_k = subparsers.add_parser("potassium", help="Potassium recommendation")
    p_k.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_k.add_argument("--k-index", required=True, type=int,
                      metavar="0-9", help="Soil potassium index (0-9)")
    straw_group_k = p_k.add_mutually_exclusive_group()
    straw_group_k.add_argument(
        "--straw-removed", dest="straw_removed", action="store_true",
        help="Straw removed (cereals, default)",
    )
    straw_group_k.add_argument(
        "--straw-incorporated", dest="straw_removed", action="store_false",
        help="Straw incorporated (cereals)",
    )
    p_k.set_defaults(straw_removed=True)
    p_k.add_argument("--expected-yield", type=float, default=None,
                      metavar="t/ha",
                      help="Expected yield (t/ha) for yield-adjusted K recommendation")
    _add_format_arg(p_k)
    p_k.set_defaults(func=_handle_potassium)

    # ── sulfur ───────────────────────────────────────────────────
    p_s = subparsers.add_parser("sulfur", help="Sulfur recommendation")
    p_s.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    _add_format_arg(p_s)
    p_s.set_defaults(func=_handle_sulfur)

    # ── sodium ───────────────────────────────────────────────────
    p_na = subparsers.add_parser(
        "sodium",
        help="Sodium recommendation (sugar beet, asparagus, grassland)",
    )
    p_na.add_argument("--crop", required=True, choices=_crop_choices(),
                       help="Crop type")
    p_na.add_argument("--k-index", type=int, default=None,
                       metavar="0-9",
                       help="Soil potassium index (required for sugar beet)")
    _add_format_arg(p_na)
    p_na.set_defaults(func=_handle_sodium)

    # ── sns ──────────────────────────────────────────────────────
    p_sns = subparsers.add_parser(
        "sns", help="Calculate Soil Nitrogen Supply index",
    )
    p_sns.add_argument("--previous-crop", required=True,
                        choices=[p.value for p in PreviousCrop],
                        help="Previous crop grown")
    p_sns.add_argument("--soil-type", required=True,
                        choices=[s.value for s in SoilType],
                        help="Soil type")
    p_sns.add_argument("--rainfall", required=True,
                        choices=[r.value for r in Rainfall],
                        help="Excess winter rainfall category")
    p_sns.add_argument("--ley-age", default=None,
                        choices=["1-2yr", "3-5yr"],
                        help=(
                            "Grass ley duration for combined assessment "
                            "(requires --ley-n-intensity and --ley-management)"
                        ))
    p_sns.add_argument("--ley-n-intensity", default=None,
                        choices=["low", "high"],
                        help="N management intensity of the grass ley")
    p_sns.add_argument("--ley-management", default=None,
                        choices=["cut", "grazed", "1-cut-then-grazed"],
                        help="Ley management regime")
    p_sns.add_argument("--ley-year", type=int, default=2,
                        choices=[1, 2, 3],
                        help="Year after ploughing out the ley (default: 2)")
    _add_format_arg(p_sns)
    p_sns.set_defaults(func=_handle_sns)

    # ── sns-smn ─────────────────────────────────────────────────
    p_smn = subparsers.add_parser(
        "sns-smn", help="Calculate SNS index from SMN measurement",
    )
    p_smn.add_argument("--smn", required=True, type=float,
                        help="Soil Mineral Nitrogen (0-90 cm, kg N/ha)")
    p_smn.add_argument("--crop-n", required=True, type=float,
                        help="Estimated crop N at sampling (kg N/ha)")
    _add_format_arg(p_smn)
    p_smn.set_defaults(func=_handle_sns_smn)

    # ── sns-ley ────────────────────────────────────────────────
    p_ley = subparsers.add_parser(
        "sns-ley", help="Calculate SNS index from grass ley history (Table 4.6)",
    )
    p_ley.add_argument("--ley-age", required=True,
                        choices=["1-2yr", "3-5yr"],
                        help="Duration of the grass ley")
    p_ley.add_argument("--n-intensity", required=True,
                        choices=["low", "high"],
                        help="N management intensity (low: <250 kg N/ha/yr, high: >250)")
    p_ley.add_argument("--management", required=True,
                        choices=["cut", "grazed", "1-cut-then-grazed"],
                        help="Ley management regime")
    p_ley.add_argument("--soil-type", required=True,
                        choices=["light", "medium", "heavy"],
                        help="Soil type (organic soils not covered by Table 4.6)")
    p_ley.add_argument("--rainfall", required=True,
                        choices=[r.value for r in Rainfall],
                        help="Excess winter rainfall category")
    p_ley.add_argument("--year", type=int, default=1,
                        choices=[1, 2, 3],
                        help="Year after ploughing out the ley (default: 1)")
    _add_format_arg(p_ley)
    p_ley.set_defaults(func=_handle_sns_ley)

    # ── organic ──────────────────────────────────────────────────
    p_org = subparsers.add_parser(
        "organic", help="Calculate nutrients from organic materials",
    )
    p_org.add_argument("--material", required=True,
                        choices=_material_choices(),
                        help="Organic material type")
    p_org.add_argument("--rate", required=True, type=float,
                        help="Application rate (t/ha or m3/ha)")
    p_org.add_argument("--timing",
                        choices=["autumn", "winter", "spring", "summer"],
                        default=None,
                        help=(
                            "Application season for timing-adjusted available-N "
                            "(autumn=Aug–Oct, winter=Nov–Jan, spring=Feb–Apr, "
                            "summer=grassland only). "
                            "Only supported for pig-slurry (RB209 Table 2.12). "
                            "When omitted, the flat default coefficient is used."
                        ))
    p_org.add_argument("--incorporated", action="store_true", default=False,
                        help=(
                            "Material is soil-incorporated promptly after "
                            "application (within 6 h for slurries, 24 h for "
                            "solids). Only meaningful when --timing is also given."
                        ))
    p_org.add_argument("--soil-type",
                        choices=[s.value for s in SoilType],
                        default=None,
                        help=(
                            "Soil type for timing-adjusted available-N lookup "
                            "(light=sandy/shallow, medium/heavy/organic=medium-heavy). "
                            "Defaults to medium-heavy when --timing is given without "
                            "--soil-type."
                        ))
    _add_format_arg(p_org)
    p_org.set_defaults(func=_handle_organic)

    # ── lime ─────────────────────────────────────────────────────
    p_lime = subparsers.add_parser("lime", help="Calculate lime requirement")
    p_lime.add_argument("--current-ph", required=True, type=float,
                         help="Current soil pH")
    p_lime.add_argument("--target-ph", type=float, default=None,
                         help=(
                             "Target soil pH. When omitted, the RB209 default "
                             "for the specified --land-use is used automatically "
                             "(arable: 6.5, grassland: 6.0)."
                         ))
    p_lime.add_argument("--land-use",
                         choices=["arable", "grassland"],
                         default=None,
                         help=(
                             "Land use category for automatic target pH selection. "
                             "Required when --target-ph is omitted. "
                             "arable → target pH 6.5; grassland → target pH 6.0."
                         ))
    p_lime.add_argument("--soil-type", required=True,
                         choices=[s.value for s in SoilType],
                         help="Soil type")
    p_lime.add_argument("--crop",
                         choices=_crop_choices(),
                         default=None,
                         help=(
                             "Optional crop type. When a potato crop is specified "
                             "and lime is required, a warning about common scab "
                             "risk is added."
                         ))
    _add_format_arg(p_lime)
    p_lime.set_defaults(func=_handle_lime)

    # ── timing ───────────────────────────────────────────────────
    p_tim = subparsers.add_parser(
        "timing",
        help="Nitrogen application timing and split dressing advice",
    )
    p_tim.add_argument("--crop", required=True, choices=_crop_choices(),
                       help="Crop type")
    p_tim.add_argument("--total-n", required=True, type=float,
                       metavar="kg/ha",
                       help="Total nitrogen recommendation (kg N/ha)")
    p_tim.add_argument("--soil-type",
                       choices=[s.value for s in SoilType],
                       help="Soil type (affects timing for some crops, e.g. potatoes)")
    _add_format_arg(p_tim)
    p_tim.set_defaults(func=_handle_timing)

    # ── veg-sns ──────────────────────────────────────────────────
    p_veg_sns = subparsers.add_parser(
        "veg-sns",
        help="Calculate SNS index for vegetable crops (Tables 6.2–6.4)",
    )
    p_veg_sns.add_argument("--previous-crop", required=True,
                            choices=[p.value for p in VegPreviousCrop],
                            help="Previous crop category (vegetable SNS tables)")
    p_veg_sns.add_argument("--soil-type", required=True,
                            choices=[s.value for s in VegSoilType],
                            help=(
                                "Soil type for vegetable SNS "
                                "(light-sand, medium, deep-clay, deep-silt, organic, peat)"
                            ))
    p_veg_sns.add_argument("--rainfall", required=True,
                            choices=["low", "moderate", "high"],
                            help=(
                                "Rainfall category: low (<600 mm / <150 mm EWR), "
                                "moderate (600–700 mm), high (>700 mm / >250 mm EWR)"
                            ))
    _add_format_arg(p_veg_sns)
    p_veg_sns.set_defaults(func=_handle_veg_sns)

    # ── veg-smn ──────────────────────────────────────────────────
    p_veg_smn = subparsers.add_parser(
        "veg-smn",
        help="Calculate SNS index for vegetable crops from SMN measurement (Table 6.6)",
    )
    p_veg_smn.add_argument("--smn", required=True, type=float,
                            metavar="kg/ha",
                            help="Soil Mineral Nitrogen (kg N/ha)")
    p_veg_smn.add_argument("--depth", required=True, type=int,
                            choices=[30, 60, 90],
                            help="Sampling depth (cm): 30, 60, or 90")
    _add_format_arg(p_veg_smn)
    p_veg_smn.set_defaults(func=_handle_veg_smn)

    # ── fruit-recommend ──────────────────────────────────────────
    _fruit_slugs = sorted(
        v for v, info in CROP_INFO.items() if info.get("category") == "fruit"
    )
    p_frec = subparsers.add_parser(
        "fruit-recommend",
        help="Full N/P/K/Mg recommendation for a fruit, vine or hop crop (Section 7)",
    )
    p_frec.add_argument("crop", choices=_fruit_slugs, help="Fruit crop slug")
    p_frec.add_argument(
        "--soil-category", "-sc", required=True,
        choices=[c.value for c in FruitSoilCategory],
        dest="soil_category",
        help="Soil category for fruit/vine/hop nitrogen recommendation "
             "(light-sand | deep-silt | clay | other-mineral)",
    )
    p_frec.add_argument("--p-index", "-p", required=True, type=int,
                         metavar="0-9", dest="p_index",
                         help="Soil phosphorus index (0-9)")
    p_frec.add_argument("--k-index", "-k", required=True, type=int,
                         metavar="0-9", dest="k_index",
                         help="Soil potassium index (0-9)")
    p_frec.add_argument("--mg-index", "-mg", required=True, type=int,
                         metavar="0-9", dest="mg_index",
                         help="Soil magnesium index (0-9)")
    p_frec.add_argument(
        "--orchard-management", "-om", default=None,
        choices=[m.value for m in OrchardManagement],
        dest="orchard_management",
        help="Orchard management system for top fruit nitrogen "
             "(grass-strip | overall-grass)",
    )
    p_frec.add_argument(
        "--sns-index", "-sns", type=int, default=None,
        metavar="0-5", dest="sns_index",
        help="SNS index (0-5); required for strawberry crops",
    )
    _add_format_arg(p_frec)
    p_frec.set_defaults(func=_handle_fruit_recommend)

    # ── fruit-nitrogen ────────────────────────────────────────────
    p_fn = subparsers.add_parser(
        "fruit-nitrogen",
        help="Nitrogen recommendation for a fruit, vine or hop crop (Section 7)",
    )
    p_fn.add_argument("crop", choices=_fruit_slugs, help="Fruit crop slug")
    p_fn.add_argument(
        "--soil-category", "-sc", required=True,
        choices=[c.value for c in FruitSoilCategory],
        dest="soil_category",
        help="Soil category for fruit/vine/hop nitrogen recommendation "
             "(light-sand | deep-silt | clay | other-mineral)",
    )
    p_fn.add_argument(
        "--orchard-management", "-om", default=None,
        choices=[m.value for m in OrchardManagement],
        dest="orchard_management",
        help="Orchard management system for top fruit nitrogen "
             "(grass-strip | overall-grass)",
    )
    p_fn.add_argument(
        "--sns-index", "-sns", type=int, default=None,
        metavar="0-5", dest="sns_index",
        help="SNS index (0-5); required for strawberry crops",
    )
    _add_format_arg(p_fn)
    p_fn.set_defaults(func=_handle_fruit_nitrogen)

    # ── list-crops ───────────────────────────────────────────────
    p_lc = subparsers.add_parser("list-crops", help="List available crops")
    p_lc.add_argument("--category",
                       choices=["arable", "grassland", "potatoes", "vegetables", "fruit"],
                       help="Filter by crop category")
    _add_format_arg(p_lc)
    p_lc.set_defaults(func=_handle_list_crops)

    # ── list-materials ───────────────────────────────────────────
    p_lm = subparsers.add_parser(
        "list-materials", help="List available organic materials",
    )
    _add_format_arg(p_lm)
    p_lm.set_defaults(func=_handle_list_materials)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
