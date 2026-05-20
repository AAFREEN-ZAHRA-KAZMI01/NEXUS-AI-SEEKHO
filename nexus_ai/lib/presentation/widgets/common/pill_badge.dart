import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

enum PillType { teal, blue, purple, green, red, orange, grey, indigo }

class PillBadge extends StatelessWidget {
  final String label;
  final PillType type;

  const PillBadge(this.label, {super.key, this.type = PillType.teal});

  @override
  Widget build(BuildContext context) {
    final colors = _getColors();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color:        colors.$1,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.$2, width: 0.8),
      ),
      child: Text(label,
        style: GoogleFonts.dmSans(
          fontSize: 11, fontWeight: FontWeight.w600, color: colors.$3)),
    );
  }

  (Color, Color, Color) _getColors() => switch (type) {
    PillType.teal   => (const Color(0xFF00E5CC).withOpacity(0.12),
                        const Color(0xFF00E5CC).withOpacity(0.5),
                        const Color(0xFF00E5CC)),
    PillType.blue   => (const Color(0xFF0EA5E9).withOpacity(0.12),
                        const Color(0xFF0EA5E9).withOpacity(0.5),
                        const Color(0xFF38BDF8)),
    PillType.green  => (const Color(0xFF10D982).withOpacity(0.12),
                        const Color(0xFF10D982).withOpacity(0.5),
                        const Color(0xFF10D982)),
    PillType.red    => (const Color(0xFFFF4D6A).withOpacity(0.12),
                        const Color(0xFFFF4D6A).withOpacity(0.5),
                        const Color(0xFFFF4D6A)),
    PillType.orange => (const Color(0xFFFFB020).withOpacity(0.12),
                        const Color(0xFFFFB020).withOpacity(0.5),
                        const Color(0xFFFFB020)),
    PillType.purple => (const Color(0xFF8B5CF6).withOpacity(0.12),
                        const Color(0xFF8B5CF6).withOpacity(0.5),
                        const Color(0xFFA78BFA)),
    PillType.indigo => (const Color(0xFF6366F1).withOpacity(0.12),
                        const Color(0xFF6366F1).withOpacity(0.5),
                        const Color(0xFFA5B4FC)),
    PillType.grey   => (const Color(0xFF243348),
                        const Color(0xFF2D3F57),
                        const Color(0xFF7A8BA0)),
  };
}
