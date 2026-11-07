"""Read-only structural audit; does not replace visual page review."""
from pathlib import Path
import hashlib,json
import fitz
R=Path(__file__).resolve().parents[1]
report=[]
for n in range(1,7):
    pdf=R/f'course-site/dist/downloads/chapter-{n:02}.pdf'
    doc=fitz.open(pdf)
    matches=[p for p in (R/'output/pdf').glob('*.pdf') if hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(pdf.read_bytes()).digest()]
    assert matches,f'No identical source PDF for chapter {n}'
    slides=json.loads((R/f'content/chapter-{n:02}-slides.json').read_text(encoding='utf-8'))
    assert len(doc)==len(slides),(n,len(doc),len(slides))
    issues=[]
    for i,page in enumerate(doc):
        text=page.get_text()
        if '\ufffd' in text or not text.strip():issues.append({'page':i+1,'issue':'missing or unreadable text'})
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if span['text'].strip() and (x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1):issues.append({'page':i+1,'issue':'text outside page','text':span['text']})
    report.append({'chapter':n,'pages':len(doc),'identical_download':True,'issues':issues})
(R/'tmp/course-pdf-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
assert not any(r['issues'] for r in report)
