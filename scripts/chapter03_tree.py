"""Data-native decision tree; identical edges and labels in PDF and SVG."""
from reportlab.lib import colors
EDGES=[(140,400,460,300),(140,400,460,500),(460,300,850,245),(460,300,850,355),(460,500,850,445),(460,500,850,555)]
TEXT=[(190,295,'小店'),(190,460,'大店'),(540,232,'高 0.6'),(540,338,'低 0.4'),(540,432,'高 0.6'),(540,534,'低 0.4'),(885,227,'8 万元'),(885,337,'2 万元'),(885,427,'16 万元'),(885,537,'−6 万元'),(350,248,'EMV 5.6'),(350,448,'EMV 7.2'),(70,420,'选大店')]
def draw_tree(c,para,line,rect,H):
    for e in EDGES:line(*e,'#8298ab',2)
    rect(123,383,34,34,'#244e79')
    c.setFillColor(colors.HexColor('#bb8637'))
    for x,y in [(460,300),(460,500)]:c.circle(x,H-y,12,fill=1,stroke=0)
    for x,y,t in TEXT:para(t,x,y,230,24,'#244e79',maxh=48)
def tree_html():
    out='<svg class="decision-diagram" viewBox="0 200 1280 400" role="img" aria-label="咖啡店决策树：小店期望5.6，大店期望7.2万元，选大店"><g stroke="#8298ab" stroke-width="2">'
    out+=''.join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a,b,c,d in EDGES)+'</g>'
    out+='<rect x="123" y="383" width="34" height="34" fill="#244e79"/>'
    out+=''.join(f'<circle cx="460" cy="{y}" r="12" fill="#bb8637"/>' for y in [300,500])
    out+=''.join(f'<text x="{x}" y="{y+28}" fill="#244e79" font-size="24">{t}</text>' for x,y,t in TEXT)
    return out+'</svg>'
