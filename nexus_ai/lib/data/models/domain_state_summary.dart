class DomainStateSummary {
  final String domain;
  final Map<String, dynamic> metrics;

  const DomainStateSummary({
    required this.domain,
    required this.metrics,
  });

  factory DomainStateSummary.fromJson(String domain, Map<String, dynamic> json) {
    return DomainStateSummary(
      domain: domain,
      metrics: json,
    );
  }
}
