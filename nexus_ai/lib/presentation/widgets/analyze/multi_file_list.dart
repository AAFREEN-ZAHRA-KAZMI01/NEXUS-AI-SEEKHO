import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/services/file_service.dart';
import '../common/nexus_card.dart';

class MultiFileList extends StatelessWidget {
  final List<String> fileNames;
  final List<int> fileSizes;
  final void Function(int) onRemove;
  final VoidCallback onAddMore;

  const MultiFileList({
    super.key,
    required this.fileNames,
    required this.fileSizes,
    required this.onRemove,
    required this.onAddMore,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${fileNames.length}/5 files selected',
              style: AppTextStyles.bodySmall.copyWith(color: text2Color),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 70,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: fileNames.length < 5 ? fileNames.length + 1 : fileNames.length,
            separatorBuilder: (context, index) => const SizedBox(width: 10),
            itemBuilder: (context, index) {
              if (index == fileNames.length) {
                // Add more button
                return GestureDetector(
                  onTap: onAddMore,
                  child: NexusCard(
                    borderColor: borderColor,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.add_circle_outline, color: blue2Color, size: 24),
                          const SizedBox(height: 4),
                          Text(
                            'Add File',
                            style: AppTextStyles.bodySmall.copyWith(color: blue2Color),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }

              // File chip
              return NexusCard(
                borderColor: blue2Color.withOpacity(0.4),
                child: Container(
                  width: 160,
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          color: card2Color,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Center(
                          child: Icon(Icons.description, color: blue2Color, size: 16),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              fileNames[index],
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w500,
                                color: textColor,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                            Text(
                              FileService.formatFileSize(fileSizes[index]),
                              style: const TextStyle(fontSize: 9, color: text3Color),
                            ),
                          ],
                        ),
                      ),
                      GestureDetector(
                        onTap: () => onRemove(index),
                        child: const Icon(Icons.close, size: 16, color: text3Color),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
