"""photos/links.json 에 적힌 원본 링크의 사진을 각 국회 폴더(01~22)에 내려받습니다.
사용법: 저장소 최상위에서  python3 photos/download.py
이미 있는 파일은 건너뜁니다."""
import json, os, urllib.request
base = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(base, 'links.json'), encoding='utf-8'))
ok = fail = skip = 0
for a, rows in data.items():
    for r in rows:
        if not r['link'] or not r['file']:
            continue
        out = os.path.join(base, '%02d' % int(a), r['file'])
        if os.path.exists(out):
            skip += 1; continue
        try:
            req = urllib.request.Request(r['link'], headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://namu.wiki/'})
            with urllib.request.urlopen(req, timeout=30) as res, open(out, 'wb') as f:
                f.write(res.read())
            ok += 1
        except Exception as e:
            fail += 1; print('실패', a, r['name'], e)
print('받음', ok, '건너뜀', skip, '실패', fail)
