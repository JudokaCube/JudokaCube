import hashlib,runpy,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Stats(unittest.TestCase):
 def test_rank_is_centered(self):
  root=ET.parse(ROOT/'assets/stats.svg')
  rank=next(e for e in root.iter() if e.get('data-testid')=='rank-circle')
  grade=next(e for e in rank.iter() if e.get('data-testid')=='level-rank-icon')
  for circle in (e for e in rank.iter() if e.tag.endswith('}circle')):
   self.assertEqual((grade.get('x'),grade.get('y')),(circle.get('cx'),circle.get('cy')))
   self.assertEqual(circle.get('cx'),'0');self.assertEqual(circle.get('cy'),'0')
 def test_image_urls_match_contents(self):
  readme=(ROOT/'README.md').read_text()
  for name in ('stats','languages','stats-mobile','languages-mobile'):
   path='assets/'+name+'.svg';revision=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
   self.assertIn(path+'?v='+revision,readme)
 def test_mobile_stats_match_desktop(self):
  desktop=ET.parse(ROOT/'assets/stats.svg');mobile=ET.parse(ROOT/'assets/stats-mobile.svg')
  texts=[''.join(e.itertext()).strip() for e in mobile.iter() if e.tag.endswith('}text')]
  for e in desktop.iter():
   if e.get('data-testid') in ('stars','commits','prs','issues','contribs','level-rank-icon'):self.assertIn(''.join(e.itertext()).strip(),texts)
 def test_desktop_cards_have_same_size(self):
  for name in ('stats','languages'):
   root=ET.parse(ROOT/'assets'/(name+'.svg')).getroot();self.assertEqual((root.get('width'),root.get('height'),root.get('viewBox')),('460','195','0 0 460 195'))
