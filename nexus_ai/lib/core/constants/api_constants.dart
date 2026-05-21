import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiConstants {
  // To specify a custom backend IP for a physical device, run:
  // flutter run --dart-define=BACKEND_IP=192.168.x.x

  static String get baseUrl {
    // Production URL injected at build time: --dart-define=BACKEND_URL=https://...
    const String backendUrl = String.fromEnvironment('BACKEND_URL', defaultValue: '');
    if (backendUrl.isNotEmpty) return backendUrl;

    const String backendIp = String.fromEnvironment('BACKEND_IP', defaultValue: '');
    if (backendIp.isNotEmpty) {
      return 'http://$backendIp:8000';
    }

    if (kIsWeb) {
      return 'http://localhost:8000';
    }

    if (kDebugMode) {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000';
      } else if (Platform.isIOS) {
        return 'http://localhost:8000';
      }
    }

    return 'http://localhost:8000';
  }

  static const String analyseText = '/api/analyse/text';
  static const String analyseUrl  = '/api/analyse/url';
  static const String analyseFile = '/api/analyse/file';

  static const String sessionsHistory     = '/api/sessions';
  static const String recentSessions      = '/api/sessions';
  static String sessionTrace(String id)    => '/api/session/$id/trace';
  static String sessionStatus(String id)   => '/api/session/$id/status';
  static String domainState(String domain) => '/api/state/$domain';
  static const String resetState           = '/api/state/reset';

  static const int connectTimeout        = 30000;
  static const int receiveTimeout        = 120000;
  static const int analysisReceiveTimeout = 300000; // 5 min for multi-stage AI pipeline
}
