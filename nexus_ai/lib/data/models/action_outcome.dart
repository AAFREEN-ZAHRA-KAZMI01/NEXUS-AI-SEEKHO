class ActionOutcome {
  final String id;
  final String sessionId;
  final String actionType;
  final String actionDescription;
  final String recommendedDelta;
  final bool userConfirmed;
  final String? confirmedAt;
  final String? actualOutcomeNote;
  final String? outcomeRecordedAt;
  final String domain;
  final String? kpiName;
  final double? projectedValue;
  final double? actualValue;
  final String? createdAt;

  const ActionOutcome({
    required this.id,
    required this.sessionId,
    required this.actionType,
    required this.actionDescription,
    required this.recommendedDelta,
    required this.userConfirmed,
    this.confirmedAt,
    this.actualOutcomeNote,
    this.outcomeRecordedAt,
    required this.domain,
    this.kpiName,
    this.projectedValue,
    this.actualValue,
    this.createdAt,
  });

  factory ActionOutcome.fromJson(Map<String, dynamic> json) {
    return ActionOutcome(
      id: json['id'] as String? ?? '',
      sessionId: json['session_id'] as String? ?? '',
      actionType: json['action_type'] as String? ?? '',
      actionDescription: json['action_description'] as String? ?? '',
      recommendedDelta: json['recommended_delta'] as String? ?? '',
      userConfirmed: json['user_confirmed'] as bool? ?? false,
      confirmedAt: json['confirmed_at'] as String?,
      actualOutcomeNote: json['actual_outcome_note'] as String?,
      outcomeRecordedAt: json['outcome_recorded_at'] as String?,
      domain: json['domain'] as String? ?? 'general',
      kpiName: json['kpi_name'] as String?,
      projectedValue: (json['projected_value'] as num?)?.toDouble(),
      actualValue: (json['actual_value'] as num?)?.toDouble(),
      createdAt: json['created_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'session_id': sessionId,
        'action_type': actionType,
        'action_description': actionDescription,
        'recommended_delta': recommendedDelta,
        'user_confirmed': userConfirmed,
        'confirmed_at': confirmedAt,
        'actual_outcome_note': actualOutcomeNote,
        'outcome_recorded_at': outcomeRecordedAt,
        'domain': domain,
        'kpi_name': kpiName,
        'projected_value': projectedValue,
        'actual_value': actualValue,
        'created_at': createdAt,
      };

  bool get hasOutcomeRecorded => outcomeRecordedAt != null;
}

class OutcomeSummary {
  final int totalActionsRecommended;
  final int totalConfirmed;
  final double confirmationRatePct;
  final int outcomesRecorded;
  final Map<String, DomainStat> byDomain;

  const OutcomeSummary({
    required this.totalActionsRecommended,
    required this.totalConfirmed,
    required this.confirmationRatePct,
    required this.outcomesRecorded,
    required this.byDomain,
  });

  factory OutcomeSummary.fromJson(Map<String, dynamic> json) {
    final rawByDomain = (json['by_domain'] as Map<String, dynamic>?) ?? {};
    final byDomain = rawByDomain.map(
      (k, v) => MapEntry(
        k,
        DomainStat.fromJson(v as Map<String, dynamic>),
      ),
    );
    return OutcomeSummary(
      totalActionsRecommended: json['total_actions_recommended'] as int? ?? 0,
      totalConfirmed: json['total_confirmed'] as int? ?? 0,
      confirmationRatePct:
          (json['confirmation_rate_pct'] as num?)?.toDouble() ?? 0.0,
      outcomesRecorded: json['outcomes_recorded'] as int? ?? 0,
      byDomain: byDomain,
    );
  }
}

class DomainStat {
  final int confirmed;
  final int recorded;

  const DomainStat({required this.confirmed, required this.recorded});

  factory DomainStat.fromJson(Map<String, dynamic> json) => DomainStat(
        confirmed: json['confirmed'] as int? ?? 0,
        recorded: json['recorded'] as int? ?? 0,
      );
}
