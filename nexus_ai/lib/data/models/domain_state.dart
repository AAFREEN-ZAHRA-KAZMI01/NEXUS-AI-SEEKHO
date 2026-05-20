class DomainState {
  final String domain;
  final Map<String, dynamic> fields;

  const DomainState({required this.domain, required this.fields});

  factory DomainState.fromJson(String domain, Map<String, dynamic> j) =>
    DomainState(domain: domain, fields: j);

  dynamic operator [](String key) => fields[key];
}
