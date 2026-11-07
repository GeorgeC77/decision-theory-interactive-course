from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re, json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'course-site/dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[];self.ids=[];self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.append(a['id'])
        for k in ['href','src']:
            if k in a:self.refs.append(a[k])
        if tag=='img':self.images.append(a)
pages={}
for path in SITE.rglob('*.html'):
    parser=Page();parser.feed(path.read_text(encoding='utf-8'));pages[path.resolve()]=parser
    assert len(parser.ids)==len(set(parser.ids)),f'Duplicate id: {path}'
    assert all('alt'in a and a['alt'] for a in parser.images),f'Missing image alt: {path}'
checked=0
for path,parser in pages.items():
    for ref in parser.refs:
        u=urlsplit(ref)
        if u.scheme or ref.startswith('//'):continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/'index.html'
        assert target.is_relative_to(SITE.resolve()),f'Outside site: {ref}'
        assert target.exists(),f'Missing asset from {path.name}: {ref}'
        if u.fragment and target in pages:assert u.fragment in pages[target].ids or u.fragment.isdigit(),f'Missing anchor: {ref}'
        checked+=1
for css in SITE.rglob('*.css'):
    for ref in re.findall(r'url\([\"\']?([^\)\"\']+)',css.read_text(encoding='utf-8')):
        assert (css.parent/ref).exists(),f'Missing CSS asset {ref}'
print(json.dumps({'html_pages':len(pages),'local_references_checked':checked,'status':'passed'},ensure_ascii=False))
