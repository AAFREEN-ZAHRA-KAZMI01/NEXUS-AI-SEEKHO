import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';
import '../../widgets/common/bottom_nav_bar.dart';
import '../../providers/analysis_provider.dart';

class StateDiffScreen extends StatelessWidget {
  const StateDiffScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>? ?? {};
    final beforeState = args['beforeState'] as Map<String, dynamic>? ?? {};
    final afterState = args['afterState'] as Map<String, dynamic>? ?? {};
    final domain = args['domain'] as String? ?? 'Business';
    final actionTaken = args['actionTaken'] as String? ?? 'No action taken';

    final keys = {...beforeState.keys, ...afterState.keys}.toList();
    
    // Sort keys alphabetically for clean display
    keys.sort();

    int totalFieldsChanged = 0;
    for (final key in keys) {
      if (beforeState[key] != afterState[key]) {
        totalFieldsChanged++;
      }
    }

    return Scaffold(
      backgroundColor: bgColor,
      bottomNavigationBar: Consumer<AnalysisProvider>(
        builder: (_, provider, __) => NexusBottomNav(
          currentIndex: 1, // Highlight insight/analysis tab
          onTap: (i) => handleBottomNavTap(context, i, provider),
        ),
      ),
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'State Change — $domain',
          style: AppTextStyles.heading3,
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
                    // Muted action chip at the top
                    Container(
                      margin: const EdgeInsets.only(bottom: 20),
                      child: PillBadge(
                        'Action: $actionTaken',
                        type: PillType.indigo,
                      ),
                    ),

                    if (keys.isEmpty)
                      Center(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 40.0),
                          child: Text(
                            'No state variables to compare.',
                            style: AppTextStyles.body.copyWith(color: text3Color),
                          ),
                        ),
                      )
                    else
                      ...keys.map((key) {
                        final beforeVal = beforeState[key];
                        final afterVal = afterState[key];
                        final isChanged = beforeVal != afterVal;

                        Color afterColor = text3Color;
                        String? deltaText;

                        if (!isChanged) {
                          afterColor = text3Color; // Grey if unchanged
                        } else {
                          final beforeNum = num.tryParse(beforeVal?.toString() ?? '');
                          final afterNum = num.tryParse(afterVal?.toString() ?? '');

                          if (beforeNum != null && afterNum != null) {
                            if (afterNum > beforeNum) {
                              afterColor = successColor; // Green if numeric value increased
                            } else if (afterNum < beforeNum) {
                              afterColor = errorColor; // Red if numeric value decreased
                            } else {
                              afterColor = text3Color;
                            }
                            
                            // Delta calculation
                            final diff = afterNum - beforeNum;
                            final sign = diff >= 0 ? '+' : '';
                            if (beforeNum != 0) {
                              final pct = (diff / beforeNum.abs()) * 100;
                              deltaText = '$sign${diff.toStringAsFixed(1)} ($sign${pct.toStringAsFixed(1)}%)';
                            } else {
                              deltaText = '$sign${diff.toStringAsFixed(1)}';
                            }
                          } else {
                            afterColor = blue2Color; // Blue if value changed but direction is neutral
                          }
                        }

                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          child: NexusCard(
                            borderColor: isChanged ? borderLight : borderColor.withOpacity(0.4),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Expanded(
                                      flex: 3,
                                      child: Text(
                                        _toTitleCase(key),
                                        style: AppTextStyles.bodyMedium.copyWith(
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      flex: 3,
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: card2Color,
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        alignment: Alignment.center,
                                        child: Text(
                                          beforeVal?.toString() ?? 'N/A',
                                          style: AppTextStyles.bodySmall.copyWith(
                                            color: text3Color,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ),
                                    const Padding(
                                      padding: EdgeInsets.symmetric(horizontal: 6.0),
                                      child: Text(
                                        '→',
                                        style: TextStyle(
                                          color: text3Color,
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    Expanded(
                                      flex: 3,
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: isChanged ? afterColor.withOpacity(0.08) : card2Color,
                                          borderRadius: BorderRadius.circular(6),
                                          border: isChanged ? Border.all(color: afterColor.withOpacity(0.3), width: 0.8) : null,
                                        ),
                                        alignment: Alignment.center,
                                        child: Text(
                                          afterVal?.toString() ?? 'N/A',
                                          style: AppTextStyles.bodySmall.copyWith(
                                            color: afterColor,
                                            fontWeight: isChanged ? FontWeight.w600 : FontWeight.normal,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                if (deltaText != null)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 6.0),
                                    child: Row(
                                      children: [
                                        const Spacer(flex: 7),
                                        Expanded(
                                          flex: 3,
                                          child: Align(
                                            alignment: Alignment.center,
                                            child: Text(
                                              deltaText,
                                              style: GoogleFonts.dmSans(
                                                fontSize: 10,
                                                fontWeight: FontWeight.w600,
                                                color: afterColor,
                                              ),
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        );
                      }),
                  ],
                ),
              ),
            ),
            // Bottom summary card
            Container(
              padding: const EdgeInsets.all(16.0),
              decoration: const BoxDecoration(
                color: surfaceColor,
                border: Border(
                  top: BorderSide(color: borderColor, width: 0.8),
                ),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Action applied: $actionTaken',
                              style: AppTextStyles.bodyMedium.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Total fields changed: $totalFieldsChanged',
                              style: AppTextStyles.bodySmall.copyWith(
                                color: text3Color,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: primaryColor,
                          foregroundColor: bgColor,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        ),
                        onPressed: () {
                          Navigator.pushNamed(context, '/trace');
                        },
                        child: Text(
                          'View full trace',
                          style: GoogleFonts.dmSans(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _toTitleCase(String text) {
    if (text.isEmpty) return '';
    return text.split('_').map((str) {
      if (str.isEmpty) return '';
      return str[0].toUpperCase() + str.substring(1);
    }).join(' ');
  }
}
