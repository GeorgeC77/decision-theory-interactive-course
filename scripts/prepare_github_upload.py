"""Prepare a clean, independent GitHub snapshot; never copy hosting credentials."""
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'tmp/github-upload'
if DEST.exists():
    raise SystemExit('Snapshot already exists; inspect it before replacing any files.')

files = [ROOT / p for p in ['.gitignore', 'README.md', 'start-course.cmd', '打开课程.html']]
for folder in ['content', 'docs', 'scripts', 'course-site/dist', 'output/pdf', 'output/imagegen']:
    files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file()
                 and not any(part in {'.git', '.openai', '__pycache__', 'node_modules'} for part in p.parts)
                 and p.suffix not in {'.pyc', '.log'} and not p.name.startswith('.env'))

secret = re.compile(r'(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9_.-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
for p in files:
    if p.suffix.lower() in {'.js', '.cjs', '.py', '.json', '.html', '.md', '.cmd', '.css'}:
        if secret.search(p.read_text(encoding='utf-8')):
            raise SystemExit('Potential credential: inspect ' + str(p.relative_to(ROOT)))

for p in files:
    target = DEST / p.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, target)
report = {'file_count': len(files), 'total_bytes': sum(p.stat().st_size for p in files),
          'largest_file_bytes': max(p.stat().st_size for p in files),
          'snapshot': str(DEST), 'excluded': ['source textbook', 'temporary files', 'ZIP archives', 'hosting configuration', 'nested Git history', 'environments']}
(ROOT / 'tmp/github-upload-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
