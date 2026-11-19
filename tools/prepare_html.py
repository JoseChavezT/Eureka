"""Copia web/eureka.html a los assets del APK, cambiando los CDN por copias locales
(para que la app funcione sin internet) e inyectando el puente de Android."""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
html = open(src, encoding="utf-8").read()

LIBS = {
    r"https://cdnjs\.cloudflare\.com/ajax/libs/pdf\.js/[^\"']*/pdf\.min\.js": "lib/pdf.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/xlsx/[^\"']*/xlsx\.full\.min\.js": "lib/xlsx.full.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/jspdf/[^\"']*/jspdf\.umd\.min\.js": "lib/jspdf.umd.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^\"']*/three\.min\.js": "lib/three.min.js",
    r"https://cdn\.jsdelivr\.net/npm/three@[^\"']*/OrbitControls\.js": "lib/OrbitControls.js",
}
for pat, local in LIBS.items():
    html, n = re.subn(pat, local, html)
    if n == 0:
        print(f"aviso: no se encontró {local} en el HTML", file=sys.stderr)

# Fuentes locales en vez de Google Fonts
html = re.sub(r'<link[^>]+href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>',
              '<link rel="stylesheet" href="fonts/fonts.css">', html)
html = re.sub(r'<link rel="preconnect"[^>]*>', "", html)

# Puente Android antes que cualquier otro script
html = re.sub(r"(<head[^>]*>)", r'\1\n<script src="android-bridge.js"></script>', html, count=1)

open(dst, "w", encoding="utf-8").write(html)
print(f"HTML preparado -> {dst}")
