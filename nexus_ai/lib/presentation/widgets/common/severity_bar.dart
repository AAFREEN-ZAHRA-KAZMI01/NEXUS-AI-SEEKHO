import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';

class SeverityBar extends StatelessWidget {
  final int severity;
  const SeverityBar({super.key, required this.severity});

  @override
  Widget build(BuildContext context) {
    final color = severity >= 7 ? errorColor
                : severity >= 5 ? warningColor
                : primaryColor;  // teal for low severity
    final label = severity >= 9 ? 'CRITICAL'
                : severity >= 7 ? 'HIGH'
                : severity >= 5 ? 'MEDIUM'
                : severity >= 3 ? 'LOW-MED' : 'LOW';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Text('Severity',
            style: GoogleFonts.dmSans(fontSize:12, color: text2Color)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: color.withOpacity(0.4))),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Text('$severity / 10',
                style: GoogleFonts.syne(
                  fontSize: 13, fontWeight: FontWeight.w700, color: color)),
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4)),
                child: Text(label,
                  style: GoogleFonts.dmSans(
                    fontSize: 9, fontWeight: FontWeight.w700, color: color,
                    letterSpacing: 0.5)),
              ),
            ]),
          ),
        ]),
        const SizedBox(height: 10),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: severity / 10,
            backgroundColor: card3Color,
            valueColor: AlwaysStoppedAnimation(color),
            minHeight: 8,
          ),
        ),
        const SizedBox(height: 6),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Low', style: GoogleFonts.dmSans(fontSize:10, color:text4Color)),
            Text('High', style: GoogleFonts.dmSans(fontSize:10, color:text4Color)),
          ],
        ),
      ],
    );
  }
}
