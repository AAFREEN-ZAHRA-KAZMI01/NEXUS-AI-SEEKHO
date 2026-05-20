import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

class TimelineItem {
  final String emoji;
  final String title;
  final String agentName;
  final String time;
  final Color dotBgColor;

  const TimelineItem({
    required this.emoji,
    required this.title,
    required this.agentName,
    required this.time,
    required this.dotBgColor,
  });
}

class TimelineWidget extends StatelessWidget {
  final List<TimelineItem> items;

  const TimelineWidget({super.key, required this.items});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(items.length, (i) {
        final item = items[i];
        final isLast = i == items.length - 1;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                children: [
                  Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: item.dotBgColor,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text(item.emoji, style: const TextStyle(fontSize: 14)),
                    ),
                  ),
                  if (!isLast)
                    Container(width: 1, height: 32, color: borderColor),
                ],
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: textColor,
                      ),
                    ),
                    Text(item.agentName, style: AppTextStyles.bodySmall),
                  ],
                ),
              ),
              Text(item.time, style: AppTextStyles.bodySmall),
            ],
          ),
        );
      }),
    );
  }
}
