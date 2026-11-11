"""Inspect built chapter-two artifacts; never import or run a renderer.

Run with env_Online_Lecture/python.exe -X utf8 scripts/verify_chapter02_presentation.py.
The HTML checks inspect DOM, stylesheet declarations and SVG coordinates. They
are not a substitute for browser layout or screenshot inspection.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import fitz
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CHART_PAGES = (6, 8, 10, 13, 20, 23, 24, 27, 31, 32, 33)
COLUMN_PAGES = (3, 4, 5, 21, 25, 29, 38)
SERIES_COLORS = ("#244e79", "#bb8637", "#24664d")
PDF_CENTER_TOLERANCE_PT = 1.0
SVG_TOLERANCE = 0.02


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalized(value):
    return re.sub(r"\s+", "", str(value)).replace("\u2212", "-")


def data_bounds(slide):
    """Derive the documented chart domain from raw source data, independently."""
    points = [point for series in slide["series"] for point in series["points"]]
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    require(xmax > xmin, "Chart needs at least two distinct x values")
    low, high = min(0, min(p[1] for p in points)), max(0, max(p[1] for p in points))
    span = high - low or 1
    ymin, ymax = slide.get("ylimits", (low - 0.07 * span, high + 0.13 * span))
    require(ymax > ymin, "Chart y limits must be increasing")
    return xmin, xmax, ymin, ymax


def expected_ticks(slide, xmin, xmax):
    if "xticks" in slide:
        return slide["xticks"]
    values = [xmin + (xmax - xmin) * j / 5 for j in range(6)]
    return [(x, f"{x:g}") for x in values]


def check_pdf_ticks(pdf_path, slides):
    """Use actual PDF text bboxes, not the renderer's alignment arguments."""
    errors, tick_count, largest_error = [], 0, 0.0
    with fitz.open(pdf_path) as doc:
        require(len(doc) == len(slides) == 47, "PDF/content must contain 47 slides")
        for page_no in CHART_PAGES:
            page, slide = doc[page_no - 1], slides[page_no - 1]
            require(abs(page.rect.width - 1280) < 0.1 and abs(page.rect.height - 720) < 0.1,
                    f"PDF p{page_no}: unexpected page dimensions")
            xmin, xmax, _, _ = data_bounds(slide)
            ticks = expected_ticks(slide, xmin, xmax)
            # Tick row is below the plot (bottom y=515); exclude y-axis numbers
            # near x=14 and right-side narrative at x>=810.
            candidates = []
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        x0, y0, x1, y1 = span["bbox"]
                        if 70 <= x0 <= x1 <= 790 and 520 <= (y0 + y1) / 2 <= 555:
                            candidates.append((normalized(span["text"]), (x0 + x1) / 2))
            labels = {normalized(label) for _, label in ticks}
            candidates = [c for c in candidates if c[0] in labels]
            if len(candidates) != len(ticks):
                errors.append(f"PDF p{page_no}: found {len(candidates)} x labels, expected {len(ticks)}")
            used = set()
            for x, label in ticks:
                expected = 122 + (x - xmin) / (xmax - xmin) * 620
                matches = [(abs(cx - expected), index, cx)
                           for index, (text, cx) in enumerate(candidates)
                           if text == normalized(label) and index not in used]
                if not matches:
                    errors.append(f"PDF p{page_no}: missing x label {label!r}")
                    continue
                distance, index, actual = min(matches)
                used.add(index)
                tick_count += 1
                largest_error = max(largest_error, distance)
                if distance > PDF_CENTER_TOLERANCE_PT:
                    errors.append(f"PDF p{page_no}, x={x:g}: label {label!r} center={actual:.3f}, "
                                  f"expected={expected:.3f}, drift={distance:.3f} pt")
    require(not errors, "\n".join(errors))
    return {"pages": len(CHART_PAGES), "ticks": tick_count,
            "max_center_error_pt": round(largest_error, 6)}


def css_rules(text, scope=()):
    """Read CSS blocks including nested at-rules; keep their scope explicit."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    start, index = 0, 0
    while index < len(text):
        if text[index] != "{":
            index += 1
            continue
        selector = text[start:index].strip()
        depth, quote, cursor = 1, None, index + 1
        while cursor < len(text) and depth:
            char = text[cursor]
            if quote:
                if char == "\\":
                    cursor += 2
                    continue
                if char == quote:
                    quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        require(depth == 0, "Unbalanced CSS braces")
        body = text[index + 1:cursor - 1]
        if selector.startswith("@"):
            if "{" in body:
                yield from css_rules(body, scope + (selector,))
        else:
            declarations = {}
            for declaration in body.split(";"):
                if ":" in declaration:
                    name, value = declaration.split(":", 1)
                    declarations[name.strip().lower()] = value.strip()
            for item in selector.split(","):
                yield item.strip(), declarations, scope
        start = index = cursor


def check_html_columns(soup, html_path, slides):
    links = soup.select('link[rel="stylesheet"][href]')
    chapter_rules, all_rules = [], []
    linked_names = []
    for link in links:
        url = urlsplit(link["href"])
        require(not url.scheme and not url.netloc, "Expected local slide stylesheets")
        css_path = (html_path.parent / unquote(url.path)).resolve()
        rules = list(css_rules(css_path.read_text(encoding="utf-8")))
        all_rules.extend(rules)
        linked_names.append(css_path.name)
        if css_path.name == "ch2-slides.css":
            chapter_rules.extend(rules)
    require("slides.css" in linked_names and "ch2-slides.css" in linked_names,
            "HTML must load both shared and chapter-two stylesheets")
    require(linked_names.index("ch2-slides.css") > linked_names.index("slides.css"),
            "Chapter stylesheet must follow the shared stylesheet")
    overrides = [props for selector, props, scope in chapter_rules
                 if " ".join(selector.split()) == "#deck .items.columns" and not scope]
    require(overrides, "Missing unconditional chapter CSS rule: #deck .items.columns")
    values = [props["grid-template-columns"] for props in overrides
              if "grid-template-columns" in props]
    require(values and normalized(values[-1]) == "repeat(2,minmax(0,1fr))",
            "#deck .items.columns must declare grid-template-columns:repeat(2,minmax(0,1fr))")
    require(any(selector == ".items.columns" and props.get("display") == "grid" and not scope
                for selector, props, scope in all_rules)
            or any(props.get("display") == "grid" for props in overrides),
            "Column items must also have an unconditional display:grid declaration")
    pages = []
    for page_no in COLUMN_PAGES:
        section = soup.select_one(f'#deck section[data-slide="{page_no}"]')
        require(section is not None, f"HTML p{page_no}: missing slide")
        columns = section.select(".items.columns")
        require(len(columns) == 1, f"HTML p{page_no}: expected one .items.columns container")
        articles = columns[0].find_all("article", recursive=False)
        require(len(articles) == len(slides[page_no - 1]["items"]) == 2,
                f"HTML p{page_no}: two-column container must contain exactly two items")
        require(not columns[0].get("style"), f"HTML p{page_no}: unexpected inline column styling")
        pages.append(page_no)
    return {"pages": pages, "check": "DOM and CSS declarations; not browser layout"}


def check_svg_points(soup, slides):
    errors, circle_count = [], 0
    for page_no in CHART_PAGES:
        slide = slides[page_no - 1]
        svgs = soup.select(f'#deck section[data-slide="{page_no}"] .chart-layout svg')
        require(len(svgs) == 1, f"HTML p{page_no}: expected one chart SVG")
        svg = svgs[0]
        require(svg.get("viewbox") == "0 0 690 355", f"SVG p{page_no}: unexpected viewBox")
        xmin, xmax, ymin, ymax = data_bounds(slide)
        expected = []
        for series_index, series in enumerate(slide["series"]):
            points = series["points"]
            if len(points) > 10 and not series.get("scatter"):
                continue
            offset = ((series_index - (len(slide["series"]) - 1) / 2) * 12
                      if slide.get("chartmode") == "stem" else 0)
            for x, y in points:
                expected.append((65 + (x - xmin) / (xmax - xmin) * 560 + offset,
                                 285 - (y - ymin) / (ymax - ymin) * 240,
                                 SERIES_COLORS[series_index % len(SERIES_COLORS)]))
        actual = []
        for circle in svg.find_all("circle"):
            cx, cy, radius = (float(circle.get(key, "nan")) for key in ("cx", "cy", "r"))
            require(all(math.isfinite(v) for v in (cx, cy, radius)) and radius > 0,
                    f"SVG p{page_no}: invalid circle attributes {circle.attrs}")
            require(not circle.get("transform") and not circle.get("style"),
                    f"SVG p{page_no}: unexpected marker transform/style")
            actual.append((cx, cy, circle.get("fill", "").lower()))
        circle_count += len(actual)
        if len(actual) != len(expected):
            errors.append(f"SVG p{page_no}: {len(actual)} circles, expected {len(expected)}")
        remaining = list(actual)
        for x, y, color in expected:
            found = next((i for i, (cx, cy, fill) in enumerate(remaining)
                          if fill == color and abs(cx - x) <= SVG_TOLERANCE
                          and abs(cy - y) <= SVG_TOLERANCE), None)
            if found is None:
                errors.append(f"SVG p{page_no}: missing {color} circle at ({x:.3f}, {y:.3f})")
            else:
                remaining.pop(found)
        if remaining:
            errors.append(f"SVG p{page_no}: {len(remaining)} unexpected/misaligned circles")
    require(not errors, "\n".join(errors))
    return {"pages": len(CHART_PAGES), "circles": circle_count, "coordinate_tolerance": SVG_TOLERANCE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=ROOT / "output/pdf/第二章-确定型决策分析.pdf")
    parser.add_argument("--html", type=Path, default=ROOT / "course-site/dist/ch2/slides.html")
    args = parser.parse_args()
    slides = json.loads((ROOT / "content/chapter-02-slides.json").read_text(encoding="utf-8"))
    actual_chart_pages = tuple(i for i, slide in enumerate(slides, 1) if slide["type"] == "chart")
    require(actual_chart_pages == CHART_PAGES, f"Chart page inventory changed: {actual_chart_pages}")
    soup = BeautifulSoup(args.html.read_text(encoding="utf-8"), "html.parser")
    results, failures = {}, {}
    checks = {
        "pdf_tick_alignment": lambda: check_pdf_ticks(args.pdf, slides),
        "html_two_columns": lambda: check_html_columns(soup, args.html.resolve(), slides),
        "svg_discrete_points": lambda: check_svg_points(soup, slides),
    }
    for name, check in checks.items():
        try:
            results[name] = check()
        except (ValueError, OSError) as exc:
            failures[name] = str(exc).splitlines()
    print(json.dumps({"status": "failed" if failures else "passed", "checks": results,
                      "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
