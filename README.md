# Eureka Flow (Android)

App Android que combina **PalletFlow** (base: todos sus apartados y gráficos) y **EUREKA**
(apartado "Recepciones"), con un tono visual propio ("Eureka Flow").

- `web/app.html` → pantalla principal (PalletFlow con el estilo Flow + apartado Recepciones).
- `web/eureka.html` → módulo Recepciones (EUREKA), se abre dentro de la app.

## Cómo actualizar la app
1. Edita `web/app.html` (PalletFlow / Eureka Flow) o `web/eureka.html` (Recepciones).
2. Sube `VERSION_CODE` (+1) y `VERSION_NAME` en `version.properties`.
3. Ejecuta `./build.sh` → el APK queda en `dist/`.
   (O haz push: GitHub Actions lo compila y lo deja en *Actions → Compilar APK → Artifacts*.)

El APK siempre se firma con `keystore/eureka.jks`, así que las nuevas versiones se instalan
encima de la anterior sin perder los datos guardados. **No borres ni cambies esa llave.**

## Qué hace el contenedor nativo
- Sirve la app desde `assets/` (funciona sin internet: pdf.js, xlsx, jsPDF, three.js y fuentes van incluidos).
- Selector de archivos (PDF, Excel, JSON, imágenes) y cámara para fotos.
- Los PDF/Excel/JSON que la app descarga se guardan en **Descargas/EUREKA**, con opción de abrir o compartir.
- Enlaces externos (WhatsApp, etc.) se abren en su app.
