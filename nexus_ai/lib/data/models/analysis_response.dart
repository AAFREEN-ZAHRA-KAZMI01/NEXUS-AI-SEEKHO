class KpiAffected {
  final String kpi;
  final dynamic currentValue;
  final String unit;
  final dynamic projectedValue;
  final String impactDirection;
  final dynamic delta;
  final dynamic deltaPct;

  const KpiAffected({
    required this.kpi,
    this.currentValue,
    required this.unit,
    this.projectedValue,
    required this.impactDirection,
    this.delta,
    this.deltaPct,
  });

  factory KpiAffected.fromJson(Map<String, dynamic> j) => KpiAffected(
    kpi:             j['kpi']              ?? '',
    currentValue:    j['current_value'],
    unit:            j['current_unit']     ?? j['unit'] ?? '',
    projectedValue:  j['projected_value'],
    impactDirection: j['impact_direction'] ?? 'stable',
    delta:           j['delta'],
    deltaPct:        j['delta_pct'],
  );

  Map<String, dynamic> toJson() => {
    'kpi': kpi, 'current_value': currentValue, 'unit': unit,
    'projected_value': projectedValue, 'impact_direction': impactDirection,
    'delta': delta, 'delta_pct': deltaPct,
  };
}

class TopAction {
  final int rank;
  final String actionType;
  final String description;
  final String apiEndpoint;
  final Map<String, dynamic> apiPayload;
  final String quantifiedDelta;
  final double feasibilityScore;
  final double impactScore;
  final double compositeScore;
  final String justification;
  final String successMetric;
  final String timeToExecute;

  const TopAction({
    required this.rank,
    required this.actionType,
    required this.description,
    required this.apiEndpoint,
    required this.apiPayload,
    required this.quantifiedDelta,
    required this.feasibilityScore,
    required this.impactScore,
    required this.compositeScore,
    required this.justification,
    required this.successMetric,
    required this.timeToExecute,
  });

  factory TopAction.fromJson(Map<String, dynamic> j) => TopAction(
    rank:             (j['rank']              ?? 1)   as int,
    actionType:        j['action_type']        ?? '',
    description:       j['description']        ?? '',
    apiEndpoint:       j['api_endpoint']       ?? '',
    apiPayload:        Map<String, dynamic>.from(j['api_payload'] ?? {}),
    quantifiedDelta:   j['quantified_delta']   ?? '',
    feasibilityScore: (j['feasibility_score']  ?? 5.0).toDouble(),
    impactScore:      (j['impact_score']        ?? 5.0).toDouble(),
    compositeScore:   (j['composite_score']     ?? 5.0).toDouble(),
    justification:     j['justification']       ?? '',
    successMetric:     j['success_metric']      ?? '',
    timeToExecute:     j['time_to_execute']     ?? '',
  );

  Map<String, dynamic> toJson() => {
    'rank': rank, 'action_type': actionType, 'description': description,
    'api_endpoint': apiEndpoint, 'api_payload': apiPayload,
    'quantified_delta': quantifiedDelta, 'feasibility_score': feasibilityScore,
    'impact_score': impactScore, 'composite_score': compositeScore,
    'justification': justification, 'success_metric': successMetric,
    'time_to_execute': timeToExecute,
  };
}

class NotificationSent {
  final String recipient;
  final String channel;
  final String messagePreview;
  final String status;
  final String timestamp;

  const NotificationSent({
    required this.recipient,
    required this.channel,
    required this.messagePreview,
    required this.status,
    required this.timestamp,
  });

  factory NotificationSent.fromJson(Map<String, dynamic> j) => NotificationSent(
    recipient:      j['recipient']       ?? '',
    channel:        j['channel']         ?? 'app',
    messagePreview: j['message_preview'] ?? '',
    status:         j['status']          ?? 'delivered',
    timestamp:      j['timestamp']       ?? '',
  );

  Map<String, dynamic> toJson() => {
    'recipient': recipient, 'channel': channel,
    'message_preview': messagePreview, 'status': status, 'timestamp': timestamp,
  };
}

class AllArtifacts {
  final Map<String, dynamic> taskPlan;
  final Map<String, dynamic> signals;
  final Map<String, dynamic> impact;
  final Map<String, dynamic> actions;
  final Map<String, dynamic> context;
  final Map<String, dynamic> masterBrief;
  final Map<String, dynamic> execLog;

  const AllArtifacts({
    required this.taskPlan,
    required this.signals,
    required this.impact,
    required this.actions,
    required this.context,
    required this.masterBrief,
    required this.execLog,
  });

  factory AllArtifacts.fromJson(Map<String, dynamic> j) => AllArtifacts(
    taskPlan:    Map<String, dynamic>.from(j['task_plan']    ?? {}),
    signals:     Map<String, dynamic>.from(j['signals']      ?? {}),
    impact:      Map<String, dynamic>.from(j['impact']       ?? {}),
    actions:     Map<String, dynamic>.from(j['actions']      ?? {}),
    context:     Map<String, dynamic>.from(j['context']      ?? {}),
    masterBrief: Map<String, dynamic>.from(j['master_brief'] ?? {}),
    execLog:     Map<String, dynamic>.from(j['exec_log']     ?? {}),
  );

  Map<String, dynamic> toJson() => {
    'task_plan': taskPlan, 'signals': signals, 'impact': impact,
    'actions': actions, 'context': context,
    'master_brief': masterBrief, 'exec_log': execLog,
  };
}

class AnalysisResponse {
  final String sessionId;
  final String domain;
  final String status;
  final double durationSeconds;
  final String insight;
  final int severity;
  final String severityLabel;
  final Map<String, dynamic> impactSummary;
  final List<KpiAffected> kpisAffected;
  final TopAction topAction;
  final List<TopAction> alternativeActions;
  final Map<String, dynamic> beforeState;
  final Map<String, dynamic> afterState;
  final Map<String, dynamic> delta;
  final List<NotificationSent> notificationsSent;
  final String executionStatus;
  final String? corroboration;
  final String? context;
  final String traceUrl;
  final AllArtifacts? artifacts;

  const AnalysisResponse({
    required this.sessionId,
    required this.domain,
    required this.status,
    required this.durationSeconds,
    required this.insight,
    required this.severity,
    required this.severityLabel,
    required this.impactSummary,
    required this.kpisAffected,
    required this.topAction,
    required this.alternativeActions,
    required this.beforeState,
    required this.afterState,
    required this.delta,
    required this.notificationsSent,
    required this.executionStatus,
    this.corroboration,
    this.context,
    required this.traceUrl,
    this.artifacts,
  });

  factory AnalysisResponse.fromJson(Map<String, dynamic> j) {
    final topActionRaw = j['top_action'];
    return AnalysisResponse(
      sessionId:        j['session_id']       ?? '',
      domain:           j['domain']           ?? 'business',
      status:           j['status']           ?? 'complete',
      durationSeconds: (j['duration_seconds'] ?? 0).toDouble(),
      insight:          j['insight']          ?? '',
      severity:        (j['severity']         ?? 5) as int,
      severityLabel:    j['severity_label']   ?? 'Medium',
      impactSummary:   Map<String, dynamic>.from(j['impact_summary'] ?? {}),
      kpisAffected:   (j['kpis_affected'] as List? ?? [])
                        .map((e) => KpiAffected.fromJson(e)).toList(),
      topAction: topActionRaw != null
                    ? TopAction.fromJson(topActionRaw)
                    : const TopAction(
                        rank: 1, actionType: 'unknown', description: '',
                        apiEndpoint: '', apiPayload: {}, quantifiedDelta: '',
                        feasibilityScore: 5, impactScore: 5, compositeScore: 5,
                        justification: '', successMetric: '', timeToExecute: '',
                      ),
      alternativeActions: (j['alternative_actions'] as List? ?? [])
                            .map((e) => TopAction.fromJson(e)).toList(),
      beforeState:      Map<String, dynamic>.from(j['before_state']      ?? {}),
      afterState:       Map<String, dynamic>.from(j['after_state']       ?? {}),
      delta:            Map<String, dynamic>.from(j['delta']             ?? {}),
      notificationsSent:(j['notifications_sent'] as List? ?? [])
                          .map((e) => NotificationSent.fromJson(e)).toList(),
      executionStatus:   j['execution_status'] ?? 'complete',
      corroboration:     j['corroboration'],
      context:           j['context'],
      traceUrl:          j['trace_url']        ?? '',
      artifacts: j['artifacts'] != null
                    ? AllArtifacts.fromJson(j['artifacts']) : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'session_id': sessionId, 'domain': domain, 'status': status,
    'duration_seconds': durationSeconds, 'insight': insight,
    'severity': severity, 'severity_label': severityLabel,
    'impact_summary': impactSummary,
    'kpis_affected': kpisAffected.map((e) => e.toJson()).toList(),
    'top_action': topAction.toJson(),
    'alternative_actions': alternativeActions.map((e) => e.toJson()).toList(),
    'before_state': beforeState, 'after_state': afterState, 'delta': delta,
    'notifications_sent': notificationsSent.map((e) => e.toJson()).toList(),
    'execution_status': executionStatus, 'corroboration': corroboration,
    'context': context, 'trace_url': traceUrl,
    'artifacts': artifacts?.toJson(),
  };
}
