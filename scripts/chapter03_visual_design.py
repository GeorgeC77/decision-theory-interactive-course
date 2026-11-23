"""Visual teaching treatment for chapter three; retain formulas and assumptions."""

def apply_visual_design(slides):
    assert len(slides)==62
    opening=slides[1]
    opening.update(type='scenario',image='ch3-demand-states.png',
        lead='两种可能的客流；金额为同一研究期的净现值，单位：万元。',
        items=[['高客流情境','小店净价值8；大店净价值16'],['低客流情境','小店净价值2；大店净价值−6']],
        takeaway='不投资在两种状态下均为0；先选方案，再说明还缺少什么概率信息。',
        source='校园咖啡店教学模拟；AI生成情境插图，不是真实客流观测')
    opening['notes']+=' 插图对照同一家店在两种需求状态下的客流，不代表已经得到的样本，也不表示图片中的人数就是概率。各行动的状态损益仍使用教学矩阵。'
    mapping={6:'emv',10:'regret',11:'perfect',19:'late_choice',20:'strategy',
             26:'frequencies',28:'posterior_policy',30:'information',36:'sampling',
             42:'lottery',44:'certainty',50:'oil'}
    for page,key in mapping.items():slides[page-1].update(type='figure',figure=key)
    # Grid positions and labels share these values; endpoints set plot limits.
    for page,ticks in {
        7: [-10,-5,0,5,10,15,20],
        12: [0,5,10,15,20],
        21: [0,200,400,600,800],
        31: [0,2,4,6,8,10],
        40: [-10,-5,0,5,10,15,20],
        43: [0,0.25,0.5,0.75,1],
    }.items():
        slides[page-1]['yticks']=ticks
    slides[42]['xticks']=[[x, str(x)] for x in range(-10,21,5)]
    slides[42]['notes']+=' 读图练习：在横轴找到5万元，沿中性线读到效用0.5。改用蓝色凹曲线，确定5万元的效用约为0.818，两个端点各半的赌局期望效用为0.5。'
    slides[5]['lead']='a为行动，θ为状态，V为净价值；EMV(a)=Σp(θ)V(a,θ)，按状态求和。'
    slides[5]['takeaway']='风险中性、无额外约束时选EMV最大的大店；期望7.2不表示某次一定得到7.2。'
    slides[9]['lead']='L(a,θ)=该状态最优损益−本方案损益；EOL(a)=Σp(θ)L(a,θ)。'
    slides[9]['takeaway']='机会损失不是账面亏损；同一模型下 EOL(a)=EVwPI−EMV(a)，因此两种准则排序一致。'
    slides[10]['lead']='风险中性；信息先于行动，不改变可行行动集合。金额：万元。'
    slides[18]['lead']='教材例3-8；以下均为后7年价值，单位万元；扩建费210，未折现。'
    slides[19]['lead']='前3年好/差概率0.75/0.25；先算后期策略，再回到期初，金额万元。'
    slides[25]['lead']='由先验0.6、敏感度0.8、特异度0.8推算的期望频数，不是观测样本。'
    slides[27]['lead']='报告后用后验重算每个行动的EMV；金额万元，显示值不参与后续舍入计算。'
    slides[29]['lead']='调查前比较两种策略：EVSI=调查后期望值（扣费前）−不调查最优值。金额：万元。'
    slides[35]['lead']='有放回抽样n=4；X为缺陷数；不买收益为0。金额：元。'
    slides[35]['takeaway']='P(X=0)=0.56453125；该分支联合贡献1.5891625；EVSI=1.5891625−1=0.5891625元。'
    slides[41]['lead']='两个方案的货币期望同为5万元，结果分布与风险却不同。'
    slides[43]['lead']='确定等价CE：与风险方案同样满意的确定金额，满足u(CE)=EU；本图k=3。'
    slides[43]['takeaway']='EU=Σpu(x)；凹效用下E[u(X)]≤u(E[X])；风险溢价=EMV−CE；效用数值没有货币单位。'
    slides[43]['notes']+=' X表示随机净结果，x表示其可能取值，p为相应概率；EU先对每个结果求效用再加权。CE是使决策者与原风险方案无差异的确定金额，不是平均效用金额。本图用附录F在x∈[−10,20]万元上归一化的指数效用，k=3；风险方案EU=0.5，CE约−3.5544万元，确定5万元的效用约0.8176，风险溢价约8.5544万元。几何读法：先在纵轴找EU，再水平对应效用曲线并向下读CE；不能把EU=0.5解释成0.5万元。'
    slides[49]['lead']='沿用教材先验P(有油)=0.3，试验费5；所有金额单位：万美元。'
    return slides
