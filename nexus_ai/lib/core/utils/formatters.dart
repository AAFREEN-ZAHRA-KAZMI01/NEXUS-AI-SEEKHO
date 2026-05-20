import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

String formatPKR(dynamic value) {
  if (value == null) return 'N/A';
  final num v = value is num ? value : num.tryParse(value.toString()) ?? 0;
  if (v >= 1000000) return '${(v / 1000000).toStringAsFixed(1)}M PKR';
  if (v >= 1000)    return '${(v / 1000).toStringAsFixed(1)}K PKR';
  return 'PKR ${v.toStringAsFixed(0)}';
}

String formatPct(dynamic value) {
  if (value == null) return 'N/A';
  final double v = value is double ? value : double.tryParse(value.toString()) ?? 0;
  final pct = (v * 100).toStringAsFixed(1);
  return v >= 0 ? '+$pct%' : '$pct%';
}

String formatSeverityLabel(int severity) {
  if (severity >= 9) return 'Critical';
  if (severity >= 7) return 'High';
  if (severity >= 5) return 'Medium';
  if (severity >= 3) return 'Low-Medium';
  return 'Low';
}

String formatActionType(String type) {
  return type
    .split('_')
    .map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}')
    .join(' ');
}

String formatAgentName(String name) {
  return name
    .replaceAll('_agent', '')
    .split('_')
    .map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}')
    .join(' ') + ' Agent';
}

String formatDomain(String domain) {
  return domain.isEmpty ? domain : '${domain[0].toUpperCase()}${domain.substring(1)}';
}

String formatTimestamp(String iso) {
  try {
    final dt = DateTime.parse(iso).toLocal();
    final h  = dt.hour.toString().padLeft(2, '0');
    final m  = dt.minute.toString().padLeft(2, '0');
    final s  = dt.second.toString().padLeft(2, '0');
    return '$h:$m:$s';
  } catch (_) {
    return iso.length > 8 ? iso.substring(11, 19) : iso;
  }
}

Color getSeverityColor(int severity) {
  if (severity >= 7) return errorColor;
  if (severity >= 5) return warningColor;
  return successColor;
}

Color getDeltaColor(dynamic changePct) {
  if (changePct == null) return text2Color;
  final v = changePct is num ? changePct.toDouble()
          : double.tryParse(changePct.toString()) ?? 0;
  return v >= 0 ? successColor : errorColor;
}
