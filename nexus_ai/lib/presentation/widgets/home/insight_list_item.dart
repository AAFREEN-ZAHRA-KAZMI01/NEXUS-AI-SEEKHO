import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/formatters.dart';
import '../common/nexus_card.dart';
import '../common/pill_badge.dart';

class InsightListItem extends StatelessWidget {
  final String title;
  final String subtitle;
  final int severity;
  final String timeAgo;
  final VoidCallback? onTap;

  const InsightListItem({
    super.key,
    required this.title,
    required this.subtitle,
    required this.severity,
    required this.timeAgo,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final borderC = severity >= 7
        ? errorColor
        : severity >= 5
            ? warningColor
            : tealBorder;

    final pillType = severity >= 7
        ? PillType.red
        : severity >= 5
            ? PillType.orange
            : PillType.teal;

    return NexusCard(
      borderColor: borderC,
      gradient: cardGrad,
      hasTealAccent: true,
      padding: EdgeInsets.zero,
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                PillBadge(
                  '${formatSeverityLabel(severity)} $severity/10',
                  type: pillType,
                ),
                const Spacer(),
                Text(
                  timeAgo,
                  style: GoogleFonts.dmSans(fontSize: 11, color: text3Color),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              title,
              style: GoogleFonts.dmSans(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: textColor,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: GoogleFonts.dmSans(
                fontSize: 12,
                color: text2Color,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.arrow_forward, size: 11, color: primaryColor),
                const SizedBox(width: 4),
                Text(
                  'View full report',
                  style: GoogleFonts.dmSans(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: primaryColor,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
