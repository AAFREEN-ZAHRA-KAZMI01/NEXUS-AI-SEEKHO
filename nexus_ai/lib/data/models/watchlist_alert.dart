class WatchlistAlert {
  final String id;
  final String userId;
  final String domain;
  final String conditionType;
  final String conditionValue;
  final String? keyword;
  final String label;
  final bool isActive;
  final String? createdAt;
  final String? lastTriggeredAt;
  final int triggerCount;

  WatchlistAlert({
    required this.id,
    required this.userId,
    required this.domain,
    required this.conditionType,
    required this.conditionValue,
    this.keyword,
    required this.label,
    required this.isActive,
    this.createdAt,
    this.lastTriggeredAt,
    required this.triggerCount,
  });

  factory WatchlistAlert.fromJson(Map<String, dynamic> json) {
    return WatchlistAlert(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      domain: json['domain'] as String,
      conditionType: json['condition_type'] as String,
      conditionValue: json['condition_value'] as String,
      keyword: json['keyword'] as String?,
      label: json['label'] as String,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] as String?,
      lastTriggeredAt: json['last_triggered_at'] as String?,
      triggerCount: json['trigger_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'domain': domain,
      'condition_type': conditionType,
      'condition_value': conditionValue,
      'keyword': keyword,
      'label': label,
      'is_active': isActive,
      'created_at': createdAt,
      'last_triggered_at': lastTriggeredAt,
      'trigger_count': triggerCount,
    };
  }
}

class AlertHistoryItem {
  final String id;
  final String alertId;
  final String sessionId;
  final String? triggeredAt;
  final String triggerReason;
  final String alertLabel;
  final String domain;
  final String conditionType;
  final String conditionValue;

  AlertHistoryItem({
    required this.id,
    required this.alertId,
    required this.sessionId,
    this.triggeredAt,
    required this.triggerReason,
    required this.alertLabel,
    required this.domain,
    required this.conditionType,
    required this.conditionValue,
  });

  factory AlertHistoryItem.fromJson(Map<String, dynamic> json) {
    return AlertHistoryItem(
      id: json['id'] as String,
      alertId: json['alert_id'] as String,
      sessionId: json['session_id'] as String,
      triggeredAt: json['triggered_at'] as String?,
      triggerReason: json['trigger_reason'] as String,
      alertLabel: json['alert_label'] as String? ?? '',
      domain: json['domain'] as String? ?? '',
      conditionType: json['condition_type'] as String? ?? '',
      conditionValue: json['condition_value'] as String? ?? '',
    );
  }
}
