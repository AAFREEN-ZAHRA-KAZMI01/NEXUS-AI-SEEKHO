import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

class InputModeTabs extends StatelessWidget {
  final String selected;
  final Function(String) onSelect;

  static const _items = [
    ('url', 'URL', Icons.link),
    ('text', 'Text', Icons.text_fields),
    ('file', 'File', Icons.attach_file),
  ];

  const InputModeTabs({
    super.key,
    required this.selected,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: _items.map((item) {
        final isSelected = item.$1 == selected;
        return Expanded(
          child: GestureDetector(
            onTap: () => onSelect(item.$1),
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 3),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isSelected ? card2Color : cardColor,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isSelected ? indigoColor : borderColor,
                  width: isSelected ? 1 : 0.5,
                ),
              ),
              child: Column(
                children: [
                  Icon(item.$3, size: 18, color: isSelected ? blue2Color : text3Color),
                  const SizedBox(height: 4),
                  Text(
                    item.$2,
                    style: AppTextStyles.label.copyWith(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: isSelected ? blue2Color : text3Color,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
