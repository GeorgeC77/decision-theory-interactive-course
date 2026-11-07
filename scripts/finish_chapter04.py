from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'course-site/dist/index.html';s=p.read_text(encoding='utf-8')
old='<article class="chapter-card"><div class="card-top"><span class="chapter-no">04</span><span>规划中 · 2 学时</span></div><h3>不确定型决策分析</h3><p>没有可靠概率，如何选择准则？</p><div class="chapter-topics">乐观与悲观 / 折中 / 后悔值</div></article>'
new='<a class="chapter-card available" href="ch4/index.html"><div class="card-top"><span class="chapter-no">04</span><span class="availability">可以学习 · 2 学时</span></div><h3>不确定型决策分析</h3><p>没有可靠概率，如何选择准则？</p><div class="chapter-topics">五准则 / 系数阈值 / 收益与成本后悔值</div><span class="card-action">打开准则比较台 →</span></a>'
s=s.replace(old,new).replace('已开放第一、二、三章','已开放第一至四章')
if 'href="ch4/index.html">第四章' not in s:s=s.replace('<a href="ch3/index.html">第三章</a>','<a href="ch3/index.html">第三章</a><a href="ch4/index.html">第四章</a>')
s=s.replace('把选择升级为有条件的策略','说明你为什么采用这项准则').replace('把投资比较加入概率、调查与风险偏好，解释何时改变选择。','概率依据不足时，比较五种准则，保留约束、并列和待补证据。').replace('href="ch3/index.html#project">完成 M3 风险决策项目','href="ch4/index.html#project">完成 M4 准则辩护')
p.write_text(s,encoding='utf-8')
p=R/'course-site/dist/ch3/index.html';s=p.read_text(encoding='utf-8').replace('<a href="../index.html">课程地图 →</a></div></main>','<a href="../ch4/index.html">第四章 →</a></div></main>');p.write_text(s,encoding='utf-8')
p=R/'打开课程.html';s=p.read_text(encoding='utf-8')
if 'ch4/index.html' not in s:s=s.replace('</body>','<p><a href="course-site/dist/ch4/index.html">第四章：不确定型决策分析</a></p></body>')
p.write_text(s,encoding='utf-8')
p=R/'scripts/package_teaching_bundle.py';s=p.read_text(encoding='utf-8').replace('第一至三章教学包.zip','第一至四章教学包.zip').replace("'course-site/dist/ch3/index.html','course-site/dist/ch3/slides.html','course-site/dist/downloads/chapter-03.pdf'","'course-site/dist/ch4/index.html','course-site/dist/ch4/slides.html','course-site/dist/downloads/chapter-04.pdf'").replace("'check_ch3_serving.py'","'check_ch3_serving.py','check_ch4_serving.py'");p.write_text(s,encoding='utf-8')
p=R/'course-site/dist/assets/ch4.css';s=p.read_text(encoding='utf-8')
if '.point-button{' not in s:s+='\n.point-button{font:inherit;color:#244e79;background:white;border:1px solid #bccbd8;border-radius:5px;padding:7px 10px;margin:6px 3px;cursor:pointer}#alpha-exact{max-width:240px}.point-button:focus-visible{outline:3px solid #bb8637}\n'
p.write_text(s,encoding='utf-8')
print('Fourth chapter integrated with portal and offline bundle.')
