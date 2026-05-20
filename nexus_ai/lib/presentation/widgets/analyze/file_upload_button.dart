import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/services/file_service.dart';
import '../common/nexus_card.dart';

class FileUploadButton extends StatelessWidget {
  final Function(String name, List<int> bytes, String type) onFilePicked;
  final String? fileName;
  final int? fileSize;
  final VoidCallback? onClear;

  const FileUploadButton({
    super.key,
    required this.onFilePicked,
    this.fileName,
    this.fileSize,
    this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    if (fileName == null) {
      return GestureDetector(
        onTap: () async {
          final file = await FileService.pickFile();
          if (file != null) {
            onFilePicked(file.name, file.bytes, file.inputType);
          }
        },
        child: CustomPaint(
          painter: _DashedBorderPainter(),
          child: SizedBox(
            width: double.infinity,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 32),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_upload, size: 32, color: primaryColor),
                  const SizedBox(height: 8),
                  Text(
                    'Tap to select file',
                    style: AppTextStyles.body.copyWith(
                      color: text2Color,
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text('PDF · DOCX · CSV · Excel', style: AppTextStyles.bodySmall),
                ],
              ),
            ),
          ),
        ),
      );
    }

    return NexusCard(
      child: Row(
        children: [
          const Icon(Icons.description, size: 20, color: primaryColor),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  fileName!,
                  style: AppTextStyles.body.copyWith(fontWeight: FontWeight.w500),
                  overflow: TextOverflow.ellipsis,
                ),
                if (fileSize != null)
                  Text(
                    FileService.formatFileSize(fileSize!),
                    style: AppTextStyles.bodySmall,
                  ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18, color: text3Color),
            onPressed: onClear,
          ),
        ],
      ),
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = primaryColor
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    const dashWidth = 6.0;
    const dashSpace = 4.0;

    final rrect = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, 0, size.width, size.height),
      const Radius.circular(14),
    );

    final path = Path()..addRRect(rrect);
    for (final metric in path.computeMetrics()) {
      double distance = 0;
      while (distance < metric.length) {
        final end = (distance + dashWidth).clamp(0.0, metric.length);
        canvas.drawPath(metric.extractPath(distance, end), paint);
        distance += dashWidth + dashSpace;
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
