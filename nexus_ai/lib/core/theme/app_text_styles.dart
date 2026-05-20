import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

class AppTextStyles {
  // Syne — headings
  static TextStyle brandLarge  = GoogleFonts.syne(
    fontSize: 30, fontWeight: FontWeight.w800, color: textColor,
    letterSpacing: -0.5);
  static TextStyle heading1    = GoogleFonts.syne(
    fontSize: 24, fontWeight: FontWeight.w700, color: textColor);
  static TextStyle heading2    = GoogleFonts.syne(
    fontSize: 20, fontWeight: FontWeight.w700, color: textColor);
  static TextStyle heading3    = GoogleFonts.syne(
    fontSize: 16, fontWeight: FontWeight.w600, color: textColor);
  static TextStyle heading4    = GoogleFonts.syne(
    fontSize: 14, fontWeight: FontWeight.w600, color: textColor);
  static TextStyle buttonLabel = GoogleFonts.syne(
    fontSize: 15, fontWeight: FontWeight.w700, color: Colors.black); // dark on teal btn
  static TextStyle metricValue = GoogleFonts.syne(
    fontSize: 26, fontWeight: FontWeight.w700, color: textColor);

  // DM Sans — body
  static TextStyle body        = GoogleFonts.dmSans(
    fontSize: 14, fontWeight: FontWeight.w400, color: text2Color, height: 1.6);
  static TextStyle bodyMedium  = GoogleFonts.dmSans(
    fontSize: 13, fontWeight: FontWeight.w500, color: text2Color);
  static TextStyle bodySmall   = GoogleFonts.dmSans(
    fontSize: 12, fontWeight: FontWeight.w400, color: text3Color);
  static TextStyle label       = GoogleFonts.dmSans(
    fontSize: 11, fontWeight: FontWeight.w600, color: text3Color,
    letterSpacing: 0.8);
  static TextStyle mono        = const TextStyle(
    fontFamily: 'Courier', fontSize: 12, color: primaryColor, height: 1.6);
  static TextStyle tealAccent  = GoogleFonts.dmSans(
    fontSize: 13, fontWeight: FontWeight.w600, color: primaryColor);
}
