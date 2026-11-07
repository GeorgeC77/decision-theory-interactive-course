"""Repair chart tick generation and separate the pure SVG builder for regression checks."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'course-site/dist/assets/ch6.js';s=p.read_text(encoding='utf-8')
old="const xt=ticks||Array.from({length:Math.min(7,Math.ceil(xmax)+1)},(_,i,a)=>[xmin+(xmax-xmin)*i/(a.length-1),F(xmin+(xmax-xmin)*i/(a.length-1),1)]);"
new="const tickCount=Math.min(7,Math.ceil(xmax)+1),xt=ticks||Array.from({length:tickCount},(_,i)=>[xmin+(xmax-xmin)*i/(tickCount-1),F(xmin+(xmax-xmin)*i/(tickCount-1),1)]);"
assert old in s
s=s.replace(old,new).replace('function chart(target,series,','function chartSVG(series,',1)
s=s.replace("$(target).innerHTML=svg;}\nfunction guarded", "return svg;}\nfunction chart(target,series,options){$(target).innerHTML=chartSVG(series,options);}\nfunction guarded",1)
assert 'return svg;'in s and 'function chart(target,series,options)'in s
p.write_text(s,encoding='utf-8')
for p in [R/'course-site/dist/ch6/index.html',R/'scripts/author_chapter06_web.py']:
    s=p.read_text(encoding='utf-8').replace('src="../assets/ch6.js?v=20260919-1"','src="../assets/ch6.js?v=20260919-1"')
    p.write_text(s,encoding='utf-8')
print('Fixed chart ticks and refreshed the script URL')
