"""Command-line interface for RB209 fertiliser recommendations."""

import argparse
import sys

from rb209 import __version__
from rb209.data.crops import CROP_INFO
from rb209.data.organic import ORGANIC_MATERIAL_INFO
from rb209.engine import (
    calculate_lime,
    calculate_organic,
    calculate_smn_sns,
    calculate_sns,
    recommend_all,
    recommend_nitrogen,
    recommend_phosphorus,
    recommend_potassium,
    recommend_sulfur,
)
from rb209.formatters import (
    format_crop_list,
    format_lime,
    format_material_list,
    format_organic,
    format_recommendation,
    format_single_nutrient,
    format_sns,
)
from rb209.models import Crop, OrganicMaterial, PreviousCrop, Rainfall, SoilType


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
    rec = recommend_all(
        crop=args.crop,
        sns_index=args.sns_index,
        p_index=args.p_index,
        k_index=args.k_index,
        mg_index=args.mg_index,
        straw_removed=args.straw_removed,
    )
    print(format_recommendation(rec, args.output_format))


def _handle_nitrogen(args: argparse.Namespace) -> None:
    value = recommend_nitrogen(args.crop, args.sns_index)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Nitrogen (N)", "kg/ha", value, args.output_format))


def _handle_phosphorus(args: argparse.Namespace) -> None:
    value = recommend_phosphorus(args.crop, args.p_index)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Phosphorus (P2O5)", "kg/ha", value, args.output_format))


def _handle_potassium(args: argparse.Namespace) -> None:
    value = recommend_potassium(args.crop, args.k_index, args.straw_removed)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Potassium (K2O)", "kg/ha", value, args.output_format))


def _handle_sulfur(args: argparse.Namespace) -> None:
    value = recommend_sulfur(args.crop)
    name = CROP_INFO[args.crop]["name"]
    print(format_single_nutrient(name, "Sulfur (SO3)", "kg/ha", value, args.output_format))


def _handle_sns(args: argparse.Namespace) -> None:
    result = calculate_sns(args.previous_crop, args.soil_type, args.rainfall)
    print(format_sns(result, args.output_format))


def _handle_sns_smn(args: argparse.Namespace) -> None:
    result = calculate_smn_sns(args.smn, args.crop_n)
    print(format_sns(result, args.output_format))


def _handle_organic(args: argparse.Namespace) -> None:
    result = calculate_organic(args.material, args.rate)
    print(format_organic(result, args.output_format))


def _handle_lime(args: argparse.Namespace) -> None:
    result = calculate_lime(args.current_ph, args.target_ph, args.soil_type)
    print(format_lime(result, args.output_format))


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
    p_rec.add_argument("--straw-removed", action="store_true", default=True,
                        help="Straw removed from field (cereals, default: true)")
    p_rec.add_argument("--straw-incorporated", action="store_true",
                        help="Straw incorporated into field (cereals)")
    _add_format_arg(p_rec)
    p_rec.set_defaults(func=_handle_recommend)

    # ── nitrogen ─────────────────────────────────────────────────
    p_n = subparsers.add_parser("nitrogen", help="Nitrogen recommendation")
    p_n.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_n.add_argument("--sns-index", required=True, type=int,
                      metavar="0-6", help="Soil Nitrogen Supply index (0-6)")
    _add_format_arg(p_n)
    p_n.set_defaults(func=_handle_nitrogen)

    # ── phosphorus ───────────────────────────────────────────────
    p_p = subparsers.add_parser("phosphorus", help="Phosphorus recommendation")
    p_p.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_p.add_argument("--p-index", required=True, type=int,
                      metavar="0-9", help="Soil phosphorus index (0-9)")
    _add_format_arg(p_p)
    p_p.set_defaults(func=_handle_phosphorus)

    # ── potassium ────────────────────────────────────────────────
    p_k = subparsers.add_parser("potassium", help="Potassium recommendation")
    p_k.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    p_k.add_argument("--k-index", required=True, type=int,
                      metavar="0-9", help="Soil potassium index (0-9)")
    p_k.add_argument("--straw-removed", action="store_true", default=True,
                      help="Straw removed (cereals, default: true)")
    p_k.add_argument("--straw-incorporated", action="store_true",
                      help="Straw incorporated (cereals)")
    _add_format_arg(p_k)
    p_k.set_defaults(func=_handle_potassium)

    # ── sulfur ───────────────────────────────────────────────────
    p_s = subparsers.add_parser("sulfur", help="Sulfur recommendation")
    p_s.add_argument("--crop", required=True, choices=_crop_choices(),
                      help="Crop type")
    _add_format_arg(p_s)
    p_s.set_defaults(func=_handle_sulfur)

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

    # ── organic ──────────────────────────────────────────────────
    p_org = subparsers.add_parser(
        "organic", help="Calculate nutrients from organic materials",
    )
    p_org.add_argument("--material", required=True,
                        choices=_material_choices(),
                        help="Organic material type")
    p_org.add_argument("--rate", required=True, type=float,
                        help="Application rate (t/ha or m3/ha)")
    _add_format_arg(p_org)
    p_org.set_defaults(func=_handle_organic)

    # ── lime ─────────────────────────────────────────────────────
    p_lime = subparsers.add_parser("lime", help="Calculate lime requirement")
    p_lime.add_argument("--current-ph", required=True, type=float,
                         help="Current soil pH")
    p_lime.add_argument("--target-ph", required=True, type=float,
                         help="Target soil pH")
    p_lime.add_argument("--soil-type", required=True,
                         choices=[s.value for s in SoilType],
                         help="Soil type")
    _add_format_arg(p_lime)
    p_lime.set_defaults(func=_handle_lime)

    # ── list-crops ───────────────────────────────────────────────
    p_lc = subparsers.add_parser("list-crops", help="List available crops")
    p_lc.add_argument("--category",
                       choices=["arable", "grassland", "potatoes"],
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

    # Handle straw-incorporated flag overriding straw-removed
    if hasattr(args, "straw_incorporated") and args.straw_incorporated:
        args.straw_removed = False

    try:
        args.func(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
