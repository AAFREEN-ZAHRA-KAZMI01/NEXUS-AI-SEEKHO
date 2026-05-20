import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';

class LiveLogView extends StatefulWidget {
  final List<String> logs;

  const LiveLogView({super.key, required this.logs});

  @override
  State<LiveLogView> createState() => _LiveLogViewState();
}

class _LiveLogViewState extends State<LiveLogView> {
  final _scrollController = ScrollController();

  @override
  void didUpdateWidget(LiveLogView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.logs.length != oldWidget.logs.length) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF060910),  // darker than bg
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Terminal header bar
          Row(children: [
            _dot(const Color(0xFFFF5F57)),   // red
            const SizedBox(width: 6),
            _dot(const Color(0xFFFFBD2E)),   // yellow
            const SizedBox(width: 6),
            _dot(const Color(0xFF28C840)),   // green
            const SizedBox(width: 12),
            Text('LIVE TRACE LOG',
              style: GoogleFonts.dmSans(
                fontSize: 10, color: text3Color, letterSpacing: 0.8)),
          ]),
          const SizedBox(height: 10),
          const Divider(color: Color(0xFF1A2438), height: 1),
          const SizedBox(height: 10),
          // Log lines - scrollable
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              itemCount: widget.logs.length,
              itemBuilder: (_, i) => _buildLogLine(widget.logs[i]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _dot(Color c) => Container(
    width: 10, height: 10,
    decoration: BoxDecoration(color: c, shape: BoxShape.circle));

  Widget _buildLogLine(String line) {
    Color msgColor = text2Color;
    if (line.contains('✓') || line.contains('ready') || line.contains('complete')) {
      msgColor = primaryColor;  // TEAL for success
    } else if (line.contains('→') || line.contains('running')) {
      msgColor = blueColor;
    } else if (line.contains('⚠') || line.contains('warning')) {
      msgColor = warningColor;
    }

    // Extract timestamp
    final tsMatch = RegExp(r'\[(\d{2}:\d{2}:\d{2})\]').firstMatch(line);
    final ts  = tsMatch?.group(1) ?? '';
    final msg = line.replaceAll(RegExp(r'\[\d{2}:\d{2}:\d{2}\]\s*'), '');

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (ts.isNotEmpty) ...[
            Text(ts,
              style: const TextStyle(
                fontFamily: 'Courier', fontSize: 11,
                color: text4Color)),
            const SizedBox(width: 10),
          ],
          Expanded(
            child: Text(msg,
              style: TextStyle(
                fontFamily: 'Courier', fontSize: 12,
                color: msgColor, height: 1.5)),
          ),
        ],
      ),
    );
  }
}
