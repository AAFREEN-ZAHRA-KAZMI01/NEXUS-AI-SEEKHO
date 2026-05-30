import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/constants/app_constants.dart';
import '../../core/constants/api_constants.dart';
import '../models/analysis_request.dart';
import '../models/analysis_response.dart';
import '../models/session_trace.dart';
import '../models/watchlist_alert.dart';
import '../models/action_outcome.dart';

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
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final apiKey = prefs.getString(AppConstants.apiKeyPrefKey);
        if (apiKey != null && apiKey.isNotEmpty) {
          options.headers['X-API-Key'] = apiKey;
        }
        return handler.next(options);
      },
    ));
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
      return _pollForResponse(r.data['session_id']);
    });
  }

  Future<AnalysisResponse> analyseUrl(UrlAnalysisRequest req) async {
    return _safeCall(() async {
      final r = await _dio.post(
        ApiConstants.analyseUrl,
        data: req.toJson(),
        options: _analysisOptions,
      );
      return _pollForResponse(r.data['session_id']);
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
      return _pollForResponse(r.data['session_id']);
    });
  }

  Future<AnalysisResponse> analyseMulti({
    required List<List<int>> fileBytesList,
    required List<String> fileNames,
    String? context,
    String? domain,
    String? sessionId,
  }) async {
    return _safeCall(() async {
      final List<MultipartFile> files = [];
      for (int i = 0; i < fileBytesList.length; i++) {
        files.add(MultipartFile.fromBytes(fileBytesList[i], filename: fileNames[i]));
      }

      final formData = FormData.fromMap({
        'files': files,
        if (context != null) 'context': context,
        if (domain != null) 'domain': domain,
        if (sessionId != null) 'session_id': sessionId,
      });

      final r = await _dio.post(
        '/api/analyse/multi', // Note: Needs to be added to ApiConstants ideally, but hardcoded here is fine based on python router
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
          receiveTimeout: const Duration(milliseconds: ApiConstants.analysisReceiveTimeout),
        ),
      );
      return _pollForResponse(r.data['session_id']);
    });
  }

  Future<AnalysisResponse> _pollForResponse(String sessionId) async {
    final endTime = DateTime.now().add(const Duration(minutes: 3));
    while (DateTime.now().isBefore(endTime)) {
      final statusResp = await getSessionStatus(sessionId);
      final status = statusResp['status'];
      if (status == 'complete') {
        final trace = await getSessionTrace(sessionId);
        return _assembleResponseFromTrace(trace, sessionId);
      } else if (status == 'failed') {
        throw Exception('Analysis failed on server.');
      }
      await Future.delayed(const Duration(seconds: 3));
    }
    throw TimeoutException('Analysis timed out after 3 minutes');
  }

  AnalysisResponse _assembleResponseFromTrace(SessionTrace trace, String sessionId) {
      final masterBriefArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'master_brief',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final execLogArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'exec_log',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final taskPlanArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'task_plan',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final signalsArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'signals',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final impactArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'impact',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final actionsArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'actions',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );
      final contextArt = trace.artifacts.firstWhere(
        (a) => a.artifactType == 'context',
        orElse: () => const AgentArtifactItem(id: '', sessionId: '', agentName: '', artifactType: '', content: {}, createdAt: ''),
      );

      final brief = masterBriefArt.content;
      final exec = execLogArt.content;

      List<KpiAffected> kpis = [];
      if (brief['kpis_affected'] is List) {
        kpis = (brief['kpis_affected'] as List).map((e) => KpiAffected.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      TopAction topAction = const TopAction(
        rank: 1, actionType: 'unknown', description: '',
        apiEndpoint: '', apiPayload: {}, quantifiedDelta: '',
        feasibilityScore: 5, impactScore: 5, compositeScore: 5,
        justification: '', successMetric: '', timeToExecute: '',
      );
      if (brief['top_action'] is Map) {
        topAction = TopAction.fromJson(Map<String, dynamic>.from(brief['top_action']));
      }

      List<TopAction> alts = [];
      if (brief['alternative_actions'] is List) {
        alts = (brief['alternative_actions'] as List).map((e) => TopAction.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      List<NotificationSent> notifications = [];
      if (exec['notifications_sent'] is List) {
        notifications = (exec['notifications_sent'] as List).map((e) => NotificationSent.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      return AnalysisResponse(
        sessionId: sessionId,
        domain: trace.session['domain'] ?? brief['domain'] ?? 'business',
        status: trace.session['status'] ?? 'complete',
        durationSeconds: trace.pipelineDurationSeconds ?? 0.0,
        insight: brief['insight'] ?? '',
        severity: brief['severity'] ?? 5,
        severityLabel: brief['severity_label'] ?? 'Medium',
        impactSummary: Map<String, dynamic>.from(brief['impact_summary'] ?? {}),
        kpisAffected: kpis,
        topAction: topAction,
        alternativeActions: alts,
        beforeState: Map<String, dynamic>.from(exec['state_before'] ?? {}),
        afterState: Map<String, dynamic>.from(exec['state_after'] ?? {}),
        delta: Map<String, dynamic>.from(exec['delta'] ?? {}),
        notificationsSent: notifications,
        executionStatus: exec['execution_status'] ?? 'complete',
        corroboration: brief['corroboration'],
        context: brief['context'],
        traceUrl: '/api/session/$sessionId/trace',
        artifacts: AllArtifacts(
          taskPlan: taskPlanArt.content,
          signals: signalsArt.content,
          impact: impactArt.content,
          actions: actionsArt.content,
          context: contextArt.content,
          masterBrief: brief,
          execLog: exec,
        ),
      );
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

  Future<Map<String, dynamic>> getAllDomainStates() async {
    return _safeCall(() async {
      final r = await _dio.get('/api/state/all');
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> resetState() async {
    return _safeCall(() async {
      final r = await _dio.post(ApiConstants.resetState);
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> registerOrg(String name) async {
    return _safeCall(() async {
      final r = await _dio.post('/api/org/register', data: {'name': name});
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> getOrgMe() async {
    return _safeCall(() async {
      final r = await _dio.get('/api/org/me');
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

  Future<Uint8List> exportSessionPdf(String sessionId) async {
    return _safeCall(() async {
      final r = await _dio.get(
        '/api/session/$sessionId/export/pdf',
        options: Options(responseType: ResponseType.bytes),
      );
      return Uint8List.fromList(r.data as List<int>);
    });
  }

  /// Connects to the SSE stream endpoint and yields status strings.
  ///
  /// Each emitted value is the ``status`` field from a server event, e.g.:
  /// ``"pending"`` → ``"ingesting"`` → ``"analysing"`` → ``"complete"``.
  ///
  /// The stream closes automatically once the server sends a terminal event
  /// (``"complete"`` or ``"failed"``).
  ///
  /// Example usage:
  /// ```dart
  /// apiService.streamSessionProgress(sessionId).listen(
  ///   (status) => setState(() => _currentStatus = status),
  ///   onDone: () => setState(() => _done = true),
  ///   onError: (e) => debugPrint('SSE error: $e'),
  /// );
  /// ```
  Stream<String> streamSessionProgress(String sessionId) async* {
    const terminalStatuses = {'complete', 'failed', 'error'};

    // Use a dedicated Dio instance with no receive-timeout so the stream
    // stays open for the full duration of the pipeline.
    final streamDio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(milliseconds: ApiConstants.connectTimeout),
      receiveTimeout: Duration.zero, // unlimited — SSE never "times out"
      headers: {'Accept': 'text/event-stream'},
    ));
    
    streamDio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final apiKey = prefs.getString(AppConstants.apiKeyPrefKey);
        if (apiKey != null && apiKey.isNotEmpty) {
          options.headers['X-API-Key'] = apiKey;
        }
        return handler.next(options);
      },
    ));

    try {
      final response = await streamDio.get<ResponseBody>(
        ApiConstants.sessionStream(sessionId),
        options: Options(responseType: ResponseType.stream),
      );

      final byteStream = response.data!.stream;

      // Buffer partial lines across chunks (SSE lines end with \n\n)
      final buffer = StringBuffer();

      await for (final chunk in byteStream) {
        buffer.write(String.fromCharCodes(chunk));
        final raw = buffer.toString();

        // Split on double-newline (SSE event boundary) but keep the tail
        // in case we received a partial event.
        final parts = raw.split('\n\n');
        buffer
          ..clear()
          ..write(parts.last); // last part may be incomplete

        for (final part in parts.sublist(0, parts.length - 1)) {
          for (final line in part.split('\n')) {
            final trimmed = line.trim();
            if (!trimmed.startsWith('data:')) continue;

            final jsonStr = trimmed.substring('data:'.length).trim();
            if (jsonStr.isEmpty) continue;

            try {
              final Map<String, dynamic> event =
                  Map<String, dynamic>.from(
                      jsonDecode(jsonStr) as Map);
              final status = event['status'] as String? ?? '';
              if (status.isNotEmpty) {
                yield status;
                if (terminalStatuses.contains(status)) return;
              }
            } catch (_) {
              // Malformed JSON in one frame — skip it
            }
          }
        }
      }
    } on DioException catch (e) {
      // Connection closed by server after terminal event — that is normal.
      if (e.type != DioExceptionType.connectionError &&
          e.type != DioExceptionType.unknown) {
        rethrow;
      }
    } finally {
      streamDio.close();
    }
  }


  Future<WatchlistAlert> createAlert(Map<String, dynamic> alertData) async {
    return _safeCall(() async {
      final r = await _dio.post(
        '/api/alerts',
        data: alertData,
      );
      return WatchlistAlert.fromJson(r.data);
    });
  }

  Future<List<WatchlistAlert>> getAlerts(String userId) async {
    return _safeCall(() async {
      final r = await _dio.get(
        '/api/alerts',
        queryParameters: {'user_id': userId},
      );
      final list = r.data as List;
      return list.map((e) => WatchlistAlert.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<void> deleteAlert(String alertId) async {
    return _safeCall(() async {
      await _dio.delete('/api/alerts/$alertId');
    });
  }

  Future<WatchlistAlert> toggleAlert(String alertId) async {
    return _safeCall(() async {
      final r = await _dio.patch('/api/alerts/$alertId/toggle');
      return WatchlistAlert.fromJson(r.data);
    });
  }

  Future<List<AlertHistoryItem>> getAlertHistory(String userId) async {
    return _safeCall(() async {
      final r = await _dio.get(
        '/api/alerts/history',
        queryParameters: {'user_id': userId},
      );
      final list = r.data as List;
      return list.map((e) => AlertHistoryItem.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  // ── Outcome tracking ──────────────────────────────────────────────────────

  Future<Map<String, dynamic>> confirmAction(
    String sessionId,
    bool confirmed, {
    String? note,
  }) async {
    return _safeCall(() async {
      final r = await _dio.post(
        '/api/session/$sessionId/confirm-action',
        data: {
          'confirmed': confirmed,
          if (note != null) 'note': note,
        },
      );
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<Map<String, dynamic>> recordOutcome(
    String outcomeId,
    String note, {
    double? actualValue,
  }) async {
    return _safeCall(() async {
      final r = await _dio.post(
        '/api/outcomes/$outcomeId/record-result',
        data: {
          'actual_outcome_note': note,
          if (actualValue != null) 'actual_value': actualValue,
        },
      );
      return Map<String, dynamic>.from(r.data);
    });
  }

  Future<List<ActionOutcome>> getOutcomes({String? domain}) async {
    return _safeCall(() async {
      final r = await _dio.get(
        '/api/outcomes',
        queryParameters: {
          if (domain != null) 'domain': domain,
          'limit': 50,
        },
      );
      final list = r.data as List;
      return list
          .map((e) => ActionOutcome.fromJson(e as Map<String, dynamic>))
          .toList();
    });
  }

  Future<OutcomeSummary> getOutcomeSummary() async {
    return _safeCall(() async {
      final r = await _dio.get('/api/outcomes/summary');
      return OutcomeSummary.fromJson(r.data as Map<String, dynamic>);
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
