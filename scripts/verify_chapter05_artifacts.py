"""Source/artifact consistency; deliberately not a browser/DOM test."""
from pathlib import Path
import hashlib,json,re,fitz
from reportlab.pdfbase.ttfonts import TTFont
from chapter02_charts import pdf_math
R=Path(__file__).resolve().parents[1];D=R/'course-site/dist'
s=json.loads((R/'content/chapter-05-slides.json').read_text(encoding='utf-8'))
assert len(s)==68 and sum(not x.get('appendix')for x in s)==54
assert all(x['notes'].strip()for x in s)
p=R/'output/pdf/第五章-多目标决策分析.pdf'
with fitz.open(p)as doc:
    assert len(doc)==68
    assert all(page.rect.width==1280 and page.rect.height==720 for page in doc)
    assert all(page.get_text().strip()for page in doc)
assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((D/'downloads/chapter-05.pdf').read_bytes()).digest()
html=(D/'ch5/index.html').read_text(encoding='utf-8');js=(D/'assets/ch5.js').read_text(encoding='utf-8')
ids=set(re.findall(r'id="([^"]+)"',html));refs=set(re.findall(r"\$\('([^']+)'\)",js))
assert not refs-ids,refs-ids
assert html.index('ch5-model.js')<html.index('ch5.js')
assert not re.search(r'https?://[^"\s]+\.js',html)
assert '???' not in js and '\ufffd' not in js
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
    for c in re.sub('<[^>]+>','',pdf_math(t)):
        if ord(c)>127 and ord(c)not in font.face.charToGlyph:missing.add(c)
assert not missing,missing
for f in ['chapter-05-task.md','chapter-05-teacher.md','chapter-05-coverage.md','chapter05_reference.py','chapter-05-reference.json']:
    assert (D/'downloads'/f).stat().st_size>100
print(json.dumps({'pdf_pages':68,'main_slides':54,'notes':68,'static_script_ids':len(refs),'missing_glyphs':0,'pdf_copies_identical':True,'status':'passed'}))
