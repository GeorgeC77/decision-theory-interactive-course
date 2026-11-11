"""Build the chapter-two PDF and editable HTML presentation from one content file.
Run with the project's env_Online_Lecture Python. No textbook raster pages are copied.
"""
from pathlib import Path
from chapter02_charts import draw_chart, chart_html, pdf_math
from chapter02_figures import draw_figure, figure_html
import json, html, shutil, math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'course-site' / 'dist'
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
(SITE / 'downloads').mkdir(exist_ok=True)
(SITE / 'ch2').mkdir(exist_ok=True)
SLIDES = json.loads((ROOT / 'content/chapter-02-slides.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('YaHei', 'C:/Windows/Fonts/msyh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold', 'C:/Windows/Fonts/msyhbd.ttc', subfontIndex=0))
W, H = 1280, 720
NAVY, BLUE, GOLD = '#132d49', '#244e79', '#bb8637'
INK, MUTED, LINE, PALE = '#1c2e41', '#586a7c', '#dce3e9', '#eaf1f8'
PDF = OUT / '第二章-确定型决策分析.pdf'
c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle('第二章 确定型决策分析 | 决策理论与方法')
c.setAuthor('决策理论与方法课程')
checks=[]

def rect(x,y,w,h,fill,stroke=None):
    c.setFillColor(colors.HexColor(fill))
    c.setStrokeColor(colors.HexColor(stroke or fill))
    c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))

def para(text,x,y,w,size=26,color=INK,bold=False,maxh=None,leading=None):
    style=ParagraphStyle('p',fontName='YaHeiBold' if bold else 'YaHei',fontSize=size,leading=leading or size*1.55,textColor=colors.HexColor(color),wordWrap='CJK',spaceAfter=0)
    safe=pdf_math(text)
    p=Paragraph(safe,style)
    _,h=p.wrap(w,1000)
    if maxh is not None and h>maxh+.1:
        raise ValueError(f'Slide {len(checks)+1}: text overflow {h}>{maxh}: {text[:40]}')
    if y+h>H-18:
        raise ValueError(f'Text outside page: {text[:50]}')
    p.drawOn(c,x,H-y-h)
    return h

def line(x1,y1,x2,y2,color=LINE,width=1):
    c.setStrokeColor(colors.HexColor(color));c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)

def arrow(x1,y1,x2,y2,color=BLUE):
    line(x1,y1,x2,y2,color,2)
    angle=math.atan2(y2-y1,x2-x1)
    for da in [-.5,.5]:
        line(x2,y2,x2-11*math.cos(angle+da),y2-11*math.sin(angle+da),color,2)

def header(s,n):
    rect(0,0,W,H,'#ffffff')
    label='补充阅读' if s.get('appendix') else '第二章 / 确定型决策分析'
    para(label,70,32,1000,15,BLUE,bold=True,maxh=30)
    para(s['title'],70,78,1140,44,NAVY,True,maxh=73)
    para(s.get('lead',''),70,152,1140,24,MUTED,maxh=80)
    line(70,662,1210,662)
    para(s.get('source',''),70,677,1060,14,MUTED,maxh=27,leading=20)
    para(f'{n:02d} / {len(SLIDES):02d}',1130,677,90,14,BLUE,maxh=27)
    if s.get('takeaway'):
        rect(70,594,1140,54,PALE)
        rect(70,594,4,54,GOLD)
        para(s['takeaway'],88,597,1103,20,BLUE,maxh=50,leading=25)

def columns(s):
    items=s['items'];gap=34;cw=(1140-gap*(len(items)-1))/len(items)
    for i,item in enumerate(items):
        x=70+i*(cw+gap)
        line(x,236,x+cw,236,GOLD,3)
        para(item[0],x,258,cw,29,BLUE,True,maxh=86)
        para(item[1],x,324,cw,22 if s['type']=='sources' else 25,INK,maxh=270)

def render_table(s):
    def cell(text,bold=False):
        return Paragraph(pdf_math(text),ParagraphStyle('table',fontName='YaHeiBold' if bold else 'YaHei',fontSize=19 if s.get('appendix') else 23,leading=25 if s.get('appendix') else 33,wordWrap='CJK',textColor=colors.HexColor(INK)))
    data=[[cell(x,True)for x in s['headers']]]+[[cell(x)for x in row]for row in s['rows']]
    ratios=[.23,.38,.39] if len(data[0])==3 else [.3,.7]
    t=Table(data,colWidths=[1140*x for x in ratios])
    pad=7 if s.get('appendix') else 10
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(PALE)),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.7,colors.HexColor(LINE)),('LEFTPADDING',(0,0),(-1,-1),16),('RIGHTPADDING',(0,0),(-1,-1),16),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad)]))
    _,h=t.wrap(1140,500)
    limit=414 if not s.get('takeaway') else 355
    if h>limit:raise ValueError(f'Table too high: {s["title"]}: {h}>{limit}')
    t.drawOn(c,70,H-228-h)

def render_flow(s):
    count=len(s['steps']);gap=26;cw=(1140-gap*(count-1))/count
    for i,(name,detail) in enumerate(zip(s['steps'],s['details'])):
        x=70+i*(cw+gap)
        rect(x,260,cw,86,PALE)
        para(name,x+11,279,cw-22,24,BLUE,True,maxh=55,leading=32)
        para(detail,x+5,376,cw-10,23,MUTED,maxh=128)
        if i<count-1:arrow(x+cw+3,303,x+cw+gap-3,303)
    if '五个步骤' in s['title']:
        line(1165,455,1165,524,BLUE,2);line(1165,524,165,524,BLUE,2);arrow(165,524,165,456)
        para('发现重大变化或原决策失误 → 回溯与追踪',366,530,770,20,BLUE,maxh=44)

def render_six(s):
    for i,(name,q,example) in enumerate(s['items']):
        col=i%3;row=i//3;x=70+col*390;y=232+row*170
        para(f'0{i+1}',x,y,65,34,GOLD,maxh=53)
        para(name,x+66,y+3,292,28,BLUE,True,maxh=48)
        para(q,x,y+56,360,22,INK,maxh=42)
        para(example,x,y+101,360,21,MUTED,maxh=60)

def render_matrix(s):
    for i,(name,tag,desc) in enumerate(s['items']):
        x=70+(i%2)*590;y=238+(i//2)*168
        rect(x,y,4,127,GOLD)
        para(name,x+20,y,215,27,BLUE,True,maxh=50)
        para(tag,x+250,y,290,28,INK,True,maxh=50)
        para(desc,x+20,y+60,520,24,MUTED,maxh=88)

def render_nine(s):
    for i,(name,desc) in enumerate(s['items']):
        x=70+(i%3)*390;y=228+(i//3)*118
        line(x,y,x+355,y,LINE)
        para(f'{i+1:02d}',x,y+17,52,24,GOLD,maxh=40)
        para(name+'原则',x+60,y+17,295,26,BLUE,True,maxh=46)
        para(desc,x,y+62,356,22,MUTED,maxh=52,leading=27)

def render_activity(s):
    for i,(name,desc) in enumerate(s['items']):
        y=231+i*109
        para(f'0{i+1}',70,y,65,39,GOLD,maxh=63)
        para(name,158,y+3,240,28,BLUE,True,maxh=66)
        para(desc,412,y+3,788,25,INK,maxh=94)
        if i<2:line(158,y+89,1210,y+89)

def render_car(s):
    rows=[('原始情境',10,2.19),('油价 × 4',10,8.76),('节油 40% + 调整车价',6.944,5.256)]
    for i,(name,a,b) in enumerate(rows):
        y=245+i*100
        para(name,70,y,380,24,BLUE,True,maxh=80)
        rect(430,y+8,a*32,38,BLUE);rect(430+a*32,y+8,b*32,38,GOLD)
        para(f'{a+b:.2f}%',1060,y,145,30,BLUE,True,maxh=54)
    para('年均购车负担',430,554,300,20,BLUE,maxh=32)
    para('年燃油负担',760,554,300,20,GOLD,maxh=32)

def render_equations(s):
    for i,(label,first,second) in enumerate(s['items']):
        y=232+i*164
        para(label,70,y,1100,26,BLUE,True,maxh=48)
        para(first,70,y+51,1135,25,INK,maxh=50)
        para(second,70,y+98,1135,25,INK,maxh=50)

def render_equipment_intro(s):
    # Crop only the lower cabinet illustration; keep both machines and worktops visible.
    c.saveState()
    clip=c.beginPath();clip.rect(70,H-457,1140,250);c.clipPath(clip,stroke=0)
    c.drawImage(str(SITE/'assets'/s['image']),70,H-207-1140*749/2098,1140,1140*749/2098,mask='auto')
    c.restoreState()
    for i,(label,body) in enumerate(s['items']):
        x=70+i*590
        para(label,x,470,540,27,BLUE,True,maxh=42)
        para(body.replace('\n','；'),x,512,540,22,INK,maxh=70,leading=29)

def render_cashflow_table(s):
    values=s['cashflows'];cw=1140/8
    for row,data in enumerate([['时点 t']+list(range(7)),['净现金流']+values]):
        y=232+row*54
        for col,value in enumerate(data):
            x=70+col*cw
            if row==0:rect(x,y,cw,54,PALE)
            para(str(value),x+9,y+13,cw-18,21,BLUE if row==0 else INK,bold=row==0,maxh=35)
            line(x,y+54,x+cw,y+54)
    for i,(label,body) in enumerate(s['items']):
        x=70+i*590
        para(label,x,382,540,27,BLUE,True,maxh=46)
        para(body,x,437,540,23,INK,maxh=100)

for n,s in enumerate(SLIDES,1):
    c.bookmarkPage(f'slide-{n}');c.addOutlineEntry(s['title'],f'slide-{n}',0)
    if s['type']=='cover':
        c.drawImage(str(ROOT/'output/imagegen/campus-cafe.png'),0,0,W,H,mask='auto')
        rect(0,0,545,H,NAVY)
        para('决策理论与方法',65,68,430,24,'#d5e1ed',maxh=44)
        para('第二章',65,162,410,28,'#e6bc79',maxh=50)
        para('确定型\n决策分析',62,233,450,74,'#ffffff',True,maxh=238,leading=98)
        para('现金流如何比较？\n多投的钱是否值得？',65,491,427,25,'#dbe5f0',maxh=104)
        para('大三经管类 · 4 学时',65,636,435,20,'#e6bc79',maxh=42)
    else:
        header(s,n)
        typ=s['type']
        if typ in ['columns','sources','closing']:columns(s)
        elif typ=='table':render_table(s)
        elif typ=='flow':render_flow(s)
        elif typ=='six':render_six(s)
        elif typ=='matrix':render_matrix(s)
        elif typ=='nine':render_nine(s)
        elif typ in ['activity','project']:render_activity(s)
        elif typ=='car':render_car(s)
        elif typ=='equations':render_equations(s)
        elif typ=='chart':draw_chart(s,c,para,line,H)
        elif typ=='figure':draw_figure(s,c,H)
        elif typ=='equipment_intro':render_equipment_intro(s)
        elif typ=='cashflow_table':render_cashflow_table(s)
        else:raise ValueError(typ)
    checks.append({'page':n,'title':s['title'],'layout':'passed'})
    c.showPage()
c.save()
shutil.copyfile(PDF,SITE/'downloads/chapter-02.pdf')

# HTML presentation remains editable through the JSON content source.
def esc(s):return html.escape(str(s)).replace('\n','<br>')
def html_body(s):
    t=s['type']
    if t=='figure':return figure_html(s)
    if t=='equipment_intro':return '<div class="equipment-intro"><img src="../assets/'+s['image']+'" alt="小型单头咖啡机与较大双头咖啡机的设备规模对比示意"><div class="equipment-copy">'+''.join('<article><h3>'+esc(a)+'</h3><p>'+esc(b).replace('<br>','；')+'</p></article>' for a,b in s['items'])+'</div></div>'
    if t=='cashflow_table':return '<table class="cashflow-table"><thead><tr><th>时点 t</th>'+''.join('<th>'+str(i)+'</th>' for i in range(7))+'</tr></thead><tbody><tr><th>净现金流</th>'+''.join('<td>'+str(v)+'</td>' for v in s['cashflows'])+'</tr></tbody></table><div class="cashflow-explanations">'+''.join('<article><h3>'+esc(a)+'</h3><p>'+esc(b)+'</p></article>' for a,b in s['items'])+'</div>'
    if t=='chart':return chart_html(s)
    if t=='cover':return '<div class="cover-copy"><p>决策理论与方法</p><p class="gold">第二章</p><h1>确定型<br>决策分析</h1><p>现金流如何比较？<br>多投的钱是否值得？</p><p class="cover-meta">大三经管类 · 4 学时</p></div>'
    if t=='table':return '<table><thead><tr>'+''.join('<th>'+esc(x)+'</th>'for x in s['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>'for x in row)+'</tr>'for row in s['rows'])+'</tbody></table>'
    if t=='flow':return '<div class="diagram-flow">'+''.join(f'<article><h3>{esc(a)}</h3><p>{esc(b)}</p></article>'for a,b in zip(s['steps'],s['details']))+'</div>'
    if t=='car':
        rows=[('原始情境',10,2.19),('油价 × 4',10,8.76),('节油 40% + 调整车价',6.944,5.256)]
        return '<div class="car-chart">'+''.join(f'<div class="chart-row"><strong>{a}</strong><div class="chart-track"><span style="width:{b/22*100}%"></span><span class="fuel" style="width:{d/22*100}%"></span></div><b>{b+d:.2f}%</b></div>'for a,b,d in rows)+'<p>深蓝：年均购车负担　金色：年燃油负担；均占年收入比例</p></div>'
    if t=='equations':return '<div class="equations">'+''.join(f'<article><h3>{esc(a)}</h3><p>{esc(b)}<br>{esc(d)}</p></article>'for a,b,d in s['items'])+'</div>'
    return '<div class="items '+t+'">'+''.join('<article>'+('<span class="item-number">'+f'{i+1:02}'+'</span>'if t in ['activity','project','six'] else '')+'<h3>'+esc(row[0])+'</h3>'+''.join('<p>'+esc(x)+'</p>'for x in row[1:])+'</article>'for i,row in enumerate(s['items']))+'</div>'

slides_html=''
for i,s in enumerate(SLIDES,1):
    classes='slide '+s['type']+(' active' if i==1 else '')+(' appendix' if s.get('appendix') else '')
    top='' if s['type']=='cover' else '<div class="slide-head"><span>'+('补充阅读'if s.get('appendix')else'第二章 / 确定型决策分析')+'</span><h2>'+esc(s['title'])+'</h2><p>'+esc(s.get('lead',''))+'</p></div>'
    takeaway='<div class="takeaway">'+esc(s['takeaway'])+'</div>'if s.get('takeaway')else''
    foot=''if s['type']=='cover'else'<div class="slide-source">'+esc(s.get('source',''))+f'<span>{i:02} / {len(SLIDES):02}</span></div>'
    slides_html+=f'<section class="{classes}" data-slide="{i}" aria-label="第 {i} 页：{html.escape(s["title"])}">'+top+'<div class="slide-body">'+html_body(s)+'</div>'+takeaway+foot+'</section>'

page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第二章 · 教学演示</title><link rel="stylesheet" href="../assets/slides.css"><link rel="stylesheet" href="../assets/ch2-slides.css"></head><body><header class="deck-toolbar"><a href="index.html">← 第二章学习</a><div><button id="prev">上一页</button><span id="page-counter" aria-live="polite"></span><button id="next">下一页</button></div><div><button id="notes-button" aria-expanded="false">讲稿</button><button id="fullscreen">全屏</button><a href="../downloads/chapter-02.pdf">PDF ↗</a></div></header><main id="deck" data-chapter="第二章">'''+slides_html+'''</main><aside id="speaker-notes" hidden></aside><p class="keyboard-hint">← → 翻页 · Home / End 首尾页 · F 全屏 · N 讲稿</p><script id="notes-data" type="application/json">'''+json.dumps([s['notes']for s in SLIDES],ensure_ascii=False).replace('</','<\/')+'''</script><script src="../assets/slides.js?v=20260919-1"></script></body></html>'''
page=page.replace('../assets/ch2-slides.css"','../assets/ch2-slides.css?v=20261111-1"')
(SITE/'ch2/slides.html').write_text(page,encoding='utf-8')
(ROOT/'tmp/ch2-pdf-layout-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {len(SLIDES)} slides: {PDF}')
