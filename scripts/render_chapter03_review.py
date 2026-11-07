from pathlib import Path
import fitz
from PIL import Image,ImageOps,ImageDraw
root=Path(__file__).resolve().parents[1]
out=root/'tmp/ch3-review';out.mkdir(exist_ok=True)
doc=fitz.open(root/'output/pdf/第三章-风险型决策分析.pdf')
for i,page in enumerate(doc):
    page.get_pixmap(matrix=fitz.Matrix(1,1)).save(out/f'slide-{i+1:02}.png')
for first in range(0,len(doc),4):
    sheet=Image.new('RGB',(1536,904),'#dae1e8');draw=ImageDraw.Draw(sheet)
    for j in range(4):
        if first+j>=len(doc):break
        im=Image.open(out/f'slide-{first+j+1:02}.png');im.thumbnail((768,432))
        x=(j%2)*768;y=(j//2)*452
        sheet.paste(im,(x,y+20));draw.text((x+12,y+3),str(first+j+1),fill='#132d49')
    sheet.save(out/f'contact-{first//4+1:02}.png')
print('Rendered',len(doc),'pages and', (len(doc)+3)//4,'contact sheets')
