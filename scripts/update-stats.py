#!/usr/bin/env python3
"""Refresh equal-sized profile cards with a Nord language palette."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import re
import hashlib
import time
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PALETTE = ['88C0D0', 'B48EAD', '81A1C1', '8FBCBB', 'A3BE8C', '5E81AC']
OPTIONS = dict(username='JudokaCube', card_width=460, hide_border='false',
               bg_color='2E3440', title_color='88C0D0', text_color='D8DEE9',
               icon_color='81A1C1', border_color='4C566A', disable_animations='true', cache_seconds=21600)

def prepare(kind):
    options = dict(OPTIONS)
    if kind == 'languages':
        options.update(layout='compact', langs_count=6)
        endpoint = 'top-langs/'
    else:
        options.update(show_icons='true')
        endpoint = ''
    url='https://github-stats-extended.vercel.app/api/' + endpoint + '?' + urlencode(options)
    for attempt in range(3):
        try:
            with urlopen(url, timeout=45) as response:svg=response.read().decode()
            break
        except (URLError, TimeoutError):
            if attempt==2:raise
            time.sleep(2**attempt)
    tree = ET.fromstring(svg)
    assert tree.tag.endswith('svg') and 'data-testid="main-card-body"' in svg, 'Invalid stats response'
    if kind == 'languages':
        assert 'data-testid="lang-name"' in svg, 'Missing language data'
        colors = list(dict.fromkeys(re.findall(r'<circle\b[^>]*fill="#([0-9a-fA-F]{6})"', svg)))
        assert 0 < len(colors) <= len(PALETTE)
        mapping = {color.lower(): PALETTE[i] for i, color in enumerate(colors)}
        svg = re.sub(r'fill="#([0-9a-fA-F]{6})"', lambda m: 'fill="#' + mapping.get(m[1].lower(), m[1]) + '"', svg)
    svg = re.sub(r'(<svg\s+width="460"\s+height=")\d+("\s+viewBox=")([^"]+)', r'\g<1>195\g<2>0 0 460 195', svg, count=1)
    svg = svg.replace('height="99%"', 'height="194"')
    svg = svg.replace('Total Commits (last year):', 'Commits (last year):').replace('Contributed to (last year):', 'Repos (last year):')
    svg = re.sub(r"(?:'Segoe UI'|\"Segoe UI\")[^;\n]*", "'JetBrains Mono', monospace", svg)
    svg = svg.replace('</style>', (ROOT / 'assets/stats-font.css').read_text() + '</style>', 1)
    svg = svg.replace('</style>', '\n* { animation: none !important; } .stagger { opacity: 1 !important; }\n</style>', 1)
    return align_card(svg,kind)


def align_card(svg,kind):
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    parsed = ET.fromstring(svg)
    assert parsed.attrib['width'] == '460' and parsed.attrib['height'] == '195'
    assert parsed.attrib['viewBox'] == '0 0 460 195'
    if kind=='stats':
        rank=next(e for e in parsed.iter() if e.get('data-testid')=='rank-circle')
        rank.set('transform','translate(373.5, 62.5)')
        for e in rank.iter():
            if e.tag.endswith('}circle'):
                e.set('cx','0');e.set('cy','0');e.set('style','transform-origin: 0px 0px;')
                offset=re.search(r'to\s*{\s*stroke-dashoffset:\s*([0-9.]+)',svg)
                if e.get('class')=='rank-circle' and offset:e.set('style','transform-origin: 0px 0px; stroke-dashoffset: '+offset[1]+';')
        circle=next(e for e in rank.iter() if e.tag.endswith('}circle'))
        grade=next(e for e in rank.iter() if e.get('data-testid')=='level-rank-icon')
        grade.set('x',circle.get('cx'));grade.set('y',circle.get('cy'))
        grade.set('text-anchor','middle');grade.set('dominant-baseline','central')
        for e in parsed.iter():
            if e.get('data-testid') in ('stars','commits','prs','issues','contribs'):
                e.set('x','275');e.set('text-anchor','end')
    else:
        for e in parsed.iter():
            if e.get('transform')=='translate(150, 0)':e.set('transform','translate(215, 0)')
    return ET.tostring(parsed,encoding='unicode')


def refresh_image_links():
    path=ROOT/'README.md';readme=path.read_text()
    def revision(match):
        asset=match[1]
        return asset+'?v='+hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()[:12]
    readme=re.sub(r'(assets/(?:stats|languages)(?:-mobile)?\.svg)(?:\?v=[a-f0-9]+)?',revision,readme)
    path.write_text(readme)

if __name__ == '__main__':
    cards = {kind: prepare(kind) for kind in ('stats', 'languages')}
    (ROOT / 'assets').mkdir(exist_ok=True)
    for kind, svg in cards.items():
        (ROOT / 'assets' / (kind + '.svg')).write_text(svg)

    import runpy
    runpy.run_path(str(ROOT / "scripts/mobile-cards.py"))["generate"]()

    refresh_image_links()
