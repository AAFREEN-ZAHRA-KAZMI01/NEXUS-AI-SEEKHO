import 'package:dio/dio.dart';
import '../constants/api_constants.dart';

class ConnectivityChecker {
  static final _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));

  static Future<bool> isBackendReachable() async {
    try {
      final r = await _dio.get('${ApiConstants.baseUrl}/');
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static String getConnectionGuide() => '''
Backend not reachable at ${ApiConstants.baseUrl}

Fix:
1. docker compose up -d
2. curl http://localhost:8000/
3. Update baseUrl in api_constants.dart:
   Android Emulator → http://10.0.2.2:8000
   iOS Simulator    → http://localhost:8000
   Physical Device  → http://YOUR_WIFI_IP:8000
''';
}
