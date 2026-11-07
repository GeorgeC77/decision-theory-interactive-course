"""Apply content/notation repairs found during PDF review; run once after authoring edits."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'scripts/author_chapter05.py';s=p.read_text(encoding='utf-8')
s=s.replace('θ*<1 → 非径向有效','θ*<1 → 径向无效率').replace('最后一种更准确读法为“径向无效率”，课件正文使用易懂描述。','')
s=s.replace('x̂ = θ*x₀ − s投入 = Xλ*','x投影 = θ*x₀ − s投入 = Xλ*').replace('ŷ = y₀ + s产出 = Yλ*','y投影 = y₀ + s产出 = Yλ*')
s=s.replace('a₃办息校（按教材名称）第一','a₃第一；方案名称见教材')
s=s.replace("# Use neutral plan index where the scanned name is ambiguous.\nslides[59]['rows'][1][2]='a₃第一；方案名称见教材'\n",'')
addition=r"""
# Native data charts for the key comparisons; all underlying values remain editable.
slides[10]['chartmode']='stem';slides[10]['xticks']=[[0,'加法'],[1,'乘法'],[2,'代换']]
slides[10]['xlabel']='同一规则内比较两个方案';slides[10]['items'][0]=['三种规则','加法用等权；乘法看共同达成；\n代换允许目标彼此代替。']
slides[29]['series'][1]['scatter']=True
slides[29]['items'][1]=['点与前沿','观察点仅作散点展示；\nCCR前沿来自样本锥包络。']
slides[19].update(type='chart',chartmode='stem',series=[{'name':'主特征向量权重','points':[[0,.6483290138],[1,.2296507941],[2,.1220201921]]}],xticks=[[0,'收益'],[1,'便利'],[2,'体验']],xlabel='相对于同一上层目标的准则',ylabel='归一化权重',items=[['形式化','Aw=λmax w，Σwᵢ=1；\n完全一致时aᵢⱼ=wᵢ/wⱼ。'],['本例数值','λmax≈3.003695；\n三项权重合计为1。']])
slides[33].update(type='chart',chartmode='stem',series=[{'name':'单位4原值','points':[[0,4],[1,2],[2,1]]},{'name':'参照组合','points':[[0,2.4],[1,1.2],[2,1]]}],xticks=[[0,'投入1'],[1,'投入2'],[2,'产出']],xlabel='按指标分别比较；不把不同指标数值相加',ylabel='教材原始计量值',items=[['λ₂=0.6，λ₃=0.2','投入：(2.4,1.2)；\n产出保持1。'],['θ=0.6','两项投入均节省40%；\n松弛为0。']])
slides[39].update(type='chart',chartmode='stem',series=[{'name':'四分厂：不同模型的结果','points':[[0,.4990688636],[1,.3439024904]]}],xticks=[[0,'径向效率'],[1,'成本效率']],xlabel='两种效率不可混称',ylabel='效率值',items=[['BCC径向模型','θ≈0.499069；\n教材所列0.49907与之吻合。'],['另建成本模型','按给定价格最小化成本；\n成本效率约0.343902。']])
slides[48].update(type='chart',chartmode='stem',series=[{'name':'尼龙布','points':[[0,70],[1,70]]},{'name':'棉布','points':[[0,20],[1,45]]}],xticks=[[0,'严格优先级'],[1,'普通加权']],xlabel='相同数据，改变目标之间的交换规则',ylabel='产量 / 千米',items=[['严格优先级','(70,20)，加班10小时；\n棉布不足25千米。'],['普通加权','(70,45)，加班35小时；\n跨层交换牺牲加班控制。']])
"""
if '# Native data charts' in s:
    start=s.index('# Native data charts');end=s.index("(R/'content/chapter-05-slides.json').write_text",start);s=s[:start]+s[end:]
s=s.replace("(R/'content/chapter-05-slides.json').write_text",addition+"\n(R/'content/chapter-05-slides.json').write_text")
p.write_text(s,encoding='utf-8')
p=R/'course-site/dist/assets/ch5.js';s=p.read_text(encoding='utf-8').replace("'???????????'","'计算暂停，请修正输入。'");p.write_text(s,encoding='utf-8')
p=R/'course-site/dist/assets/ch5-model.js';s=p.read_text(encoding='utf-8')
for a,b in [('正常工时不少于80','正常工时保障'),('总工时不超过90','总工时控制'),('尼龙布销量70','尼龙布销量'),('棉布销量45','棉布销量'),('减少超过80的工时','加班压减')]:s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
print('Chapter 5 notation and visual comparisons refined')
