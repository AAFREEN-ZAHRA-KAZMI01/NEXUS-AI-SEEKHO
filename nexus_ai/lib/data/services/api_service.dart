import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../core/constants/api_constants.dart';
import '../models/analysis_request.dart';
import '../models/analysis_response.dart';
import '../models/session_trace.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  late final Dio _dio;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: Duration(milliseconds: ApiConstants.connectTimeout),
      receiveTimeout: Duration(milliseconds: ApiConstants.receiveTimeout),
      headers: {'Content-Type': 'application/json'},
    ));
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(
        requestBody: true, responseBody: false,
        logPrint: (o) => debugPrint('[API] ${o.toString()}'),
      ));
    }
  }

  static final Options _analysisOptions = Options(
    receiveTimeout: const Duration(milliseconds: ApiConstants.analysisReceiveTimeout),
  );

  Future<AnalysisResponse> analyseText(TextAnalysisRequest req) async {
    return _safeCall(() async {
      final r = await _dio.post(
        ApiConstants.analyseText,
        data: req.toJson(),
        options: _analysisOptions,
      );
      return AnalysisResponse.fromJson(r.data);
    });
  }

  Future<AnalysisResponse> analyseUrl(UrlAnalysisRequest req) async {
    return _safeCall(() async {
      final r = await _dio.post(
        ApiConstants.analyseUrl,
        data: req.toJson(),
        options: _analysisOptions,
      );
      return AnalysisResponse.fromJson(r.data);
    });
  }

  Future<AnalysisResponse> analyseFile({
    required List<int> fileBytes,
    required String fileName,
    required String inputType,
    String? domain,
    String? sessionId,
  }) async {
    return _safeCall(() async {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(fileBytes, filename: fileName),
        'input_type': inputType,
        if (domain != null) 'domain': domain,
        if (sessionId != null) 'session_id': sessionId,
      });
      final r = await _dio.post(
        ApiConstants.analyseFile,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
          receiveTimeout: const Duration(milliseconds: ApiConstants.analysisReceiveTimeout),
        ),
      );
      return AnalysisResponse.fromJson(r.data);
    });
  }

  Future<SessionTrace> getSessionTrace(String sessionId) async {
    return _safeCall(() async {
      final r = await _dio.get(ApiConstants.sessionTrace(sessionId));
      return SessionTrace.fromJson(r.data);
    });
  }

  Future<Map<String, dynamic>> getSessionStatus(String sessionId) async {
    return _safeCall(() async {
      final r = await _dio.get(ApiConstants.sessionStatus(sessionId));
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> getDomainState(String domain) async {
    return _safeCall(() async {
      final r = await _dio.get(ApiConstants.domainState(domain));
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> resetState() async {
    return _safeCall(() async {
      final r = await _dio.post(ApiConstants.resetState);
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<List<dynamic>> getSessionsHistory() async {
    return _safeCall(() async {
      final r = await _dio.get(ApiConstants.sessionsHistory);
      return List<dynamic>.from(r.data);
    });
  }

  Future<List<Map<String, dynamic>>> getRecentSessions() async {
    return _safeCall(() async {
      final r = await _dio.get(ApiConstants.recentSessions);
      final List sessionsList = r.data['sessions'] ?? [];
      return sessionsList.map((e) => Map<String, dynamic>.from(e)).toList();
    });
  }

  Future<Map<String, dynamic>> emailReport(String sessionId, {String? recipientEmail}) async {
    return _safeCall(() async {
      final r = await _dio.post(
        '/api/session/$sessionId/email-report',
        data: {'recipient_email': recipientEmail},
      );
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<T> _safeCall<T>(Future<T> Function() call) async {
    try {
      return await call();
    } on DioException catch (e) {
      switch (e.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.connectionError:
          throw Exception('Cannot reach backend — is Docker running?\n${ApiConstants.baseUrl}');
        case DioExceptionType.receiveTimeout:
          throw Exception('Backend timeout — pipeline took too long');
        default:
          final code   = e.response?.statusCode ?? 0;
          final detail = e.response?.data?['detail'] ?? e.message ?? 'Unknown error';
          throw Exception('Backend error $code: $detail');
      }
    } catch (e) {
      throw Exception('Unexpected error: $e');
    }
  }
}
