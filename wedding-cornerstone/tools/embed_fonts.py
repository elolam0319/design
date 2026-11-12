# Subset the uploaded fonts to the glyphs index.html uses and inline them as woff2 data URIs between the @fonts markers.
import base64, re, sys, io
from fontTools import subset
from fontTools.ttLib import TTFont
html_path, up = sys.argv[1], sys.argv[2]
FACES = [  # (family, file, css weight)
    ('Pretendard Variable', '3b7814fb-PretendardVariable.ttf', '45 930'),
    ('Hada Condensed', 'a2a490b2-HadaCondensed-Bold.otf', '700'),
]
src = open(html_path, encoding='utf-8').read()
start, end = '/* @fonts:start */', '/* @fonts:end */'
a, b = src.index(start), src.index(end)
body = src[:a] + src[b:]
text = ''.join(sorted(set(re.sub(r'\s', '', body)) | set(chr(c) for c in range(0x20, 0x7f)) | set('·–—♥’…')))
rules = []
for fam, fn, w in FACES:
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['*']; opts.name_IDs = ['*']; opts.notdef_outline = True
    f = TTFont(f'{up}/{fn}')
    sub = subset.Subsetter(opts); sub.populate(text=text); sub.subset(f)
    buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    print(f'{fam}: {len(buf.getvalue())//1024} KB', file=sys.stderr)
    rules.append(f'@font-face {{ font-family: "{fam}"; font-weight: {w}; font-display: block; src: url(data:font/woff2;base64,{data}) format("woff2"); }}')
note = '/* Pretendard, Hada Condensed: SIL OFL 1.1. Subset to the glyphs this page uses. */'
out = src[:a] + start + '\n' + note + '\n' + '\n'.join(rules) + '\n' + src[b:]
open(html_path, 'w', encoding='utf-8').write(out)
