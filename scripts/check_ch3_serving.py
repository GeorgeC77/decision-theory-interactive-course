"""Check local or authorized hosted routes. Tokens remain only in process memory."""
import sys,urllib.request
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8765'
token=sys.argv[2] if len(sys.argv)>2 else ''
paths=['/','/ch1/index.html','/ch2/index.html','/ch3/index.html','/ch3/slides.html','/assets/ch3-model.js','/assets/ch3.js','/assets/ch3.css','/assets/ch3-slides.css','/downloads/chapter-03.pdf','/downloads/chapter-03-task.md','/downloads/chapter-03-teacher.md']
for path in paths:
    req=urllib.request.Request(base+path,headers={'OAI-Sites-Authorization':'Bearer '+token} if token else {})
    with urllib.request.urlopen(req,timeout=30) as response:
        data=response.read();assert response.status==200
        if path.endswith('.pdf'):assert data.startswith(b'%PDF-')
        if path.endswith('.js'):assert b'<!doctype html' not in data.lower()
        if path=='/ch3/index.html':assert '期望与随机结果'.encode() in data
        print(path,response.status,len(data),response.headers.get('Content-Type'))
