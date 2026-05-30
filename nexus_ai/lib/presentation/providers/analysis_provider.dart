import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';
import '../../data/models/analysis_request.dart';
import '../../data/models/analysis_response.dart';
import '../../data/models/session_trace.dart';
import '../../data/services/api_service.dart';

enum AnalysisStatus { idle, loading, queued, complete, error }

class AnalysisProvider extends ChangeNotifier {
  final _api = ApiService();

  AnalysisStatus status         = AnalysisStatus.idle;
  AnalysisResponse? result;
  String? errorMessage;
  String? currentSessionId;

  // Progress tracking
  int agentProgressStep         = 0;
  List<String> liveLogs         = [];
  Timer? _pollingTimer;

  // Notifications
  List<Map<String, dynamic>> notifications = [];

  void addNotification(String title, String message, {String type = 'info'}) {
    notifications.insert(0, {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'title': title,
      'message': message,
      'timestamp': DateTime.now(),
      'type': type,
      'read': false,
    });
    notifyListeners();
  }

  void markAllNotificationsAsRead() {
    for (var n in notifications) {
      n['read'] = true;
    }
    notifyListeners();
  }

  int get unreadNotificationsCount => notifications.where((n) => !n['read']).length;

  // Input state
  String selectedInputType      = 'text';
  String? selectedDomain;
  String textContent            = '';
  String urlContent             = '';
  
  // Multi-file state
  List<String> selectedFileNames = [];
  List<List<int>> selectedFileBytesList = [];
  List<int> selectedFileSizes = [];

  // ── Setters ────────────────────────────────────────────────────────────

  void setInputType(String t)   { selectedInputType = t; notifyListeners(); }
  void setDomain(String? d)     { selectedDomain    = d; notifyListeners(); }
  void setTextContent(String t) { textContent       = t; notifyListeners(); }
  void setUrlContent(String u)  { urlContent        = u; notifyListeners(); }

  void setFile(String name, List<int> bytes) {
    selectedFileNames = [name];
    selectedFileBytesList = [bytes];
    selectedFileSizes = [bytes.length];
    notifyListeners();
  }

  void addFile(String name, List<int> bytes) {
    if (selectedFileNames.length >= 5) return;
    selectedFileNames.add(name);
    selectedFileBytesList.add(bytes);
    selectedFileSizes.add(bytes.length);
    notifyListeners();
  }

  void removeFile(int index) {
    if (index >= 0 && index < selectedFileNames.length) {
      selectedFileNames.removeAt(index);
      selectedFileBytesList.removeAt(index);
      selectedFileSizes.removeAt(index);
      notifyListeners();
    }
  }

  bool get hasValidInput {
    if (selectedInputType == 'text') return textContent.trim().length >= 20;
    if (selectedInputType == 'url')  return urlContent.trim().isNotEmpty;
    if (selectedInputType == 'multi_document') return selectedFileNames.isNotEmpty;
    return selectedFileNames.isNotEmpty;
  }

  // ── Main pipeline trigger ──────────────────────────────────────────────

  Future<void> runAnalysis() async {
    status            = AnalysisStatus.loading;
    errorMessage      = null;
    agentProgressStep = 0;
    liveLogs          = ['[${_ts()}] Initializing pipeline...'];

    // Generate unique session ID: timestamp + 6-char random hex
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final rng = Random.secure();
    final suffix = List.generate(6, (_) => rng.nextInt(16).toRadixString(16)).join();
    final newSid = '${timestamp}_$suffix';
    currentSessionId = newSid;
    notifyListeners();

    // Start polling *concurrently*!
    _pollProgress(newSid);

    try {
      AnalysisResponse response;

      if (selectedInputType == 'text') {
        response = await _api.analyseText(
          TextAnalysisRequest(content: textContent, domain: selectedDomain, sessionId: newSid));
      } else if (selectedInputType == 'url') {
        response = await _api.analyseUrl(
          UrlAnalysisRequest(url: urlContent, domain: selectedDomain, sessionId: newSid));
      } else if (selectedInputType == 'multi_document' || selectedFileNames.length > 1) {
        response = await _api.analyseMulti(
          fileBytesList: selectedFileBytesList,
          fileNames: selectedFileNames,
          domain: selectedDomain,
          sessionId: newSid,
        );
      } else {
        response = await _api.analyseFile(
          fileBytes: selectedFileBytesList.first,
          fileName:  selectedFileNames.first,
          inputType: selectedInputType,
          domain:    selectedDomain,
          sessionId: newSid,
        );
      }

      result = response;
      _pollingTimer?.cancel(); // Cancel polling timer since we have the final result now
      status = AnalysisStatus.complete;
      agentProgressStep = 6;

      // Add system notifications
      final isMock = response.insight.contains("MOCK DATA") ||
                     response.insight.contains("MOCK") ||
                     (response.artifacts?.signals['mock_mode_active'] == true);

      if (isMock) {
        addNotification(
          "Mock Data Active",
          "The system switched to mock data mode because Gemini was unavailable.",
          type: "warning",
        );
      } else {
        addNotification(
          "Analysis Complete",
          "Executive brief successfully generated for domain: ${response.domain.toUpperCase()}.",
          type: "info",
        );
      }

      _saveSessionToHistory();
      notifyListeners();

    } catch (e) {
      _pollingTimer?.cancel();
      status       = AnalysisStatus.error;
      errorMessage = e.toString();
      notifyListeners();
    }
  }

  // ── Real polling ───────────────────────────────────────────────────────

  bool _polling = false;

  void _pollProgress(String sessionId) {
    _pollingTimer?.cancel();
    _polling = false;

    _pollingTimer = Timer.periodic(const Duration(seconds: 1), (timer) async {
      if (_polling) return; // skip tick if previous call is still in-flight
      _polling = true;
      try {
        final trace = await _api.getSessionTrace(sessionId);
        final backendStatus = trace.session['status'] as String?;

        if (backendStatus != null) {
          if (backendStatus == 'queued') {
            if (status != AnalysisStatus.queued) {
              status = AnalysisStatus.queued;
              notifyListeners();
            }
          } else if (backendStatus == 'pending') {
            if (status == AnalysisStatus.queued || status == AnalysisStatus.loading) {
              status = AnalysisStatus.loading;
              notifyListeners();
            }
            agentProgressStep = 0;
          } else if (backendStatus == 'ingesting') {
            agentProgressStep = 1;
          } else if (backendStatus == 'researching') {
            agentProgressStep = 2;
          } else if (backendStatus == 'analysing') {
            agentProgressStep = 3;
          } else if (backendStatus == 'deciding') {
            agentProgressStep = 4;
          } else if (backendStatus == 'executing') {
            agentProgressStep = 5;
          } else if (backendStatus == 'complete' || backendStatus == 'failed') {
            agentProgressStep = 6;
          }

          // Build live logs based on trace artifacts
          final List<String> logs = [];
          logs.add('[${_ts()}] Pipeline status: ${backendStatus.toUpperCase()}');
          for (final art in trace.artifacts) {
            logs.add('[${_formatTime(art.createdAt)}] ${art.agentName.toUpperCase()} generated ${art.artifactType}.json');
          }
          liveLogs = logs;
          notifyListeners();

          if (backendStatus == 'complete' || backendStatus == 'failed') {
            timer.cancel();
            if (backendStatus == 'failed') {
              status = AnalysisStatus.error;
              errorMessage = 'Pipeline failed during processing';
              notifyListeners();
            }
          }
        }
      } catch (e) {
        // Don't interrupt on transient fetch errors or 404 at start
        debugPrint('Polling error: $e');
      } finally {
        _polling = false;
      }
    });
  }

  String _formatTime(String isoString) {
    try {
      final dt = DateTime.parse(isoString).toLocal();
      return '${dt.hour.toString().padLeft(2, '0')}:'
             '${dt.minute.toString().padLeft(2, '0')}:'
             '${dt.second.toString().padLeft(2, '0')}';
    } catch (_) {
      return '';
    }
  }

  String _ts() {
    final n = DateTime.now();
    return '${n.hour.toString().padLeft(2, '0')}:'
           '${n.minute.toString().padLeft(2, '0')}:'
           '${n.second.toString().padLeft(2, '0')}';
  }

  Future<void> _saveSessionToHistory() async {
    if (result == null || currentSessionId == null) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyRaw = prefs.getStringList('history_sessions') ?? [];

      final insight = result!.insight;
      final sessionData = {
        'sessionId': currentSessionId,
        'domain': result!.domain,
        'severityLabel': result!.severityLabel ?? 'Unknown',
        'insightPreview': insight.length > 80 ? '${insight.substring(0, 80)}...' : insight,
        'createdAt': DateTime.now().toIso8601String(),
      };

      // Ensure no duplicates
      historyRaw.removeWhere((item) {
        final map = jsonDecode(item);
        return map['sessionId'] == currentSessionId;
      });

      historyRaw.insert(0, jsonEncode(sessionData));

      if (historyRaw.length > 20) {
        historyRaw.removeRange(20, historyRaw.length);
      }

      await prefs.setStringList('history_sessions', historyRaw);
    } catch (e) {
      debugPrint('Failed to save session to history: $e');
    }
  }

  Future<void> loadSession(String sessionId) async {
    status = AnalysisStatus.loading;
    errorMessage = null;
    currentSessionId = sessionId;
    notifyListeners();

    try {
      final trace = await _api.getSessionTrace(sessionId);
      
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

      // Extract KPIs
      List<KpiAffected> kpis = [];
      if (brief['kpis_affected'] is List) {
        kpis = (brief['kpis_affected'] as List).map((e) => KpiAffected.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      // Extract TopAction
      TopAction topAction = const TopAction(
        rank: 1, actionType: 'unknown', description: '',
        apiEndpoint: '', apiPayload: {}, quantifiedDelta: '',
        feasibilityScore: 5, impactScore: 5, compositeScore: 5,
        justification: '', successMetric: '', timeToExecute: '',
      );
      if (brief['top_action'] is Map) {
        topAction = TopAction.fromJson(Map<String, dynamic>.from(brief['top_action']));
      }

      // Extract alternatives
      List<TopAction> alts = [];
      if (brief['alternative_actions'] is List) {
        alts = (brief['alternative_actions'] as List).map((e) => TopAction.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      // Extract notifications
      List<NotificationSent> notifications = [];
      if (exec['notifications_sent'] is List) {
        notifications = (exec['notifications_sent'] as List).map((e) => NotificationSent.fromJson(Map<String, dynamic>.from(e))).toList();
      }

      result = AnalysisResponse(
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

      status = AnalysisStatus.complete;
      notifyListeners();
    } catch (e) {
      status = AnalysisStatus.error;
      errorMessage = 'Failed to load session details: $e';
      notifyListeners();
      rethrow;
    }
  }

  // ── Reset ──────────────────────────────────────────────────────────────

  void reset() {
    _pollingTimer?.cancel();
    status            = AnalysisStatus.idle;
    result            = null;
    errorMessage      = null;
    textContent       = '';
    urlContent        = '';
    selectedFileNames = [];
    selectedFileBytesList = [];
    selectedFileSizes = [];
    selectedDomain    = null;
    liveLogs          = [];
    agentProgressStep = 0;
    notifyListeners();
  }
}
