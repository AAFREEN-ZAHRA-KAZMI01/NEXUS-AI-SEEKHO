import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/analysis_provider.dart';
import '../../../core/theme/app_colors.dart';

void showNotificationsBottomSheet(BuildContext context) {
  final provider = Provider.of<AnalysisProvider>(context, listen: false);
  provider.markAllNotificationsAsRead();

  showModalBottomSheet(
    context: context,
    backgroundColor: bgColor,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (context) {
      return Consumer<AnalysisProvider>(
        builder: (context, ap, _) {
          final list = ap.notifications;
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
            height: 400,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.notifications_active, color: primaryColor, size: 22),
                        const SizedBox(width: 8),
                        Text(
                          'System Notifications',
                          style: TextStyle(
                            color: textColor,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'Syne',
                          ),
                        ),
                      ],
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: text2Color, size: 20),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                if (list.isEmpty)
                  Expanded(
                    child: Container(
                      alignment: Alignment.center,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.notifications_none, color: text2Color, size: 40),
                          const SizedBox(height: 12),
                          Text(
                            'No new notifications',
                            style: TextStyle(color: text2Color, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  Expanded(
                    child: ListView.builder(
                      shrinkWrap: true,
                      itemCount: list.length,
                      itemBuilder: (context, index) {
                        final n = list[index];
                        final isWarning = n['type'] == 'warning';
                        final dt = n['timestamp'] as DateTime;
                        final timeStr = DateFormat('hh:mm a').format(dt);

                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: cardColor,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isWarning ? Colors.amber.withOpacity(0.3) : borderColor,
                              width: 0.5,
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: isWarning ? Colors.amber.withOpacity(0.1) : primaryColor.withOpacity(0.1),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  isWarning ? Icons.warning_amber_rounded : Icons.info_outline,
                                  color: isWarning ? Colors.amber : primaryColor,
                                  size: 18,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Expanded(
                                          child: Text(
                                            n['title'] ?? '',
                                            style: TextStyle(
                                              color: textColor,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 13,
                                            ),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                        Text(
                                          timeStr,
                                          style: TextStyle(
                                            color: text2Color,
                                            fontSize: 11,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      n['message'] ?? '',
                                      style: TextStyle(
                                        color: text2Color,
                                        fontSize: 12,
                                        height: 1.4,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
              ],
            ),
          );
        },
      );
    },
  );
}
