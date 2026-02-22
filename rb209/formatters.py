"""Output formatters for human-readable tables and JSON."""

import json
from dataclasses import asdict

from rb209.models import (
    LimeRecommendation,
    NitrogenTimingResult,
    NutrientRecommendation,
    OrganicNutrients,
    SNSResult,
)


# ── Helpers ─────────────────────────────────────────────────────────

def _box(title: str, rows: list[tuple[str, str]], notes: list[str] | None = None) -> str:
    """Format a simple box with title, key-value rows, and optional notes."""
    lines: list[str] = []
    # Determine column widths
    label_w = max(len(r[0]) for r in rows) if rows else 10
    value_w = max(len(r[1]) for r in rows) if rows else 10
    inner_w = max(label_w + value_w + 3, len(title) + 2)

    sep = "+" + "-" * (inner_w + 2) + "+"
    lines.append(sep)
    lines.append(f"| {title:<{inner_w}} |")
    lines.append(sep)
    for label, value in rows:
        padded = f"  {label:<{label_w}}   {value:>{value_w}}"
        lines.append(f"| {padded:<{inner_w}} |")
    lines.append(sep)

    if notes:
        for note in notes:
            # Wrap long notes
            while len(note) > inner_w:
                lines.append(f"| {note[:inner_w]} |")
                note = note[inner_w:]
            lines.append(f"| {note:<{inner_w}} |")
        lines.append(sep)

    return "\n".join(lines)


# ── Nutrient recommendation ────────────────────────────────────────

def format_recommendation(rec: NutrientRecommendation, fmt: str = "table") -> str:
    if fmt == "json":
        return json.dumps(asdict(rec), indent=2)

    rows = [
        ("Nitrogen (N)", f"{rec.nitrogen:.0f} kg/ha"),
        ("Phosphorus (P2O5)", f"{rec.phosphorus:.0f} kg/ha"),
        ("Potassium (K2O)", f"{rec.potassium:.0f} kg/ha"),
        ("Magnesium (MgO)", f"{rec.magnesium:.0f} kg/ha"),
        ("Sulfur (SO3)", f"{rec.sulfur:.0f} kg/ha"),
    ]
    return _box(f"Nutrient Recommendations — {rec.crop}", rows, rec.notes)


# ── Single nutrient ────────────────────────────────────────────────

def format_single_nutrient(
    crop_name: str, nutrient: str, unit: str, value: float, fmt: str = "table"
) -> str:
    if fmt == "json":
        return json.dumps({"crop": crop_name, "nutrient": nutrient, "value": value, "unit": unit}, indent=2)

    rows = [(nutrient, f"{value:.0f} {unit}")]
    return _box(f"{nutrient} — {crop_name}", rows)


# ── SNS ─────────────────────────────────────────────────────────────

def format_sns(result: SNSResult, fmt: str = "table") -> str:
    if fmt == "json":
        return json.dumps(asdict(result), indent=2)

    rows = [("SNS Index", str(result.sns_index))]

    if result.method == "smn":
        if result.smn is not None:
            rows.append(("SMN (0-90 cm)", f"{result.smn:.0f} kg N/ha"))
        if result.crop_n is not None:
            rows.append(("Crop N", f"{result.crop_n:.0f} kg N/ha"))
        if result.sns_value is not None:
            rows.append(("Total SNS", f"{result.sns_value:.0f} kg N/ha"))
    else:
        if result.previous_crop:
            rows.append(("Previous crop", result.previous_crop))
        rows.append(("Soil type", result.soil_type))
        rows.append(("Rainfall", result.rainfall))

    rows.append(("Method", result.method))
    return _box("Soil Nitrogen Supply (SNS)", rows, result.notes)


# ── Organic materials ──────────────────────────────────────────────

def format_organic(org: OrganicNutrients, fmt: str = "table") -> str:
    if fmt == "json":
        return json.dumps(asdict(org), indent=2)

    rows = [
        ("Application rate", f"{org.rate:.1f} {org.unit}/ha"),
        ("Total N", f"{org.total_n:.1f} kg/ha"),
        ("Available N (yr 1)", f"{org.available_n:.1f} kg/ha"),
        ("P2O5", f"{org.p2o5:.1f} kg/ha"),
        ("K2O", f"{org.k2o:.1f} kg/ha"),
        ("MgO", f"{org.mgo:.1f} kg/ha"),
        ("SO3", f"{org.so3:.1f} kg/ha"),
    ]
    return _box(f"Organic Nutrients — {org.material}", rows, org.notes)


# ── Lime ────────────────────────────────────────────────────────────

def format_lime(lime: LimeRecommendation, fmt: str = "table") -> str:
    if fmt == "json":
        return json.dumps(asdict(lime), indent=2)

    rows = [
        ("Current pH", f"{lime.current_ph:.1f}"),
        ("Target pH", f"{lime.target_ph:.1f}"),
        ("Soil type", lime.soil_type),
        ("Lime required", f"{lime.lime_required:.1f} t CaCO3/ha"),
    ]
    return _box("Lime Requirement", rows, lime.notes)


# ── Nitrogen timing ─────────────────────────────────────────────────

def format_timing(result: NitrogenTimingResult, fmt: str = "table") -> str:
    if fmt == "json":
        return json.dumps(asdict(result), indent=2)

    rows = [("Total N", f"{result.total_n:.0f} kg/ha")]
    for i, split in enumerate(result.splits, start=1):
        label = f"Dressing {i}"
        value = f"{split.amount:.0f} kg/ha — {split.timing}"
        rows.append((label, value))

    return _box(
        f"N Timing — {result.crop}",
        rows,
        result.notes if result.notes else None,
    )


# ── Crop list ───────────────────────────────────────────────────────

def format_crop_list(
    crops: list[dict], fmt: str = "table"
) -> str:
    if fmt == "json":
        return json.dumps(crops, indent=2)

    lines: list[str] = []
    # Group by category
    categories: dict[str, list[dict]] = {}
    for c in crops:
        cat = c["category"]
        categories.setdefault(cat, []).append(c)

    for cat in ["arable", "grassland", "potatoes"]:
        if cat not in categories:
            continue
        lines.append(f"\n  {cat.upper()}")
        lines.append("  " + "-" * 50)
        for c in categories[cat]:
            lines.append(f"    {c['value']:<30s} {c['name']}")

    header = "Available Crops"
    lines.insert(0, header)
    lines.insert(1, "=" * len(header))
    return "\n".join(lines)


# ── Material list ───────────────────────────────────────────────────

def format_material_list(
    materials: list[dict], fmt: str = "table"
) -> str:
    if fmt == "json":
        return json.dumps(materials, indent=2)

    lines: list[str] = []
    header = "Available Organic Materials"
    lines.append(header)
    lines.append("=" * len(header))
    lines.append("")
    lines.append(f"  {'Value':<25s} {'Name':<35s} {'Unit'}")
    lines.append("  " + "-" * 68)
    for m in materials:
        lines.append(f"  {m['value']:<25s} {m['name']:<35s} {m['unit']}")

    return "\n".join(lines)
