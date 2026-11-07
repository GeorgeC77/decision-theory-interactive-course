"""Static source checks and PDF content checks; no browser/DOM automation."""
from pathlib import Path
import hashlib,json,re,fitz
from reportlab.pdfbase.ttfonts import TTFont
from chapter02_charts import pdf_math
R=Path(__file__).resolve().parents[1];D=R/'course-site/dist'
s=json.loads((R/'content/chapter-06-slides.json').read_text(encoding='utf-8'))
assert len(s)==72 and sum(not x.get('appendix')for x in s)==54
assert all(x['notes'].strip()for x in s)
p=R/'output/pdf/第六章-序贯决策分析.pdf'
with fitz.open(p)as doc:
    assert len(doc)==72
    assert all(page.rect.width==1280 and page.rect.height==720 for page in doc)
    assert all(page.get_text().strip()for page in doc)
assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((D/'downloads/chapter-06.pdf').read_bytes()).digest()
page=(D/'ch6/index.html').read_text(encoding='utf-8');js=(D/'assets/ch6.js').read_text(encoding='utf-8')
ids=set(re.findall(r'id="([^"]+)"',page));refs=set(re.findall(r"\$\('([^']+)'\)",js));assert not refs-ids,refs-ids
for prefix,fields in [('b',['horizon','initial','good','worn','cost','terminal']),('t',['prior','sensitivity','specificity','revenue','investment','cost','aversion','mode']),('m',['horizon','initial','r0','r1','cost','beta','g0','g1','p00','p01','p10','p11'])]:
    for field in fields:assert prefix+'-'+field in ids
assert page.index('ch6-model.js')<page.index('ch6.js')
assert not re.search(r'https?://[^"\s]+\.js',page)
font=TTFont('qa','C:/Windows/Fonts/msyh.ttc',subfontIndex=0)
def texts(x):
    if isinstance(x,str):yield x
    elif isinstance(x,list):
        for item in x:yield from texts(item)
    elif isinstance(x,dict):
        for k,v in x.items():
            if k!='notes':yield from texts(v)
missing=set()
for t in texts(s):
    for char in re.sub('<[^>]+>','',pdf_math(t)):
        if ord(char)>127 and ord(char)not in font.face.charToGlyph:missing.add(char)
assert not missing,missing
assert '???' not in js and '\ufffd' not in js
for f in ['chapter-06-task.md','chapter-06-teacher.md','chapter-06-coverage.md','chapter06_reference.py','chapter-06-reference.json']:assert (D/'downloads'/f).stat().st_size>100
print(json.dumps({'pdf_pages':72,'main_slides':54,'notes':72,'script_literal_ids':len(refs),'missing_glyphs':0,'pdf_copies_identical':True,'status':'passed'}))
