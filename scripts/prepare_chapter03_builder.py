from pathlib import Path
r=Path(__file__).resolve().parents[1]
s=(r/'scripts/build_chapter02.py').read_text(encoding='utf-8')
for a,b in [('chapter-two','chapter-three'),('chapter-02','chapter-03'),('第二章','第三章'),('确定型','风险型'),("'ch2'","'ch3'"),('ch2/slides','ch3/slides'),('ch2-pdf','ch3-pdf'),('ch2-slides.css','ch3-slides.css'),('4 学时','8 学时'),('现金流如何比较？','客流不确定，怎么选？'),('多投的钱是否值得？','调查与风险如何评价？')]:s=s.replace(a,b)
s=s.replace("ratios=[.23,.38,.39] if len(data[0])==3 else [.3,.7]","ratios=[.23,.38,.39] if len(data[0])==3 else ([1/len(data[0])]*len(data[0]) if len(data[0])>3 else [.3,.7])")
s=s.replace('from chapter02_charts import draw_chart, chart_html, pdf_math','from chapter02_charts import draw_chart, chart_html, pdf_math\nfrom chapter03_tree import draw_tree, tree_html')
s=s.replace("elif typ=='chart':draw_chart(s,c,para,line,H)","elif typ=='chart':draw_chart(s,c,para,line,H)\n        elif typ=='tree':draw_tree(c,para,line,rect,H)")
s=s.replace("if t=='chart':return chart_html(s)","if t=='chart':return chart_html(s)\n    if t=='tree':return tree_html()")
(r/'scripts/build_chapter03.py').write_text(s,encoding='utf-8')
s=(r/'scripts/render_chapter02_review.py').read_text(encoding='utf-8').replace('ch2-review','ch3-review').replace('第二章-确定型','第三章-风险型')
(r/'scripts/render_chapter03_review.py').write_text(s,encoding='utf-8')
(r/'course-site/dist/assets/ch3-slides.css').write_text((r/'course-site/dist/assets/ch2-slides.css').read_text(encoding='utf-8')+'\n.decision-diagram{width:100%;height:100%}.tree .slide-body{top:30%;height:49%}\n',encoding='utf-8')
