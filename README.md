# EUREKA (Android)

EUREKA es la app. PalletFlow corre detrás como "motor" (escaneo con IA, resumen del día,
almacén, panel de ingreso, estadísticas, kilos, KPI, hoja de peso por foto), con la piel de EUREKA.

- `web/eureka.html` → la app (pantalla principal, barra inferior, Ajustes, Máster).
- `web/palletflow.html` → motor PalletFlow ya adaptado (se genera, no editar a mano).
- `web/palletflow-original.html` → PalletFlow original de José (fuente del motor).

## Cómo actualizar
1. Cambios de EUREKA: edita `web/eureka.html`.
2. Nueva versión de PalletFlow: reemplaza `web/palletflow-original.html` y corre
   `python3 tools/build_palletflow.py web/palletflow-original.html tools/logo-eureka.b64`.
3. Sube `VERSION_CODE` (+1) y `VERSION_NAME` en `version.properties`.
4. `./build.sh` → el APK queda en `dist/`.

El APK siempre se firma con `keystore/eureka.jks`: las nuevas versiones se instalan encima sin
perder datos. **No borres ni cambies esa llave.**
