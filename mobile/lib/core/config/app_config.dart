class AppConfig {
  // Production: pass a secure HTTPS API endpoint with --dart-define=AADWIK_API_BASE_URL=https://api.example.com
  // Android emulator default: http://10.0.2.2:8000
  static const String baseUrl = String.fromEnvironment(
    'AADWIK_API_BASE_URL',
    defaultValue: 'http://192.168.1.4:8000'
  );
}
