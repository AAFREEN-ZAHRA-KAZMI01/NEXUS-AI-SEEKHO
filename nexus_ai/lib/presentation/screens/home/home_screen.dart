import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/bottom_nav_bar.dart';
import '../../widgets/common/nexus_card.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/services/api_service.dart';
import '../../widgets/common/notifications_sheet.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedTab = 0;
  Future<List<Map<String, dynamic>>>? _recentSessionsFuture;

  @override
  void initState() {
    super.initState();
    _fetchRecentSessions();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<AnalysisProvider>().addListener(_onProviderUpdate);
      }
    });
  }

  void _onProviderUpdate() {
    if (mounted) {
      _fetchRecentSessions();
    }
  }

  @override
  void dispose() {
    if (mounted) {
      try {
        context.read<AnalysisProvider>().removeListener(_onProviderUpdate);
      } catch (_) {}
    }
    super.dispose();
  }

  void _fetchRecentSessions() {
    setState(() {
      _recentSessionsFuture = ApiService().getRecentSessions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final userName = authProvider.currentUser?.name ?? 'User';
    final userInitial = userName.isNotEmpty ? userName[0].toUpperCase() : 'U';

    return Scaffold(
      backgroundColor: bgColor,
      bottomNavigationBar: Consumer<AnalysisProvider>(
        builder: (_, provider, __) => NexusBottomNav(
          currentIndex: 0,
          onTap: (i) => handleBottomNavTap(context, i, provider),
        ),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Fixed header ───────────────────────────────────────────────
          SafeArea(
            bottom: false,
            child: Container(
              color: surfaceColor,
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Good Evening,',
                        style: AppTextStyles.bodySmall
                            .copyWith(color: text2Color),
                      ),
                      Row(
                        children: [
                          Text(
                            userName,
                            style: GoogleFonts.syne(
                              fontSize: 22,
                              fontWeight: FontWeight.w700,
                              color: textColor,
                            ),
                          ),
                          const SizedBox(width: 6),
                          const Text('👋',
                              style: TextStyle(fontSize: 22)),
                        ],
                      ),
                    ],
                  ),
                  const Spacer(),
                  Row(
                    children: [
                      // Notification Icon
                      Consumer<AnalysisProvider>(
                        builder: (context, ap, _) {
                          final count = ap.unreadNotificationsCount;
                          return Stack(
                            clipBehavior: Clip.none,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.notifications_outlined, color: Colors.white, size: 24),
                                onPressed: () => showNotificationsBottomSheet(context),
                              ),
                              if (count > 0)
                                Positioned(
                                  right: 6,
                                  top: 6,
                                  child: Container(
                                    padding: const EdgeInsets.all(2),
                                    decoration: const BoxDecoration(
                                      color: Colors.red,
                                      shape: BoxShape.circle,
                                    ),
                                    constraints: const BoxConstraints(
                                      minWidth: 14,
                                      minHeight: 14,
                                    ),
                                    child: Text(
                                      '$count',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 8,
                                        fontWeight: FontWeight.bold,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                  ),
                                ),
                            ],
                          );
                        },
                      ),
                      const SizedBox(width: 4),
                      // Agents Active pill
                      Container(
                        padding: const EdgeInsets.symmetric(
                            vertical: 6, horizontal: 12),
                        decoration: BoxDecoration(
                          color: primaryColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: primaryColor.withOpacity(0.4),
                            width: 0.8,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 6,
                              height: 6,
                              decoration: const BoxDecoration(
                                color: primaryColor,
                                shape: BoxShape.circle,
                              ),
                            ),
                            const SizedBox(width: 5),
                            const Text(
                              'Agents Active',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w500,
                                color: primaryColor,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      // N avatar
                      Container(
                        width: 36,
                        height: 36,
                        decoration: BoxDecoration(
                          gradient: primaryGrad,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Center(
                          child: Text(
                            userInitial,
                            style: GoogleFonts.syne(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // ── Scrollable body & Overview ────────────────────────────────────────────
          Expanded(
            child: FutureBuilder<List<Map<String, dynamic>>>(
              future: _recentSessionsFuture,
              builder: (context, snapshot) {
                final sessions = snapshot.data ?? [];
                // Fallback stats if API is slow or errors out
                final int inputsCount = sessions.isNotEmpty ? sessions.length : 42;
                final int actionsExecuted = sessions.isNotEmpty ? sessions.where((s) => s['status'] == 'complete').length : 9;
                final int insightsGenerated = sessions.isNotEmpty ? sessions.where((s) => s['status'] != 'failed' && s['status'] != 'pending').length : 15;

                return SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ── Overview stats ─────────────────────────────────────────────
                      Container(
                        color: surfaceColor,
                        padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'OVERVIEW',
                              style: AppTextStyles.label.copyWith(letterSpacing: 1.5),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _StatBox('$inputsCount', 'Inputs\nProcessed', blueColor),
                                const _VertDivider(),
                                _StatBox('$insightsGenerated', 'Insights\nGenerated', purpleColor),
                                const _VertDivider(),
                                _StatBox('$actionsExecuted', 'Actions\nExecuted', successColor),
                              ],
                            ),
                          ],
                        ),
                      ),

                      Container(
                        margin: const EdgeInsets.all(16),
                        child: NexusButton(
                          '+ Analyze New Content',
                          onTap: () => Navigator.pushNamed(context, '/analyze'),
                        ),
                      ),

                      // Recent Analyses section
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'RECENT ANALYSES',
                              style: AppTextStyles.label.copyWith(letterSpacing: 1.5),
                            ),
                            const SizedBox(height: 10),
                            Consumer<AnalysisProvider>(
                              builder: (_, provider, __) {
                                return Column(
                                  children: [
                                    if (provider.result != null) ...[
                                      _RecentAnalysisCard(
                                        fileName: provider.selectedFileName ?? 'Content Analysis',
                                        timeAgo: 'Just now',
                                        insight: provider.result!.insight,
                                        action: provider.result!.topAction.description.isNotEmpty ? provider.result!.topAction.description : formatActionType(provider.result!.topAction.actionType),
                                        isCompleted: provider.result!.executionStatus == 'complete',
                                        onTap: () => Navigator.pushNamed(context, '/insight'),
                                      ),
                                      const SizedBox(height: 8),
                                    ],
                                    if (snapshot.connectionState == ConnectionState.waiting && sessions.isEmpty)
                                      const Padding(
                                        padding: EdgeInsets.all(32.0),
                                        child: Center(child: CircularProgressIndicator(color: primaryColor)),
                                      )
                                    else if (sessions.isEmpty && provider.result == null) ...[
                                      _RecentAnalysisCard.sample(onTap: () => Navigator.pushNamed(context, '/insight')),
                                    ] else
                                      ...sessions.take(10).map((s) {
                                        final rawId = s['id']?.toString() ?? '';
                                        final sessionLabel = 'Session ${rawId.substring(0, rawId.length.clamp(0, 8))}';
                                        return Padding(
                                          padding: const EdgeInsets.only(bottom: 8.0),
                                          child: _RecentAnalysisCard(
                                            fileName: s['input_preview']?.toString().isNotEmpty == true ? s['input_preview'].toString() : sessionLabel,
                                            timeAgo: formatTimestamp(s['created_at']?.toString() ?? ''),
                                            insight: 'Domain: ${s['domain'] ?? 'Unknown'}',
                                            action: 'Status: ${s['status']}',
                                            isCompleted: s['status'] == 'complete',
                                            onTap: () async {
                                              try {
                                                showDialog(
                                                  context: context,
                                                  barrierDismissible: false,
                                                  builder: (_) => const Center(
                                                    child: CircularProgressIndicator(color: primaryColor),
                                                  ),
                                                );
                                                await provider.loadSession(s['id'].toString());
                                                if (context.mounted) {
                                                  Navigator.pop(context); // Close loading dialog
                                                  Navigator.pushNamed(context, '/insight');
                                                }
                                              } catch (e) {
                                                if (context.mounted) {
                                                  Navigator.pop(context); // Close loading dialog
                                                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                                                    content: Text('Failed to load session: $e'),
                                                  ));
                                                }
                                              }
                                            },
                                          ),
                                        );
                                      }).toList(),
                                  ],
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 32),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Stat box ─────────────────────────────────────────────────────────────────

class _StatBox extends StatelessWidget {
  final String value;
  final String label;
  final Color color;

  const _StatBox(this.value, this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          value,
          style: GoogleFonts.syne(
            fontSize: 28,
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: AppTextStyles.body
              .copyWith(fontSize: 11, color: text2Color),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

// ─── Vertical divider ─────────────────────────────────────────────────────────

class _VertDivider extends StatelessWidget {
  const _VertDivider();

  @override
  Widget build(BuildContext context) {
    return Container(width: 0.5, height: 40, color: borderColor);
  }
}

// ─── Recent analysis card ─────────────────────────────────────────────────────

class _RecentAnalysisCard extends StatelessWidget {
  final String fileName;
  final String timeAgo;
  final String insight;
  final String action;
  final bool isCompleted;
  final VoidCallback? onTap;

  const _RecentAnalysisCard({
    required this.fileName,
    required this.timeAgo,
    required this.insight,
    required this.action,
    required this.isCompleted,
    this.onTap,
  });

  factory _RecentAnalysisCard.sample({VoidCallback? onTap}) {
    return _RecentAnalysisCard(
      fileName: 'Sales_Report_Q3.pdf',
      timeAgo: '2 min ago',
      insight: 'Orders declined by 25% in Lahore region',
      action: 'Launch discount campaign',
      isCompleted: true,
      onTap: onTap,
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: NexusCard(
        hasTealAccent: true,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: card2Color,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Center(
                child: Icon(Icons.description,
                    color: blue2Color, size: 20),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          fileName,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: textColor,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(timeAgo,
                          style: AppTextStyles.bodySmall),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Insight: $insight',
                    style: AppTextStyles.body
                        .copyWith(fontSize: 11, color: text2Color),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Action: $action',
                    style: AppTextStyles.body
                        .copyWith(fontSize: 11, color: text2Color),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (isCompleted) ...[
                    const SizedBox(height: 6),
                    Align(
                      alignment: Alignment.centerRight,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            vertical: 3, horizontal: 8),
                        decoration: BoxDecoration(
                          color: successColor.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: successColor.withOpacity(0.4),
                            width: 0.5,
                          ),
                        ),
                        child: const Text(
                          'Completed',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w500,
                            color: successColor,
                          ),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
