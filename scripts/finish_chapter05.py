from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];D=R/'course-site/dist'
for kind,name in [('teacher','教师使用指南'),('task','学生任务单'),('coverage','知识点覆盖与核对')]:
    shutil.copyfile(R/f'docs/第五章-{name}.md',D/f'downloads/chapter-05-{kind}.md')
shutil.copyfile(R/'scripts/chapter05_reference.py',D/'downloads/chapter05_reference.py')
shutil.copyfile(R/'content/chapter-05-reference.json',D/'downloads/chapter-05-reference.json')
p=D/'index.html';s=p.read_text(encoding='utf-8')
old='<article class="chapter-card"><div class="card-top"><span class="chapter-no">05</span><span>规划中 · 8 学时</span></div><h3>多目标决策分析</h3><p>多个目标冲突，如何取舍？</p><div class="chapter-topics">效用并合 / AHP / DEA / 目标规划</div></article>'
new='<a class="chapter-card available" href="ch5/index.html"><div class="card-top"><span class="chapter-no">05</span><span class="availability">可以学习 · 8 学时</span></div><h3>多目标决策分析</h3><p>多个目标冲突，如何取舍？</p><div class="chapter-topics">效用并合 / AHP / DEA / 目标规划</div><span class="card-action">打开四个交互实验 →</span></a>'
s=s.replace(old,new).replace('已开放第一至四章，其余章节待建设。','已开放第一至五章，第六章待建设。')
if 'href="ch5/index.html">第五章' not in s:s=s.replace('<a href="ch4/index.html">第四章</a>','<a href="ch4/index.html">第四章</a><a href="ch5/index.html">第五章</a>')
s=s.replace('说明你为什么采用这项准则','把多目标推荐讲清楚').replace('概率依据不足时，比较五种准则，保留约束、并列和待补证据。','说明指标与权重，诊断资源效率，在约束下安排目标优先级。').replace('href="ch4/index.html#project">完成 M4 准则辩护','href="ch5/index.html#project">完成 M5 多目标项目')
p.write_text(s,encoding='utf-8')
p=D/'ch4/index.html';s=p.read_text(encoding='utf-8').replace('<a href="../index.html">课程地图 →</a></div></main>','<a href="../ch5/index.html">第五章 →</a></div></main>');p.write_text(s,encoding='utf-8')
# Keep the chapter-four page generator aligned with its updated next-chapter link.
p=R/'scripts/author_chapter04_web.py';s=p.read_text(encoding='utf-8').replace('<a href="../index.html">课程地图 →</a></div></main>','<a href="../ch5/index.html">第五章 →</a></div></main>');p.write_text(s,encoding='utf-8')
p=R/'打开课程.html';s=p.read_text(encoding='utf-8')
if 'ch5/index.html' not in s:s=s.replace('</body>','<p><a href="course-site/dist/ch5/index.html">第五章：多目标决策分析</a></p></body>')
p.write_text(s,encoding='utf-8')
p=R/'scripts/package_teaching_bundle.py';s=p.read_text(encoding='utf-8').replace('第一至四章教学包.zip','第一至五章教学包.zip').replace("'course-site/dist/ch4/index.html','course-site/dist/ch4/slides.html','course-site/dist/downloads/chapter-04.pdf'","'course-site/dist/ch5/index.html','course-site/dist/ch5/slides.html','course-site/dist/downloads/chapter-05.pdf'")
if "'check_ch5_serving.py'" not in s:s=s.replace("'check_ch4_serving.py'","'check_ch4_serving.py','check_ch5_serving.py'")
p.write_text(s,encoding='utf-8')
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('第一至四章教学包','第一至五章教学包').replace('与第四章（2学时）。','、第四章（2学时）与第五章（8学时）。').replace('目前前四章可学习，第五、六章规划中。','目前前五章可学习，第六章规划中。')
section='''## 第五章交付物

在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch5/index.html

本地入口：`course-site/dist/ch5/index.html`；完整解压最新的`output/第一至五章教学包.zip`可离线使用。在线保留原有仅所有者权限。

- `output/pdf/第五章-多目标决策分析.pdf`：68页，54页主讲+14页附录，按四次90分钟课堂组织。
- `course-site/dist/ch5/slides.html`：网页演示，含全部逐页讲稿。
- 四实验：多维效用与敏感性、AHP权重与一致性、正式CCR/BCC求解及松弛、严格优先级/普通加权目标规划；八题测验、本机笔记、JSON导出。
- `docs/第五章-教师使用指南.md`、`第五章-学生任务单.md`、`第五章-知识点覆盖与核对.md`：8学时安排、M5、翻转课堂、教材例题与六道习题的核验。
- `scripts/chapter05_reference.py`：NumPy/SciPy独立复算，保留交通、利润分配、八分厂与防洪原始表；下载区同时提供源码和结果JSON。

使用指定环境`C:\\Users\\admin\\.conda\\envs\\env_Online_Lecture\\python.exe`运行构建与核验。编辑`content/chapter-05-slides.json`后运行`build_chapter05.py`；`author_chapter05.py`会覆盖JSON。网页HTML由`author_chapter05_web.py`生成，模型和交互分别在`ch5-model.js`、`ch5.js`。资料复制与门户集成使用`finish_chapter05.py`。

数值核验：`scripts/verify_chapter05.py`，对照独立主特征向量与线性规划。已做PDF渲染、源码语法、静态资源和HTTP检查；这些不是浏览器点击或端到端验证。页面本身无外部CDN依赖。

'''
if '## 第五章交付物' not in s:s=s.replace('## 第四章交付物',section+'## 第四章交付物')
p.write_text(s,encoding='utf-8')
print('Chapter 5 resources, portal, previous chapter and offline entry integrated')
