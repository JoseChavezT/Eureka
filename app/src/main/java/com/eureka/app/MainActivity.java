package com.eureka.app;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.media.MediaScannerConnection;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.webkit.DownloadListener;
import android.webkit.JavascriptInterface;
import android.webkit.MimeTypeMap;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * EUREKA: contenedor nativo de la app web.
 * La app se sirve desde assets/ bajo un origen https propio (así localStorage,
 * IndexedDB y el portapapeles funcionan igual que en el navegador).
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + HOST + "/index.html";
    private static final int REQ_FILE = 1001;
    private static final int REQ_PERM = 1002;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private Uri cameraUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.BLACK);
        getWindow().setNavigationBarColor(Color.BLACK);

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#050506"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setTextZoom(100);
        s.setSupportMultipleWindows(false);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);

        web.addJavascriptInterface(new Bridge(), "EurekaAndroid");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (HOST.equals(u.getHost())) return serveAsset(u.getPath());
                return null;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                Uri u = Uri.parse(url);
                if (HOST.equals(u.getHost())) return false;
                openExternal(u);
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                return showFileChooser(callback, params);
            }
        });

        web.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String ua, String cd, String mime, long len) {
                if (url != null && (url.startsWith("http://") || url.startsWith("https://"))) {
                    openExternal(Uri.parse(url));
                }
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(START_URL);
        }
    }

    // ---------- Assets ----------

    private static final Map<String, String> MIME = new HashMap<String, String>();
    static {
        MIME.put("html", "text/html");
        MIME.put("js", "application/javascript");
        MIME.put("mjs", "application/javascript");
        MIME.put("css", "text/css");
        MIME.put("json", "application/json");
        MIME.put("woff2", "font/woff2");
        MIME.put("woff", "font/woff");
        MIME.put("ttf", "font/ttf");
        MIME.put("png", "image/png");
        MIME.put("jpg", "image/jpeg");
        MIME.put("jpeg", "image/jpeg");
        MIME.put("svg", "image/svg+xml");
        MIME.put("webp", "image/webp");
        MIME.put("ico", "image/x-icon");
        MIME.put("wasm", "application/wasm");
    }

    private WebResourceResponse serveAsset(String path) {
        if (path == null || path.equals("") || path.equals("/")) path = "/index.html";
        String p = path.startsWith("/") ? path.substring(1) : path;
        String ext = p.contains(".") ? p.substring(p.lastIndexOf('.') + 1).toLowerCase() : "";
        String mime = MIME.containsKey(ext) ? MIME.get(ext) : "application/octet-stream";
        Map<String, String> headers = new HashMap<String, String>();
        headers.put("Access-Control-Allow-Origin", "*");
        headers.put("Cache-Control", "no-cache");
        try {
            InputStream in = getAssets().open(p);
            return new WebResourceResponse(mime, "UTF-8", 200, "OK", headers, in);
        } catch (Exception e) {
            return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", headers,
                    new ByteArrayInputStream(new byte[0]));
        }
    }

    private void openExternal(Uri u) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, u);
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "No hay una app para abrir este enlace", Toast.LENGTH_SHORT).show();
        }
    }

    // ---------- Selección de archivos / cámara ----------

    private boolean showFileChooser(ValueCallback<Uri[]> callback, WebChromeClient.FileChooserParams params) {
        if (fileCallback != null) fileCallback.onReceiveValue(null);
        fileCallback = callback;
        cameraUri = null;

        String[] accept = params.getAcceptTypes();
        boolean images = false, pdf = false, other = false;
        if (accept != null) {
            for (String a0 : accept) {
                for (String a : a0.split(",")) {
                    a = a.trim().toLowerCase();
                    if (a.length() == 0) continue;
                    if (a.startsWith("image/")) images = true;
                    else if (a.equals("application/pdf") || a.equals(".pdf")) pdf = true;
                    else other = true;
                }
            }
        }

        Intent get = new Intent(Intent.ACTION_GET_CONTENT);
        get.addCategory(Intent.CATEGORY_OPENABLE);
        if (images && !pdf && !other) get.setType("image/*");
        else if (pdf && !images && !other) get.setType("application/pdf");
        else get.setType("*/*");
        if (params.getMode() == WebChromeClient.FileChooserParams.MODE_OPEN_MULTIPLE) {
            get.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        }

        Intent camera = null;
        if (images) camera = buildCameraIntent();

        try {
            if (camera != null && params.isCaptureEnabled()) {
                startActivityForResult(camera, REQ_FILE);
            } else {
                Intent chooser = Intent.createChooser(get, "Seleccionar archivo");
                if (camera != null) chooser.putExtra(Intent.EXTRA_INITIAL_INTENTS, new Intent[]{camera});
                startActivityForResult(chooser, REQ_FILE);
            }
        } catch (ActivityNotFoundException e) {
            fileCallback.onReceiveValue(null);
            fileCallback = null;
            return false;
        }
        return true;
    }

    private Intent buildCameraIntent() {
        try {
            Intent cam = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            if (cam.resolveActivity(getPackageManager()) == null) return null;
            ContentValues cv = new ContentValues();
            cv.put(MediaStore.Images.Media.DISPLAY_NAME, "eureka_" + System.currentTimeMillis() + ".jpg");
            cv.put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg");
            if (Build.VERSION.SDK_INT >= 29) cv.put("relative_path", "Pictures/EUREKA");
            cameraUri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, cv);
            if (cameraUri == null) return null;
            cam.putExtra(MediaStore.EXTRA_OUTPUT, cameraUri);
            cam.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
            return cam;
        } catch (Exception e) {
            cameraUri = null;
            return null;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != REQ_FILE) {
            super.onActivityResult(requestCode, resultCode, data);
            return;
        }
        Uri[] result = null;
        boolean usedCamera = false;
        if (resultCode == RESULT_OK) {
            List<Uri> list = new ArrayList<Uri>();
            if (data != null && data.getClipData() != null) {
                for (int i = 0; i < data.getClipData().getItemCount(); i++) {
                    list.add(data.getClipData().getItemAt(i).getUri());
                }
            } else if (data != null && data.getData() != null) {
                list.add(data.getData());
            }
            if (list.isEmpty() && cameraUri != null) {
                list.add(cameraUri);
                usedCamera = true;
            }
            if (!list.isEmpty()) result = list.toArray(new Uri[0]);
        }
        if (cameraUri != null && !usedCamera) {
            try { getContentResolver().delete(cameraUri, null, null); } catch (Exception ignored) {}
        }
        cameraUri = null;
        if (fileCallback != null) fileCallback.onReceiveValue(result);
        fileCallback = null;
    }

    // ---------- Descargas (PDF, Excel, JSON...) ----------

    private class Bridge {
        @JavascriptInterface
        public String saveFile(String name, String mime, String base64) {
            try {
                byte[] bytes = Base64.decode(base64, Base64.DEFAULT);
                if (name == null || name.trim().length() == 0) name = "archivo";
                name = name.replaceAll("[\\\\/:*?\"<>|]", "_");
                if (mime == null || mime.length() == 0) {
                    String ext = name.contains(".") ? name.substring(name.lastIndexOf('.') + 1).toLowerCase() : "";
                    mime = MimeTypeMap.getSingleton().getMimeTypeFromExtension(ext);
                    if (mime == null) mime = "application/octet-stream";
                }
                Uri saved = writeToDownloads(name, mime, bytes);
                if (saved == null) return "Concede el permiso de almacenamiento y vuelve a intentarlo";
                final Uri fUri = saved;
                final String fName = name, fMime = mime;
                runOnUiThread(new Runnable() {
                    public void run() { onSaved(fName, fMime, fUri); }
                });
                return "ok";
            } catch (Exception e) {
                return "Error: " + e.getMessage();
            }
        }

        @JavascriptInterface
        public String version() {
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "";
            }
        }
    }

    private Uri writeToDownloads(String name, String mime, byte[] bytes) throws Exception {
        if (Build.VERSION.SDK_INT >= 29) {
            ContentValues cv = new ContentValues();
            cv.put("_display_name", name);
            cv.put("mime_type", mime);
            cv.put("relative_path", Environment.DIRECTORY_DOWNLOADS + "/EUREKA");
            cv.put("is_pending", 1);
            Uri col = Uri.parse("content://media/external/downloads");
            Uri u = getContentResolver().insert(col, cv);
            if (u == null) throw new Exception("No se pudo crear el archivo");
            OutputStream out = getContentResolver().openOutputStream(u);
            out.write(bytes);
            out.close();
            ContentValues done = new ContentValues();
            done.put("is_pending", 0);
            getContentResolver().update(u, done, null, null);
            return u;
        }
        if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            runOnUiThread(new Runnable() {
                public void run() {
                    requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_PERM);
                }
            });
            return null;
        }
        File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "EUREKA");
        dir.mkdirs();
        File f = new File(dir, name);
        FileOutputStream out = new FileOutputStream(f);
        out.write(bytes);
        out.close();
        MediaScannerConnection.scanFile(this, new String[]{f.getAbsolutePath()}, new String[]{mime}, null);
        return Uri.fromFile(f);
    }

    private void onSaved(final String name, final String mime, final Uri uri) {
        if (isFinishing()) return;
        boolean canOpen = !"file".equals(uri.getScheme());
        AlertDialog.Builder b = new AlertDialog.Builder(this)
                .setTitle("Archivo guardado")
                .setMessage(name + "\n\nEn: Descargas/EUREKA")
                .setNegativeButton("OK", null);
        if (canOpen) {
            b.setPositiveButton("Abrir", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface d, int w) {
                    try {
                        Intent i = new Intent(Intent.ACTION_VIEW);
                        i.setDataAndType(uri, mime);
                        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivity(Intent.createChooser(i, "Abrir con"));
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "No hay una app para abrir este archivo", Toast.LENGTH_SHORT).show();
                    }
                }
            });
            b.setNeutralButton("Compartir", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface d, int w) {
                    try {
                        Intent i = new Intent(Intent.ACTION_SEND);
                        i.setType(mime);
                        i.putExtra(Intent.EXTRA_STREAM, uri);
                        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivity(Intent.createChooser(i, "Compartir"));
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "No se pudo compartir", Toast.LENGTH_SHORT).show();
                    }
                }
            });
        }
        b.show();
    }

    // ---------- Ciclo de vida ----------

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }
}
