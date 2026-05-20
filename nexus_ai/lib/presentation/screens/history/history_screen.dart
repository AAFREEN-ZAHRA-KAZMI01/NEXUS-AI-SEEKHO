import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/services/api_service.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  bool _isLoading = true;
  List<Map<String, dynamic>> _sessions = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyRaw = prefs.getStringList('history_sessions') ?? [];

      List<Map<String, dynamic>> sessions = [];
      for (final raw in historyRaw) {
        try {
          final data = jsonDecode(raw) as Map<String, dynamic>;
          final sessionId = data['sessionId'] as String;

          // Fetch real-time status as requested
          final statusMap = await ApiService().getSessionStatus(sessionId);
          final backendStatus = statusMap['status'] as String?;
          final duration = statusMap['duration_seconds'] as num?;

          data['realStatus'] = backendStatus;
          data['duration'] = duration;

          sessions.add(data);
        } catch (e) {
          debugPrint('Error loading a history session: $e');
        }
      }

      if (mounted) {
        setState(() {
          _sessions = sessions;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  String _timeAgo(DateTime? date) {
    if (date == null) return '';
    final diff = DateTime.now().difference(date);
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'Just now';
  }

  String _getDomainEmoji(String domain) {
    domain = domain.toLowerCase();
    if (domain.contains('logistics')) return '📦';
    if (domain.contains('business')) return '🏢';
    if (domain.contains('finance')) return '💹';
    if (domain.contains('policy')) return '🏛️';
    if (domain.contains('healthcare')) return '🏥';
    if (domain.contains('urban')) return '🏙️';
    return '📁';
  }

  PillType _getSeverityPillType(String label) {
    label = label.toLowerCase();
    if (label.contains('critical') || label.contains('high')) return PillType.red;
    if (label.contains('medium')) return PillType.orange;
    if (label.contains('unknown') || label.contains('n/a')) return PillType.grey;
    return PillType.green;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('Session History', style: AppTextStyles.heading3),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: primaryColor))
          : _sessions.isEmpty
              ? Center(
                  child: Text(
                    'No past sessions found.',
                    style: AppTextStyles.body.copyWith(color: text3Color),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _sessions.length,
                  itemBuilder: (context, index) {
                    final session = _sessions[index];
                    final domain = session['domain'] as String? ?? 'Unknown';
                    final severityLabel = session['severityLabel'] as String? ?? 'N/A';
                    final insightPreview = session['insightPreview'] as String? ?? '';
                    final createdAtStr = session['createdAt'] as String?;
                    final status = session['realStatus'] as String? ?? 'unknown';

                    DateTime? createdAt;
                    if (createdAtStr != null) {
                      createdAt = DateTime.tryParse(createdAtStr);
                    }

                    return GestureDetector(
                      onTap: () {
                        Navigator.pushNamed(
                          context,
                          '/trace',
                          arguments: session['sessionId'],
                        );
                      },
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: NexusCard(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(
                                    _getDomainEmoji(domain),
                                    style: const TextStyle(fontSize: 18),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      domain.toUpperCase(),
                                      style: AppTextStyles.label.copyWith(
                                        color: textColor,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                  Text(
                                    _timeAgo(createdAt),
                                    style: AppTextStyles.bodySmall,
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                insightPreview.isEmpty ? 'No insight available' : insightPreview,
                                style: AppTextStyles.body.copyWith(color: text2Color),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 12),
                              Row(
                                children: [
                                  PillBadge(
                                    severityLabel,
                                    type: _getSeverityPillType(severityLabel),
                                  ),
                                  const SizedBox(width: 8),
                                  PillBadge(
                                    status.toUpperCase(),
                                    type: status == 'complete' ? PillType.green : PillType.orange,
                                  ),
                                ],
                              )
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
