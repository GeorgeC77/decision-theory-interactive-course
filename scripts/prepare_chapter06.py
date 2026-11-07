from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
for src,dst in [('scripts/build_chapter05.py','scripts/build_chapter06.py'),('scripts/render_chapter05_review.py','scripts/render_chapter06_review.py')]:
    s=(R/src).read_text(encoding='utf-8')
    for a,b in [('chapter-five','chapter-six'),('chapter-05','chapter-06'),('第五章','第六章'),('多目标','序贯'),('ch5','ch6'),('多个目标，怎样取舍？','今天的选择如何影响明天？'),('偏好、效率与资源配置','条件策略、状态与群体意见')]:s=s.replace(a,b)
    (R/dst).write_text(s,encoding='utf-8')
(R/'course-site/dist/ch6').mkdir(exist_ok=True)
shutil.copyfile(R/'course-site/dist/assets/ch5-slides.css',R/'course-site/dist/assets/ch6-slides.css')
