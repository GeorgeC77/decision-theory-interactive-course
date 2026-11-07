"""Create chapter-two renderer from the established chapter-one design."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'scripts/build_chapter01.py').read_text(encoding='utf-8')
for a,b in [('chapter-one','chapter-two'),('chapter-01','chapter-02'),('第一章','第二章'),('决策分析概述','确定型决策分析'),('ch1/slides','ch2/slides'),('pdf-layout-checks','ch2-pdf-layout-checks'),('2 学时','4 学时')]:s=s.replace(a,b)
s=s.replace("para('决策分析\\n概述'","para('确定型\\n决策分析'")
s=s.replace('决策分析<br>概述','确定型<br>决策分析')
s=s.replace('谁在选择？依据是什么？\\n条件变了怎么办？','现金流如何比较？\\n多投的钱是否值得？')
s=s.replace('谁在选择？依据是什么？<br>条件变了怎么办？','现金流如何比较？<br>多投的钱是否值得？')
s=s.replace("from pathlib import Path","from pathlib import Path\nfrom chapter02_charts import draw_chart, chart_html, pdf_math")
s=s.replace("safe=html.escape(str(text)).replace('\\n','<br/>')","safe=pdf_math(text)")
s=s.replace("Paragraph(html.escape(text),ParagraphStyle", "Paragraph(pdf_math(text),ParagraphStyle")
s=s.replace("elif typ=='equations':render_equations(s)","elif typ=='equations':render_equations(s)\n        elif typ=='chart':draw_chart(s,c,para,line,H)")
s=s.replace("t=s['type']\n    if t=='cover'","t=s['type']\n    if t=='chart':return chart_html(s)\n    if t=='cover'")
s=s.replace("classes='slide '+s['type']", "classes='slide '+s['type']+(' active' if i==1 else '')")
s=s.replace('href="../assets/slides.css"','href="../assets/slides.css"><link rel="stylesheet" href="../assets/ch2-slides.css"')
s=s.replace('<main id="deck">','<main id="deck" data-chapter="第二章">')
s=s.replace("(SITE / 'downloads').mkdir(exist_ok=True)","(SITE / 'downloads').mkdir(exist_ok=True)\n(SITE / 'ch2').mkdir(exist_ok=True)")
(root/'scripts/build_chapter02.py').write_text(s,encoding='utf-8')
