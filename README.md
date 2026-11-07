# 决策理论与方法 · 第一至六章教学包

## 公开课程网站

学生入口：<https://georgec77.github.io/decision-theory-interactive-course/>

GitHub Pages 发布 `gh-pages` 分支根目录，内容来自 `main` 分支的 `course-site/dist`。课程网页、六章演示与 PDF 可直接访问；下文的旧 Sites 链接仍是原有教师预览地址，其访问权限不影响 GitHub Pages。

更新课程后，先提交并推送 `main`，再在仓库根目录运行 `powershell -ExecutionPolicy Bypass -File scripts/publish_github_pages.ps1`。该脚本只把静态课程目录发布到 `gh-pages`，GitHub 随后自动部署。

面向大三经管类，课程前六章共32学时。已完成门户、第一章（2学时）、第二章（4学时）、第三章（8学时）、第四章（2学时）、第五章（8学时）与第六章（8学时）；六章内容现已齐全。

## 第五章交付物

在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch5/index.html

本地入口：`course-site/dist/ch5/index.html`；完整解压最新的`output/第一至六章教学包.zip`可离线使用。在线保留原有仅所有者权限。

- `output/pdf/第五章-多目标决策分析.pdf`：68页，54页主讲+14页附录，按四次90分钟课堂组织。
- `course-site/dist/ch5/slides.html`：网页演示，含全部逐页讲稿。
- 四实验：多维效用与敏感性、AHP权重与一致性、正式CCR/BCC求解及松弛、严格优先级/普通加权目标规划；八题测验、本机笔记、JSON导出。
- `docs/第五章-教师使用指南.md`、`第五章-学生任务单.md`、`第五章-知识点覆盖与核对.md`：8学时安排、M5、翻转课堂、教材例题与六道习题的核验。
- `scripts/chapter05_reference.py`：NumPy/SciPy独立复算，保留交通、利润分配、八分厂与防洪原始表；下载区同时提供源码和结果JSON。

使用指定环境`C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe`运行构建与核验。编辑`content/chapter-05-slides.json`后运行`build_chapter05.py`；`author_chapter05.py`会覆盖JSON。网页HTML由`author_chapter05_web.py`生成，模型和交互分别在`ch5-model.js`、`ch5.js`。资料复制与门户集成使用`finish_chapter05.py`。

数值核验：`scripts/verify_chapter05.py`，对照独立主特征向量与线性规划。已做PDF渲染、源码语法、静态资源和HTTP检查；这些不是浏览器点击或端到端验证。页面本身无外部CDN依赖。

## 第四章交付物

在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch4/index.html

本地入口：`course-site/dist/ch4/index.html`；启动本地服务后访问 <http://127.0.0.1:8765/ch4/index.html>。在线保留仅所有者权限；分发用 `output/第一至六章教学包.zip`。

- `output/pdf/第四章-不确定型决策分析.pdf`：34页，24页主讲与10页附录，按一次90分钟课堂组织。
- `course-site/dist/ch4/slides.html`：可翻页演示、逐页教师讲稿。
- 五准则比较台、α精确切换区间、收益/成本后悔值分步放大镜、三个准则反例、11组数据预设、六题测验、本机笔记和JSON导出。
- `docs/第四章-教师使用指南.md`、`第四章-学生任务单.md`、`第四章-知识点覆盖与核对.md`：90分钟安排、M4、翻转课堂与教材例题/习题核验。
- 编辑 `content/chapter-04-slides.json` 后，用 `C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe` 运行 `scripts/build_chapter04.py` 重建演示；运行 `author_chapter04.py` 会覆盖JSON。学习网页由 `author_chapter04_web.py` 生成；模型与交互为 `assets/ch4-model.js`、`ch4.js`。

模型核验：`node scripts/verify_chapter04.cjs`。本章执行数值、源码语法、静态资源和HTTP检查；未将这些检查称为真实浏览器端到端验证。

## 第三章交付物

第三章在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch3/index.html

本地入口：`course-site/dist/ch3/index.html`；运行 `start-course.cmd` 后可访问 <http://127.0.0.1:8765/ch3/index.html>。在线版保留仅所有者权限；课堂分发可使用最新的 `output/第一至六章教学包.zip`。

- `output/pdf/第三章-风险型决策分析.pdf`：62页，53页主讲与9页附录，按四次90分钟组织。
- `course-site/dist/ch3/slides.html`：网页演示和逐页讲稿。
- 六类交互：期望模拟、决策树回溯、贝叶斯调查、最优抽样、概率敏感性、风险效用；含8题测验、本机笔记和JSON记录导出。
- `docs/第三章-教师使用指南.md`、`第三章-学生任务单.md`、`第三章-知识点覆盖与核对.md`：课堂安排、M3、翻转课堂及教材数值核对。
- 编辑 `content/chapter-03-slides.json` 后，使用 `C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe` 运行 `scripts/build_chapter03.py` 重建演示。`author_chapter03.py` 会覆盖生成JSON；网页源由 `author_chapter03_web.py` 生成，行为与模型在 `assets/ch3.js` 和 `ch3-model.js`。

数值检查：`node scripts/verify_chapter03.cjs`。`verify_chapter03_dom.cjs` 是开发用DOM集成检查，依赖本地jsdom；网站运行不需要这些开发依赖。

第二章本地学习入口：`course-site/dist/ch2/index.html`；本地服务运行时可访问 <http://127.0.0.1:8765/ch2/index.html>。

第二章在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch2/index.html

## 第二章交付物

- `output/pdf/第二章-确定型决策分析.pdf`：47页，38页主讲与9页附录。
- `course-site/dist/ch2/index.html`：现金流、盈亏、投资比较、资本限额及投资时机实验，含知识速查、学习记录与六题测验。
- `course-site/dist/ch2/slides.html`：HTML演示与逐页教师讲稿。
- `docs/第二章-教师使用指南.md`：两次90分钟课堂安排、答案与数值口径。
- `docs/第二章-学生任务单.md`：项目M2、实验记录、翻转课堂与AI核验要求。
- `docs/第二章-知识点覆盖与核对.md`：教材p.17—49覆盖表、原文差异和处理方式。

编辑第二章内容可直接修改 `content/chapter-02-slides.json`，然后使用指定Python环境运行 `scripts/build_chapter02.py`；完整重建原始内容可先运行 `scripts/author_chapter02.py`，它会重新生成该JSON文件。财务模型、交互和样式分别在 `ch2-model.js`、`ch2.js`、`ch2.css`。

第二章检查命令：`node scripts/verify_chapter02.cjs`；所有网页的引用检查：使用指定Python运行 `scripts/verify_static.py`。DOM集成检查脚本需要本地 `tmp/ch2-dom-test` 的jsdom依赖，它是开发检查工具，不是网站运行依赖，也不包含在教学包内。

在线入口：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site

当前为仅所有者可访问的私有版本，适合教师预览与投影。学生访问范围尚未开放；本地文件和离线教学包不依赖该在线权限。

## 第一章交付物

- `output/pdf/第一章-决策分析概述.pdf`：30页，24页主讲＋6页补充。
- `course-site/dist/index.html`：课程门户，第一至第六章均已完成。
- `course-site/dist/ch1/index.html`：第一章交互学习。
- `course-site/dist/ch1/slides.html`：HTML教学演示，含逐页讲稿。
- `docs/第一章-教师使用指南.md`：90分钟安排、例题口径与参考答案。
- `course-site/dist/downloads/chapter-01-task.md`：学生任务单。
- `docs/第一章-知识点覆盖与核对.md`：教材对应和疑点说明。

## 本地使用

若在线入口空白，可直接双击项目根目录的 `打开课程.html`，无需登录。如需本地服务，双击 `start-course.cmd`，保持窗口开启，然后访问 <http://127.0.0.1:8765/>。启动脚本使用指定的 `env_Online_Lecture` 环境。教学包须完整解压后使用。

网页不依赖外部CDN。可直接打开 `course-site/dist/index.html`；推荐通过本地服务获得稳定的下载与本设备草稿保存行为。在项目目录运行：

```powershell
& 'C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe' -m http.server 8765 --bind 127.0.0.1 --directory course-site/dist
```

然后打开 `http://127.0.0.1:8765/`。

网页画布仅保存在浏览器本设备存储中，可导出Markdown；不会自动上传或提交。教学演示支持左右方向键、Home/End、F全屏和N讲稿，也有屏幕按钮。

## 修改与重建

指定Python环境为 `env_Online_Lecture`。生成PDF需要ReportLab，已在该环境安装；页面渲染检查使用环境已有的PyMuPDF。

1. 修改 `content/chapter-01-slides.json` 中的演示内容与讲稿。
2. 运行以下命令，生成PDF并同步网页演示与下载副本：

```powershell
& 'C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe' scripts/build_chapter01.py
```

3. 网站样式位于 `course-site/dist/assets/style.css`；教学模型位于 `model.js`；页面行为位于 `chapter.js`；演示样式位于 `slides.css`。

PDF构建使用Windows微软雅黑字体并嵌入PDF。迁移到其他系统时需调整构建脚本的字体路径，不能假定同一路径存在。本次未生成PPTX。

## 教学数据

以项目教材为依据，具体页码见知识点覆盖表。咖啡店及插画为教学创作。汽车例题明确区分原始数据与教材逐步舍入口径。涉及第一章之外的方法仅作课程联系，不提供未完成章节的虚假入口。


## 第六章：序贯决策分析（已完成）

第13—16次课，共8学时；前六章共32学时现已齐备。第六章包含72页课件（54主讲＋18补充）及逐页讲稿，四个实验：逆向归纳、试营业与扩张、马尔可夫经营、委员会投票与意见协调。

- 在线学习：https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site/ch6/index.html （沿用课程原私有访问权限）
- 离线网页：`course-site/dist/ch6/index.html`；演示：`course-site/dist/ch6/slides.html`。
- PDF：`output/pdf/第六章-序贯决策分析.pdf`。
- 教师指南、学生任务单、知识点覆盖与核对：`docs/第六章-*.md`。
- 独立复算：`scripts/chapter06_reference.py`；数值验证：`scripts/verify_chapter06.py`。
- 完整离线包：`output/第一至六章教学包.zip`，解压后打开根目录“打开课程.html”或运行“start-course.cmd”。

教材例6-1、6-6等数据差异单独记录；计算结果由原始数据复算。网页提供完整策略与并列、零概率处理、输入验证、讨论前后快照和JSON导出。M6整合既有档案，包含8—12页终稿、复现附件与K3扩展，不重复新增大作业。

重新生成本章时，依次使用指定Python环境运行 `chapter06_reference.py`、`author_chapter06.py`、`build_chapter06.py`、`author_chapter06_web.py`、`finish_chapter06.py`，再执行验证与打包脚本。
