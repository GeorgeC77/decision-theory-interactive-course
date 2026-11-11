"""Data-driven PDF and SVG charts (editable series remain in slide JSON)."""
import html, math
import re

def pdf_math(text):
    """Use PDF text positioning for glyphs absent from Microsoft YaHei."""
    s=html.escape(str(text)).replace('\n','<br/>')
    sub=dict(zip('₀₁₂₃₄₅₆₇₈₉ₜₙ','0123456789tn'))
    sub.update({'ᵢ':'i','ⱼ':'j','ₛ':'s','ₖ':'k','ₐ':'a','ₚ':'p','ₘ':'m','ᵣ':'r','ₕ':'h','₋':'-','₊':'+','₍':'(','₎':')'})
    sup=dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺ⁿᵗᵏ','0123456789-+ntk'))
    sup.update({'⁽':'(','⁾':')'})
    s=re.sub('['+''.join(sub)+']+',lambda m:'<sub>'+''.join(sub[c] for c in m[0])+'</sub>',s)
    return re.sub('['+''.join(sup)+']+',lambda m:'<super>'+''.join(sup[c] for c in m[0])+'</super>',s)

COLORS=['#244e79','#bb8637','#24664d']
def geometry(s):
    pts=[p for series in s['series'] for p in series['points']]
    xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts)
    ymin=min(0,min(p[1] for p in pts));ymax=max(0,max(p[1] for p in pts))
    span=ymax-ymin or 1
    lo,hi=s.get('ylimits',[ymin-span*.07,ymax+span*.13])
    return xmin,xmax or 1,lo,hi

def draw_chart(s,c,para,line,H):
    from reportlab.lib.colors import HexColor
    xmin,xmax,ymin,ymax=geometry(s);left,top,w,h=122,260,620,255
    px=lambda x:left+(x-xmin)/(xmax-xmin)*w
    py=lambda y:top+h-(y-ymin)/(ymax-ymin)*h
    for j in range(5):
        y=ymin+(ymax-ymin)*j/4
        line(left,py(y),left+w,py(y),'#dce3e9',.7)
        para(f'{y:.1f}',left-108,py(y)-12,103,17,'#586a7c',maxh=30)
    line(left,py(0),left+w,py(0),'#586a7c',1)
    c.saveState()
    c.setFont('YaHei',17)
    c.setFillColor(HexColor('#586a7c'))
    for x,label in s.get('xticks',[(xmin+(xmax-xmin)*j/5,f'{xmin+(xmax-xmin)*j/5:g}')for j in range(6)]):
        line(px(x),top+h,px(x),top+h+5,'#586a7c',1)
        c.drawCentredString(px(x),H-(top+h+27),str(label))
    c.restoreState()
    para(s['ylabel'],left,220,650,18,'#244e79',maxh=32)
    para(s['xlabel'],left+160,top+h+47,450,18,'#586a7c',maxh=32)
    for idx,series in enumerate(s['series']):
        col=COLORS[idx%len(COLORS)];points=series['points']
        if s.get('chartmode')=='stem':
            offset=(idx-(len(s['series'])-1)/2)*12
            for x,y in points:line(px(x)+offset,py(0),px(x)+offset,py(y),col,7)
        elif not series.get('scatter'):
            for a,b in zip(points,points[1:]):line(px(a[0]),py(a[1]),px(b[0]),py(b[1]),col,3)
        for x,y in points:
            if len(points)<=10 or series.get('scatter'):
                offset=(idx-(len(s['series'])-1)/2)*12 if s.get('chartmode')=='stem' else 0
                c.setFillColor(HexColor(col));c.circle(px(x)+offset,H-py(y),3,fill=1,stroke=0)
        para(series['name'],810,234+idx*33,390,18,col,True,maxh=32)
    for j,(label,body) in enumerate(s['items']):
        y=325+j*119
        para(label,810,y,380,24,'#244e79',True,maxh=44)
        para(body,810,y+43,380,21,'#1c2e41',maxh=85,leading=29)

def chart_html(s):
    xmin,xmax,ymin,ymax=geometry(s);left,top,w,h=65,45,560,240
    px=lambda x:left+(x-xmin)/(xmax-xmin)*w
    py=lambda y:top+h-(y-ymin)/(ymax-ymin)*h
    e=html.escape
    parts=[f'<svg viewBox="0 0 690 355" role="img" aria-label="{e(s["title"])}"><title>{e(s["title"])}</title>']
    for j in range(5):
        y=ymin+(ymax-ymin)*j/4
        parts.append(f'<line x1="{left}" y1="{py(y)}" x2="{left+w}" y2="{py(y)}" stroke="#dce3e9"/><text x="{left-9}" y="{py(y)+5}" text-anchor="end">{y:.1f}</text>')
    parts.append(f'<line x1="{left}" y1="{py(0)}" x2="{left+w}" y2="{py(0)}" stroke="#586a7c"/>')
    for x,label in s.get('xticks',[(xmin+(xmax-xmin)*j/5,f'{xmin+(xmax-xmin)*j/5:g}')for j in range(6)]):
        parts.append(f'<line x1="{px(x)}" y1="{top+h}" x2="{px(x)}" y2="{top+h+5}" stroke="#586a7c"/>')
        parts.append(f'<text x="{px(x)}" y="310" text-anchor="middle">{e(label)}</text>')
    for idx,series in enumerate(s['series']):
        col=COLORS[idx%len(COLORS)]
        if s.get('chartmode')=='stem':
            offset=(idx-(len(s['series'])-1)/2)*12
            for x,y in series['points']:parts.append(f'<line x1="{px(x)+offset}" y1="{py(0)}" x2="{px(x)+offset}" y2="{py(y)}" stroke="{col}" stroke-width="7"/>')
        elif not series.get('scatter'):
            xy=' '.join(f'{px(x):.2f},{py(y):.2f}' for x,y in series['points'])
            parts.append(f'<polyline points="{xy}" fill="none" stroke="{col}" stroke-width="3"/>')
        if len(series['points'])<=10 or series.get('scatter'):
            offset=(idx-(len(s['series'])-1)/2)*12 if s.get('chartmode')=='stem' else 0
            for x,y in series['points']:parts.append(f'<circle cx="{px(x)+offset}" cy="{py(y)}" r="3" fill="{col}"/>')
    parts.extend([f'<text x="65" y="22">{e(s["ylabel"])}</text>',f'<text x="350" y="343" text-anchor="middle">{e(s["xlabel"])}</text></svg>'])
    legend=''.join(f'<p class="chart-legend" style="color:{COLORS[i%3]}">{e(x["name"])}</p>'for i,x in enumerate(s['series']))
    items=''.join('<h3>'+e(a)+'</h3><p>'+e(b).replace('\n','<br>')+'</p>' for a,b in s['items'])
    return '<div class="chart-layout">'+''.join(parts)+'<div>'+legend+items+'</div></div>'
