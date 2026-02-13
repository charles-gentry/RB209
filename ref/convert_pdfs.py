#!/usr/bin/env python3
"""Convert RB209 AHDB PDF guides to Markdown.

Requires: pip install pdfplumber
Usage:    python ref/convert_pdfs.py [--pdf FILENAME] [--verify]
"""

import argparse
import re
import sys
from pathlib import Path

import pdfplumber

REF_DIR = Path(__file__).parent

PDF_TO_MD = {
    "NutManGuideRB209S1_230526_WEB (1).pdf": "section1_principles.md",
    "NutManGuideRB209S2_230526_WEB.pdf": "section2_organic_materials.md",
    "Nut Man Guide RB209 - SECTION 3 UPDATE (2023) _230821_WEB.pdf": "section3_grass_forage.md",
    "NutManGuideRB209S4_230526_WEB (1).pdf": "section4_arable_crops.md",
    "RB209_Section5_2021-210208_WEB.pdf": "section5_potatoes.md",
    "RB209_Section6_2021-210208_WEB.pdf": "section6_vegetables.md",
    "RB209_Section7_2020_200113_WEB.pdf": "section7_fruit_vines_hops.md",
}

# Font size thresholds for heading detection.
# Derived from analysis: body=10pt, headings at 13/14/16/17/30pt.
HEADING_LEVELS = [
    (25.0, 1),  # Main title
    (15.0, 2),  # Major section heading
    (12.0, 3),  # Subsection heading
    (11.0, 4),  # Minor heading
]

# Patterns to strip from page bottom (footers, page numbers, nav links)
FOOTER_PATTERNS = [
    re.compile(r"^\d{1,3}$"),  # standalone page numbers
    re.compile(r"Return to Contents", re.IGNORECASE),
    re.compile(r"^\d{1,3}\s+Return to Contents", re.IGNORECASE),
]


def fix_chemical_formulas(text: str) -> str:
    """Normalize common chemical formula artifacts from PDF extraction."""
    # Phosphate: P2O5 variants (footnote markers like 'a','b' may appear before subscript)
    text = re.sub(r"\(P\s*O\s*\)[a-z]?\s*\n?\s*2\s*5", "(P2O5)", text)
    text = re.sub(r"\(PO\)[a-z]?\s*\n?\s*2\s*5", "(P2O5)", text)
    text = re.sub(r"P\s*O\s*(?:\n?\s*)2\s*5", "P2O5", text)
    text = re.sub(r"PO\s*2\s*5", "P2O5", text)
    text = re.sub(r"\(PO\)\n2 5", "(P2O5)", text)
    # Potash: K2O variants (footnote markers like 'a','b' may appear before subscript)
    text = re.sub(r"\(K\s*O\s*\)[a-z]?\s*\n?\s*2", "(K2O)", text)
    text = re.sub(r"\(KO\)[a-z]?\s*\n?\s*2", "(K2O)", text)
    text = re.sub(r"K\s*O\s*(?:\n?\s*)2(?!\d)", "K2O", text)
    text = re.sub(r"KO\s*2(?!\d)", "K2O", text)
    text = re.sub(r"\(KO\)\n2", "(K2O)", text)
    # Sulphur: SO3 variants
    text = re.sub(r"\(SO\s*\)\s*\n?\s*3", "(SO3)", text)
    text = re.sub(r"SO\s*(?:\n?\s*)3(?!\d)", "SO3", text)
    text = re.sub(r"\(SO\)\n3", "(SO3)", text)
    # Nitrogen: N2O variants
    text = re.sub(r"N\s*2\s*O(?!\d)", "N2O", text)
    # CO2
    text = re.sub(r"CO\s*2(?!\d)", "CO2", text)
    return text


def clean_cell(cell: str | None) -> str:
    """Clean a table cell value."""
    if cell is None:
        return ""
    text = cell.strip().replace("\n", " ")
    text = re.sub(r"  +", " ", text)
    text = fix_chemical_formulas(text)
    return text


def table_to_markdown(table: list[list[str | None]]) -> str:
    """Convert a pdfplumber table to a markdown pipe table."""
    if not table or not table[0]:
        return ""

    num_cols = max(len(row) for row in table)

    # Pad rows to uniform width and clean cells
    cleaned = []
    for row in table:
        padded = list(row) + [None] * (num_cols - len(row))
        cleaned.append([clean_cell(c) for c in padded])

    if not cleaned:
        return ""

    # Build markdown table
    lines = []
    header = cleaned[0]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for row in cleaned[1:]:
        if not any(row):
            continue
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def get_heading_level(avg_size: float) -> int | None:
    """Determine heading level from average font size."""
    for threshold, level in HEADING_LEVELS:
        if avg_size >= threshold:
            return level
    return None


def is_footer_text(text: str) -> bool:
    """Check if text matches common footer patterns."""
    for pat in FOOTER_PATTERNS:
        if pat.search(text):
            return True
    return False


def extract_text_from_region(page_or_crop, skip_texts: set[str],
                              table_bboxes: list[tuple]) -> list[dict]:
    """Extract text lines from a page/crop region, returning content items."""
    chars = page_or_crop.chars
    if not chars:
        return []

    sorted_chars = sorted(chars, key=lambda c: (round(c["top"], 1), c["x0"]))

    # Group characters into lines
    raw_lines = []
    current_line = []
    last_top = None

    for c in sorted_chars:
        top = round(c["top"], 1)
        if last_top is not None and abs(top - last_top) > 3:
            if current_line:
                raw_lines.append(current_line)
            current_line = []
        current_line.append(c)
        last_top = top
    if current_line:
        raw_lines.append(current_line)

    items = []
    for line_chars in raw_lines:
        text = "".join(ch["text"] for ch in line_chars).strip()
        if not text:
            continue
        avg_size = sum(ch["size"] for ch in line_chars) / len(line_chars)
        top = line_chars[0]["top"]

        # Skip known repeating headers/footers
        if text in skip_texts:
            continue
        # Skip footer patterns
        if is_footer_text(text):
            continue
        # Skip text inside table bounding boxes
        if any(bbox[1] - 5 <= top <= bbox[3] + 5 for bbox in table_bboxes):
            continue

        heading_level = get_heading_level(avg_size)
        if heading_level:
            items.append({
                "type": "heading",
                "top": top,
                "content": f"{'#' * heading_level} {text}",
            })
        else:
            items.append({"type": "text", "top": top, "content": text})

    return items


def process_page(page, page_number: int, skip_texts: set[str]) -> str:
    """Process a single page and return markdown content."""
    # Find tables and their bounding boxes
    found_tables = page.find_tables()
    table_bboxes = [t.bbox for t in found_tables]
    tables_data = [t.extract() for t in found_tables]

    content_items = []

    # Add tables with their top y-position
    for bbox, table_data in zip(table_bboxes, tables_data):
        md_table = table_to_markdown(table_data)
        if md_table:
            content_items.append({"type": "table", "top": bbox[1], "content": md_table})

    # For pages without tables, use column splitting (landscape two-column layout)
    if not found_tables:
        mid_x = page.width / 2
        margin = 10  # gutter margin

        left = page.crop((0, 0, mid_x - margin, page.height))
        right = page.crop((mid_x + margin, 0, page.width, page.height))

        left_items = extract_text_from_region(left, skip_texts, [])
        right_items = extract_text_from_region(right, skip_texts, [])

        # Check if this is truly two-column or single-column
        # If right side has very little content, treat as single-column
        right_char_count = sum(len(item["content"]) for item in right_items
                               if item["type"] == "text")
        left_char_count = sum(len(item["content"]) for item in left_items
                              if item["type"] == "text")

        if right_char_count > 50 and left_char_count > 50:
            # Two-column: left column first, then right column
            # Adjust right column tops to sort after all left content
            max_left_top = max((i["top"] for i in left_items), default=0)
            for item in right_items:
                item["top"] = max_left_top + 1 + item["top"]
            content_items.extend(left_items)
            content_items.extend(right_items)
        else:
            # Single-column: use full page extraction
            items = extract_text_from_region(page, skip_texts, [])
            content_items.extend(items)
    else:
        # Pages with tables: extract text from full page, excluding table regions
        items = extract_text_from_region(page, skip_texts, table_bboxes)
        content_items.extend(items)

    # Sort by vertical position
    content_items.sort(key=lambda x: x["top"])

    # Merge consecutive text items into paragraphs
    merged = []
    for item in content_items:
        if (item["type"] == "text" and merged and merged[-1]["type"] == "text"):
            merged[-1]["content"] += " " + item["content"]
        else:
            merged.append(item)

    # Build final output
    parts = [f"<!-- Page {page_number} -->"]
    for item in merged:
        parts.append(item["content"])

    return "\n\n".join(parts)


def detect_header_footer(pdf) -> set[str]:
    """Detect repeating header/footer text across pages."""
    sample_pages = pdf.pages[:min(10, len(pdf.pages))]
    text_counts = {}
    page_height = sample_pages[0].height if sample_pages else 800

    for page in sample_pages:
        chars = page.chars
        if not chars:
            page.flush_cache()
            continue

        sorted_chars = sorted(chars, key=lambda c: (round(c["top"], 1), c["x0"]))
        current_line = []
        last_top = None

        for c in sorted_chars:
            top = round(c["top"], 1)
            if last_top is not None and abs(top - last_top) > 3:
                if current_line:
                    text = "".join(ch["text"] for ch in current_line).strip()
                    y = current_line[0]["top"]
                    if text and (y < page_height * 0.08 or y > page_height * 0.90):
                        text_counts[text] = text_counts.get(text, 0) + 1
                current_line = []
            current_line.append(c)
            last_top = top

        if current_line:
            text = "".join(ch["text"] for ch in current_line).strip()
            y = current_line[0]["top"]
            if text and (y < page_height * 0.08 or y > page_height * 0.90):
                text_counts[text] = text_counts.get(text, 0) + 1

        page.flush_cache()

    threshold = len(sample_pages) * 0.4
    return {text for text, count in text_counts.items() if count >= threshold}


def convert_pdf(pdf_path: Path, md_path: Path) -> None:
    """Convert a single PDF to markdown."""
    print(f"Converting: {pdf_path.name}")
    print(f"  Output:   {md_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"  Pages:    {total_pages}")

        skip_texts = detect_header_footer(pdf)
        if skip_texts:
            print(f"  Detected repeating headers/footers: {len(skip_texts)}")

        md_parts = []
        for i, page in enumerate(pdf.pages):
            page_md = process_page(page, page_number=i + 1, skip_texts=skip_texts)
            md_parts.append(page_md)
            page.flush_cache()

            if (i + 1) % 10 == 0 or i + 1 == total_pages:
                print(f"  Processed {i + 1}/{total_pages} pages")

        full_md = "\n\n".join(md_parts)

        # Global post-processing
        full_md = fix_chemical_formulas(full_md)
        # Collapse excessive blank lines
        full_md = re.sub(r"\n{4,}", "\n\n\n", full_md)
        # Clean up "P 2O5" style remnants
        full_md = re.sub(r"P\s+2\s*O\s*5", "P2O5", full_md)
        full_md = re.sub(r"K\s+2\s*O(?!\d)", "K2O", full_md)
        # Clean up "(KO)b 2" and "(PO) 2 5" cell remnants
        full_md = re.sub(r"\(KO\)([a-z])?\s+2(?!\d)", r"(K2O)\1", full_md)
        full_md = re.sub(r"\(PO\)\s+2\s*5", "(P2O5)", full_md)
        # Context-aware cleanup: "phosphate (PO)" → "phosphate (P2O5)" etc.
        full_md = re.sub(r"phosphate\s+\(PO\)", "phosphate (P2O5)", full_md, flags=re.IGNORECASE)
        full_md = re.sub(r"potash\s+\(KO\)", "potash (K2O)", full_md, flags=re.IGNORECASE)
        full_md = re.sub(r"sulphur trioxide\s+\(SO\)", "sulphur trioxide (SO3)", full_md, flags=re.IGNORECASE)
        # Final catch-all for remaining standalone (PO), (KO), (SO) in chemical context
        full_md = re.sub(r"\(PO\)(?!\d)", "(P2O5)", full_md)
        full_md = re.sub(r"\(KO\)(?!\d)", "(K2O)", full_md)
        full_md = re.sub(r"\(SO\)(?!\d)", "(SO3)", full_md)

        md_path.write_text(full_md, encoding="utf-8")
        print(f"  Written:  {md_path} ({len(full_md):,} chars)")


def verify_output(pdf_path: Path, md_path: Path) -> list[str]:
    """Verify conversion quality."""
    issues = []

    if not md_path.exists():
        issues.append(f"Output file missing: {md_path.name}")
        return issues

    with pdfplumber.open(pdf_path) as pdf:
        pdf_page_count = len(pdf.pages)

    md_text = md_path.read_text(encoding="utf-8")

    # Check page markers
    page_markers = re.findall(r"<!-- Page \d+ -->", md_text)
    if len(page_markers) != pdf_page_count:
        issues.append(
            f"{md_path.name}: Page count mismatch - PDF has {pdf_page_count} pages, "
            f"markdown has {len(page_markers)} page markers"
        )

    # Check for tables
    table_count = md_text.count("| ---")
    if table_count < 1:
        issues.append(f"{md_path.name}: No tables detected (expected some)")

    # Check for empty pages
    for i in range(1, pdf_page_count + 1):
        pattern = rf"<!-- Page {i} -->(.*?)(?=<!-- Page {i + 1} -->|$)"
        match = re.search(pattern, md_text, re.DOTALL)
        if match and len(match.group(1).strip()) < 5:
            issues.append(f"{md_path.name}: Page {i} appears empty")

    # Check total content size
    if len(md_text) < 1000:
        issues.append(
            f"{md_path.name}: Suspiciously small output ({len(md_text)} chars)"
        )

    return issues


def main():
    parser = argparse.ArgumentParser(description="Convert RB209 PDFs to Markdown")
    parser.add_argument(
        "--pdf",
        help="Convert a single PDF (filename only, not full path)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify conversion output quality",
    )
    args = parser.parse_args()

    if args.pdf:
        if args.pdf not in PDF_TO_MD:
            print(f"Error: Unknown PDF '{args.pdf}'")
            print(f"Known PDFs: {list(PDF_TO_MD.keys())}")
            sys.exit(1)
        pairs = {args.pdf: PDF_TO_MD[args.pdf]}
    else:
        pairs = PDF_TO_MD

    if args.verify:
        all_issues = []
        for pdf_name, md_name in pairs.items():
            pdf_path = REF_DIR / pdf_name
            md_path = REF_DIR / md_name
            issues = verify_output(pdf_path, md_path)
            all_issues.extend(issues)

        if all_issues:
            print("Verification issues found:")
            for issue in all_issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("All verifications passed.")
            sys.exit(0)

    for pdf_name, md_name in pairs.items():
        pdf_path = REF_DIR / pdf_name
        md_path = REF_DIR / md_name

        if not pdf_path.exists():
            print(f"Warning: PDF not found: {pdf_path}")
            continue

        convert_pdf(pdf_path, md_path)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
