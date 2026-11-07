from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/build_chapter03.py').read_text(encoding='utf-8')
for a,b in [('chapter-three','chapter-four'),('chapter-03','chapter-04'),('第三章','第四章'),('风险型','不确定型'),("'ch3'","'ch4'"),('ch3/slides','ch4/slides'),('ch3-pdf','ch4-pdf'),('ch3-slides.css','ch4-slides.css'),('8 学时','2 学时'),('客流不确定，怎么选？','没有可靠概率，怎么选？'),('调查与风险如何评价？','五种准则如何辩护？')]:s=s.replace(a,b)
s=s.replace('from chapter03_tree import draw_tree, tree_html','from chapter03_tree import draw_tree, tree_html\nfrom chapter04_visuals import draw_visual, visual_html')
s=s.replace("elif typ=='tree':draw_tree(c,para,line,rect,H)","elif typ=='tree':draw_tree(c,para,line,rect,H)\n        elif typ in ['heatmap','interval']:draw_visual(s,c,para,line,rect,H)")
s=s.replace("if t=='tree':return tree_html()","if t=='tree':return tree_html()\n    if t in ['heatmap','interval']:return visual_html(s)")
(R/'scripts/build_chapter04.py').write_text(s,encoding='utf-8')
s=(R/'scripts/render_chapter03_review.py').read_text(encoding='utf-8').replace('ch3-review','ch4-review').replace('第三章-风险型','第四章-不确定型')
(R/'scripts/render_chapter04_review.py').write_text(s,encoding='utf-8')
(R/'course-site/dist/assets/ch4-slides.css').write_text((R/'course-site/dist/assets/ch2-slides.css').read_text(encoding='utf-8')+'\n.interval .slide-body svg{width:100%;height:100%}.value-matrix td{background:#eaf1f8;font-weight:700}.heatmap .slide-body{top:31%;height:48%}\n',encoding='utf-8')
