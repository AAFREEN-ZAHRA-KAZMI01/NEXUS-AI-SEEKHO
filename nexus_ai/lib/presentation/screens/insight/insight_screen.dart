import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/analysis_response.dart';
import '../../../data/services/api_service.dart';
import '../../providers/analysis_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';
import '../../widgets/common/bottom_nav_bar.dart';
import '../../../core/constants/api_constants.dart';
import 'package:url_launcher/url_launcher.dart';

class InsightScreen extends StatelessWidget {
  const InsightScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AnalysisProvider>(
      builder: (_, provider, __) {
        final result = provider.result;
        if (result == null) {
          return Scaffold(
            backgroundColor: bgColor,
            appBar: AppBar(
              backgroundColor: bgColor,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, color: textColor),
                onPressed: () => Navigator.pop(context),
              ),
              title: Text('Insight', style: AppTextStyles.heading3),
            ),
            body: Center(
              child: Text(
                'No analysis result yet.',
                style: AppTextStyles.body,
              ),
            ),
          );
        }

        final severityPillType = result.severity >= 7
            ? PillType.red
            : result.severity >= 5
                ? PillType.orange
                : PillType.green;

        final appBarTitle = result.insight.length > 40
            ? '${result.insight.substring(0, 40)}...'
            : result.insight;

        return Scaffold(
          backgroundColor: bgColor,
          bottomNavigationBar: NexusBottomNav(
            currentIndex: 1,
            onTap: (i) => handleBottomNavTap(context, i, provider),
          ),
          appBar: AppBar(
            backgroundColor: bgColor,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: textColor),
              onPressed: () => Navigator.pop(context),
            ),
            title: Text(appBarTitle, style: AppTextStyles.heading3),
            actions: [
              IconButton(
                icon: const Icon(Icons.share, color: textColor),
                onPressed: () async {
                  await Clipboard.setData(
                      ClipboardData(text: result.insight));
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Insight copied to clipboard'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  }
                },
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (result.insight.contains("MOCK DATA") ||
                    result.insight.contains("MOCK") ||
                    (result.artifacts?.signals['mock_mode_active'] == true)) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: warningColor.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: warningColor.withOpacity(0.5), width: 1),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning_amber_rounded, color: warningColor, size: 22),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: const [
                              Text(
                                'MOCK DATA FALLBACK ACTIVE',
                                style: TextStyle(
                                  color: warningColor,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                              SizedBox(height: 2),
                              Text(
                                'The system switched to mock data because Gemini was unavailable. A warning email alert was sent to your configured SMTP inbox.',
                                style: TextStyle(
                                  color: text2Color,
                                  fontSize: 11,
                                  height: 1.3,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                // 1. Severity bar card
                NexusCard(
                  borderColor: getSeverityColor(result.severity),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text('Severity Score', style: AppTextStyles.body),
                          const Spacer(),
                          PillBadge(
                            '${result.severity} / 10 — ${result.severityLabel}',
                            type: severityPillType,
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: result.severity / 10.0,
                          backgroundColor: card2Color,
                          valueColor: AlwaysStoppedAnimation<Color>(
                              getSeverityColor(result.severity)),
                          minHeight: 6,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        result.severityLabel,
                        style: AppTextStyles.bodySmall.copyWith(
                          color: getSeverityColor(result.severity),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 2. Key insight card
                NexusCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('🔍  KEY INSIGHT',
                          style: AppTextStyles.label
                              .copyWith(letterSpacing: 1.0)),
                      const SizedBox(height: 8),
                      Text(
                        result.insight,
                        style: AppTextStyles.body.copyWith(
                          fontSize: 13,
                          height: 1.6,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 2b. Recommended actions card
                NexusCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '⚡  RECOMMENDED ACTIONS',
                        style: AppTextStyles.label
                            .copyWith(letterSpacing: 1.0),
                      ),
                      const SizedBox(height: 10),
                      ...[
                        result.topAction,
                        ...result.alternativeActions.take(2),
                      ].map((a) => _ActionRow(action: a)),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 3. Business impact card
                NexusCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('📈  BUSINESS IMPACT',
                          style: AppTextStyles.label
                              .copyWith(letterSpacing: 1.0)),
                      const SizedBox(height: 10),
                      GridView.count(
                        crossAxisCount: 2,
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        crossAxisSpacing: 8,
                        mainAxisSpacing: 8,
                        childAspectRatio: 1.8,
                        children: [
                          _ImpactBox(
                            'Cost Impact',
                            result.kpisAffected.isNotEmpty
                                ? formatPct(
                                    result.kpisAffected.first.deltaPct)
                                : 'N/A',
                          ),
                          _ImpactBox(
                            'Revenue at Risk',
                            formatPKR(
                                result.impactSummary['financial_pkr']),
                          ),
                          _ImpactBox(
                            'KPIs Affected',
                            '${result.kpisAffected.length}',
                          ),
                          _ImpactBox(
                            'Affected Parties',
                            '${(result.impactSummary['affected_parties'] as List?)?.length ?? 0}',
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 4. Action card
                NexusCard(
                  borderColor: indigoColor,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      PillBadge(
                        'Action #${result.topAction.rank} — Executed',
                        type: PillType.indigo,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        formatActionType(result.topAction.actionType),
                        style: AppTextStyles.body.copyWith(
                          fontSize: 13,
                          color: purple2Color,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        result.topAction.justification,
                        style: AppTextStyles.body.copyWith(
                          color: text3Color,
                          fontSize: 12,
                        ),
                        maxLines: 4,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: _BABox(
                              'Before',
                              _findBeforeValue(result),
                              text3Color,
                              strikethrough: true,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _BABox(
                              'After',
                              _findAfterValue(result),
                              successColor,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // 5. Notifications card
                if (result.notificationsSent.isNotEmpty)
                  NexusCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('📧  NOTIFICATIONS SENT',
                            style: AppTextStyles.label
                                .copyWith(letterSpacing: 1.0)),
                        const SizedBox(height: 8),
                        ...result.notificationsSent
                            .map((n) => _NotifRow(notif: n)),
                      ],
                    ),
                  ),

                // 5b. AI confidence score card
                const SizedBox(height: 12),
                NexusCard(
                  borderColor: blue2Color.withOpacity(0.3),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '🤖  AI CONFIDENCE SCORE',
                        style: AppTextStyles.label
                            .copyWith(letterSpacing: 1.0),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '${(result.topAction.compositeScore * 10).round()}%',
                                  style: GoogleFonts.syne(
                                    fontSize: 28,
                                    fontWeight: FontWeight.w800,
                                    color: primaryColor,
                                  ),
                                ),
                                Text(
                                  'Composite Score',
                                  style: AppTextStyles.bodySmall,
                                ),
                              ],
                            ),
                          ),
                          Container(width: 1, height: 48, color: borderColor),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  '${(result.topAction.feasibilityScore * 10).round()}%',
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.w700,
                                    color: successColor,
                                  ),
                                ),
                                Text(
                                  'Feasibility',
                                  style: AppTextStyles.bodySmall,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: result.topAction.compositeScore / 10.0,
                          backgroundColor: card2Color,
                          valueColor: const AlwaysStoppedAnimation<Color>(
                              primaryColor),
                          minHeight: 6,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                 // 6. Bottom buttons
                Row(
                  children: [
                    Expanded(
                      child: NexusButton(
                        'Simulate Execution',
                        onTap: () =>
                            Navigator.pushNamed(context, '/simulate'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: NexusButton(
                        'Full Trace →',
                        isOutline: true,
                        onTap: () =>
                            Navigator.pushNamed(context, '/trace'),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                // 1. Send Interactive Report to Email (Premium Full Width Button)
                NexusButton(
                  '📧 Send Dashboard Report to Email',
                  onTap: () => _sendToEmail(context, result),
                ),
                
                const SizedBox(height: 12),

                // 2. Export Files (JSON and CSV side by side)
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          side: const BorderSide(color: blue2Color, width: 1.5),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          backgroundColor: cardColor,
                        ),
                        icon: const Icon(Icons.code, color: blue2Color, size: 18),
                        label: Text(
                          'Export JSON',
                          style: GoogleFonts.dmSans(
                            color: blue2Color,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        onPressed: () => _downloadAsJson(context, result),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          side: const BorderSide(color: successColor, width: 1.5),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          backgroundColor: cardColor,
                        ),
                        icon: const Icon(Icons.table_chart, color: successColor, size: 18),
                        label: Text(
                          'Export CSV',
                          style: GoogleFonts.dmSans(
                            color: successColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        onPressed: () => _downloadAsCsv(context, result),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 32),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _downloadAsJson(BuildContext context, AnalysisResponse result) async {
    final url = '${ApiConstants.baseUrl}/api/session/${result.sessionId}/export/json';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not start download')),
      );
    }
  }

  Future<void> _downloadAsCsv(BuildContext context, AnalysisResponse result) async {
    final url = '${ApiConstants.baseUrl}/api/session/${result.sessionId}/export/csv';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not start download')),
      );
    }
  }

  Future<void> _sendToEmail(BuildContext context, AnalysisResponse result) async {
    // Show a loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return Center(
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor, width: 0.5),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                CircularProgressIndicator(color: primaryColor),
                SizedBox(height: 16),
                Text(
                  'Sending report to your email...',
                  style: TextStyle(color: textColor, fontSize: 13, decoration: TextDecoration.none),
                ),
              ],
            ),
          ),
        );
      },
    );

    try {
      final userEmail = Provider.of<AuthProvider>(context, listen: false).currentUser?.email;
      await ApiService().emailReport(result.sessionId, recipientEmail: userEmail);
      
      // Close the loading dialog
      Navigator.pop(context);

      // Add UI notification
      final analysisProvider = Provider.of<AnalysisProvider>(context, listen: false);
      analysisProvider.addNotification(
        "Report Emailed",
        "Executive report for session #${result.sessionId} has been sent successfully to your configured SMTP email.",
        type: "info",
      );

      // Show a success dialog/notification popup
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            backgroundColor: cardColor,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: const BorderSide(color: borderColor, width: 0.5),
            ),
            title: Row(
              children: const [
                Icon(Icons.email_outlined, color: successColor),
                SizedBox(width: 8),
                Text('Email Sent', style: TextStyle(color: textColor, fontFamily: 'Syne', fontWeight: FontWeight.bold)),
              ],
            ),
            content: Text(
              'A beautiful HTML dashboard report of Session #${result.sessionId} has been successfully sent to your email.',
              style: const TextStyle(color: text2Color, fontSize: 13),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Great!', style: TextStyle(color: primaryColor, fontWeight: FontWeight.bold)),
              ),
            ],
          );
        },
      );
    } catch (e) {
      // Close loading dialog
      Navigator.pop(context);

      // Show error snackbar
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to send email: ${e.toString().replaceAll("Exception: ", "")}'),
          backgroundColor: errorColor,
        ),
      );
    }
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

String _findBeforeValue(AnalysisResponse result) {
  for (final entry in result.delta.entries) {
    final val = entry.value;
    if (val is Map && val.containsKey('from')) {
      return val['from'].toString();
    }
  }
  return 'N/A';
}

String _findAfterValue(AnalysisResponse result) {
  for (final entry in result.delta.entries) {
    final val = entry.value;
    if (val is Map && val.containsKey('to')) {
      return val['to'].toString();
    }
  }
  return 'N/A';
}

// ── Private widgets ───────────────────────────────────────────────────────────

class _ImpactBox extends StatelessWidget {
  final String label;
  final String value;

  const _ImpactBox(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F14),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label, style: AppTextStyles.bodySmall),
          const SizedBox(height: 4),
          Text(
            value,
            style: AppTextStyles.heading3.copyWith(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

class _BABox extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  final bool strikethrough;

  const _BABox(
    this.label,
    this.value,
    this.color, {
    this.strikethrough = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F0F14),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTextStyles.bodySmall),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w500,
              color: color,
              decoration:
                  strikethrough ? TextDecoration.lineThrough : null,
              decorationColor: strikethrough ? color : null,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionRow extends StatelessWidget {
  final TopAction action;

  const _ActionRow({required this.action});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: card2Color,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: indigoColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                '${action.rank}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: indigoColor,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              action.description.isNotEmpty
                  ? action.description
                  : formatActionType(action.actionType),
              style: AppTextStyles.body.copyWith(fontSize: 12),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            action.compositeScore.toStringAsFixed(1),
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: blue2Color,
            ),
          ),
        ],
      ),
    );
  }
}

class _NotifRow extends StatelessWidget {
  final NotificationSent notif;

  const _NotifRow({required this.notif});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: borderColor, width: 0.5),
        ),
      ),
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: card2Color,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: Icon(Icons.business, color: blue2Color, size: 14),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  notif.recipient,
                  style: AppTextStyles.body.copyWith(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(notif.channel, style: AppTextStyles.bodySmall),
              ],
            ),
          ),
          const PillBadge('Sent', type: PillType.green),
        ],
      ),
    );
  }
}
