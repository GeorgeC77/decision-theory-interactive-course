"""Read-only HTTP checks. Optional owner-private Sites token is not printed/stored."""
import sys,urllib.request
base=sys.argv[1]if len(sys.argv)>1 else 'http://127.0.0.1:8765';token=sys.argv[2]if len(sys.argv)>2 else ''
paths=['/','/ch5/index.html','/ch6/index.html','/ch6/slides.html','/assets/ch6-model.js','/assets/ch6.js','/assets/ch6.css','/assets/ch6-slides.css','/downloads/chapter-06.pdf','/downloads/chapter-06-task.md','/downloads/chapter-06-teacher.md','/downloads/chapter-06-coverage.md','/downloads/chapter06_reference.py','/downloads/chapter-06-reference.json']
opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) if base.startswith('http://127.0.0.1:') else urllib.request.build_opener()
for path in paths:
    req=urllib.request.Request(base+path,headers={'OAI-Sites-Authorization':'Bearer '+token}if token else {})
    with opener.open(req,timeout=30)as response:
        data=response.read();assert response.status==200
        if path.endswith('.pdf'):assert data.startswith(b'%PDF-')
        if path.endswith('.js'):assert b'<!doctype html'not in data.lower()
        print(path,response.status,len(data),response.headers.get('Content-Type'),flush=True)
