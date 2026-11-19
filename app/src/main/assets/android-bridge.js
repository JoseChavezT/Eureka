/* Puente Android para Eureka Flow y su módulo Recepciones.
   - Descargas (<a download> con blob:/data:) -> se guardan en Descargas/EUREKA del teléfono.
   - window.open de un PDF/imagen en memoria -> se abre con el visor del teléfono.
   - window.claude.use('downloads') -> mismo guardado (lo usa el módulo Recepciones). */
(function () {
  if (!window.EurekaAndroid) return;
  var A = window.EurekaAndroid;

  function toBase64(blob) {
    return new Promise(function (res, rej) {
      var r = new FileReader();
      r.onload = function () { var s = String(r.result); res(s.slice(s.indexOf(',') + 1)); };
      r.onerror = function () { rej(r.error); };
      r.readAsDataURL(blob);
    });
  }
  async function aBlob(href) {
    var b = blobs.get(href);
    if (b) return b;
    return await (await fetch(href)).blob();
  }
  async function guardar(nombre, blob) {
    if (!(blob instanceof Blob)) blob = new Blob([blob == null ? '' : blob]);
    var r = A.saveFile(nombre || 'archivo', blob.type || '', await toBase64(blob));
    if (r !== 'ok') throw new Error(r);
  }
  function avisar(e) {
    var t = 'No se pudo guardar el archivo: ' + ((e && e.message) || e);
    if (window.pfAlerta) window.pfAlerta(t); else alert(t);
  }

  // recordar los blobs para poder leerlos aunque luego se revoque la URL
  var blobs = new Map();
  var oc = URL.createObjectURL;
  URL.createObjectURL = function (b) { var u = oc.call(URL, b); try { if (b instanceof Blob) blobs.set(u, b); } catch (e) {} return u; };

  function interceptar(a) {
    if (!a || !a.hasAttribute || !a.hasAttribute('download')) return false;
    var href = a.href || '';
    if (!/^(blob:|data:)/.test(href)) return false;
    var nombre = a.getAttribute('download') || 'archivo';
    aBlob(href).then(function (b) { return guardar(nombre, b); }).catch(avisar);
    return true;
  }
  var origClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () { if (interceptar(this)) return; return origClick.call(this); };
  var origDispatch = EventTarget.prototype.dispatchEvent;
  HTMLAnchorElement.prototype.dispatchEvent = function (e) { if (e && e.type === 'click' && interceptar(this)) return true; return origDispatch.call(this, e); };
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest && e.target.closest('a[download]');
    if (a && interceptar(a)) { e.preventDefault(); e.stopPropagation(); }
  }, true);

  // window.open de archivos en memoria -> visor del teléfono
  var origOpen = window.open;
  window.open = function (u) {
    var s = String(u || '');
    if (/^(blob:|data:)/.test(s) && A.openFile) {
      aBlob(s).then(async function (b) {
        var ext = /pdf/.test(b.type) ? '.pdf' : /png/.test(b.type) ? '.png' : /jpe?g/.test(b.type) ? '.jpg' : '';
        A.openFile('ver-' + Date.now() + ext, b.type || 'application/pdf', await toBase64(b));
      }).catch(avisar);
      return null;
    }
    return origOpen.apply(window, arguments);
  };

  // capacidad "downloads" (la usa el módulo Recepciones)
  var downloads = { save: async function (o) { await guardar(o && o.filename, o && o.data); } };
  window.claude = Object.assign(window.claude || {}, {
    use: async function (name) { return name === 'downloads' ? downloads : null; }
  });

  // barra del sistema con el color de la app (solo la ventana principal)
  if (window.parent === window && A.setBarColor) { try { A.setBarColor('#07060f', false); } catch (e) {} }
})();
