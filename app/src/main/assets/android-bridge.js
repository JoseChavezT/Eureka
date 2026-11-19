/* Puente Android: la app ya sabe guardar archivos vía window.claude.use('downloads').
   Aquí se lo damos, pero guardando en Descargas/EUREKA del teléfono. */
(function () {
  if (!window.EurekaAndroid) return;
  function toBase64(blob) {
    return new Promise(function (res, rej) {
      var r = new FileReader();
      r.onload = function () { var s = String(r.result); res(s.slice(s.indexOf(',') + 1)); };
      r.onerror = function () { rej(r.error); };
      r.readAsDataURL(blob);
    });
  }
  var downloads = {
    save: async function (opts) {
      var data = opts && opts.data;
      if (!(data instanceof Blob)) data = new Blob([data == null ? '' : data]);
      var b64 = await toBase64(data);
      var r = window.EurekaAndroid.saveFile((opts && opts.filename) || 'archivo', data.type || '', b64);
      if (r !== 'ok') throw new Error(r);
    }
  };
  window.claude = Object.assign(window.claude || {}, {
    use: async function (name) { return name === 'downloads' ? downloads : null; }
  });
})();
