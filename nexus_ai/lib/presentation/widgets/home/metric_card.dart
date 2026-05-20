import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final String delta;
  final Color deltaColor;
  final String emoji;

  const MetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.delta,
    required this.deltaColor,
    required this.emoji,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1A2438), Color(0xFF131C2E)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF243348), width: 0.8),
        boxShadow: const [
          BoxShadow(color: Color(0x30000000), blurRadius: 10, offset: Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Text(emoji, style: const TextStyle(fontSize: 18)),
            const Spacer(),
            Container(
              width: 8, height: 8,
              decoration: BoxDecoration(
                color: deltaColor,
                shape: BoxShape.circle,
                boxShadow: [BoxShadow(color: deltaColor.withOpacity(0.5),
                  blurRadius: 6)],
              ),
            ),
          ]),
          const SizedBox(height: 10),
          Text(
            value,
            style: GoogleFonts.syne(
              fontSize: 24, fontWeight: FontWeight.w700,
              color: Colors.white),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.dmSans(
              fontSize: 12, color: const Color(0xFF7A8BA0)),
          ),
          const SizedBox(height: 6),
          // Delta row with colored indicator
          Row(children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: deltaColor.withOpacity(0.12),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: deltaColor.withOpacity(0.3), width: 0.5),
              ),
              child: Text(
                delta,
                style: GoogleFonts.dmSans(
                  fontSize: 10, fontWeight: FontWeight.w600,
                  color: deltaColor),
              ),
            ),
          ]),
        ],
      ),
    );
  }
}
