import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../data/services/api_service.dart';
import '../../../../data/models/domain_state_summary.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/nexus_button.dart';

class DomainDetailScreen extends StatefulWidget {
  const DomainDetailScreen({super.key});

  @override
  State<DomainDetailScreen> createState() => _DomainDetailScreenState();
}

class _DomainDetailScreenState extends State<DomainDetailScreen> {
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _domainSessions = [];
  bool _loadingSessions = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is DomainStateSummary) {
      _loadSessions(args.domain);
    }
  }

  Future<void> _loadSessions(String domain) async {
    setState(() {
      _loadingSessions = true;
    });
    try {
      final sessions = await _apiService.getRecentSessions();
      final filtered = sessions.where((s) => s['domain']?.toString().toLowerCase() == domain.toLowerCase()).toList();
      setState(() {
        _domainSessions = filtered.take(3).toList();
        _loadingSessions = false;
      });
    } catch (_) {
      setState(() {
        _loadingSessions = false;
      });
    }
  }

  String _formatMetricKey(String key) {
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .map((str) => str.isNotEmpty ? '${str[0].toUpperCase()}${str.substring(1)}' : '')
        .join(' ');
  }

  String _formatMetricValue(String key, dynamic value) {
    if (value == null) return '—';
    if (value is num) {
      String result = '';
      double numVal = value.toDouble();
      if (numVal.abs() >= 1000000) {
        result = '${(numVal / 1000000).toStringAsFixed(1)}M';
      } else if (numVal.abs() >= 1000) {
        result = '${(numVal / 1000).toStringAsFixed(1)}K';
      } else {
        result = value.toString();
        if (value is double) {
          result = value.toStringAsFixed(1);
        }
      }

      if (key.endsWith('_pct') || key.endsWith('_rate')) {
        result = '$result%';
      }
      if (key.endsWith('_pkr') || key.startsWith('pkr_') || key.contains('_revenue_')) {
        result = '₨$result';
      }
      return result;
    }
    return value.toString();
  }

  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args == null || args is! DomainStateSummary) {
      return Scaffold(
        backgroundColor: bgColor,
        body: const Center(child: Text('Invalid arguments')),
      );
    }
    final summary = args;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        title: Text(
          summary.domain.toUpperCase(),
          style: GoogleFonts.syne(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'METRICS',
                      style: AppTextStyles.label.copyWith(letterSpacing: 1.5),
                    ),
                    const SizedBox(height: 12),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: summary.metrics.length,
                      itemBuilder: (context, idx) {
                        final entry = summary.metrics.entries.elementAt(idx);
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: NexusCard(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    _formatMetricKey(entry.key),
                                    style: GoogleFonts.dmSans(
                                      color: text2Color,
                                      fontWeight: FontWeight.w500,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                                Text(
                                  _formatMetricValue(entry.key, entry.value),
                                  style: GoogleFonts.dmSans(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                // neutral trend indicator
                                const Icon(Icons.trending_flat, color: text3Color, size: 18),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'RECENT SESSIONS',
                      style: AppTextStyles.label.copyWith(letterSpacing: 1.5),
                    ),
                    const SizedBox(height: 12),
                    if (_loadingSessions)
                      const Center(child: CircularProgressIndicator(color: primaryColor))
                    else if (_domainSessions.isEmpty)
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Text(
                          'No recent sessions for this domain.',
                          style: AppTextStyles.bodySmall.copyWith(color: text3Color),
                        ),
                      )
                    else
                      Column(
                        children: _domainSessions.map((session) {
                          final String id = session['id']?.toString() ?? '';
                          final preview = session['input_preview']?.toString() ?? 'Session';
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: NexusCard(
                              padding: const EdgeInsets.all(12),
                              child: Row(
                                children: [
                                  const Icon(Icons.chat_bubble_outline, color: primaryColor, size: 16),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      preview.isNotEmpty ? preview : 'Session ${id.substring(0, id.length.clamp(0, 8))}',
                                      style: AppTextStyles.body.copyWith(fontSize: 12, color: textColor),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    session['status']?.toString() ?? '',
                                    style: AppTextStyles.bodySmall.copyWith(
                                      color: session['status'] == 'complete' ? successColor : warningColor,
                                      fontSize: 10,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: NexusButton(
                'Run Analysis',
                onTap: () {
                  Navigator.pushNamed(
                    context,
                    '/analyze',
                    arguments: {'domain': summary.domain.toLowerCase()},
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
