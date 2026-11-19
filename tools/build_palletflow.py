"""Genera web/palletflow.html (el "motor" PalletFlow dentro de EUREKA) a partir del
PalletFlow original. No toca cálculos, lectura de guías, rótulos ni hojas de peso:
solo la piel (estilo EUREKA), la marca, el modo incrustado y accesos para EUREKA.

Uso: python3 tools/build_palletflow.py <palletflow original.html> <logo-mask.b64>
"""
import re
import sys

SRC, LOGO = sys.argv[1], sys.argv[2]
DST = 'web/palletflow.html'
s = open(SRC, encoding='utf-8').read()
lines = s.split('\n')


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f'ERROR {n}x: {old[:90]!r}')
    s = s.replace(old, new)


# ---------- 1. Piel EUREKA: capa propia sobre la estructura "Nítido" de PalletFlow 4 ----------
start = next(i for i, l in enumerate(lines) if 'PALLETFLOW 4 — ESTILO "NÍTIDO"' in l) - 1
end = next(i for i, l in enumerate(lines) if l.startswith('/* ===== Tarjeta de lote: textos más grandes'))
nit = '\n'.join(lines[start:end])
sk = nit.replace('pf2-cards-nitido', 'pf2-cards-eureka')
swaps = [
    ('PALLETFLOW 4 — ESTILO "NÍTIDO"', 'EUREKA — piel de EUREKA para el motor PalletFlow'),
    ('--n-bg:#000000;', '--n-bg:#000000;'),
    ('--n-s1:#0A0A0C;', '--n-s1:#0a0a0a;'),
    ('--n-s2:#111114;', '--n-s2:#111111;'),
    ('--n-s3:#18181C;', '--n-s3:#181818;'),
    ('--n-line:rgba(255,255,255,.075);', '--n-line:rgba(255,255,255,.08);'),
    ('--n-tx:#F5F5F7;', '--n-tx:#f7f7f8;'),
    ('--n-r:14px; --n-r-sm:10px;', '--n-r:18px; --n-r-sm:12px;'),
    ('--pf2-surface-3:#202026;', '--pf2-surface-3:#222228;'),
    ('color-mix(in srgb, var(--pf-accent) 9%, transparent), transparent 70%);}', 'color-mix(in srgb, var(--pf-accent) 18%, transparent), transparent 70%);}'),
    ("transparent 70%), #000 !important; font-family:'Inter', var(--pf2-font), sans-serif;}", "transparent 70%), #050506 !important; font-family:'Inter', sans-serif;}"),
]
for a, b in swaps:
    if a not in sk:
        sys.exit('swap no encontrado: ' + a[:70])
    sk = sk.replace(a, b)
# acción principal: ámbar con texto oscuro, como el botón + de EUREKA
sk = re.sub(r'(html body\.pf2-cards-eureka \.dia-btn\.pri:not\(#pf4-x\)\{)background:var\(--n-tx\) !important; color:#000 !important;',
            r'\1background:#f5a524 !important; color:#111 !important;', sk)
sk = sk.replace("html body.pf2-cards-eureka #app .conc-cta:hover{transform:translateY(-1px) !important; filter:none !important; background:#fff !important;}",
                "html body.pf2-cards-eureka #app .conc-cta:hover{transform:translateY(-1px) !important; filter:brightness(1.06) !important;}")

ESENCIA = r'''
/* ---------- Esencia EUREKA ---------- */
html body.pf2-cards-eureka{font-family:'Inter', sans-serif !important;}
html body.pf2-cards-eureka .pf-page-t{font-family:'Inter Tight','Inter',sans-serif !important; font-weight:900 !important; letter-spacing:-.045em !important;}
html body.pf2-cards-eureka :is(.pf-page-kicker, #pfDate){letter-spacing:.22em !important; font-size:10.5px !important; font-weight:600 !important;}
html body.pf2-cards-eureka .pf-card-h h2{font-family:'Inter Tight','Inter',sans-serif !important; font-weight:800 !important; letter-spacing:-.01em !important;}
html body.pf2-cards-eureka #app .lot-card .lot-name, html body.pf2-cards-eureka #app .lot-card b:first-child{color:#fcd34d !important; font-family:'Inter Tight','Inter',sans-serif !important; font-weight:900 !important; letter-spacing:-.03em !important;}
html body.pf2-cards-eureka #app .lot-title-stack .lot-num-badge{color:#fcd34d !important; font-family:'Inter Tight','Inter',sans-serif !important; font-weight:900 !important; font-size:30px !important; letter-spacing:-.04em !important;}
html body.pf2-cards-eureka :is(.rsp-value, #stepperValue, #diaTotal){font-family:'Inter Tight','Inter',sans-serif !important; font-weight:900 !important; letter-spacing:-.04em !important;}
html body.pf2-cards-eureka .pf-status{border-radius:999px !important; background:var(--n-s1) !important;}
html body.pf2-cards-eureka #pfLock .pf-lock-title{font-family:'Inter',sans-serif; letter-spacing:.22em; font-size:11px; text-transform:uppercase; color:#7c7c87;}
html body.pf2-cards-eureka #pfLock .pf-lock-pad button:not(#x){border-radius:22px !important;}
html body.pf2-cards-eureka #pfLock .pf-lock-dots i{border-color:#52525b !important;}
html body.pf2-cards-eureka #pfLock .pf-lock-dots i.on{background:#f5a524 !important; border-color:#f5a524 !important;}
html body.pf2-cards-eureka .pf-brand-logo{background:linear-gradient(180deg,#ffffff 30%,#a1a1aa 140%) !important;}
html body.pf2-cards-eureka .pf-brand-sub{background:none !important; color:#7c7c87 !important; -webkit-text-fill-color:#7c7c87 !important; letter-spacing:.22em !important; font-weight:600 !important; font-size:10.5px !important;}
'''
sk += ESENCIA
s = s.replace(nit, nit + '\n' + sk, 1)

# ---------- 2. Marca EUREKA ----------
b64 = open(LOGO).read().strip()
m = re.search(r'(\.pf-brand-logo\{[^}]*?-webkit-mask:url\(data:image/png;base64,)([A-Za-z0-9+/=]+)(\))', s)
if not m:
    sys.exit('mask no encontrada')
s = s.replace(m.group(2), b64)
rep('<title>PalletFlow — Recepción</title>', '<title>EUREKA</title>')
s = s.replace('aria-label="PalletFlow"', 'aria-label="EUREKA"')
rep("titulo:'¿Bloquear PalletFlow?'", "titulo:'¿Bloquear EUREKA?'")
rep("titulo:titulo || 'PalletFlow', ok:'Entendido'", "titulo:titulo || 'EUREKA', ok:'Entendido'")
rep("titulo:'PalletFlow', input:true", "titulo:'EUREKA', input:true")
s = s.replace('<span class="pf-sb-sub pf-nav-t">RECEPCIÓN</span>', '<span class="pf-sb-sub pf-nav-t">RECEPCIÓN DE ARÁNDANOS</span>')

# ---------- 3. Tema EUREKA por defecto ----------
rep("  { id: 'blanco', name: 'Blanco', accent: '#FFFFFF',",
    "  { id: 'eureka', name: 'EUREKA', accent: '#3B82F6', accent2: '#60A5FA', accentFg: '#FFFFFF', glow: 'rgba(59,130,246,0.30)', glow2: 'rgba(96,165,250,0.22)', bg: '#050506' },\n  { id: 'blanco', name: 'Blanco', accent: '#FFFFFF',")
rep("  { id:'amoled', name:'Negro AMOLED', css:'#000000' },",
    "  { id:'eureka-negro', name:'Negro EUREKA', css:'#050506' },\n  { id:'amoled', name:'Negro AMOLED', css:'#000000' },")
rep("  { id:'blanco', name:'Blanco', css:'#FFFFFF' },\n  { id:'negro'",
    "  { id:'eureka-texto', name:'EUREKA', css:'#F7F7F8' },\n  { id:'blanco', name:'Blanco', css:'#FFFFFF' },\n  { id:'negro'")
rep("  { id:'cyan',    name:'Cyan',     a:'#10404a', b:'#a6f2ef' },",
    "  { id:'eureka',  name:'EUREKA',   a:'#a1a1aa', b:'#ffffff' },\n  { id:'cyan',    name:'Cyan',     a:'#10404a', b:'#a6f2ef' },")
rep("let themeId = 'electrico';", "let themeId = 'eureka';")
rep("let fondoId = 'amoled';", "let fondoId = 'eureka-negro';")
rep("let textoColorId = 'blanco';", "let textoColorId = 'eureka-texto';")
rep("let logoColorId = 'cyan';", "let logoColorId = 'eureka';")
rep("let pf2 = Object.assign({}, PF2_DEF);\ntry { const s = localStorage.getItem(PF2_KEY); if (s) pf2 = Object.assign({}, PF2_DEF, JSON.parse(s)); } catch (e) {}",
    "const PF_EK_SET = { gradType:'solid', gradAngle:135, glow:true, ca1:'#3B82F6', ca2:'#60A5FA', bgCustom:false, pattern:'none', patternOp:0.04, ambient:false,\n  font:'Inter', numFont:'Inter Tight', zoom:1, numScale:1, radius:'redondeada', cards:'eureka', density:'normal', borders:'sutil', sidebar:'expandida',\n  anim:'completas', hover:'elevar', spotlight:false, lc:false, logoGlow:false, logoSize:1 };\nlet pf2 = Object.assign({}, PF2_DEF, PF_EK_SET);\ntry { const s = localStorage.getItem(PF2_KEY); if (s) pf2 = Object.assign({}, PF2_DEF, JSON.parse(s)); } catch (e) {}")
rep("['solido','contorno','vidrio','elevado','degradado','nitido'].forEach(k => b.classList.toggle('pf2-cards-' + k, pf2.cards === k));",
    "['solido','contorno','vidrio','elevado','degradado','nitido','eureka'].forEach(k => b.classList.toggle('pf2-cards-' + k, pf2.cards === k));")
rep("pf2Seg('cards', [['nitido','Nítidas','AMOLED, borde fino'],", "pf2Seg('cards', [['eureka','EUREKA','Negro, Inter'],['nitido','Nítidas','AMOLED, borde fino'],")
rep("const PF2_PRESETS = [\n", "const PF2_PRESETS = [\n  { id:'eureka', name:'EUREKA', sub:'Negro EUREKA, Inter y cifras Inter Tight, acento azul.', theme:'eureka', fondo:'eureka-negro', texto:'eureka-texto', logo:'eureka', set:PF_EK_SET },\n")
rep("const PF2_SYS_FONTS = ['Figtree', 'Albert Sans', 'Cabin', 'Inconsolata'];", "const PF2_SYS_FONTS = ['Figtree', 'Albert Sans', 'Cabin', 'Inconsolata', 'Inter', 'Inter Tight', 'Manrope', 'Sora'];")
rep("function pf3Login(u){", "const PF_EK_SNAP = { pf2:PF_EK_SET, themeId:'eureka', fondoId:'eureka-negro', textoColorId:'eureka-texto', logoColorId:'eureka', light:false };\nfunction pf3Login(u){")
rep("""    pf3Put('temas', lista); pf3Put('pred', 'pf4-base'); pf3Put('look4V1', 1);
  }""", """    pf3Put('temas', lista); pf3Put('pred', 'pf4-base'); pf3Put('look4V1', 1);
  }
  if (pf3Get('eurekaV3', null) !== 1) {
    const lista = pf3Temas().filter(t => t.id !== 'flow-base');
    if (!lista.some(t => t.id === 'eureka-base')) lista.unshift({ id:'eureka-base', nombre:'EUREKA', fecha:'predeterminado', snap:JSON.parse(JSON.stringify(PF_EK_SNAP)) });
    pf3Put('temas', lista); pf3Put('pred', 'eureka-base'); pf3Put('eurekaV3', 1);
  }""")
rep("else if (u.id === 'general') pf3ApplySnapshot({ pf2:{}, themeId:'electrico', fondoId:'amoled', textoColorId:'blanco', logoColorId:'cyan' });",
    "else if (u.id === 'general') pf3ApplySnapshot(JSON.parse(JSON.stringify(PF_EK_SNAP)));")

# ---------- 4. Modo incrustado + accesos para EUREKA ----------
rep('<head>', '<head>\n<script>try { if (window.parent !== window) document.documentElement.classList.add("pf-embed"); } catch (e) { document.documentElement.classList.add("pf-embed"); }</script>')
MOTOR = r'''
<style>
/* ===== PalletFlow dentro de EUREKA: sin menú propio (EUREKA pone la barra de abajo) ===== */
html.pf-embed, html.pf-embed body{--pf-sb-w:0px !important; --pf4-nav-h:0px !important;}
html.pf-embed #pfSidebar, html.pf-embed #pfSbToggle, html.pf-embed #pfLock{display:none !important;}
html.pf-embed body .pf-shell::before{left:0 !important;}
html.pf-embed body #app{padding-bottom:24px !important;}
/* la X para salir, siempre arriba a la derecha */
html.pf-embed :is(#klOverlay, #ffOverlay, #ingresoOverlay, #ubOv, #hfOverlay, #masterOverlay, #kpiOv) button:has(path[d^="M18 6"]){order:99 !important; margin-left:auto !important;}
html.pf-embed, html.pf-embed body{touch-action:pan-x pan-y;}
html.pf-embed body{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;}
html.pf-embed input, html.pf-embed textarea{-webkit-user-select:text;user-select:text;}
/* ===== Almacén pensado para el celular ===== */
@media (max-width:900px){
  html.pf-embed #ubOv{padding:10px 10px 16px !important; gap:8px !important; overflow-x:hidden !important; overflow-y:auto !important;}
  html.pf-embed #ubOv .kdx-h{position:relative; display:block !important; padding-right:48px;}
  html.pf-embed #ubOv .kdx-tit b{font-size:22px; font-weight:900; letter-spacing:-.03em;}
  html.pf-embed #ubOv .kdx-tit span{font-size:12px; opacity:.7;}
  html.pf-embed #ubOv .kdx-acc{display:grid !important; grid-template-columns:repeat(4,1fr); gap:6px; margin-top:10px;}
  html.pf-embed #ubOv .kdx-acc .dia-btn{width:100%; min-height:42px; padding:0 4px !important; border-radius:999px !important; font-size:12.5px !important; justify-content:center;}
  html.pf-embed #ubOv #ubCerrar{position:absolute; top:0; right:0; width:42px; height:42px; border-radius:999px;}
  html.pf-embed .ub-zonas{gap:6px;}
  html.pf-embed .ub-zonas button{border-radius:16px !important; padding:8px 12px !important;}
  html.pf-embed .ub-barra{flex-wrap:nowrap !important; overflow-x:auto; gap:6px !important; padding-bottom:4px; scrollbar-width:none;}
  html.pf-embed .ub-barra::-webkit-scrollbar{display:none;}
  html.pf-embed .ub-barra > *{flex:none;}
  html.pf-embed .ub-barra .mat-sp{display:none;}
  html.pf-embed .ub-cuerpo{flex-direction:column !important; gap:8px !important; min-width:0;}
  html.pf-embed .ub-izq{position:sticky; top:-10px; z-index:3; flex:none !important; background:var(--n-bg, #000); padding:6px 0 8px !important; margin:0 -10px; padding-left:10px !important; padding-right:10px !important; border-bottom:1px solid rgba(255,255,255,.08);}
  html.pf-embed .ub-izq-h b{font-size:13px; letter-spacing:.1em; text-transform:uppercase; opacity:.7;}
  html.pf-embed #ubLista{display:flex !important; gap:8px; overflow-x:auto; scroll-snap-type:x proximity; scrollbar-width:none;}
  html.pf-embed #ubLista::-webkit-scrollbar{display:none;}
  html.pf-embed .ub-lote{flex:none !important; min-width:150px; min-height:58px; border-radius:16px !important;}
  html.pf-embed .ub-lote.sel{transform:translateY(-1px); box-shadow:0 8px 20px -10px var(--lb);}
  html.pf-embed .ub-tip, html.pf-embed .ub-flecha{display:none !important;}
  html.pf-embed .ub-der{flex:none !important; width:100%; min-width:0; max-width:100%; overflow:hidden !important;}
  html.pf-embed .ub-grid{width:100% !important; max-width:100% !important; min-width:0; gap:3px !important;}
  html.pf-embed .ub-c{min-height:0 !important; min-width:0 !important; aspect-ratio:1 !important; border-radius:7px !important;}
  html.pf-embed .ub-c.llena b{font-size:11px !important;}
  html.pf-embed .ub-c .ub-c-f{font-size:8px !important;}
  html.pf-embed .ub-dis{position:fixed !important; left:0; right:0; bottom:0; z-index:20; max-height:62vh; border-radius:24px 24px 0 0 !important; background:var(--n-s1, #0a0a0a) !important; box-shadow:0 -20px 50px rgba(0,0,0,.7);}
}
/* todo en negro (o el fondo del tema de EUREKA); los gráficos no cambian */
html.pf-embed body :is(#ffOverlay, #klOverlay, #ingresoRoot, #ubOv, #masterOverlay, #hfOverlay){background:var(--n-bg, #000) !important;}
html.pf-embed body :is(#diaOverlay, #ubOv, #pesajeOverlay, #masterOverlay){left:0 !important; bottom:0 !important;}
/* sin calculadora: Recepción muestra escanear guías y correlativos impresos */
html body #app #calcView > .pf-calc-card{display:none !important;}
html body #app #calcView > .pf-calc-side{flex:1 1 100%; flex-direction:row; flex-wrap:wrap; align-items:stretch;}
html body #app #calcView > .pf-calc-side > .pf-card{flex:1 1 380px; min-width:0;}
@media (max-width:520px){ html body #app #pfGuideSlot .guide-card{grid-template-columns:minmax(0,1fr) minmax(0,1fr) !important;} html body #app #pfGuideSlot .guide-card #rotuloTodosBtn{padding-inline:10px !important;} }
@media (max-width:900px){ html body #app #calcView > .pf-calc-side{flex-direction:column;} html body #app #calcView > .pf-calc-side > .pf-card{flex:none;} }
</style>
<script>
/* Capturas y gráficos: tocarlos abre el visor de EUREKA (ahí sí hay zoom con los dedos) */
document.addEventListener('click', e => {
  if (!document.documentElement.classList.contains('pf-embed')) return;
  const im = e.target.closest && e.target.closest('img');
  if (!im || im.closest('button, a, label') || (im.naturalWidth || 0) < 360 || !im.closest('#klOverlay, #ffOverlay, #ingresoOverlay, #ubOv, #hfOverlay')) return;
  try { window.parent.ekOpenViewer(im.src); } catch (x) {}
}, true);
/* Sin PIN: dentro de EUREKA entra solo, como usuario general */
(function(){
  if (!document.documentElement.classList.contains('pf-embed')) return;
  const pad = document.getElementById('pfLockPad'); if (!pad) return;
  // sin sonido de "PIN correcto" al abrir la app
  const AC = window.AudioContext, WAC = window.webkitAudioContext;
  window.AudioContext = undefined; window.webkitAudioContext = undefined;
  try { ['1','2','3','6'].forEach(k => { const b = pad.querySelector('[data-k="' + k + '"]'); if (b) b.click(); }); }
  finally { window.AudioContext = AC; window.webkitAudioContext = WAC; }
})();
(function(){
  const P = { dia:['diaBtn','diaOverlay'], ub:['ubBtn','ubOv'], ingreso:['ingresoBtn','ingresoOverlay'], ff:['ffBtn','ffOverlay'], kl:['klBtn','klOverlay'],
              kpi:['kpiBtn','kpiOv'], hf:['hfBtn','hfOverlay'], master:['masterBtn','masterOverlay'], ajustes:['themeBtn','themeOverlay'] };
  const el = id => document.getElementById(id);
  window.pfApi = {
    abrir(k){ const b = el(P[k][0]); if (b) b.click(); },
    abierto(k){ const e = el(P[k][1]); return !!(e && e.classList.contains('open')); },
    cerrarTodo(){ Object.keys(P).forEach(k => { const e = el(P[k][1]); if (e && e.classList.contains('open')) e.classList.remove('open'); }); document.body.style.overflow = ''; },
    bloqueado(){ return document.body.classList.contains('pf-locked') || !!el('pfLock'); },
    usuario(){ return window.__pfUsuario || null; },
    masterGet(){ return JSON.parse(JSON.stringify(master)); },
    masterDefault(){ return JSON.parse(JSON.stringify(MASTER_DEFAULT)); },
    masterSet(m){ master = JSON.parse(JSON.stringify(m || [])); saveMaster(); try { if (el('masterOverlay').classList.contains('open')) renderMasterTable(); } catch (e) {} try { window.dispatchEvent(new Event('pf:master')); } catch (e) {} },
    escanear(files){ return pf5EscanearVarias(files); },
    elegirPdf(){ el('scanPdfBtn').click(); },
    elegirImagen(){ el('scanImgBtn').click(); },
    rotulosFechaManual(){ el('rotuloManualBtn').click(); },
    fechaAyer(){ el('rotuloAyerBtn').click(); return !!rotuloFechaAyer; },
    fechaAyerOn(){ return !!rotuloFechaAyer; },
    // Almacén: usa las guías que EUREKA leyó en el turno (mismo formato del motor)
    setGuias(lista, corr){ try { guides = JSON.parse(JSON.stringify(lista || [])); if (corr) correlativoAutoState = JSON.parse(JSON.stringify(corr)); } catch (e) { console.error(e); } },
    // colores del tema de EUREKA
    tema(v){ const b = document.body.style; Object.keys(v || {}).forEach(k => b.setProperty(k, v[k])); document.documentElement.style.setProperty('--pf-bg', v['--n-bg'] || '#000'); },
    leerConIA(file){ return extractGuideViaAI(file); },
    verImagen(src){ try { window.parent.ekOpenViewer(src); } catch (e) {} },
    guiasAbiertas(){ return (typeof guides !== 'undefined' && guides) ? guides.length : 0; },
  };
})();
</script>
'''
rep('\n</body>', MOTOR + '\n</body>')

open(DST, 'w', encoding='utf-8').write(s)
print('ok ->', DST, len(s))
