# Nexus AI — Flutter App

## Quick Start
    cd nexus_ai
    flutter pub get
    flutter run

## Device Setup (update api_constants.dart)

| Device            | URL                        |
|-------------------|----------------------------|
| Android Emulator  | http://10.0.2.2:8000       |
| iOS Simulator     | http://localhost:8000       |
| Physical Device   | http://YOUR_WIFI_IP:8000   |

Find WiFi IP:  Windows: ipconfig / Mac/Linux: ifconfig

## Backend must be running
    docker compose up -d          # from newsops-project root
    curl http://localhost:8000/   # verify

## Build APK for demo
    flutter build apk --release
    flutter install

## Run integration tests
    flutter test integration_test/app_test.dart

## Screens
    /splash   → Onboarding with backend status indicator
    /home     → Dashboard: metrics + recent insights
    /analyze  → Input: text / URL / PDF / DOCX / CSV / Excel
    /progress → Live agent progress with real-time log
    /insight  → Severity, impact, before/after, notifications
    /actions  → Ranked actions with execute/simulate buttons
    /simulate → Animated execution log + before/after state
    /results  → Outcome grid + timeline + export
    /trace    → Full Antigravity agent reasoning trace
