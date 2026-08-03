#!/usr/bin/env python3
from pathlib import Path
import re, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'src').resolve()

manifest='''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <uses-feature android:name="android.hardware.location" android:required="false" />
    <uses-feature android:name="android.hardware.location.gps" android:required="false" />

    <application
        android:allowBackup="false"
        android:fullBackupContent="false"
        android:usesCleartextTraffic="false"
        android:theme="@style/AppTheme"
        android:label="@string/app_name"
        android:icon="@drawable/ic_launcher"
        android:roundIcon="@drawable/ic_launcher"
        android:supportsRtl="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:screenOrientation="unspecified">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service
            android:name=".GeoUpdateJobService"
            android:permission="android.permission.BIND_JOB_SERVICE"
            android:exported="false" />
    </application>
</manifest>
'''
(root/'app/src/main/AndroidManifest.xml').write_text(manifest)

p=root/'app/src/main/java/jp/gumi/geoguard/AppPrefs.java'
s=p.read_text()
s=s.replace('    private static final String BOOT_NAME = "geoguard_boot";\n','')
s=re.sub(r'\n    private static SharedPreferences bootPrefs\(Context c\) \{.*?\n    \}', '', s, flags=re.S)
s=re.sub(r'    public static boolean isMonitoringEnabled\(Context c\) \{.*?\n    \}', '    public static boolean isMonitoringEnabled(Context c) {\n        return prefs(c).getBoolean("monitoring_enabled", false);\n    }', s, flags=re.S)
s=re.sub(r'    public static void setMonitoringEnabled\(Context c, boolean enabled\) \{.*?\n    \}', '    public static void setMonitoringEnabled(Context c, boolean enabled) {\n        prefs(c).edit().putBoolean("monitoring_enabled", enabled).apply();\n    }', s, flags=re.S)
p.write_text(s)

p=root/'app/src/main/assets/index.html'
s=p.read_text()
s=s.replace('*{box-sizing:border-box}body{margin:0;', '*{box-sizing:border-box}html,body{max-width:100%;overflow-x:hidden;-webkit-text-size-adjust:100%}body{margin:0;')
old='<section id="settings" class="page"><div class="grid"><div class="card full"><h2>常時監視</h2><div class="setting"><div><b>前景サービス監視</b><div class="small muted">位置を30秒・25m目安で更新し、重要APIを約3分ごとに確認</div></div><button class="toggle" id="monitorToggle"><i></i></button></div><div class="setting"><div><b>全国の公式更新も通知</b><div class="small muted">OFFでは現在地の都道府県・市区町村に一致する更新を優先</div></div><button class="toggle" id="nationwideToggle"><i></i></button></div><div class="setting"><div><b>位置権限</b><div class="small muted" id="permissionState">確認中</div></div><button class="secondary" id="permissionSettings">設定</button></div><div class="setting"><div><b>バックグラウンド位置</b><div class="small muted">「常に許可」を要求します</div></div><button class="secondary" id="backgroundBtn">許可</button></div><div class="setting"><div><b>電池最適化を除外</b><div class="small muted">HyperOSによる長時間停止を減らすための任意設定</div></div><button class="secondary" id="batteryBtn">設定</button></div></div>'
new='<section id="settings" class="page"><div class="grid"><div class="card full"><h2>更新・位置</h2><div class="setting"><div><b>15分以上の定期更新</b><div class="small muted">最後に保存した地点だけを使います。バックグラウンドでGPSを再取得しません。</div></div><button class="toggle" id="monitorToggle"><i></i></button></div><div class="setting"><div><b>全国の公式更新も通知</b><div class="small muted">OFFでは保存済みの都道府県・市区町村名に一致する更新を優先</div></div><button class="toggle" id="nationwideToggle"><i></i></button></div><div class="setting"><div><b>現在地</b><div class="small muted" id="permissionState">確認中</div></div><div class="row"><button class="secondary" id="currentLocationBtn">再取得</button><button class="secondary" id="permissionSettings">設定</button></div></div></div>'
if old not in s: raise SystemExit('settings block not found')
s=s.replace(old,new)
s=s.replace("$('#permissionState').textContent=`精密:${p.fine?'許可':'未許可'} / 常時:${p.background?'許可':'未許可'} / 通知:${p.notifications?'許可':'未許可'}`;", "$('#permissionState').textContent=`精密:${p.fine?'許可':'未許可'} / 概略:${p.coarse?'許可':'未許可'} / 通知:${p.notifications?'許可':'未許可'}`;")
s=s.replace("$('#mainStatus').textContent=s.monitoring?'地域監視を継続中':'必要時のみ更新';", "$('#mainStatus').textContent=s.monitoring?'定期更新を有効化':'必要時のみ更新';")
s=s.replace("$('#backgroundBtn').onclick=()=>native()?.requestBackgroundLocation();$('#batteryBtn').onclick=()=>native()?.requestIgnoreBatteryOptimizations();", "$('#currentLocationBtn').onclick=()=>native()?.requestCurrentLocation();")
s=s.replace("$('#gpsBtn').onclick=()=>{native()?.clearManualLocation();setTimeout(loadNativeState,300)};", "$('#gpsBtn').onclick=()=>{native()?.clearManualLocation();native()?.requestCurrentLocation();setTimeout(loadNativeState,500)};")
p.write_text(s)

p=root/'app/build.gradle'
s=p.read_text().replace('versionCode 100','versionCode 101').replace("versionName '1.0.0'","versionName '1.0.1'")
p.write_text(s)

p=root/'README.md'
s=p.read_text().replace('- 常時位置監視、前景サービス、端末再起動後の復帰','- 単発の現在地取得、手動地点、15分以上のOS定期更新')
s=s.replace('- 最新位置のみ保存し、移動履歴は作成しない','- バックグラウンドGPSを使わず、最新位置のみ保存し、移動履歴は作成しない')
p.write_text(s)

p=root/'docs/ARCHITECTURE.md'
s=p.read_text().replace('- `MonitorService`: 30秒/25mの位置更新、3分周期の公式フィード・天気・地震補助監視\n- `BootReceiver`: BOOT_COMPLETED、更新、watchdog、task removalから復帰','- `GeoUpdateJobService`: 15分以上のOS定期処理で、最後に保存した地点を使い公式フィード・天気・地震補助情報を更新')
s=re.sub(r'## 常駐\n.*?\n## 位置','## バックグラウンド更新\n\nOS標準JobSchedulerの最短15分周期を使用する。Doze等で実行時刻は前後する。バックグラウンドではGPSを取得せず、最後に保存した地点だけを使う。\n\n## 位置',s,flags=re.S)
p.write_text(s)

p=root/'docs/PRIVACY.md'
s=p.read_text().replace('- 設定から手動地点を使用可能','- 設定から手動地点を使用可能\n- `ACCESS_BACKGROUND_LOCATION`は要求せず、バックグラウンドGPS取得を行わない')
p.write_text(s)

p=root/'scripts/static_audit.py'
s=p.read_text()
s=s.replace(" 'location': 'ACCESS_BACKGROUND_LOCATION' in manifest,\n 'boot': 'RECEIVE_BOOT_COMPLETED' in manifest and 'BOOT_COMPLETED' in manifest,\n 'foreground': 'FOREGROUND_SERVICE' in manifest and 'MonitorService' in manifest,", " 'foreground_location': 'ACCESS_FINE_LOCATION' in manifest and 'ACCESS_COARSE_LOCATION' in manifest,\n 'no_background_location': 'ACCESS_BACKGROUND_LOCATION' not in manifest,\n 'no_foreground_service': 'FOREGROUND_SERVICE' not in manifest and 'MonitorService' not in manifest,\n 'no_boot_autostart': 'RECEIVE_BOOT_COMPLETED' not in manifest and 'BootReceiver' not in manifest,\n 'periodic_job': 'GeoUpdateJobService' in manifest,")
p.write_text(s)
