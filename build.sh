#!/usr/bin/env bash
# Compila EUREKA.apk a partir de web/eureka.html
# Requisitos (Ubuntu): apt-get install -y android-sdk-platform-23 android-sdk-build-tools apksigner zipalign default-jdk python3 zip
set -euo pipefail
cd "$(dirname "$0")"

SDK="${ANDROID_SDK:-/usr/lib/android-sdk}"
BT="$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)"
JAR="$SDK/platforms/android-23/android.jar"
source version.properties
KS="${EUREKA_KEYSTORE:-keystore/eureka.jks}"
KS_PASS="${EUREKA_KEYSTORE_PASS:-eureka2026}"

OUT=build
rm -rf "$OUT"; mkdir -p "$OUT"/{assets,gen,classes}

echo "==> Preparando HTML"
cp -r app/src/main/assets/. "$OUT/assets/"
python3 tools/prepare_html.py web/eureka.html "$OUT/assets/index.html"

echo "==> Recursos"
"$BT/aapt2" compile --dir app/src/main/res -o "$OUT/res.zip"
"$BT/aapt2" link -I "$JAR" \
  --manifest app/src/main/AndroidManifest.xml \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" \
  --java "$OUT/gen" -A "$OUT/assets" \
  -o "$OUT/unsigned.apk" "$OUT/res.zip"

echo "==> Java"
javac -nowarn -source 8 -target 8 -bootclasspath "$JAR" -d "$OUT/classes" \
  $(find app/src/main/java "$OUT/gen" -name '*.java') -Xlint:-options
"$BT/dx" --dex --min-sdk-version=24 --output="$OUT/classes.dex" "$OUT/classes"
(cd "$OUT" && zip -q -j unsigned.apk classes.dex)

echo "==> Firmando"
"$BT/zipalign" -p -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
mkdir -p dist
APK="dist/EUREKA-v${VERSION_NAME}.apk"
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$KS_PASS" --ks-key-alias eureka --out "$APK" "$OUT/aligned.apk"
"$BT/apksigner" verify "$APK"
echo "==> Listo: $APK ($(du -h "$APK" | cut -f1))"
