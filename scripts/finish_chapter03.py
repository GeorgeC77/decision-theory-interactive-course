from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'course-site/dist/index.html';s=p.read_text(encoding='utf-8')
s=s.replace('<a href="ch2/index.html">第二章</a>','<a href="ch2/index.html">第二章</a><a href="ch3/index.html">第三章</a>') if 'href="ch3/index.html">第三章' not in s else s
old='<article class="chapter-card"><div class="card-top"><span class="chapter-no">03</span><span>规划中 · 8 学时</span></div><h3>风险型决策分析</h3><p>概率已知，如何权衡风险？</p><div class="chapter-topics">决策树 / 贝叶斯 / 效用</div></article>'
new='<a class="chapter-card available" href="ch3/index.html"><div class="card-top"><span class="chapter-no">03</span><span class="availability">可以学习 · 8 学时</span></div><h3>风险型决策分析</h3><p>概率已知，如何权衡风险？</p><div class="chapter-topics">期望与树 / 信息价值 / 抽样与效用</div><span class="card-action">打开交互实验 →</span></a>'
s=s.replace(old,new).replace('已开放第一、二章','已开放第一、二、三章')
s=s.replace('先把“开不开店”问清楚','把选择升级为有条件的策略').replace('明确谁在决策、想达到什么目标、有哪些选择，以及还缺少什么证据。','把投资比较加入概率、调查与风险偏好，解释何时改变选择。').replace('href="ch1/index.html#project">完成一页决策画布','href="ch3/index.html#project">完成 M3 风险决策项目')
p.write_text(s,encoding='utf-8')
p=r/'course-site/dist/ch2/index.html';s=p.read_text(encoding='utf-8').replace('<a href="../index.html">课程地图 →</a></div></main>','<a href="../ch3/index.html">第三章 →</a></div></main>');p.write_text(s,encoding='utf-8')
p=r/'打开课程.html';s=p.read_text(encoding='utf-8')
if 'ch3/index.html' not in s:s=s.replace('</body>','<p><a href="course-site/dist/ch3/index.html">第三章：风险型决策分析</a></p></body>')
p.write_text(s,encoding='utf-8')
p=r/'scripts/package_teaching_bundle.py';s=p.read_text(encoding='utf-8').replace('第一至二章教学包.zip','第一至三章教学包.zip').replace("'course-site/dist/ch2/index.html','course-site/dist/ch2/slides.html','course-site/dist/downloads/chapter-02.pdf'","'course-site/dist/ch3/index.html','course-site/dist/ch3/slides.html','course-site/dist/downloads/chapter-03.pdf'").replace("'check_ch2_serving.py'","'check_ch2_serving.py','check_ch3_browser.cjs'");p.write_text(s,encoding='utf-8')
# Update inaccurate main-deck count before the final rebuild.
p=r/'scripts/author_chapter03.py';s=p.read_text(encoding='utf-8').replace('主讲54页','主讲53页').replace('39—54','39—53').replace('共54页','共53页').replace('≈2.8150','≈2.8150');p.write_text(s,encoding='utf-8')
print('Portal and offline entry integrated with chapter three.')
