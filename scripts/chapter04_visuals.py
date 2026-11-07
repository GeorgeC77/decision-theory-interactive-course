"""Native vector diagrams for mathematical data, shared between PDF and HTML."""
from html import escape
from reportlab.lib.colors import HexColor
def draw_visual(s,c,para,line,rect,H):
    if s['type']=='heatmap':
        a=s['matrix'];n=len(a[0]);left=260;cw=910/n
        for j,h in enumerate(s['headers']):para(h,left+j*cw,228,cw-15,22,'#244e79',True,maxh=38)
        mn=min(map(min,a));mx=max(map(max,a));span=mx-mn or 1
        for i,row in enumerate(a):
            y=280+i*70;para(s['rows'][i],70,y+7,175,25,'#244e79',True,maxh=45)
            for j,v in enumerate(row):
                t=(v-mn)/span
                base=(234-int(t*38),241-int(t*34),248-int(t*28)) if not s.get('regret') else (249,241-int(t*40),226-int(t*55))
                rect(left+j*cw,y,cw-12,56,'#' + ''.join(f'{z:02x}'for z in base))
                para(f'{v:g}',left+j*cw+20,y+7,cw-48,27,'#132d49',True,maxh=43)
    else:
        a=s['matrix'];lo=min(map(min,a))-2;hi=max(map(max,a))+2;px=lambda x:290+(x-lo)/(hi-lo)*790
        for x in [-10,0,10,20]:
            line(px(x),235,px(x),550,'#dce3e9',1);para(str(x),px(x)-17,555,75,18,'#586a7c',maxh=33)
        for i,row in enumerate(a):
            y=266+i*76;left,right=min(row),max(row);para(s['rows'][i],70,y-20,170,25,'#244e79',True,maxh=45)
            line(px(left),y,px(right),y,'#244e79',5)
            for x,val in [(px(left),left),(px(right),right)]:
                c.setFillColor(HexColor('#bb8637'));c.circle(x,H-y,6,fill=1,stroke=0)
            para(f'{left:g}',px(left)-10,y+10,72,19,'#586a7c',maxh=32)
            if right!=left:para(f'{right:g}',px(right)-10,y+10,72,19,'#586a7c',maxh=32)
        para('最坏 ← 净价值范围 / 万元 → 最好',575,230,610,20,'#586a7c',maxh=33)
def visual_html(s):
    if s['type']=='heatmap':
        return '<table class="value-matrix"><thead><tr><th>方案</th>'+''.join('<th>'+escape(x)+'</th>'for x in s['headers'])+'</tr></thead><tbody>'+''.join('<tr><th>'+escape(s['rows'][i])+'</th>'+''.join(f'<td class="value-cell">{v:g}</td>'for v in row)+'</tr>'for i,row in enumerate(s['matrix']))+'</tbody></table>'
    a=s['matrix'];lo=min(map(min,a))-2;hi=max(map(max,a))+2;X=lambda x:240+(x-lo)/(hi-lo)*790
    svg='<svg viewBox="0 0 1150 350" role="img" aria-label="各方案最好最坏净价值区间"><text x="570" y="25" font-size="20" fill="#586a7c">最坏 ← 净价值范围 / 万元 → 最好</text>'
    for x in [-10,0,10,20]:svg+=f'<line x1="{X(x)}" x2="{X(x)}" y1="40" y2="320" stroke="#dce3e9"/><text x="{X(x)-8}" y="348" font-size="18">{x}</text>'
    for i,row in enumerate(a):
        y=70+75*i;left,right=min(row),max(row)
        svg+=f'<text x="20" y="{y+8}" font-size="25" fill="#244e79">{escape(s["rows"][i])}</text><line x1="{X(left)}" y1="{y}" x2="{X(right)}" y2="{y}" stroke="#244e79" stroke-width="5"/>'
        for v in set([left,right]):svg+=f'<circle cx="{X(v)}" cy="{y}" r="6" fill="#bb8637"/><text x="{X(v)-7}" y="{y+28}" font-size="19">{v:g}</text>'
    return svg+'</svg>'
