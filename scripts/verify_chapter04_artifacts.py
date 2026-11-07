"""Static source/output consistency checks, not browser or DOM testing."""
from pathlib import Path
import json,re,hashlib,fitz
R=Path(__file__).resolve().parents[1];D=R/'course-site/dist'
s=json.loads((R/'content/chapter-04-slides.json').read_text(encoding='utf-8'))
assert len(s)==34 and sum(not x.get('appendix')for x in s)==24
assert all(x['notes'].strip() for x in s)
p=R/'output/pdf/第四章-不确定型决策分析.pdf'
with fitz.open(p) as doc:
    assert len(doc)==34
    assert all(page.rect.width==1280 and page.rect.height==720 for page in doc)
    assert all(page.get_text().strip()for page in doc)
assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((D/'downloads/chapter-04.pdf').read_bytes()).digest()
html=(D/'ch4/index.html').read_text(encoding='utf-8');js=(D/'assets/ch4.js').read_text(encoding='utf-8')
ids=set(re.findall(r'id="([^"]+)"',html));refs=set(re.findall(r"\$\('([^']+)'\)",js))
assert not refs-ids,refs-ids
assert html.index('ch4-model.js')<html.index('ch4.js')
assert html.count('id="alpha-exact"')==1
assert not re.search(r'https?://[^"\s]+\.js',html)
print(json.dumps({'pdf_pages':34,'slides_with_notes':len(s),'static_script_ids_verified':len(refs),'pdf_copies_identical':True,'status':'passed'}))
