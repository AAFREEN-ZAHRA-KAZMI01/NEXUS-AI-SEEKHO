import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: bgColor,
      colorScheme: const ColorScheme.dark(
        primary:    primaryColor,
        secondary:  blueColor,
        surface:    surfaceColor,
        background: bgColor,
        error:      errorColor,
        onPrimary:  Colors.black,     // text ON teal button = black
        onSurface:  textColor,
        onBackground: textColor,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: surfaceColor,
        elevation: 0,
        centerTitle: false,
        systemOverlayStyle: SystemUiOverlayStyle.light,
        titleTextStyle: GoogleFonts.syne(
          color: textColor, fontSize: 16, fontWeight: FontWeight.w700),
        iconTheme: const IconThemeData(color: text2Color),
        actionsIconTheme: const IconThemeData(color: text2Color),
      ),
      cardColor: cardColor,
      dividerColor: borderColor,
      dividerTheme: const DividerThemeData(
        color: borderColor, thickness: 0.5, space: 0),

      // TextField theme — high visibility
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: card2Color,
        hintStyle: GoogleFonts.dmSans(color: text4Color, fontSize: 13),
        labelStyle: GoogleFonts.dmSans(color: text3Color),
        prefixIconColor: text3Color,
        suffixIconColor: text3Color,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderColor, width: 1)),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryColor, width: 1.5)),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: errorColor, width: 1)),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: errorColor, width: 1.5)),
      ),

      // Switch
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith((s) =>
          s.contains(MaterialState.selected) ? primaryColor : text3Color),
        trackColor: MaterialStateProperty.resolveWith((s) =>
          s.contains(MaterialState.selected)
            ? primaryColor.withOpacity(0.3) : card2Color),
      ),

      // Progress indicator
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: primaryColor,
        linearMinHeight: 4,
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: card2Color,
        contentTextStyle: GoogleFonts.dmSans(color: text2Color, fontSize: 13),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: const BorderSide(color: borderLight)),
        behavior: SnackBarBehavior.floating,
      ),

      fontFamily: GoogleFonts.dmSans().fontFamily,
    );
  }
}
