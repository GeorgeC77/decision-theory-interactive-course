"""Chapter-two visual treatment applied after the authored mathematical content."""
def apply_visual_design(slides):
    assert len(slides)==47
    s=slides[1]
    s['type']='equipment_intro'
    s['image']='ch2-equipment-comparison.png'
    s['source']='校园咖啡店教学模拟；设备为AI生成示意图'
    s['notes']+=' 插图仅说明设备规模差别，不是品牌报价或真实门店资料。'

    for page,kind in {7:'growth',12:'contribution',14:'capacity',15:'equipment',16:'target',19:'npv',26:'rankings',34:'budget'}.items():
        slides[page-1].update(type='figure',figure=kind)
    slides[6]['lead']='复利 F = P(1+i)ⁿ；折现 P = F/(1+i)ⁿ。先统一比较时点。'
    slides[6]['notes']+=' 图中的5年数据是同一10%复利规律的延伸；原例仍看第2年121万元。'
    slides[11]['lead']='收入 S = pQ；利润 L = (p−v)Q−F。每杯贡献12元，先补固定成本。'
    slides[11]['takeaway']='保本销量 Q₀=F/(p−v)（p>v）；假设产销相等、p与v固定、相关范围内F不变。'
    slides[13]['lead']='同一利润线：L = 12Q−24 000。产能限制决定能走到曲线的哪里。'
    slides[13]['takeaway']='若 p≤v 且 F>0，则非负销量上不能保本；“更优”与“盈利”仍须分开判断。'
    slides[14]['lead']='售价15元；旧设备 F=3 200、v=7，新设备 F=3 800、v=5（固定成本：元/月）。'
    slides[15]['lead']='p=8元/瓶，v=4元/瓶，F=40 000元；目标利润60 000元。'
    slides[15]['takeaway']='Q目标=(F+L目标)/(p−v)=25 000瓶；先检查需求与产能能否达到，再讨论利润目标是否合理。'
    slides[18]['lead']='NPV=Σ[CFₜ/(1+i)ᵗ]，t=0,…,n；期初投入不折现。金额单位：万元。'
    slides[18]['notes']+=' 图中后续流入现值包含每年1.15及第4年残值0.5；与期初投入4比较，差额才是NPV。'
    slides[25]['lead']='同为5年：A投入20、B投入30万元；静态回收期分别约2.86、3.16年。'
    slides[25]['takeaway']='NPV按8%折现；IRR不使用该基准率计算。预算充足且互斥时，本例选B。'
    slides[33]['lead']='三组都用满600万元；第二组按NPVR初选并调整，并非严格逐项贪心。色块表示投资额。'
    slides[28]['items'][0][1]='设备1：投入2.5万，年末净现金流0.75万，5年\n设备2：投入5万，年末净现金流1万，9年\n不能只按各自寿命的NPV直接排名'
    slides[28]['notes']+=' 本例沿用教材简化，将利润贡献视为年末净现金流；真实项目应另行调整折旧、税与营运资金。'
    slides[40]['items'][1][0]='仅期初一笔投资 I₀ > 0，后续净收益非负'

    # Turn two case calculations into literal cash-flow evidence, retaining formulas in notes.
    old=slides[30]
    old.update(type='chart',lead='与继续使用旧设备相比的增量；按教材不计所得税，i=10%。',
        series=[{'name':'更新的增量现金流','points':[[0,-250]]+[[t,43 if t<15 else 63] for t in range(1,16)]}],
        chartmode='stem',xlabel='时点 t / 年',ylabel='增量净现金流 / 万元',
        xticks=[[0,'0'],[1,'1'],[5,'5'],[10,'10'],[15,'15']],
        items=[['现在多投入250','新设备440 − 旧设备可售190'],['未来收回什么？','每年78−35=43；第15年加残值20']],
        takeaway='ΔNPV = −250 + 43(P/A,10%,15) + 20(P/F,10%,15) ≈ +81.85万元，支持更新。')
    old['notes']+=' 先沿图读出−250、每年43及末年63，再代入年金和单笔现值式；不能把残值折现两次。'
    old['notes']+=' 年经营现金流：旧设备100−65=35，新设备160−82=78，年度增量78−35=43，单位均为万元。'
    old=slides[31]
    old.update(type='chart',lead='自制相对外购；所得税率40%，i=12%。金额单位：万元。',
        series=[{'name':'自制相对外购的现金流','points':[[0,-48],[1,13.8],[2,13.8],[3,13.8],[4,25.8]]}],
        chartmode='stem',xlabel='时点 t / 年',ylabel='增量净现金流 / 万元',
        xticks=[[i,str(i)] for i in range(5)],
        items=[['年经营增量如何得到？','税前现金节约：80−48−15=17\n年折旧：(38−2)/4=9'],['期初流出与末年流入','期初：设备38＋营运资金10\n末年：13.8＋残值2＋回收资金10']],
        takeaway='13.8=17×(1−40%)+9×40%；折旧不直接付现，但可抵税；ΔNPV≈+1.54万元，支持自制。')
    old['notes']+=' 税前年现金节约=80−(48+15)=17；年折旧=(38−2)/4=9。图中各年现金流与这些计算一致。'
    old['notes']+=' 年需8万件：外购单价10元，年成本80万元；自制单位变动成本6元，年变动成本48万元，另增固定现金支出15万元。40%为所得税率；9×40%=3.6万元是折旧抵税额，不是折旧本身的现金流入。'

    # A compact timeline table for construction-period outlays, avoiding a dangling amount.
    old=slides[43]
    old['type']='cashflow_table'
    old['cashflows']=[-6000,-4000,3000,3500,5000,4500,4000]
    old['lead']='t=0与t=1均有投资流出；动态回收期按10%折现。金额单位：万元。'
    old['items']=[['静态：3.70年','第3年末尚缺3 500；第4年流入5 000。'],['动态：约4.40年','第4年末现值尚缺1 112.36；第5年折现流入2 794.15。']]
    return slides
