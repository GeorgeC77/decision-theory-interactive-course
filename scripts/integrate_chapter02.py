"""Connect the completed chapter to existing local entrypoints."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
p=root/'course-site/dist/index.html';s=p.read_text(encoding='utf-8')
pattern=r'<article class="chapter-card"><div class="card-top"><span class="chapter-no">02</span>.*?</article>'
replacement='<a class="chapter-card available" href="ch2/index.html"><div class="card-top"><span class="chapter-no">02</span><span class="availability">可以学习 · 4 学时</span></div><h3>确定型决策分析</h3><p>条件已知，哪个方案值得做？</p><div class="chapter-topics">时间价值 / 盈亏 / 投资与预算</div><span class="card-action">打开交互实验 →</span></a>'
if re.search(pattern,s):s=re.sub(pattern,replacement,s)
else:assert 'href="ch2/index.html"' in s,'Chapter two card not found'
s=s.replace('本次开放门户与第一章，其余章节待建设。','已开放第一、二章，其余章节待建设。')
s=s.replace('<a href="ch1/index.html">第一章学习</a>','<a href="ch1/index.html">第一章</a><a href="ch2/index.html">第二章</a>')
p.write_text(s,encoding='utf-8')
p=root/'course-site/dist/assets/slides.js';s=p.read_text(encoding='utf-8')
s=s.replace('· 第一章教学演示','· ${byId(\'deck\').dataset.chapter||\'第一章\'}教学演示')
s=s.replace("history.replaceState(null,'','#'+(current+1));","try{history.replaceState(null,'','#'+(current+1));}catch{}")
p.write_text(s,encoding='utf-8')
p=root/'打开课程.html';s=p.read_text(encoding='utf-8')
if 'ch2/index.html' not in s:s=s.replace('</ul>','  <li><a href="course-site/dist/ch2/index.html">第二章交互学习</a></li>\n  </ul>')
p.write_text(s,encoding='utf-8')
