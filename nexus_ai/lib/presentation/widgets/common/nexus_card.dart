import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class NexusCard extends StatelessWidget {
  final Widget child;
  final Color? borderColor;
  final double radius;
  final EdgeInsets? padding;
  final Gradient? gradient;
  final Color? backgroundColor;
  final List<BoxShadow>? boxShadow;
  final VoidCallback? onTap;
  final bool hasTealAccent; // adds left teal border line

  const NexusCard({
    super.key,
    required this.child,
    this.borderColor,
    this.radius = 14,
    this.padding,
    this.gradient,
    this.backgroundColor,
    this.boxShadow,
    this.onTap,
    this.hasTealAccent = false,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveBorder = borderColor ?? borderLight;
    final effectiveBg     = backgroundColor ?? cardColor;
    final effectivePad    = padding ?? const EdgeInsets.all(16);

    Widget card = Container(
      decoration: BoxDecoration(
        gradient: gradient,
        color:    gradient == null ? effectiveBg : null,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: effectiveBorder, width: 0.8),
        boxShadow: boxShadow ?? cardShadow,
      ),
      padding: hasTealAccent
        ? EdgeInsets.zero
        : effectivePad,
      child: hasTealAccent
        ? ClipRRect(
            borderRadius: BorderRadius.circular(radius),
            child: IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(width: 3, color: primaryColor),
                  Expanded(child: Padding(padding: effectivePad, child: child)),
                ],
              ),
            ),
          )
        : child,
    );

    if (onTap != null) {
      return GestureDetector(onTap: onTap, child: card);
    }
    return card;
  }
}
