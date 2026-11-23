"""Editable chapter-three figures using the shared native PDF / SVG scene.

All coordinates are in a 1140 x 350 canvas; Scene places PDF at (70, 228).
DATA contains the teaching inputs, with derived values computed at rendering.
"""
from math import comb, exp, log, sin, cos, pi

from chapter02_figures import Scene, NAVY, GOLD, GREEN, RED, INK, MUTED, GRID

PALE = '#eaf1f8'
SOFT_GREEN = '#e7f1ec'
SOFT_RED = '#f4e7e5'
DATA = {
    'campus': {'prior': [.6, .4], 'payoffs': [[0, 0], [8, 2], [16, -6]],
               'names': ['不投资', '小店', '大店'], 'likelihood_good': [.8, .2], 'fee': .5},
    'late': {'years': 7, 'expansion_fee': 210, 'good': [.85, .15],
             'poor': [.1, .9], 'expand': [150, 10], 'keep': [60, 2]},
    'sampling': {'theta': [.2, .1, .05], 'prior': [.5, .3, .2],
                 'purchase': [-5, 5, 10], 'n': 4},
    'utility': {'k': 3, 'minimum': -10, 'maximum': 20, 'p_high': .5},
    'oil': {'prior': .3, 'closed_likelihood': [.8, .4],
            'closed_value': 30, 'open_value': 11.25, 'baseline': 13, 'fee': 5},
}


def weighted(values, probabilities):
    return sum(v*p for v, p in zip(values, probabilities))


def table(sc, headers, rows, widths, x=15, y=48, row_height=53, highlights=()):
    """Text table with explicit cell widths and optional highlighted rows."""
    total = sum(widths)
    sc.rect(x, y, total, row_height, PALE)
    for r, row in enumerate([headers] + rows):
        yy = y + r*row_height
        if r-1 in highlights:
            sc.rect(x, yy, total, row_height, SOFT_GREEN)
        xx = x
        for value, width in zip(row, widths):
            sc.text(xx+14, yy+row_height/2+8, value, 23,
                    NAVY if r == 0 else INK, r == 0 or r-1 in highlights)
            xx += width
        sc.line(x, yy+row_height, x+total, yy+row_height, GRID, 1)


def bar(sc, x, y, value, scale, label, color=NAVY, height=42):
    width = value*scale
    sc.rect(x, y, width, height, color)
    sc.text(x+width+13, y+height/2+9, label, 26, color, True)


def emv(sc):
    d = DATA['campus'];p = d['prior'];small, large = d['payoffs'][1:]
    values = [weighted(row, p) for row in [small, large]]
    sc.text(20, 26, '同一状态概率；损益与期望值单位均为万元', 23, NAVY, True)
    table(sc, ['方案', '高客流 0.6', '低客流 0.4'],
          [['小店', '8', '2'], ['大店', '16', '-6']], [140, 190, 190], y=66)
    sc.text(620, 83, '加权后的 EMV', 24, NAVY, True)
    for i, (name, row, value) in enumerate(zip(['小店', '大店'], [small, large], values)):
        y = 115+i*93
        sc.text(550, y+30, name, 24, NAVY, True)
        bar(sc, 620, y, value, 45, f'{value:.1f}', GREEN if i else NAVY)
        sc.text(620, y+70, f'{p[0]} × {row[0]} + {p[1]} × ({row[1]})', 22, MUTED)
    sc.text(20, 310, '加权比较不改变原始损益；大店仍可能亏损 6 万元。', 23, MUTED)
    sc.text(620, 337, '风险中性且无额外约束：选大店', 24, GREEN, True)


def regret(sc):
    d = DATA['campus'];best = [max(row[j] for row in d['payoffs']) for j in range(2)]
    losses = [[best[j]-row[j] for j in range(2)] for row in d['payoffs']]
    sc.text(20, 26, '各状态的事后最优损益：高客流 16；低客流 2（万元）', 23, NAVY, True)
    rows = [[name, str(row[0]), str(row[1]), f'{weighted(row,d["prior"]):.1f}']
            for name, row in zip(d['names'], losses)]
    table(sc, ['行动', '高客流损失', '低客流损失', 'EOL = 0.6 × 高 + 0.4 × 低'],
          rows, [170, 230, 230, 470], y=55, row_height=57, highlights=(2,))
    sc.text(30, 331, '同一状态下最优行动的损失为 0；事前比较选择最小 EOL：3.2 万元。', 24, GREEN, True)


def perfect(sc):
    d=DATA['campus'];p=d['prior'];base=max(weighted(row,p) for row in d['payoffs'])
    perfect_value=weighted([max(row[j] for row in d['payoffs']) for j in range(2)],p)
    sc.text(20, 26, '先知道状态，再选择行动', 25, NAVY, True)
    sc.rect(20, 60, 470, 82, PALE)
    sc.text(40, 94, '高客流 0.6 → 大店 → 16 万元', 25, NAVY, True)
    sc.text(40, 126, '贡献期望值：0.6 × 16 = 9.6', 22, MUTED)
    sc.rect(20, 165, 470, 82, SOFT_GREEN)
    sc.text(40, 199, '低客流 0.4 → 小店 → 2 万元', 25, GREEN, True)
    sc.text(40, 231, '贡献期望值：0.4 × 2 = 0.8', 22, MUTED)
    sc.text(565, 64, '无信息：事前固定选大店', 23, NAVY)
    bar(sc, 565, 82, base, 40, f'{base:.1f}')
    sc.text(565, 172, '完全信息：按状态选行动', 23, GREEN)
    bar(sc, 565, 190, perfect_value, 40, f'{perfect_value:.1f}', GREEN)
    sc.text(565, 296, f'EVPI = {perfect_value:.1f} - {base:.1f} = {perfect_value-base:.1f} 万元', 29, GOLD, True)
    sc.text(20, 330, '两条价值柱使用同一万元尺度。', 22, MUTED)


def late_choice(sc):
    d=DATA['late'];n=d['years'];fee=d['expansion_fee']
    expand=n*weighted(d['expand'],d['good'])-fee
    keep=n*weighted(d['keep'],d['good']);poor=n*weighted(d['keep'],d['poor'])
    sc.text(20, 26, '前期好：后期好 / 差 = 0.85 / 0.15', 24, NAVY, True)
    sc.text(20, 66, '只比较此节点往后的 7 年损益（万元）', 22, MUTED)
    formulas = [
        f'{n} × ({d["good"][0]} × {d["expand"][0]} + {d["good"][1]} × {d["expand"][1]}) - {fee} = {expand:g}',
        f'{n} × ({d["good"][0]} × {d["keep"][0]} + {d["good"][1]} × {d["keep"][1]}) = {keep:g}',
    ]
    for (y, name, value, color), formula in zip(
            [(124,'扩建',expand,GREEN),(238,'保持',keep,NAVY)], formulas):
        sc.text(20,y-17,formula,22,color,True)
        sc.text(20,y+29,name,25,color,True)
        bar(sc,100,y,value,.64,f'{value:g}',color)
    sc.line(710,45,710,300,GRID,2)
    sc.text(755,65,'前期差：按教材保持',25,NAVY,True)
    sc.text(755,111,'后期好 / 差 = 0.1 / 0.9',23,MUTED)
    sc.text(755,162,'7 × (0.1 × 60 + 0.9 × 2)',22,INK)
    sc.text(755,218,f'= {poor:.1f} 万元',32,NAVY,True)
    sc.text(755,277,'此分支不借用“前期好”的概率',21,MUTED)
    sc.text(20,337,'条件策略：前期好则扩建，前期差则保持；再带回期初比较。',24,GREEN,True)


def frequencies(sc):
    d=DATA['campus'];n=1000;p=d['prior'];lik=d['likelihood_good']
    counts=[[n*p[j]*lik[j],n*p[j]*(1-lik[j])] for j in range(2)]
    sc.text(20,27,'1000 个同类情境的期望频数（非一次实际抽样结果）',24,NAVY,True)
    sc.rect(775,52,22,22,GREEN);sc.text(810,72,'好报告',22,GREEN)
    sc.rect(950,52,22,22,GOLD);sc.text(985,72,'差报告',22,GOLD)
    for j,(name,row) in enumerate(zip(['高客流 600','低客流 400'],counts)):
        y=103+j*91;sc.text(20,y+35,name,25,NAVY,True)
        x=225
        for value,col in zip(row,[GREEN,GOLD]):
            sc.rect(x,y,value,56,col)
            sc.text(x+value/2,y+37,f'{value:.0f}',25,'#ffffff' if col==GREEN else INK,True,'middle')
            x+=value
    good=sum(row[0] for row in counts)
    sc.text(20,307,f'好报告：480 + 80 = {good:.0f}；其中高客流 480',25,GREEN,True)
    sc.text(650,307,'P(高客流 | 好报告) = 6/7',26,GREEN,True)
    sc.text(225,343,'条长按期望频数同比例绘制；分母是好报告总数 560。',21,MUTED)


def report_values():
    d=DATA['campus'];p=d['prior'];lik=d['likelihood_good'];out=[]
    for likelihood in [lik,[1-v for v in lik]]:
        joint=[a*b for a,b in zip(p,likelihood)];prob=sum(joint)
        posterior=[v/prob for v in joint]
        out.append((prob,posterior,[weighted(row,posterior) for row in d['payoffs'][1:]]))
    return out


def posterior_policy(sc):
    sc.text(20,27,'先用报告更新概率，再在同一后验下比较行动（万元）',24,NAVY,True)
    for i,((prob,post,values),report,fraction) in enumerate(zip(report_values(),['好报告','差报告'],['6/7','3/11'])):
        x=20+i*570;winner=max(range(2),key=values.__getitem__)
        sc.rect(x,55,535,76,PALE)
        sc.text(x+15,81,f'{report} P = {prob:.2f}',25,NAVY,True)
        sc.text(x+15,116,f'P(高客流 | {report}) = {fraction}',21,MUTED)
        for j,(name,value) in enumerate(zip(['小店','大店'],values)):
            y=147+j*74;color=GREEN if j==winner else NAVY
            sc.text(x+12,y+28,name,24,color,True)
            if value>1e-10:bar(sc,x+87,y,value,24,f'{value:.4f}',color,37)
            else:
                sc.line(x+87,y,x+87,y+37,color,2)
                sc.text(x+101,y+28,'0.0000',26,color,True)
        sc.text(x+15,321,f'选择：{["小店","大店"][winner]}',28,GREEN,True)


def information(sc):
    d=DATA['campus'];base=max(weighted(row,d['prior']) for row in d['payoffs'])
    gross=sum(prob*max(values) for prob,post,values in report_values());net=gross-d['fee']
    sc.text(20,26,'价值水平 / 万元（各柱同一尺度）',24,NAVY,True)
    for i,(name,value,color) in enumerate([('不调查',base,NAVY),('调查后（扣费前）',gross,GREEN),('扣费后净价值',net,GOLD)]):
        y=71+i*80;sc.text(20,y+29,name,24,color,True)
        bar(sc,230,y,value,46,f'{value:.1f}',color)
    sc.line(810,50,810,295,GRID,2)
    sc.text(850,79,f'调查费 {d["fee"]:.1f} 万元',24,MUTED)
    sc.text(850,135,f'EVSI = {gross-base:.1f}',30,GREEN,True)
    sc.text(850,185,f'净改善 = {net-base:.1f}',29,GOLD,True)
    sc.text(850,246,'EVPI = 3.2',29,NAVY,True)
    sc.text(850,283,'各类调查的期望增益上限',22,MUTED)
    sc.text(20,337,'EVSI 是调查带来的毛增值；扣除一次调查费后，才得到净改善。',24,NAVY,True)


def sampling_values():
    d=DATA['sampling'];out=[]
    for x in range(d['n']+1):
        joint=[p*comb(d['n'],x)*theta**x*(1-theta)**(d['n']-x)
               for theta,p in zip(d['theta'],d['prior'])]
        prob=sum(joint);contribution=sum(p*v for p,v in zip(joint,d['purchase']))
        out.append((x,prob,contribution/prob,contribution))
    return out


def sampling(sc):
    sc.text(20,25,'抽取 4 件；X 为缺陷数；不买的收益为 0；金额单位：元',23,NAVY,True)
    rows=[[str(x),f'{p:.8f}',f'{ev:.4f}','买' if ev>0 else '不买'] for x,p,ev,_ in sampling_values()]
    table(sc,['X','P(X)','买的条件期望','最优行动'],rows,[75,220,220,150],x=15,y=46,row_height=47,highlights=(0,))
    sc.text(730,76,'模型输入',24,NAVY,True)
    sc.text(730,115,'缺陷率：0.20 / 0.10 / 0.05',21,INK)
    sc.text(730,153,'先验：0.50 / 0.30 / 0.20',21,INK)
    sc.text(730,191,'买收益：-5 / 5 / 10 元',22,INK)
    sc.text(730,246,'X=0 的联合贡献',24,GREEN,True)
    sc.text(730,288,f'{sampling_values()[0][3]:.7f} 元',30,GREEN,True)
    sc.text(730,332,'= P(X=0) × 买的条件期望',21,MUTED)


def certainty(sc):
    d=DATA['utility'];lo=d['minimum'];hi=d['maximum'];k=d['k'];p=d['p_high']
    u=lambda value:(1-exp(-k*(value-lo)/(hi-lo)))/(1-exp(-k))
    eu=p;emv=p*hi+(1-p)*lo
    ce=lo-(hi-lo)/k*log(1-eu*(1-exp(-k)))
    X=lambda value:75+(value-lo)/(hi-lo)*590
    Y=lambda value:275-value*215
    sc.text(20,25,'规范化效用 u(x)；k = 3',23,NAVY,True)
    sc.line(X(lo),Y(0),X(hi),Y(0),MUTED,1)
    sc.line(X(lo),Y(0),X(lo),Y(1),MUTED,1)
    for v in [0,.5,1]:
        sc.text(X(lo)-14,Y(v)+7,f'{v:g}',20,MUTED,anchor='end')
    sc.polyline([(X(lo+(hi-lo)*j/100),Y(u(lo+(hi-lo)*j/100))) for j in range(101)],NAVY,4)
    sc.line(X(lo),Y(0),X(hi),Y(1),GOLD,2,[6,5])
    sc.line(X(lo),Y(eu),X(emv),Y(eu),GREEN,1.5,[5,4])
    sc.line(X(ce),Y(0),X(ce),Y(eu),GREEN,1.5,[5,4])
    sc.line(X(emv),Y(eu),X(emv),Y(u(emv)),RED,2)
    for value,utility,col in [(lo,0,NAVY),(hi,1,NAVY),(ce,eu,GREEN),(emv,eu,GOLD),(emv,u(emv),RED)]:
        sc.point(X(value),Y(utility),col,9)
    for value in [lo,emv,hi]:sc.text(X(value),305,f'{value:g}',21,MUTED,anchor='middle')
    sc.text(X(ce),334,f'CE ≈ {ce:.3f}',21,GREEN,True,anchor='middle')
    sc.text(665,334,'结果 x / 万元',21,MUTED,anchor='end')
    sc.text(745,66,'教学参数示例',26,NAVY,True)
    sc.text(745,108,'风险方案：各半得到 20 / -10',22,INK)
    sc.text(745,151,f'EU = {eu:.1f}；EMV = {emv:g} 万元',24,GOLD,True)
    sc.text(745,197,f'确定 5 万元：u(5) = {u(emv):.4f}',23,RED,True)
    sc.text(745,243,f'CE = {ce:.4f} 万元 < 5 万元',24,GREEN,True)
    sc.text(745,289,'凹效用：u(E[V]) > E[u(V)]',23,NAVY)
    sc.text(745,331,'金色虚线连接两端结果的效用',21,MUTED)


def oil(sc):
    d=DATA['oil'];p=d['prior'];lh,ll=d['closed_likelihood']
    closed=p*lh+(1-p)*ll;opened=1-closed
    gross=closed*d['closed_value']+opened*d['open_value'];net=gross-d['fee']
    sc.text(20,26,'先验 P(有油)=0.3；P(封闭|有油)=0.8；P(封闭|无油)=0.4',23,NAVY,True)
    table(sc,['报告及概率','有油的后验','最优行动','条件期望 / 万美元'],
          [[f'封闭  {closed:.2f}','6/13','自采',f'{d["closed_value"]:g}'],
           [f'开放  {opened:.2f}','1/8','租让',f'{d["open_value"]:g}']],
          [260,230,210,400],y=56,row_height=56)
    sc.text(25,271,f'试验毛价值 {gross:g}',27,GREEN,True)
    sc.text(355,271,f'减试验费 {d["fee"]:g}',27,GOLD,True)
    sc.text(660,271,f'净价值 {net:g}',27,GREEN,True)
    sc.text(25,330,f'不试验基准 {d["baseline"]:g}；EVSI = {gross-d["baseline"]:g}；净改善 = {net-d["baseline"]:g}（万美元）',26,NAVY,True)


def strategy(sc):
    sc.text(20,26,'最晚节点先选好行动，再把条件价值带回期初（万元）',24,NAVY,True)
    sc.text(40,64,'前 3 年经营期望',22,MUTED)
    sc.text(380,64,'后 7 年：按前期好 / 差加权',22,MUTED)
    sc.text(890,64,'减去期初投入',22,MUTED)
    cases=[('中店',232.5,903,168,400,GREEN),('小店',136.5,693,54.6,150,NAVY)]
    for i,(name,early,good,poor,cost,color) in enumerate(cases):
        y=85+i*121;value=early+.75*good+.25*poor-cost
        for x,w in [(20,285),(365,435),(865,255)]:sc.rect(x,y,w,90,SOFT_GREEN if i==0 else PALE)
        sc.text(40,y+34,name,26,color,True)
        sc.text(40,y+72,f'{early:g}',28,color,True)
        sc.text(385,y+34,f'0.75 × {good:g} + 0.25 × {poor:g}',24,color,True)
        sc.text(385,y+71,'条件策略已计入后期价值',21,MUTED)
        for start,end in [(313,355),(808,855)]:
            sc.line(start,y+45,end,y+45,color,2)
            sc.line(end-8,y+39,end,y+45,color,2)
            sc.line(end-8,y+51,end,y+45,color,2)
        sc.text(885,y+33,f'{value:g}' + ('  选中' if i==0 else ''),29,color,True)
        sc.text(885,y+71,f'已扣投入 {cost:g}',22,MUTED)
    sc.text(20,342,'小店的后期规则：好则扩建（693），差则保持（54.6）；不再重复扣扩建费。',23,NAVY,True)


def lottery(sc):
    d=DATA['utility'];lo,hi,p=d['minimum'],d['maximum'],d['p_high'];mean=p*hi+(1-p)*lo
    sc.text(20,26,'相同的期望金额，不同的结果分布；金额单位：万元',24,NAVY,True)
    sc.rect(20,59,520,230,PALE)
    sc.text(45,98,'确定方案',27,NAVY,True)
    sc.text(280,173,f'{mean:g} 万元',42,NAVY,True,'middle')
    sc.text(280,228,'概率 100%',26,MUTED,False,'middle')
    sc.text(590,98,'风险方案',27,GOLD,True)
    cx,cy,r=635,186,16
    sc.polyline([(cx+r*cos(2*pi*j/40),cy+r*sin(2*pi*j/40)) for j in range(41)],GOLD,2)
    for y,value,prob in [(134,hi,p),(267,lo,1-p)]:
        sc.line(cx+r,cy,862,y,GOLD,2)
        sc.line(862,y,895,y,GOLD,2)
        sc.text(920,y+9,f'{value:g} 万元',30,NAVY if value>=0 else RED,True)
        sc.text(755,y-19 if value==hi else y+26,f'{prob:.0%}',24,GOLD,True)
    sc.text(590,230,'机会节点',20,MUTED)
    sc.text(45,332,f'EMV = {mean:g} 万元',28,NAVY,True)
    sc.text(590,332,f'EMV = 0.5 × 20 + 0.5 × (-10) = {mean:g}',25,GOLD,True)


FIGURES = {'emv': emv, 'regret': regret, 'perfect': perfect,
           'late_choice': late_choice, 'frequencies': frequencies,
           'posterior_policy': posterior_policy, 'information': information,
           'sampling': sampling, 'certainty': certainty, 'oil': oil,
           'strategy': strategy, 'lottery': lottery}


def make_figure(s):
    key=s['figure']
    if key not in FIGURES:
        raise ValueError(f'Unknown chapter-three figure: {key}')
    scene=Scene(s.get('title',key))
    FIGURES[key](scene)
    return scene


def draw_figure(s,c,H):
    make_figure(s).pdf(c,H)


def figure_html(s):
    return make_figure(s).svg()
