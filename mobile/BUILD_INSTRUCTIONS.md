# Aadwik Android build

1. Install Flutter and Android Studio/Android SDK.
2. From this `mobile` directory run:

```bash
flutter create . --project-name aadwik --org com.aadwik.ai
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
```

For a real phone, start the backend on a reachable server and use a secure endpoint:

```bash
flutter run --dart-define=AADWIK_API_BASE_URL=https://api.example.com
```

For an emulator, the default `http://10.0.2.2:8000` is used.

For a release APK:

```bash
flutter build apk --release
```

Do not put AI provider API keys in the mobile app.
