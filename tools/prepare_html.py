"""Prepara los HTML de web/ para el APK:
- web/app.html     -> index.html  (Eureka Flow: base PalletFlow + apartado Recepciones)
- web/eureka.html  -> eureka.html (módulo Recepciones, se abre dentro de la app)
Cambia los CDN por copias locales (funciona sin internet), usa fuentes locales
e inyecta el puente de Android."""
import re
import sys

LIBS = {
    r"https://cdnjs\.cloudflare\.com/ajax/libs/pdf\.js/[^\"']*/pdf\.min\.js": "lib/pdf.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/xlsx/[^\"']*/xlsx\.full\.min\.js": "lib/xlsx.full.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/jspdf/[^\"']*/jspdf\.umd\.min\.js": "lib/jspdf.umd.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/html2canvas/[^\"']*/html2canvas\.min\.js": "lib/html2canvas.min.js",
    r"https://cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^\"']*/three\.min\.js": "lib/three.min.js",
    r"https://cdn\.jsdelivr\.net/npm/three@[^\"']*/OrbitControls\.js": "lib/OrbitControls.js",
}


def prepare(src, dst):
    html = open(src, encoding="utf-8").read()
    for pat, local in LIBS.items():
        html = re.sub(pat, local, html)
    # Google Fonts -> fuentes locales
    html = re.sub(r"@import url\('https://fonts\.googleapis\.com/css2[^']*'\);", "@import url('fonts/pf-fonts.css');", html)
    html = re.sub(r'<link[^>]+href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>',
                  '<link rel="stylesheet" href="fonts/fonts.css"><link rel="stylesheet" href="fonts/pf-fonts.css">', html)
    html = re.sub(r'<link rel="preconnect"[^>]*>', "", html)
    # Puente Android antes que cualquier otro script
    html = re.sub(r"(<head[^>]*>)", r'\1\n<script src="android-bridge.js"></script>', html, count=1)
    left = re.findall(r'(?:src|href)="(https://cdn[^"]+)"', html)
    if left:
        print("aviso: quedan CDN sin copia local:", left, file=sys.stderr)
    open(dst, "w", encoding="utf-8").write(html)
    print(f"{src} -> {dst}")


out = sys.argv[1]
prepare("web/app.html", f"{out}/index.html")
prepare("web/eureka.html", f"{out}/eureka.html")
