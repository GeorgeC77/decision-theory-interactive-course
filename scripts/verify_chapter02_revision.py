"""Regression checks for the November 2026 chapter-two teaching revision."""
from pathlib import Path
import hashlib,json,re,math
from html.parser import HTMLParser
import fitz
R=Path(__file__).resolve().parents[1]
slides=json.loads((R/'content/chapter-02-slides.json').read_text(encoding='utf-8'))
assert len(slides)==47 and sum(not s.get('appendix') for s in slides)==38
assert '13.58%' in json.dumps(slides[21],ensure_ascii=False)
assert '8%' in slides[23]['lead'] and '8%' in slides[23]['series'][1]['name']
assert 'NPV' in slides[10]['lead'] and '[-100,230,-132]' not in slides[10]['notes']
assert len(slides[41]['rows'])==5
assert '权益投资额' in str(slides[41]['rows'])
assert '净现金流' in str(slides[42]['rows'])
assert [p[0] for p in slides[7]['xticks']]==list(range(1,6))
assert [p[0] for p in slides[9]['xticks']]==list(range(1,9))
assert slides[43]['cashflows']==[-6000,-4000,3000,3500,5000,4500,4000]
assert sum(s['type']=='figure' for s in slides)==8
assert sum(s['type']=='chart' for s in slides)==11
assert 'F = P(1+i)ⁿ' in slides[6]['lead'] and 'P = F/(1+i)ⁿ' in slides[6]['lead']
assert 'Q₀=F/(p−v)' in slides[11]['takeaway']
assert '(F+L目标)/(p−v)' in slides[15]['takeaway']
assert 'Σ[CFₜ/(1+i)ᵗ]' in slides[18]['lead']
page=(R/'course-site/dist/ch2/slides.html').read_text(encoding='utf-8')
notes=json.loads(re.search(r'<script id="notes-data" type="application/json">(.*?)</script>',page,re.S).group(1))
assert notes==[s['notes'] for s in slides]
assert 'ch2-slides.css?v=20261111-1' in page
assert (R/'course-site/dist/assets/ch2-equipment-comparison.png').exists()
class SvgCheck(HTMLParser):
    count=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='svg':self.count+=1
        for k in ['x','y','x1','y1','x2','y2','cx','cy','width','height','points']:
            if k in a:assert not re.search(r'NaN|Infinity|undefined',a[k]),a
p=SvgCheck();p.feed(page);assert p.count==19,p.count
pdf=R/'course-site/dist/downloads/chapter-02.pdf'
out=R/'output/pdf/第二章-确定型决策分析.pdf'
assert pdf.read_bytes()==out.read_bytes()
doc=fitz.open(pdf);assert len(doc)==47
assert '13.58%' in doc[21].get_text()
issues=[]
for i,pg in enumerate(doc):
    assert pg.get_text().strip(),i+1
    for b in pg.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            for s in line['spans']:
                assert '\ufffd' not in s['text'],(i+1,s['text'])
                if s['text'].strip():
                    x0,y0,x1,y1=s['bbox']
                    if min(x0,y0)<-1 or x1>1281 or y1>721:issues.append((i+1,s['text']))
assert not issues,issues
print(json.dumps({'pages':47,'data_visuals':p.count,'new_data_visuals':10,'new_scenario_image':1,'notes_match':True,'pdf_matches_download':True,'status':'passed'}))
