# GeoGuard JP build workspace

Android 8+ / POCO F7向けの地域統合気象・地学・防災情報アプリです。

- package: `jp.gumi.geoguard`
- minSdk: 26
- targetSdk: 28
- compatibility release: APK Signature Scheme v1 only
- always-on foreground monitoring, boot restore, and location monitoring are user-controlled in-app

This repository is used only for the GeoGuard JP source and reproducible build workflow.

## Validation scope

The CI workflow performs an actual Android 16 / API 36 install and cold start, verifies the system `Displayed` log, checks process survival after five seconds and rejects app fatal exceptions. It then performs an Android 10 / API 29 cold start and validates the rendered UI using the accessibility hierarchy plus screenshot pixel analysis. APK v1 signature, alignment and ZIP integrity are also checked.
