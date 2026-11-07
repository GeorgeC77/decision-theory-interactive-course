"""Non-browser route checks. Optional Sites token never written or printed."""
import sys,urllib.request
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765';token=sys.argv[2] if len(sys.argv)>2 else ''
paths=['/','/ch3/index.html','/ch4/index.html','/ch4/slides.html','/assets/ch4-model.js','/assets/ch4.js','/assets/ch4.css','/assets/ch4-slides.css','/downloads/chapter-04.pdf','/downloads/chapter-04-task.md','/downloads/chapter-04-teacher.md','/downloads/chapter-04-coverage.md']
for path in paths:
    req=urllib.request.Request(base+path,headers={'OAI-Sites-Authorization':'Bearer '+token} if token else {})
    with urllib.request.urlopen(req,timeout=30) as response:
        data=response.read();assert response.status==200
        if path.endswith('.pdf'):assert data.startswith(b'%PDF-')
        if path.endswith('.js'):assert b'<!doctype html' not in data.lower()
        print(path,response.status,len(data),response.headers.get('Content-Type'))
