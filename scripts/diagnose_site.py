"""Read-only checks of the deployed course; credentials are never written."""
import sys, urllib.request, urllib.error, hashlib
from pathlib import Path

origin = 'https://decision-theory-lab-20260916.cuigengutokyo.chatgpt.site'
token = sys.argv[1] if len(sys.argv) > 1 else ''
for path in ['/', '/index.html', '/assets/style.css', '/ch1/index.html']:
    headers = {'OAI-Sites-Authorization': 'Bearer ' + token} if token else {}
    request = urllib.request.Request(origin + path, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    except Exception as error:
        print(path, type(error).__name__, str(error)); continue
    body = response.read()
    local = Path('course-site/dist') / (path.strip('/') or 'index.html')
    print(path, 'status=', response.status, 'type=', response.headers.get('Content-Type'),
          'length=', len(body), 'matches_local=', local.exists() and body == local.read_bytes())
    print('server=', response.headers.get('Server'), 'location=', response.headers.get('Location'))
    if response.status == 200 and local.exists() and path.endswith(('html', '/')):
        import difflib
        original = local.read_text(encoding='utf-8')
        actual = body.decode('utf-8', errors='replace')
        print('HTML_DIFF:', '\n'.join(difflib.unified_diff(original.splitlines(), actual.splitlines()))[:5000])
    if response.status != 200:
        print(body[:1200].decode('utf-8', errors='replace'))
