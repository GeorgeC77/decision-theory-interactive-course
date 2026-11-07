from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/build_chapter04.py').read_text(encoding='utf-8')
for a,b in [('chapter-four','chapter-five'),('chapter-04','chapter-05'),('第四章','第五章'),('不确定型','多目标'),("'ch4'","'ch5'"),('ch4/slides','ch5/slides'),('ch4-pdf','ch5-pdf'),('ch4-slides.css','ch5-slides.css'),('2 学时','8 学时'),('没有可靠概率，怎么选？','多个目标，怎样取舍？'),('五种准则如何辩护？','偏好、效率与资源配置')]:s=s.replace(a,b)
# Tables use consistent readable body sizes; do not reduce below 20 for the main deck.
s=s.replace("19 if s.get('appendix') else 23","19 if s.get('appendix') else 21").replace("25 if s.get('appendix') else 33","25 if s.get('appendix') else 29")
(R/'scripts/build_chapter05.py').write_text(s,encoding='utf-8')
s=(R/'scripts/render_chapter04_review.py').read_text(encoding='utf-8').replace('ch4-review','ch5-review').replace('第四章-不确定型','第五章-多目标')
(R/'scripts/render_chapter05_review.py').write_text(s,encoding='utf-8')
(R/'course-site/dist/assets/ch5-slides.css').write_text((R/'course-site/dist/assets/ch2-slides.css').read_text(encoding='utf-8'),encoding='utf-8')
