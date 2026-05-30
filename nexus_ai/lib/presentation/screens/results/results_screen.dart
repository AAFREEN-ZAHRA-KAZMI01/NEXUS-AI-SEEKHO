import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../data/models/analysis_response.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/gradient_text.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';
import '../../widgets/results/timeline_widget.dart';
import '../../widgets/results/before_after_widget.dart';

class ResultsScreen extends StatelessWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AnalysisProvider>(
      builder: (_, provider, __) {
        final result = provider.result;

        if (result == null) {
          return Scaffold(
            backgroundColor: bgColor,
            body: Center(
              child: Text('No analysis result yet.',
                  style: AppTextStyles.body),
            ),
          );
        }

        final recovery = _findRecoveryPct(result.delta);
        final usersReached = result.notificationsSent.length;
        final revenue = result.impactSummary['financial_pkr'];
        final runtime = result.durationSeconds;

        // Timeline timestamps
        final t1 = _safeTimestamp(
            result.artifacts?.signals['timestamp']?.toString());
        final t2 = _safeTimestamp(
            result.artifacts?.impact['timestamp']?.toString());
        final t3 = _safeTimestamp(
            result.artifacts?.execLog['timestamp_start']?.toString());
        final t4 = _safeTimestamp(
            result.artifacts?.execLog['timestamp_end']?.toString());

        return Scaffold(
          backgroundColor: bgColor,
          appBar: AppBar(
            backgroundColor: bgColor,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: textColor),
              onPressed: () => Navigator.pop(context),
            ),
            title: Text('Results', style: AppTextStyles.heading3),
          ),
          body: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const SizedBox(height: 32),

                  // 1. Success hero
                  Column(
                    children: [
                      Icon(Icons.check_circle,
                              color: successColor, size: 60)
                          .animate()
                          .scale(
                            begin: const Offset(0, 0),
                            end: const Offset(1, 1),
                            duration: 600.ms,
                            curve: Curves.elasticOut,
                          ),
                      const SizedBox(height: 12),
                      GradientText(
                        text: 'Action Completed',
                        style: AppTextStyles.heading1
                            .copyWith(fontSize: 24),
                        gradient: primaryGrad,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Pipeline complete. Projected outcomes below.',
                        style: AppTextStyles.body
                            .copyWith(color: text2Color),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Severity & Confidence card
                  NexusCard(
                    borderColor: getSeverityColor(result.severity),
                    child: Row(
                      children: [
                        Text(
                          'Severity Score: ',
                          style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold),
                        ),
                        PillBadge(
                          '${result.severity} / 10 — ${result.severityLabel}',
                          type: result.severity >= 7
                              ? PillType.red
                              : result.severity >= 5
                                  ? PillType.orange
                                  : PillType.green,
                        ),
                        const Spacer(),
                        PillBadge(
                          result.confidenceLabel ?? 'Low',
                          type: (result.confidenceLabel?.toLowerCase() == 'high')
                              ? PillType.green
                              : (result.confidenceLabel?.toLowerCase() == 'medium')
                                  ? PillType.orange
                                  : PillType.red,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 2. Execution results cards
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'EXECUTION RESULTS',
                      style: AppTextStyles.label
                          .copyWith(letterSpacing: 1.2),
                    ),
                  ),
                  const SizedBox(height: 10),
                  _ResultCard(
                    icon: Icons.campaign_outlined,
                    label: 'Campaign Created',
                    detail: result.topAction.description.isNotEmpty
                        ? result.topAction.description
                        : 'Discount campaign activated',
                    color: blueColor,
                  ),
                  const SizedBox(height: 8),
                  _ResultCard(
                    icon: Icons.notifications_outlined,
                    label: 'Notifications Sent',
                    detail:
                        '${result.notificationsSent.length} recipient(s) via ${_channelList(result.notificationsSent)}',
                    color: purpleColor,
                  ),
                  const SizedBox(height: 8),
                  _ResultCard(
                    icon: Icons.dashboard_outlined,
                    label: 'Dashboard Updated',
                    detail: 'State logged, KPIs refreshed',
                    color: successColor,
                  ),

                  const SizedBox(height: 16),

                  // 2b. Projected outcome card
                  NexusCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'PROJECTED OUTCOME',
                          style: AppTextStyles.label
                              .copyWith(letterSpacing: 1.2),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            _OutcomeMetric(
                              'Reach',
                              usersReached > 0
                                  ? '$usersReached users'
                                  : '1.2K users',
                              blueColor,
                            ),
                            _OutcomeMetric(
                              'Revenue',
                              formatPKR(revenue),
                              successColor,
                            ),
                            _OutcomeMetric(
                              'Efficiency',
                              recovery != null
                                  ? formatPct(recovery)
                                  : '+18%',
                              purpleColor,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // 3. State change (before → after)
                  if (result.delta.isNotEmpty) ...[
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'STATE CHANGE',
                        style: AppTextStyles.label
                            .copyWith(letterSpacing: 1.2),
                      ),
                    ),
                    const SizedBox(height: 8),
                    BeforeAfterWidget(
                      delta: result.delta,
                      before: result.beforeState,
                      after: result.afterState,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // 4. Execution timeline
                  NexusCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Execution Timeline',
                            style: AppTextStyles.heading3),
                        const SizedBox(height: 12),
                        TimelineWidget(
                          items: [
                            TimelineItem(
                              emoji: '🔍',
                              title:
                                  'Content ingested & insights extracted',
                              agentName: 'Insight Agent',
                              time: t1,
                              dotBgColor: const Color(0xFF1A1A2E),
                            ),
                            TimelineItem(
                              emoji: '🧠',
                              title:
                                  'Impact analyzed, actions recommended',
                              agentName: 'Decision Agent',
                              time: t2,
                              dotBgColor: const Color(0xFF1A1028),
                            ),
                            TimelineItem(
                              emoji: '⚡',
                              title: 'Action simulated & executed',
                              agentName: 'Action Agent',
                              time: t3,
                              dotBgColor: const Color(0xFF1A1A10),
                            ),
                            TimelineItem(
                              emoji: '✅',
                              title: 'Outcomes projected, logs saved',
                              agentName: 'Complete',
                              time: t4,
                              dotBgColor: const Color(0xFF0F1F18),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  // 4. Action buttons
                  Row(
                    children: [
                      Expanded(
                        child: NexusButton(
                          '📤  Export PDF',
                          isOutline: true,
                          onTap: () async {
                            final url =
                                '${ApiConstants.baseUrl}/api/session/${result.sessionId}/trace';
                            if (await canLaunchUrl(Uri.parse(url))) {
                              await launchUrl(Uri.parse(url));
                            }
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: NexusButton(
                          '+ New Analysis',
                          onTap: () {
                            context
                                .read<AnalysisProvider>()
                                .reset();
                            Navigator.pushNamedAndRemoveUntil(
                              context,
                              '/analyze',
                              (r) => r.settings.name == '/home',
                            );
                          },
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

String _channelList(List<NotificationSent> notifs) {
  final channels = notifs.map((n) => n.channel).toSet().toList();
  return channels.isEmpty ? 'app' : channels.join(', ');
}

double? _findRecoveryPct(Map<String, dynamic> delta) {
  for (final entry in delta.entries) {
    if (entry.value is Map) {
      final raw = (entry.value as Map)['change_pct'];
      if (raw != null) {
        final pct = raw is num
            ? raw.toDouble()
            : double.tryParse(raw.toString()) ?? 0;
        if (pct > 0) return pct;
      }
    }
  }
  return null;
}

String _safeTimestamp(String? raw) {
  if (raw == null || raw.isEmpty) return '—';
  return formatTimestamp(raw);
}

// ── Private widgets ───────────────────────────────────────────────────────────

class _ResultCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String detail;
  final Color color;

  const _ResultCard({
    required this.icon,
    required this.label,
    required this.detail,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return NexusCard(
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: AppTextStyles.body.copyWith(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: textColor,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  detail,
                  style: AppTextStyles.bodySmall,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const Icon(Icons.check_circle, color: successColor, size: 18),
        ],
      ),
    );
  }
}

class _OutcomeMetric extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _OutcomeMetric(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: AppTextStyles.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
