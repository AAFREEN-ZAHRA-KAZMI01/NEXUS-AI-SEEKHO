class TextAnalysisRequest {
  final String content;
  final String? domain;
  final String? sessionId;
  const TextAnalysisRequest({required this.content, this.domain, this.sessionId});
  Map<String, dynamic> toJson() => {
    'content': content,
    if (domain != null) 'domain': domain,
    if (sessionId != null) 'session_id': sessionId,
  };
}

class UrlAnalysisRequest {
  final String url;
  final String? domain;
  final String? sessionId;
  const UrlAnalysisRequest({required this.url, this.domain, this.sessionId});
  Map<String, dynamic> toJson() => {
    'url': url,
    if (domain != null) 'domain': domain,
    if (sessionId != null) 'session_id': sessionId,
  };
}
