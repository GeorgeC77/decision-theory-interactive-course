"""Verify exact chapter-three axes without writing course artifacts.

Default: apply the visual specification in memory and inspect PDF drawing
commands plus generated SVG. --artifacts also checks the rebuilt PDF/HTML.
"""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from chapter02_charts import chart_html, draw_chart, geometry, vertical_ticks
from chapter03_visual_design import apply_visual_design

ROOT = Path(__file__).resolve().parents[1]
# Independent expected values: do not import the author's tick mapping.
EXPECTED = {
    7: [-10, -5, 0, 5, 10, 15, 20],
    12: [0, 5, 10, 15, 20],
    21: [0, 200, 400, 600, 800],
    31: [0, 2, 4, 6, 8, 10],
    40: [-10, -5, 0, 5, 10, 15, 20],
    43: [0, .25, .5, .75, 1],
}
COLORS = ['#244e79', '#bb8637', '#24664d']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def near(actual, expected, message, tolerance=1e-8):
    require(abs(actual-expected) <= tolerance, f'{message}: {actual} != {expected}')


def check_specs(slides):
    for page, ticks in EXPECTED.items():
        s = slides[page-1]
        require(s.get('yticks') == ticks, f'p{page}: missing or changed exact ticks')
        require(all(math.isfinite(t) for t in ticks), f'p{page}: non-finite tick')
        step = ticks[1]-ticks[0]
        for a, b in zip(ticks, ticks[1:]):
            near(b-a, step, f'p{page}: ticks are not equally spaced')
        _, _, lo, hi = geometry(s)
        require((lo, hi) == (ticks[0], ticks[-1]), f'p{page}: axis endpoints differ')
        require(all(lo <= y <= hi for series in s['series'] for _, y in series['points']),
                f'p{page}: axis clips data')


def svg_root(fragment):
    return ET.fromstring(re.search(r'<svg\b.*?</svg>', fragment, re.S).group())


def check_svg(s, page, svg):
    ticks = EXPECTED[page]
    lo, hi = ticks[0], ticks[-1]
    Y = lambda value: 285-(value-lo)/(hi-lo)*240
    grids = [e for e in svg.findall('line') if e.get('stroke') == '#dce3e9']
    labels = [e for e in svg.findall('text') if e.get('text-anchor') == 'end']
    require(len(grids) == len(labels) == len(ticks), f'p{page}: SVG grid/label count')
    for value, grid, label in zip(ticks, grids, labels):
        near(float(label.text), value, f'p{page}: rounded SVG tick label', 0)
        near(float(grid.get('y1')), Y(value), f'p{page}: SVG grid position')
        near(float(grid.get('y2')), Y(value), f'p{page}: SVG grid alignment')
        near(float(label.get('y'))-5, Y(value), f'p{page}: SVG label position')
    points = [p for series in s['series'] for p in series['points']]
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    X = lambda value: 65+(value-xmin)/(xmax-xmin)*560
    for i, series in enumerate(s['series']):
        color = COLORS[i % len(COLORS)]
        if s.get('chartmode') == 'stem':
            lines = [e for e in svg.findall('line') if e.get('stroke') == color
                     and e.get('stroke-width') == '7']
            require(len(lines) == len(series['points']), f'p{page}: SVG stem count')
            offset = (i-(len(s['series'])-1)/2)*12
            for line, (x, y) in zip(lines, series['points']):
                near(float(line.get('x1')), X(x)+offset, f'p{page}: SVG state position')
                near(float(line.get('y1')), Y(0), f'p{page}: SVG stem zero')
                near(float(line.get('y2')), Y(y), f'p{page}: SVG stem value')
        else:
            line = next(e for e in svg.findall('polyline') if e.get('stroke') == color)
            actual = [tuple(map(float, pair.split(','))) for pair in line.get('points').split()]
            require(len(actual) == len(series['points']), f'p{page}: SVG point count')
            for (xx, yy), (x, y) in zip(actual, series['points']):
                near(xx, X(x), f'p{page}: SVG data x', .00501)
                near(yy, Y(y), f'p{page}: SVG data y', .00501)


class CanvasProbe:
    """Record coordinates passed to the PDF renderer, without creating a file."""
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def check_renderers(slides):
    check_specs(slides)
    for page, ticks in EXPECTED.items():
        s = slides[page-1]
        lo, hi = ticks[0], ticks[-1]
        Y = lambda value: 515-(value-lo)/(hi-lo)*255
        lines, paragraphs = [], []
        draw_chart(s, CanvasProbe(), lambda *a, **k: paragraphs.append(a),
                   lambda *a, **k: lines.append(a), 720)
        grids = [a for a in lines if a[4] == '#dce3e9']
        labels = [a for a in paragraphs if a[1] == 14]
        require(len(grids) == len(labels) == len(ticks), f'p{page}: PDF grid/label count')
        for value, grid, label in zip(ticks, grids, labels):
            near(float(label[0]), value, f'p{page}: rounded PDF tick label', 0)
            near(grid[1], Y(value), f'p{page}: PDF grid position')
            near(grid[3], Y(value), f'p{page}: PDF grid alignment')
            near(label[2]+12, Y(value), f'p{page}: PDF label position')
        points = [p for series in s['series'] for p in series['points']]
        xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
        X = lambda value: 122+(value-xmin)/(xmax-xmin)*620
        for i, series in enumerate(s['series']):
            plotted = [a for a in lines if a[4] == COLORS[i % len(COLORS)]]
            if s.get('chartmode') == 'stem':
                offset = (i-(len(s['series'])-1)/2)*12
                expected = [(X(x)+offset, Y(0), X(x)+offset, Y(y)) for x, y in series['points']]
            else:
                expected = [(X(a[0]), Y(a[1]), X(b[0]), Y(b[1]))
                            for a, b in zip(series['points'], series['points'][1:])]
            require(len(plotted) == len(expected), f'p{page}: PDF data segment count')
            for actual, wanted in zip(plotted, expected):
                for a, b in zip(actual[:4], wanted):
                    near(a, b, f'p{page}: PDF plotted data position')
        check_svg(s, page, svg_root(chart_html(s)))
    return {'pages': list(EXPECTED), 'exact_labels_and_positions': True,
            'data_positions_and_coverage': True, 'pdf_scope': 'drawing commands'}


def check_legacy_defaults():
    checked = 0
    for path in (ROOT/'content').glob('chapter-*-slides.json'):
        if path.name == 'chapter-03-slides.json':
            continue
        for s in json.loads(path.read_text(encoding='utf-8')):
            if s['type'] != 'chart' or 'yticks' in s:
                continue
            points = [p for series in s['series'] for p in series['points']]
            low, high = min(0, min(y for _, y in points)), max(0, max(y for _, y in points))
            span = high-low or 1
            lo, hi = s.get('ylimits', [low-span*.07, high+span*.13])
            require(geometry(s)[2:] == (lo, hi), f'{path.name}: default limits changed')
            old = [(lo+(hi-lo)*j/4, f'{lo+(hi-lo)*j/4:.1f}') for j in range(5)]
            require(vertical_ticks(s, lo, hi) == old, f'{path.name}: default ticks changed')
            checked += 1
    return {'other_chapter_charts': checked, 'defaults_unchanged': True}


def check_artifacts(slides):
    """Used by the main revision verifier after the parent rebuilds artifacts."""
    import fitz
    check_specs(slides)
    source = (ROOT/'course-site/dist/ch3/slides.html').read_text(encoding='utf-8')
    sections = re.findall(r'<section\b.*?</section>', source, re.S)
    with fitz.open(ROOT/'course-site/dist/downloads/chapter-03.pdf') as doc:
        for page, ticks in EXPECTED.items():
            check_svg(slides[page-1], page, svg_root(sections[page-1]))
            spans = [span for block in doc[page-1].get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']]
            labels = [span for span in spans if abs(span['bbox'][0]-14) < .1
                      and 245 < span['bbox'][1] < 530]
            require(len(labels) == len(ticks), f'p{page}: actual PDF tick count')
            for value, label in zip(ticks, labels):
                near(float(label['text']), value, f'p{page}: actual PDF label', 0)
                expected_y = 515-(value-ticks[0])/(ticks[-1]-ticks[0])*255
                near((label['bbox'][1]+label['bbox'][3])/2, expected_y,
                     f'p{page}: actual PDF label alignment', 1)
                require(any(item[0] == 'l' and abs(item[1].x-122) < .01
                            and abs(item[2].x-742) < .01
                            and abs(item[1].y-expected_y) < .01
                            and abs(item[2].y-expected_y) < .01
                            for drawing in doc[page-1].get_drawings()
                            for item in drawing['items']), f'p{page}: actual PDF grid position')
    return {'pages': list(EXPECTED), 'actual_pdf_and_html_axes': 'passed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', action='store_true')
    args = parser.parse_args()
    slides = json.loads((ROOT/'content/chapter-03-slides.json').read_text(encoding='utf-8'))
    planned = apply_visual_design(deepcopy(slides))
    results = {'renderers': check_renderers(planned), 'compatibility': check_legacy_defaults()}
    if args.artifacts:
        results['artifacts'] = check_artifacts(slides)
    print(json.dumps({'status': 'passed', 'checks': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
