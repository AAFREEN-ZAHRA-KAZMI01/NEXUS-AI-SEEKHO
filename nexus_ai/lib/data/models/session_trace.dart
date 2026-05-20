class AgentArtifactItem {
  final String id;
  final String sessionId;
  final String agentName;
  final String artifactType;
  final Map<String, dynamic> content;
  final String createdAt;
  final double? durationSeconds;

  const AgentArtifactItem({
    required this.id,
    required this.sessionId,
    required this.agentName,
    required this.artifactType,
    required this.content,
    required this.createdAt,
    this.durationSeconds,
  });

  factory AgentArtifactItem.fromJson(Map<String, dynamic> j) => AgentArtifactItem(
    id:              j['id']            ?? '',
    sessionId:       j['session_id']    ?? '',
    agentName:       j['agent_name']    ?? '',
    artifactType:    j['artifact_type'] ?? '',
    content:        Map<String, dynamic>.from(j['content'] ?? {}),
    createdAt:       j['created_at']    ?? '',
    durationSeconds: j['duration_seconds'] != null
                       ? (j['duration_seconds']).toDouble() : null,
  );

  Map<String, dynamic> toJson() => {
    'id': id, 'session_id': sessionId, 'agent_name': agentName,
    'artifact_type': artifactType, 'content': content,
    'created_at': createdAt, 'duration_seconds': durationSeconds,
  };
}

class SessionTrace {
  final Map<String, dynamic> session;
  final List<AgentArtifactItem> artifacts;
  final int totalArtifacts;
  final double? pipelineDurationSeconds;

  const SessionTrace({
    required this.session,
    required this.artifacts,
    required this.totalArtifacts,
    this.pipelineDurationSeconds,
  });

  factory SessionTrace.fromJson(Map<String, dynamic> j) => SessionTrace(
    session:        Map<String, dynamic>.from(j['session'] ?? {}),
    artifacts:     (j['artifacts'] as List? ?? [])
                     .map((e) => AgentArtifactItem.fromJson(e)).toList(),
    totalArtifacts: (j['total_artifacts'] ?? 0) as int,
    pipelineDurationSeconds: j['pipeline_duration_seconds'] != null
                               ? (j['pipeline_duration_seconds']).toDouble() : null,
  );

  Map<String, dynamic> toJson() => {
    'session': session,
    'artifacts': artifacts.map((e) => e.toJson()).toList(),
    'total_artifacts': totalArtifacts,
    'pipeline_duration_seconds': pipelineDurationSeconds,
  };
}
