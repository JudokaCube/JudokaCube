"""Generate readable, narrow profile cards from the desktop content."""
from pathlib import Path
from html import escape
import textwrap
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

def card(title, rows):
    y=76; body=[]
    for label,value in rows:
        body.append(f'<text x="20" y="{y}" fill="#88C0D0" font-size="14">{escape(label)}</text>');y+=25
        for line in textwrap.wrap(value,29):
            body.append(f'<text x="20" y="{y}" fill="#D8DEE9" font-size="17">{escape(line)}</text>');y+=24
        y+=14
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="{y}" viewBox="0 0 360 {y}" role="img"><title>{escape(title)}</title>
<rect x=".5" y=".5" width="359" height="{y-1}" rx="10" fill="#2E3440" stroke="#4C566A"/>
<path d="M20 48 H340" stroke="#B48EAD" opacity=".6"/>
<g font-family="monospace"><text x="20" y="31" font-size="18" fill="#88C0D0" font-weight="bold">{escape(title)}</text>{''.join(body)}</g></svg>'''

def texts(path):
    return [''.join(e.itertext()).strip() for e in ET.parse(path).iter() if e.tag.endswith('}text')]

def generate():
    about=texts(ROOT/'about.svg')
    rows=[tuple(t.split(': ',1)) for t in about if ': ' in t and not t.startswith('jdkcube')]
    (ROOT/'assets/about-mobile.svg').write_text(card('about.txt',rows))
    setup=texts(ROOT/'fastfetch.svg');rows=[]
    for key in ('OS','Dotfiles','Packages','Uptime','CPU','GPU','Memory','Disk'):
        rows.append((key,setup[setup.index(key)+1]))
    (ROOT/'assets/setup-mobile.svg').write_text(card('Setup / fastfetch',rows))
    stats=ET.parse(ROOT/'assets/stats.svg');rows=[]
    for key,label in [('stars','Stars earned'),('commits','Commits (last year)'),('prs','Pull requests'),('issues','Issues'),('contribs','Repositories contributed to')]:
        e=next(e for e in stats.iter() if e.get('data-testid')==key)
        rows.append((label,''.join(e.itertext()).strip()))
    rank=next(e for e in stats.iter() if e.get('data-testid')=='level-rank-icon')
    rows.append(('Rank',''.join(rank.itertext()).strip()))
    (ROOT/'assets/stats-mobile.svg').write_text(card('GitHub stats',rows))
    langs=ET.parse(ROOT/'assets/languages.svg');rows=[]
    for e in langs.iter():
        if e.get('data-testid')=='lang-name':
            name,value=''.join(e.itertext()).strip().rsplit(' ',1);rows.append((name,value))
    (ROOT/'assets/languages-mobile.svg').write_text(card('Most used languages',rows))

if __name__=='__main__': generate()
