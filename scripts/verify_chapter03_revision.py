"""Read-only regression checks for the November 2026 chapter-three revision.

Use env_Online_Lecture/python.exe -X utf8 scripts/verify_chapter03_revision.py.
Expected chart values are independently recomputed below; no authoring or
rendering module is imported. DOM/SVG checks do not claim browser visual QA.
"""
from collections import Counter
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
import fitz


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "course-site/dist"
CHART_PAGES = (7, 12, 21, 31, 40, 43)
FIGURES = {6: "emv", 10: "regret", 11: "perfect", 19: "late_choice",
           20: "strategy", 26: "frequencies", 28: "posterior_policy",
           30: "information", 36: "sampling", 42: "lottery",
           44: "certainty", 50: "oil"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(text):
    return re.sub(r"\s+", "", str(text)).translate(str.maketrans({
        "−": "-", "（": "(", "）": ")", "：": ":", "，": ",",
    }))


# These must occur in actual slide text, not merely in hidden speaker notes or
# in unused JSON fields left over after a slide changes to the figure renderer.
VISIBLE_REQUIREMENTS = {
    6: ("EMV(a)=Σp(θ)V(a,θ)", "风险中性", "7.2"),
    7: ("低客流（0）", "高客流（1）", "非连续数轴"),
    10: ("L(a,θ)=", "EOL(a)=Σp(θ)L(a,θ)", "3.2"),
    11: ("风险中性", "信息先于行动", "不改变可行行动集合", "EVPI=10.4-7.2=3.2"),
    13: ("SD=√[", "先对加权平方差求和，再开方", "28-21=7"),
    16: ("EMV5.6", "EMV7.2", "选大店"),
    18: ("P(前期好)=0.75", "P(后期好|前期好)=0.85", "P(后期好|前期差)=0.10", "不折现"),
    19: ("7×(0.85×150+0.15×10)-210=693", "7×(0.85×60+0.15×2)=359.1", "54.6"),
    20: ("551.75", "519.9", "0.75×693+0.25×54.6"),
    26: ("期望频数", "不是观测样本", "480", "120", "80", "320", "6/7"),
    28: ("6/7", "3/11", "3.6364", "0.0000"),
    30: ("EVSI=1.6", "净改善=1.1", "调查费0.5"),
    34: ("15000/-5000元", "P(好报告|成功)=0.95", "P(好报告|失败)=0.10"),
    36: ("有放回", "0.56453125", "1.5891625", "0.5891625"),
    39: ("需评估进一步信息是否值得",),
    42: ("货币期望同为5万元", "概率100%", "50%"),
    44: ("u(CE)=EU", "k=3", "CE=-3.5544", "u(5)=0.8176", "效用数值没有货币单位"),
    47: ("0.2/0.3/0.5", "0.2525", "0.524"),
    48: ("成功概率0.8", "7/-2", "12/-10", "0.924"),
    50: ("P(有油)=0.3", "万美元", "EVSI=8", "净价值16", "净改善=3"),
    57: ("风险中性", "信息可忽略", "不改变状态、损益和可行行动集合"),
    59: ("k=0:u(x)=z,CE=-10+30EU", "k≠0:CE=-10-(30/k)"),
    61: ("第6题有偏好回答冲突", "第7题缺少状态概率"),
}


def check_inventory(slides):
    require(len(slides) == 62, "Expected 62 slides")
    require(all(not s.get("appendix") for s in slides[:53])
            and all(s.get("appendix") for s in slides[53:]),
            "Expected 53 main slides followed by 9 appendix slides")
    counts = Counter(s["type"] for s in slides)
    require(counts["figure"] == 12 and counts["chart"] == 6 and counts["tree"] == 1
            and counts["scenario"] == 1 and counts["flow"] == 4,
            f"Unexpected visual inventory: {dict(counts)}")
    require(tuple(i for i, s in enumerate(slides, 1) if s["type"] == "chart") == CHART_PAGES,
            "Chart page inventory changed")
    for page_no, key in FIGURES.items():
        require(slides[page_no - 1].get("figure") == key,
                f"p{page_no}: missing expected figure {key}")
    require(slides[6].get("chartmode") == "stem"
            and [tick[0] for tick in slides[6].get("xticks", [])] == [0, 1],
            "p7 must show two discrete categories, not intermediate demand states")
    require("40/11" in slides[27]["notes"] and "36/11" not in slides[27]["notes"],
            "p28 speaker-note arithmetic correction was lost")
    require(all(term in slides[43]["notes"] for term in ("连续", "严格递增", "正仿射", "a>0")),
            "p44 must retain the CE conditions and positive affine transformation restriction")
    require(all(term in slides[60]["notes"] for term in ("0.65", "p=.02", "p=.03", "未给")),
            "p61 must retain textbook probability/elicitation caveats")
    return {"pages": 62, "main": 53, "appendix": 9, "types": dict(counts)}


def expected_chart_series():
    """Original teaching models, evaluated independently of renderer helpers."""
    # Include the exact kink: continuing past it is a different optimal action.
    expansion_costs = [*range(0, 541, 10), 543.9, *range(550, 701, 10)]
    return {
        7: [[(0, 2), (1, 8)], [(0, -6), (1, 16)]],
        12: [[(p, max(0, 2 + 0.06*p, -6 + 0.22*p)) for p in range(101)],
             [(p, 2 + 0.14*p) for p in range(101)]],
        21: [[(cost, 551.75) for cost in expansion_costs],
             [(cost, 677.4-0.75*cost if cost <= 543.9 else 269.475)
              for cost in expansion_costs]],
        31: [[(j/10, 8.8-j/10) for j in range(31)], [(0, 7.2), (3, 7.2)]],
        40: [[(p, 0) for p in range(101)],
             [(p, 2 + 0.06*p) for p in range(101)],
             [(p, -6 + 0.22*p) for p in range(101)]],
        43: [[(x, (x+10)/30 if k == 0 else
               math.expm1(-k*(x+10)/30)/math.expm1(-k))
              for x in range(-10, 21)] for k in (3, 0, -3)],
    }


def check_chart_values(slides):
    total, max_error = 0, 0.0
    for page_no, expected in expected_chart_series().items():
        actual = slides[page_no - 1]["series"]
        require(len(actual) == len(expected), f"p{page_no}: unexpected series count")
        for index, (series, points) in enumerate(zip(actual, expected)):
            require(len(series["points"]) == len(points), f"p{page_no} series {index}: point count changed")
            for (x, y), (expected_x, expected_y) in zip(series["points"], points):
                require(math.isfinite(x) and math.isfinite(y), f"p{page_no}: non-finite chart data")
                error = abs(y-expected_y)
                require(abs(x-expected_x) < 1e-12 and error < 1e-9,
                        f"p{page_no} series {index}: ({x}, {y}) != ({expected_x}, {expected_y})")
                max_error = max(max_error, error)
                total += 1
    require(total == 779, f"Expected 779 independently checked points, got {total}")
    return {"points": total, "max_absolute_error": max_error}


def check_visible(texts, artifact):
    missing = []
    for page_no, terms in VISIBLE_REQUIREMENTS.items():
        text = compact(texts[page_no])
        for term in terms:
            if compact(term) not in text:
                missing.append(f"{artifact} p{page_no}: missing visible {term!r}")
    require(not missing, "\n".join(missing))


def check_html(slides):
    path = SITE / "ch3/slides.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    sections = soup.select("#deck section[data-slide]")
    require([int(section["data-slide"]) for section in sections] == list(range(1, 63)),
            "HTML slide numbers must be exactly 1..62")
    note_tag = soup.select_one("script#notes-data")
    require(note_tag is not None, "Missing speaker-note data")
    require(json.loads(note_tag.string or note_tag.get_text()) == [s["notes"] for s in slides],
            "HTML notes are stale or do not match the content JSON")
    texts = {int(section["data-slide"]): section.get_text(" ", strip=True) for section in sections}
    check_visible(texts, "HTML")
    svg_count = 0
    for page_no, section in enumerate(sections, 1):
        svgs = section.find_all("svg")
        expected_count = int(slides[page_no - 1]["type"] in ("figure", "chart", "tree"))
        require(len(svgs) == expected_count, f"HTML p{page_no}: expected {expected_count} SVG(s)")
        svg_count += len(svgs)
        for svg in svgs:
            for element in [svg, *svg.find_all(True)]:
                for attribute in ("x", "y", "x1", "x2", "y1", "y2", "cx", "cy", "r",
                                  "width", "height", "points", "viewbox", "transform", "d"):
                    if attribute in element.attrs:
                        value = str(element[attribute])
                        require(not re.search(r"NaN|Infinity|undefined|\binf\b", value, flags=re.I),
                                f"HTML p{page_no}: invalid SVG {attribute}={value!r}")
    require(svg_count == 19, f"Expected 19 SVGs, got {svg_count}")
    image = sections[1].select_one(".scenario-visual img")
    require(image is not None and bool(image.get("alt")), "p2 must have the labelled scenario image")
    require((path.parent / unquote(urlsplit(image["src"]).path)).resolve().is_file(),
            "p2 scenario image is missing")
    styles = [urlsplit(link.get("href", "")).path for link in soup.select('link[rel="stylesheet"]')]
    require(any(url.endswith("/ch3-slides.css") for url in styles), "Chapter stylesheet is not linked")
    return {"svg_count": svg_count, "notes_match": True,
            "visible_requirement_pages": len(VISIBLE_REQUIREMENTS),
            "scenario_image": True, "scope": "DOM and SVG inspection, not browser layout"}


def check_pdf():
    output = ROOT / "output/pdf/第三章-风险型决策分析.pdf"
    download = SITE / "downloads/chapter-03.pdf"
    require(output.read_bytes() == download.read_bytes(), "PDF download differs from generated PDF")
    issues, texts, span_count = [], {}, 0
    with fitz.open(download) as doc:
        require(len(doc) == 62, f"Expected 62 PDF pages, got {len(doc)}")
        for page_no, page in enumerate(doc, 1):
            require(abs(page.rect.width-1280) < 0.1 and abs(page.rect.height-720) < 0.1,
                    f"PDF p{page_no}: unexpected page dimensions")
            text = page.get_text()
            require(text.strip(), f"PDF p{page_no}: no extractable text")
            texts[page_no] = text
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if not span["text"].strip():
                            continue
                        span_count += 1
                        if "\ufffd" in span["text"] or "\x00" in span["text"]:
                            issues.append(f"PDF p{page_no}: missing/replacement character in {span['text']!r}")
                        x0, y0, x1, y1 = span["bbox"]
                        if min(x0, y0) < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                            issues.append(f"PDF p{page_no}: text outside page: {span['text']!r} {span['bbox']}")
            # Glyph 0 is the font's missing-glyph slot. Exclude whitespace.
            for trace in page.get_texttrace():
                for codepoint, glyph_id, *_ in trace["chars"]:
                    if glyph_id == 0 and chr(codepoint).strip():
                        issues.append(f"PDF p{page_no}: missing glyph for U+{codepoint:04X}")
    require(not issues, "\n".join(issues))
    check_visible(texts, "PDF")
    return {"pages": 62, "pdf_matches_download": True, "text_spans": span_count,
            "text_bounds": "passed", "missing_glyphs": 0,
            "visible_requirement_pages": len(VISIBLE_REQUIREMENTS)}


def main():
    slides = json.loads((ROOT / "content/chapter-03-slides.json").read_text(encoding="utf-8"))
    results, failures = {}, {}
    checks = {"inventory": lambda: check_inventory(slides),
              "independent_chart_values": lambda: check_chart_values(slides),
              "html": lambda: check_html(slides), "pdf": check_pdf}
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
