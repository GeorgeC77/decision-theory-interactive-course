from pathlib import Path
import shutil,re
R=Path(__file__).resolve().parents[1];D=R/'course-site/dist'
for name,target in [('第六章-教师指南.md','chapter-06-teacher.md'),('第六章-学生任务单.md','chapter-06-task.md'),('第六章-知识点覆盖与核对.md','chapter-06-coverage.md')]:shutil.copyfile(R/'docs'/name,D/'downloads'/target)
shutil.copyfile(R/'scripts/chapter06_reference.py',D/'downloads/chapter06_reference.py')
shutil.copyfile(R/'content/chapter-06-reference.json',D/'downloads/chapter-06-reference.json')
p=D/'index.html';s=p.read_text(encoding='utf-8')
s=re.sub(r'<article class="chapter-card"><div class="card-top"><span class="chapter-no">06</span>.*?</article>','<a class="chapter-card available" href="ch6/index.html"><div class="card-top"><span class="chapter-no">06</span><span class="availability">可以学习 · 8 学时</span></div><h3>序贯决策分析</h3><p>今天的选择如何影响明天？</p><div class="chapter-topics">逆向归纳 / 试营业 / 马尔可夫 / 群体决策</div><span class="card-action">打开四个交互实验 →</span></a>',s,flags=re.S)
if '<a href="ch6/index.html">第六章</a>'not in s:s=s.replace('<a href="ch5/index.html">第五章</a>','<a href="ch5/index.html">第五章</a><a href="ch6/index.html">第六章</a>')
s=s.replace('把多目标推荐讲清楚','形成能执行、能复现的最终建议').replace('说明指标与权重，诊断资源效率，在约束下安排目标优先级。','整合六章成果，写出条件策略，保留群体意见与推荐的适用边界。').replace('href="ch5/index.html#project">完成 M5 多目标项目','href="ch6/index.html#project">完成 M6 综合项目').replace('已开放第一至五章，第六章待建设。','六章已开放 · 共32学时、19个交互实验模块。')
p.write_text(s,encoding='utf-8')
for p in [D/'ch5/index.html',R/'scripts/author_chapter05_web.py']:
    s=p.read_text(encoding='utf-8').replace('<a href="../index.html">课程地图 →</a>','<a href="../ch6/index.html">第六章 →</a>');p.write_text(s,encoding='utf-8')
p=R/'打开课程.html';s=p.read_text(encoding='utf-8')
if 'course-site/dist/ch6/index.html'not in s:s=s.replace('</body>','<p><a href="course-site/dist/ch6/index.html">第六章：序贯决策分析 · 四个交互实验</a> · <a href="course-site/dist/ch6/slides.html">第六章教学演示</a></p></body>')
s=s.replace('第一至五章','第一至六章');p.write_text(s,encoding='utf-8')
p=R/'scripts/package_teaching_bundle.py';s=p.read_text(encoding='utf-8').replace('第一至五章','第一至六章').replace('dist/ch5/','dist/ch6/').replace('downloads/chapter-05.pdf','downloads/chapter-06.pdf')
if "'check_ch6_serving.py'" not in s:s=s.replace("'check_ch5_serving.py',","'check_ch5_serving.py','check_ch6_serving.py',")
p.write_text(s,encoding='utf-8')
p=R/'scripts/check_ch6_serving.py';s=(R/'scripts/check_ch5_serving.py').read_text(encoding='utf-8').replace("'/ch4/index.html'","'/ch5/index.html'").replace("'/ch5/index.html','/ch5/index.html'","'/ch5/index.html','/ch6/index.html'").replace('/ch5/slides','/ch6/slides').replace('assets/ch5','assets/ch6').replace('chapter-05','chapter-06').replace('chapter05_reference','chapter06_reference');p.write_text(s,encoding='utf-8')
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('第一至五章教学包','第一至六章教学包').replace('第四章（2学时）与第五章（8学时）。','第四章（2学时）、第五章（8学时）与第六章（8学时）；六章内容现已齐全。')
if '## 第六章'not in s:s+='''\n\n## 第六章：序贯决策分析（已完成）\n\n第13—16次课，共8学时；前六章共32学时现已齐备。第六章包含72页课件（54主讲＋18补充）及逐页讲稿，四个实验：逆向归纳、试营业与扩张、马尔可夫经营、委员会投票与意见协调。\n\n- 在线学习：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch6/index.html （沿用课程原私有访问权限）\n- 离线网页：`course-site/dist/ch6/index.html`；演示：`course-site/dist/ch6/slides.html`。\n- PDF：`output/pdf/第六章-序贯决策分析.pdf`。\n- 教师指南、学生任务单、知识点覆盖与核对：`docs/第六章-*.md`。\n- 独立复算：`scripts/chapter06_reference.py`；数值验证：`scripts/verify_chapter06.py`。\n- 完整离线包：`output/第一至六章教学包.zip`，解压后打开根目录“打开课程.html”或运行“start-course.cmd”。\n\n教材例6-1、6-6等数据差异单独记录；计算结果由原始数据复算。网页提供完整策略与并列、零概率处理、输入验证、讨论前后快照和JSON导出。M6整合既有档案，包含8—12页终稿、复现附件与K3扩展，不重复新增大作业。\n\n重新生成本章时，依次使用指定Python环境运行 `chapter06_reference.py`、`author_chapter06.py`、`build_chapter06.py`、`author_chapter06_web.py`、`finish_chapter06.py`，再执行验证与打包脚本。\n'''
p.write_text(s,encoding='utf-8')
print('Chapter 6 downloads, portal and six-chapter bundle configuration updated')
