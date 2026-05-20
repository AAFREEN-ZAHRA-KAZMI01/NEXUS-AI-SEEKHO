import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';

enum NexusButtonVariant { gradient, outline }

class NexusButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  final bool isGradient;
  final bool isOutline;
  final bool isLoading;
  final double? width;
  final EdgeInsets? padding;

  const NexusButton(
    this.label, {
    super.key,
    this.onTap,
    this.isGradient = true,
    this.isOutline  = false,
    this.isLoading  = false,
    this.width,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final bool disabled = onTap == null && !isLoading;
    final effectivePad = padding
      ?? const EdgeInsets.symmetric(vertical: 16, horizontal: 20);

    Widget content = isLoading
      ? const SizedBox(
          width: 20, height: 20,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation(Colors.black),
          ))
      : Text(
          label,
          style: GoogleFonts.syne(
            fontSize: 15, fontWeight: FontWeight.w700,
            color: isOutline ? primaryColor : Colors.black),
          textAlign: TextAlign.center,
        );

    Widget button;

    if (isOutline) {
      button = Container(
        width: width ?? double.infinity,
        padding: effectivePad,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: primaryColor, width: 1.5),
          color: primaryColor.withOpacity(0.06),
        ),
        child: Center(child: content),
      );
    } else {
      button = Container(
        width: width ?? double.infinity,
        padding: effectivePad,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          gradient: const LinearGradient(
            colors: [Color(0xFF00E5CC), Color(0xFF0EA5E9)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          boxShadow: [
            BoxShadow(
              color: primaryColor.withOpacity(0.35),
              blurRadius: 16, offset: const Offset(0, 6)),
          ],
        ),
        child: Center(child: content),
      );
    }

    if (disabled) {
      return Opacity(opacity: 0.4, child: button);
    }

    return GestureDetector(
      onTap: isLoading ? null : onTap,
      child: button,
    );
  }
}
