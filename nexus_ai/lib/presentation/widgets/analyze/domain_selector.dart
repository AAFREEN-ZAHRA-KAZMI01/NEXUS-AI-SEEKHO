import 'package:flutter/material.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';

class DomainSelector extends StatelessWidget {
  final String? selected;
  final Function(String?) onSelect;

  const DomainSelector({
    super.key,
    required this.selected,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('SELECT DOMAIN', style: AppTextStyles.label),
        const SizedBox(height: 10),
        GridView.count(
          crossAxisCount: 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
          childAspectRatio: 1.5,
          children: AppConstants.domains.map((domain) {
            return DomainChip(
              domain: domain,
              isSelected: selected == domain,
              onTap: () => onSelect(selected == domain ? null : domain),
            );
          }).toList(),
        ),
      ],
    );
  }
}

class DomainChip extends StatelessWidget {
  final String domain;
  final bool isSelected;
  final VoidCallback onTap;

  const DomainChip({
    super.key,
    required this.domain,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final emoji = AppConstants.domainIcons[domain] ?? '🔷';
    final label = AppConstants.domainLabels[domain] ?? domain;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0F1F18) : cardColor,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isSelected ? successColor : borderColor,
            width: isSelected ? 1 : 0.5,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 5),
            Text(
              label,
              style: AppTextStyles.label.copyWith(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isSelected ? successColor : text3Color,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
