"""Build the offline teaching bundle without source textbook or credentials."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
target=root/'output/第一至六章教学包.zip'
files=[root/x for x in ['README.md','打开课程.html','start-course.cmd']]
for folder in ['docs','content','scripts','course-site/dist','output/pdf','output/imagegen']:
    files.extend(p for p in (root/folder).rglob('*') if p.is_file()
        and not any(x in p.parts for x in ['.openai','__pycache__','node_modules'])
        and p.name not in ['diagnose_site.py','check_ch2_serving.py','check_ch3_serving.py','check_ch4_serving.py','check_ch5_serving.py','check_ch6_serving.py','check_ch3_browser.cjs'])
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(set(files)):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for required in ['打开课程.html','course-site/dist/ch6/index.html','course-site/dist/ch6/slides.html','course-site/dist/downloads/chapter-06.pdf']:
        assert required in z.namelist()
print('Bundle files:',len(files),'bytes:',target.stat().st_size)
