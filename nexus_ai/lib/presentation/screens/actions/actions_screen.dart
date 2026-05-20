import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/analysis_response.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/gradient_text.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';
import '../../widgets/common/bottom_nav_bar.dart';

class ActionsScreen extends StatelessWidget {
  const ActionsScreen({super.key});

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
              title: Text('Recommended Actions',
                  style: AppTextStyles.heading3),
            ),
            body: Center(
              child: Text('No analysis result yet.',
                  style: AppTextStyles.body),
            ),
          );
        }

        final alternatives =
            result.alternativeActions.take(3).toList();

        return Scaffold(
          backgroundColor: bgColor,
          bottomNavigationBar: NexusBottomNav(
            currentIndex: 2,
            onTap: (i) => handleBottomNavTap(context, i, provider),
          ),
          appBar: AppBar(
            backgroundColor: bgColor,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: textColor),
              onPressed: () => Navigator.pop(context),
            ),
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Recommended Actions',
                    style: AppTextStyles.heading3),
                Text(
                  '${1 + result.alternativeActions.length} recommended · 1 auto-selected',
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. Top recommendation card
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        indigoColor.withOpacity(0.3),
                        purpleColor.withOpacity(0.3),
                      ],
                    ),
                    border:
                        Border.all(color: indigoColor, width: 0.5),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '⚡  TOP RECOMMENDATION',
                        style: AppTextStyles.label.copyWith(
                          fontSize: 11,
                          color: blue2Color,
                          letterSpacing: 1.0,
                        ),
                      ),
                      const SizedBox(height: 8),
                      GradientText(
                        text: formatActionType(
                            result.topAction.actionType),
                        style: AppTextStyles.heading3
                            .copyWith(fontSize: 14),
                        gradient: primaryGrad,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        result.topAction.justification,
                        style: AppTextStyles.body.copyWith(
                          color: text2Color,
                          fontSize: 12,
                        ),
                        maxLines: 4,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Expected: ${result.topAction.quantifiedDelta}',
                        style: AppTextStyles.bodySmall
                            .copyWith(color: successColor),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: NexusButton(
                              '▶ Execute Now',
                              onTap: () => Navigator.pushNamed(
                                  context, '/simulate'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: NexusButton(
                              'Simulate',
                              isOutline: true,
                              onTap: () => Navigator.pushNamed(
                                  context, '/simulate'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // 2. Section header
                Padding(
                  padding: const EdgeInsets.only(top: 20, bottom: 10),
                  child: Text('Alternative Actions',
                      style: AppTextStyles.heading3),
                ),

                // 3. Alternative actions
                ...List.generate(alternatives.length, (i) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _AltActionCard(alternatives[i], i),
                  );
                }),

                const SizedBox(height: 32),
              ],
            ),
          ),
        );
      },
    );
  }
}

// ── Private widgets ───────────────────────────────────────────────────────────

class _AltActionCard extends StatelessWidget {
  final TopAction action;
  final int index;

  const _AltActionCard(this.action, this.index);

  @override
  Widget build(BuildContext context) {
    final priorityLabel =
        index == 0 ? 'High' : index == 1 ? 'Med' : 'Low';
    final priorityType = index == 0
        ? PillType.red
        : index == 1
            ? PillType.orange
            : PillType.grey;

    return GestureDetector(
      onTap: () => _showDetails(context),
      child: NexusCard(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: card2Color,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Center(
                child: Text(
                  _actionEmoji(action.actionType),
                  style: const TextStyle(fontSize: 18),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    formatActionType(action.actionType),
                    style: AppTextStyles.body.copyWith(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: textColor,
                    ),
                  ),
                  Text(
                    action.justification,
                    style: AppTextStyles.bodySmall,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            PillBadge(priorityLabel, type: priorityType),
          ],
        ),
      ),
    );
  }

  void _showDetails(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: bgColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (_) => SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: NexusCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  formatActionType(action.actionType),
                  style: AppTextStyles.heading2,
                ),
                const SizedBox(height: 8),
                Text(action.justification, style: AppTextStyles.body),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Text('Feasibility:',
                        style: AppTextStyles.bodySmall),
                    const Spacer(),
                    Text(
                      '${action.feasibilityScore.toStringAsFixed(1)}/10',
                      style: AppTextStyles.body
                          .copyWith(color: blue2Color, fontSize: 13),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Text('Impact:', style: AppTextStyles.bodySmall),
                    const Spacer(),
                    Text(
                      '${action.impactScore.toStringAsFixed(1)}/10',
                      style: AppTextStyles.body.copyWith(
                          color: successColor, fontSize: 13),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Text('Composite:',
                        style: AppTextStyles.bodySmall),
                    const Spacer(),
                    Text(
                      action.compositeScore.toStringAsFixed(1),
                      style: AppTextStyles.body
                          .copyWith(color: textColor, fontSize: 13),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Success metric: ${action.successMetric}',
                  style: AppTextStyles.bodySmall,
                ),
                Text(
                  'Time to execute: ${action.timeToExecute}',
                  style: AppTextStyles.bodySmall,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _actionEmoji(String type) {
    final t = type.toLowerCase();
    if (t.contains('pricing') || t.contains('price')) return '💰';
    if (t.contains('campaign') || t.contains('crm')) return '📢';
    if (t.contains('hedge') || t.contains('finance')) return '📈';
    if (t.contains('compliance')) return '📋';
    if (t.contains('dispatch') || t.contains('crew')) return '🚨';
    return '⚡';
  }
}
