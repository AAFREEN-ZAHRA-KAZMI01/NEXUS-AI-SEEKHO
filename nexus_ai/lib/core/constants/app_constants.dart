class AppConstants {
  static const String appName     = 'Nexus AI';
  static const String appTagline  = 'Transforming Insights into Actions';
  static const String appSubtitle = 'AI Agents that understand, analyze, and take action';
  static const String brandShort  = 'NEXUS';
  static const String brandSub    = 'AI';
  static String deviceId = '';
  static const String apiKeyPrefKey = 'org_api_key';
  static const String orgIdPrefKey = 'org_id';
  static const List<String> domains = [
    'logistics', 'business', 'finance',
    'policy', 'healthcare', 'urban',
  ];

  static const Map<String, String> domainIcons = {
    'logistics':  '🚚',
    'business':   '🏪',
    'finance':    '📈',
    'policy':     '🏛️',
    'healthcare': '🏥',
    'urban':      '🌆',
  };

  static const Map<String, String> domainLabels = {
    'logistics':  'Logistics',
    'business':   'Business',
    'finance':    'Finance',
    'policy':     'Policy',
    'healthcare': 'Healthcare',
    'urban':      'Urban',
  };

  static const List<String> inputTypes = ['text', 'url', 'pdf', 'docx', 'csv', 'excel'];

  static const Map<String, String> agentModels = {
    'orchestrator': 'Gemini 1.5 Pro',
    'ingestion':    'Gemini 1.5 Flash',
    'analysis':     'Gemini 1.5 Pro',
    'decision':     'Gemini 1.5 Pro',
    'research':     'Gemini 1.5 Flash',
    'execution':    'Python Executor',
  };

  static const Map<String, String> agentEmojis = {
    'orchestrator': '🎯',
    'ingestion':    '📥',
    'analysis':     '🔬',
    'decision':     '⚖️',
    'research':     '🔍',
    'execution':    '⚡',
  };
}
