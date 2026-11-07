"""Read-only route checks; optional Sites token is kept out of files/output."""
import sys,urllib.request
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
token=sys.argv[2] if len(sys.argv)>2 else ''
paths=['/','/ch1/index.html','/ch2/index.html','/ch2/slides.html','/assets/ch2-model.js','/assets/ch2.js','/assets/ch2.css','/assets/ch2-slides.css','/downloads/chapter-02.pdf','/downloads/chapter-02-task.md']
for path in paths:
    req=urllib.request.Request(base+path,headers={'OAI-Sites-Authorization':'Bearer '+token} if token else {})
    with urllib.request.urlopen(req,timeout=30) as response:
        data=response.read()
        assert response.status==200
        if path.endswith('.pdf'):assert data.startswith(b'%PDF-')
        if path.endswith('.js'):assert b'<!doctype html' not in data.lower()
        if path=='/ch2/index.html':assert '现金流时间机器'.encode() in data
        print(path,response.status,len(data),response.headers.get('Content-Type'))
