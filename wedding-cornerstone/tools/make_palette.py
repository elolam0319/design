# Write a palette copy of index.html by injecting a :root override before </style>.
# usage: python tools/make_palette.py index.html out.html {01|03}
import sys

PALETTES = {
    '01': '--navy:#26334A;--navy-ray:#2f3d57;--navy-deep:#1b2537;--cream:#EDE4D5;--cream-ray:#e6dbc8;--coral:#AF6554',  # Vintage Ink & Ivory
    '03': '--navy:#30322F;--navy-ray:#3a3c38;--navy-deep:#232522;--cream:#E8E0D2;--cream-ray:#e0d6c5;--coral:#A64F45',  # Charcoal & Muted Red
}
src, out, key = sys.argv[1:4]
html = open(src, encoding='utf-8').read()
i = html.index('</style>')
open(out, 'w', encoding='utf-8').write(html[:i] + ':root{' + PALETTES[key] + '}\n' + html[i:])
print('wrote', out)
