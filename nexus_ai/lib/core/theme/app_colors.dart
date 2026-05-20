import 'package:flutter/material.dart';

// ── BACKGROUNDS ────────────────────────────────────────────────────────────
const Color bgColor      = Color(0xFF080B14);   // deep navy black — main bg
const Color surfaceColor = Color(0xFF0E1420);   // slightly lighter — surfaces
const Color cardColor    = Color(0xFF131C2E);   // card background
const Color card2Color   = Color(0xFF1A2438);   // elevated card
const Color card3Color   = Color(0xFF1F2B40);   // highest elevation card

// ── ACCENT — TEAL/CYAN (matches reference image) ───────────────────────────
const Color primaryColor  = Color(0xFF00E5CC);  // bright teal — main accent
const Color primary2Color = Color(0xFF00BFA5);  // slightly deeper teal
const Color primary3Color = Color(0xFF00FFF0);  // bright cyan glow
const Color accentGlow    = Color(0x3300E5CC);  // teal with 20% opacity

// ── SECONDARY ACCENT — ELECTRIC BLUE ──────────────────────────────────────
const Color blueColor     = Color(0xFF0EA5E9);  // sky blue
const Color blue2Color    = Color(0xFF38BDF8);  // light sky blue
const Color indigoColor   = Color(0xFF6366F1);  // indigo (keep for variety)

// ── SUPPORTING COLORS ──────────────────────────────────────────────────────
const Color purpleColor   = Color(0xFF8B5CF6);
const Color purple2Color  = Color(0xFFA78BFA);

// ── TEXT — HIGH CONTRAST ───────────────────────────────────────────────────
const Color textColor     = Color(0xFFFFFFFF);  // pure white — headings
const Color text2Color    = Color(0xFFCDD5E0);  // light grey — body
const Color text3Color    = Color(0xFF7A8BA0);  // medium grey — captions
const Color text4Color    = Color(0xFF4A5A6E);  // dim — placeholders

// ── BORDER — VISIBLE ───────────────────────────────────────────────────────
const Color borderColor   = Color(0xFF1E2D42);  // visible dark border
const Color borderLight   = Color(0xFF243348);  // slightly lighter border
const Color tealBorder    = Color(0x4400E5CC);  // teal border 27% opacity

// ── STATUS COLORS — BRIGHT ─────────────────────────────────────────────────
const Color successColor  = Color(0xFF10D982);  // bright green
const Color errorColor    = Color(0xFFFF4D6A);  // bright red-pink
const Color warningColor  = Color(0xFFFFB020);  // amber
const Color infoColor     = Color(0xFF0EA5E9);  // info blue

// ── GRADIENTS ──────────────────────────────────────────────────────────────
const LinearGradient primaryGrad = LinearGradient(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
  colors: [Color(0xFF00E5CC), Color(0xFF0EA5E9)],  // teal → blue
);

const LinearGradient grad2 = LinearGradient(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
  colors: [Color(0xFF0EA5E9), Color(0xFF6366F1)],  // blue → indigo
);

const LinearGradient darkGrad = LinearGradient(
  begin: Alignment.topCenter,
  end: Alignment.bottomCenter,
  colors: [Color(0xFF131C2E), Color(0xFF0E1420)],
);

const LinearGradient cardGrad = LinearGradient(
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
  colors: [Color(0xFF1A2438), Color(0xFF131C2E)],
);

// ── SHADOWS / GLOWS ────────────────────────────────────────────────────────
const List<BoxShadow> tealGlow = [
  BoxShadow(color: Color(0x4400E5CC), blurRadius: 20, spreadRadius: 0),
];
const List<BoxShadow> cardShadow = [
  BoxShadow(color: Color(0x40000000), blurRadius: 12, offset: Offset(0, 4)),
];
