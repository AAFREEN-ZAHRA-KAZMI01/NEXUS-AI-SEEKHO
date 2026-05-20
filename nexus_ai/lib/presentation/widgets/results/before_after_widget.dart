import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../common/nexus_card.dart';
import '../common/pill_badge.dart';

class BeforeAfterWidget extends StatelessWidget {
  final Map<String, dynamic> delta;
  final Map<String, dynamic> before;
  final Map<String, dynamic> after;

  const BeforeAfterWidget({
    super.key,
    required this.delta,
    required this.before,
    required this.after,
  });

  @override
  Widget build(BuildContext context) {
    final rows = delta.entries.where((e) {
      if (e.value is! Map) return false;
      return (e.value as Map)['change_pct'] != null;
    }).toList();

    return NexusCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: rows.map((e) {
          final label = e.key
              .split('_')
              .map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}')
              .join(' ');
          final raw = (e.value as Map)['change_pct'];
          final pct = raw is num
              ? raw.toDouble()
              : double.tryParse(raw.toString()) ?? 0;

          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: AppTextStyles.bodySmall),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Text(
                      before[e.key]?.toString() ?? '—',
                      style: const TextStyle(fontSize: 15, color: errorColor),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 8),
                      child: Icon(Icons.arrow_forward, size: 12, color: text3Color),
                    ),
                    Text(
                      after[e.key]?.toString() ?? '—',
                      style: const TextStyle(fontSize: 15, color: successColor),
                    ),
                    const Spacer(),
                    ChangeChip(pct: pct),
                  ],
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

class ChangeChip extends StatelessWidget {
  final double pct;
  const ChangeChip({super.key, required this.pct});

  @override
  Widget build(BuildContext context) {
    return pct >= 0
        ? PillBadge('+${pct.toStringAsFixed(1)}%', type: PillType.green)
        : PillBadge('${pct.toStringAsFixed(1)}%', type: PillType.red);
  }
}
