"""Chapter-two data figures sharing one native PDF / inline SVG scene.

Coordinates use a 1140 x 350 canvas. PDF figures begin at x=70, top=228.
No raster assets, chart-library runtime, or browser dependencies are required.
"""
from html import escape
from math import pow

NAVY = '#244e79'
GOLD = '#bb8637'
GREEN = '#24664d'
RED = '#ad4d46'
INK = '#1c2e41'
MUTED = '#586a7c'
GRID = '#dce3e9'


class Scene:
    """Small display list; text remains text in both output formats."""
    def __init__(self, title):
        self.title = title
        self.ops = []

    def line(self, x1, y1, x2, y2, color=NAVY, width=2, dash=None):
        self.ops.append(('line', x1, y1, x2, y2, color, width, dash))

    def rect(self, x, y, width, height, color, stroke=None, line_width=1):
        self.ops.append(('rect', x, y, width, height, color, stroke, line_width))

    def text(self, x, y, value, size=23, color=INK, bold=False, anchor='start'):
        self.ops.append(('text', x, y, str(value), size, color, bold, anchor))

    def point(self, x, y, color=NAVY, size=8):
        self.rect(x-size/2, y-size/2, size, size, color)

    def polyline(self, points, color=NAVY, width=3):
        for a, b in zip(points, points[1:]):
            self.line(*a, *b, color, width)

    def pdf(self, canvas, H):
        from reportlab.lib.colors import HexColor
        canvas.saveState()
        ox, oy = 70, H-228
        for op in self.ops:
            kind, *v = op
            if kind == 'line':
                x1, y1, x2, y2, color, width, dash = v
                canvas.setStrokeColor(HexColor(color));canvas.setLineWidth(width)
                canvas.setDash(dash or [])
                canvas.line(ox+x1, oy-y1, ox+x2, oy-y2)
            elif kind == 'rect':
                x, y, w, h, fill, stroke, width = v
                canvas.setDash([]);canvas.setLineWidth(width)
                if fill:canvas.setFillColor(HexColor(fill))
                if stroke:canvas.setStrokeColor(HexColor(stroke))
                canvas.rect(ox+x, oy-y-h, w, h, fill=bool(fill), stroke=bool(stroke))
            else:
                x, y, value, size, color, bold, anchor = v
                canvas.setFont('YaHeiBold' if bold else 'YaHei', size)
                canvas.setFillColor(HexColor(color))
                fn = {'start':canvas.drawString, 'middle':canvas.drawCentredString,
                      'end':canvas.drawRightString}[anchor]
                fn(ox+x, oy-y, value)
        canvas.restoreState()

    def svg(self):
        fmt = lambda n: f'{n:.3f}'.rstrip('0').rstrip('.') if isinstance(n, float) else str(n)
        title = escape(self.title, quote=True)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 350" '
                 f'role="img" aria-label="{title}" style="width:100%;height:auto;display:block">',
                 f'<title>{title}</title>']
        for op in self.ops:
            kind, *v = op
            if kind == 'line':
                x1, y1, x2, y2, color, width, dash = v
                dashed = f' stroke-dasharray="{" ".join(map(fmt,dash))}"' if dash else ''
                parts.append(f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" '
                             f'y2="{fmt(y2)}" stroke="{color}" stroke-width="{width}"{dashed}/>')
            elif kind == 'rect':
                x, y, w, h, fill, stroke, width = v
                parts.append(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" '
                             f'height="{fmt(h)}" fill="{fill or "none"}" '
                             f'stroke="{stroke or "none"}" stroke-width="{width}"/>')
            else:
                x, y, value, size, color, bold, anchor = v
                parts.append(f'<text x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}" '
                             f'style="font-family:Microsoft YaHei,sans-serif;font-size:{size}px;'
                             f'font-weight:{700 if bold else 400};fill:{color}">{escape(value)}</text>')
        return ''.join(parts)+'</svg>'


def axes(sc, x, y, w, h, xlim, ylim, xticks, yticks, xlabel, ylabel):
    X = lambda value: x+(value-xlim[0])/(xlim[1]-xlim[0])*w
    Y = lambda value: y+h-(value-ylim[0])/(ylim[1]-ylim[0])*h
    for value, label in yticks:
        sc.line(x, Y(value), x+w, Y(value), GRID, 1)
        sc.text(x-12, Y(value)+7, label, 20, MUTED, anchor='end')
    sc.line(x, y, x, y+h, MUTED, 1.5)
    sc.line(x, Y(0), x+w, Y(0), MUTED, 1.5)
    for value, label in xticks:
        sc.line(X(value), y+h, X(value), y+h+5, MUTED, 1)
        sc.text(X(value), y+h+30, label, 20, MUTED, anchor='middle')
    sc.text(x, 25, ylabel, 22, NAVY)
    sc.text(x+w, 345, xlabel, 21, MUTED, anchor='end')
    return X, Y


def growth(sc):
    X, Y = axes(sc, 80, 65, 640, 220, (0,5), (0,180),
                [(i,str(i)) for i in range(6)], [(i,str(i)) for i in [0,50,100,150]],
                '年末 t / 年', '本利和 / 万元')
    sc.polyline([(X(t/20),Y(100*pow(1.1,t/20))) for t in range(101)], NAVY, 4)
    sc.line(X(2), Y(0), X(2), Y(121), GOLD, 2, [6,5])
    for t, value, label, dx in [(0,100,'100',14),(2,121,'121',12),(5,161.051,'161.05',-90)]:
        sc.point(X(t),Y(value),GOLD if t==2 else NAVY)
        sc.text(X(t)+dx,Y(value)-15,label,25,GOLD if t==2 else NAVY,True)
    sc.text(810,75,'本金 100 万元',26,NAVY,True)
    sc.text(810,116,'年利率 10%，按年复利',23)
    sc.text(810,178,'第 2 年：100 × 1.1 × 1.1',22)
    sc.text(810,218,'= 121 万元',30,GOLD,True)
    sc.text(810,285,'第 5 年约为 161.05 万元',22,MUTED)


def contribution(sc):
    sc.text(35,27,'售价的构成 /（元/杯）',23,NAVY,True)
    sc.text(35,88,'售价 18 元',25,NAVY,True)
    x, w = 250, 720
    sc.rect(x,49,w/3,54,GOLD)
    sc.rect(x+w/3,49,w*2/3,54,NAVY)
    sc.text(x+w/6,84,'变动成本 6',24,INK,True,'middle')
    sc.text(x+w*2/3,84,'边际贡献 12',25,'#ffffff',True,'middle')
    sc.text(35,146,'月度边际贡献的用途 / 元',23,NAVY,True)
    for q, y, profit in [(2000,166,0),(3000,250,12000)]:
        sc.text(35,y+34,f'{q:,} 杯/月',25,NAVY,True)
        sc.rect(x,y,480,52,NAVY)
        sc.text(x+240,y+34,'覆盖固定成本 24,000',24,'#ffffff',True,'middle')
        if profit:
            sc.rect(x+480,y,240,52,GREEN)
            sc.text(x+600,y+34,'利润 12,000',24,'#ffffff',True,'middle')
        else:sc.text(x+505,y+34,'贡献 24,000，利润 0',23,MUTED)
    sc.text(250,340,'3,000 杯 × 12 元/杯 = 36,000 元；超过固定成本的部分形成利润。',21,MUTED)


def capacity(sc):
    # The shaded region is mathematically calculable but beyond current capacity.
    x, y, w, h = 105,65,615,220
    capx=x+w*1800/3000
    sc.rect(capx,y,x+w-capx,h,'#f0f3f6')
    X,Y=axes(sc,x,y,w,h,(0,3000),(-24000,12000),
             [(i,f'{i:,}') for i in [0,1000,2000,3000]],
             [(i,f'{i:,}') for i in [-24000,-12000,0,12000]],
             '月销量 Q / 杯', '月利润 / 元')
    sc.polyline([(X(q),Y(12*q-24000)) for q in [0,3000]],NAVY,4)
    sc.line(X(1800),y,X(1800),y+h,GOLD,2,[6,5])
    sc.point(X(1800),Y(-2400),RED,10)
    sc.point(X(2000),Y(0),GREEN,9)
    sc.text(X(1800)+12,91,'超出现有产能',21,MUTED)
    sc.text(810,64,'L = 12Q - 24,000',25,NAVY,True)
    sc.text(810,106,'售价 18；变动成本 6 元/杯',22)
    sc.text(810,149,'产能上限：1,800 杯/月',24,GOLD,True)
    sc.text(810,190,'最大可实现利润',23)
    sc.text(810,231,'-2,400 元/月',31,RED,True)
    sc.text(810,294,'保本需 2,000 杯/月',24,GREEN,True)


def equipment(sc):
    X,Y=axes(sc,95,65,625,220,(0,500),(-4000,1500),
             [(i,str(i)) for i in [0,100,200,300,400,500]],
             [(i,f'{i:,}') for i in [-4000,-2000,0,1000]],
             '月销量 Q / 件', '月利润 / 元')
    sc.text(270,25,'旧：L = 8Q - 3,200',20,NAVY)
    sc.text(520,25,'新：L = 10Q - 3,800',20,GOLD)
    sc.polyline([(X(q),Y(8*q-3200)) for q in [0,500]],NAVY,4)
    sc.polyline([(X(q),Y(10*q-3800)) for q in [0,500]],GOLD,4)
    sc.point(X(300),Y(-800),RED,10)
    sc.line(X(380),Y(0),X(380),285,GOLD,1.5,[5,4])
    sc.line(X(400),Y(0),X(400),285,NAVY,1.5,[5,4])
    sc.point(X(380),Y(0),GOLD);sc.point(X(400),Y(0),NAVY)
    sc.text(810,70,'相同利润：300 件/月',24,RED,True)
    sc.text(810,108,'此时均亏损 800 元/月',23)
    sc.text(810,167,'新设备保本：380 件/月',23,GOLD,True)
    sc.text(810,208,'旧设备保本：400 件/月',23,NAVY,True)
    sc.text(810,273,'350 件/月时',23)
    sc.text(810,309,'旧亏 400，新亏 300 元/月',22,MUTED)


def target(sc):
    X,Y=axes(sc,105,65,615,220,(0,30000),(-40000,80000),
             [(i,f'{i:,}') for i in [0,10000,20000,30000]],
             [(i,f'{i:,}') for i in [-40000,0,40000,80000]],
             '销量 Q / 瓶（同一核算期）', '利润 / 元')
    sc.polyline([(X(q),Y(4*q-40000)) for q in [0,30000]],NAVY,4)
    for q, profit, color in [(10000,0,GOLD),(25000,60000,GREEN)]:
        sc.line(X(q),Y(-40000),X(q),Y(profit),color,1.5,[6,5])
        if profit:sc.line(X(0),Y(profit),X(q),Y(profit),color,1.5,[6,5])
        sc.point(X(q),Y(profit),color,10)
    sc.text(810,64,'L = 4Q - 40,000',25,NAVY,True)
    sc.text(810,103,'售价 8；变动成本 4 元/瓶',22)
    sc.text(810,160,'保本销量：10,000 瓶',25,GOLD,True)
    sc.text(810,218,'利润目标：60,000 元',24,GREEN,True)
    sc.text(810,258,'所需销量：25,000 瓶',25,GREEN,True)
    sc.text(810,309,'比保本销量多 15,000 瓶',22,MUTED)


def rankings(sc):
    panels=[(20,'净现值 NPV / 万元（i = 8%）',10,[9.3101,9.9725],1),
            (610,'内部收益率 IRR / %',26,[23.7666,19.4381],0)]
    for x,title,limit,values,winner in panels:
        sc.text(x,29,title,24,NAVY,True)
        bx=x+70;bw=415
        for i,value in enumerate(values):
            y=80+i*104;color=GREEN if i==winner else NAVY
            sc.text(x+16,y+33,['A','B'][i],27,color,True)
            sc.rect(bx,y,bw*value/limit,50,color)
            sc.text(bx+bw*value/limit-15,y+34,f'{value:.4f}',25,'#ffffff',True,'end')
        sc.line(bx,266,bx+bw,266,MUTED,1)
        for value in [0,limit/2,limit]:
            px=bx+bw*value/limit
            sc.line(px,266,px,272,MUTED,1)
            sc.text(px,294,f'{value:g}',20,MUTED,anchor='middle')
        sc.text(x+70,337,'按总价值：B 更高' if winner==1 else '按收益率：A 更高',25,GREEN,True)


def budget(sc):
    amounts={'A':200,'B':120,'C':40,'D':90,'E':130,'F':360,'H':150}
    colors={'A':NAVY,'B':GOLD,'C':GREEN,'D':GOLD,'E':GREEN,'F':GOLD,'H':RED}
    sc.text(190,25,'投资构成 / 万元；每组总投资均为 600 万元',23,NAVY,True)
    rows=[('NPV 排序','AFC',189.8),('教材组合','ABHDC',258.5),('枚举最优','ABEH',259.6)]
    for i,(label,ids,npv) in enumerate(rows):
        y=65+i*88
        sc.text(5,y+33,label,25,NAVY,True)
        x=190
        for name in ids:
            width=610*amounts[name]/600;color=colors[name]
            sc.rect(x,y,width,48,color)
            sc.text(x+width/2,y+31,f'{name}{amounts[name]}',20,INK if color==GOLD else '#ffffff',True,'middle')
            x+=width
        sc.text(850,y+32,f'NPV {npv:.1f} 万元',27,GREEN if i==2 else NAVY,True)
    sc.text(190,337,'枚举比 NPV 排序多 69.8 万元，比教材组合多 1.1 万元。',23,GREEN,True)


def npv(sc):
    x,w,maximum=230,570,5
    investment=x+4/maximum*w
    sc.text(investment,29,'初始投入 4 万元',23,NAVY,True,'middle')
    sc.line(investment,42,investment,276,GOLD,2,[7,5])
    for i,(rate,present,net) in enumerate([(5,4.489194,0.489194),(20,3.218171,-0.781829)]):
        y=86+i*125;end=x+present/maximum*w
        sc.text(30,y+35,f'i = {rate}%',28,NAVY,True)
        sc.rect(x,y,present/maximum*w,53,NAVY)
        if net>0:sc.rect(investment,y,end-investment,53,GREEN)
        else:sc.rect(end,y,investment-end,53,'#f4e7e5',RED)
        sc.text(x,y-12,f'流入现值 {present:.4f} 万元',24,NAVY,True)
        sc.text(850,y+8,'净现值 NPV',23)
        sc.text(850,y+45,f'{net:+.4f} 万元',28,GREEN if net>0 else RED,True)
    sc.text(30,333,'同一现金流：期初投入 4 万元；年净流入 1.15 万元，共 4 年；末年另收残值 0.5 万元。',21,MUTED)


FIGURES={'growth':growth,'contribution':contribution,'capacity':capacity,
         'equipment':equipment,'target':target,'rankings':rankings,'budget':budget,'npv':npv}


def make_figure(s):
    key=s['figure']
    if key not in FIGURES:raise ValueError(f'Unknown chapter-two figure: {key}')
    sc=Scene(s.get('title',key));FIGURES[key](sc)
    return sc


def draw_figure(s,c,H):
    """Draw the selected figure at PDF x=70, top=228, size 1140 x 350."""
    make_figure(s).pdf(c,H)


def figure_html(s):
    """Return one self-contained SVG using the same data and geometry as PDF."""
    return make_figure(s).svg()
