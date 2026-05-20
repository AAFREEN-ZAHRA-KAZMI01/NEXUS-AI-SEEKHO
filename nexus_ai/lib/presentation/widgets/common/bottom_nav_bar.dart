import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';
import '../../providers/analysis_provider.dart';
import '../../../data/services/api_service.dart';

void handleBottomNavTap(BuildContext context, int index, AnalysisProvider provider) {
  final currentRoute = ModalRoute.of(context)?.settings.name;

  if (index == 0) {
    if (currentRoute != '/home') {
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    }
  } else if (index == 1) {
    if (provider.result != null) {
      if (currentRoute != '/insight') {
        Navigator.pushNamed(context, '/insight');
      }
    } else {
      _loadLatestAndNavigate(context, provider, '/insight');
    }
  } else if (index == 2) {
    if (provider.result != null) {
      if (currentRoute != '/actions') {
        Navigator.pushNamed(context, '/actions');
      }
    } else {
      _loadLatestAndNavigate(context, provider, '/actions');
    }
  } else if (index == 3) {
    if (provider.result != null) {
      if (currentRoute != '/trace') {
        Navigator.pushNamed(context, '/trace');
      }
    } else {
      _loadLatestAndNavigate(context, provider, '/trace');
    }
  } else if (index == 4) {
    if (currentRoute != '/profile') {
      Navigator.pushNamed(context, '/profile');
    }
  }
}

Future<void> _loadLatestAndNavigate(BuildContext context, AnalysisProvider provider, String routeName) async {
  try {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(
        child: CircularProgressIndicator(color: primaryColor),
      ),
    );
    
    final sessions = await ApiService().getRecentSessions();
    if (context.mounted) {
      Navigator.pop(context); // Close loading dialog
    }
    
    if (sessions.isNotEmpty) {
      final latestSessionId = sessions.first['id'].toString();
      
      if (context.mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (_) => const Center(
            child: CircularProgressIndicator(color: primaryColor),
          ),
        );
      }
      
      await provider.loadSession(latestSessionId);
      
      if (context.mounted) {
        Navigator.pop(context); // Close loading dialog
        Navigator.pushNamed(context, routeName);
      }
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('No previous analysis sessions found. Please run an analysis first.')),
        );
      }
    }
  } catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading latest session: $e')),
      );
    }
  }
}

class NexusBottomNav extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const NexusBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final items = [
      (Icons.home_outlined,         Icons.home,         'Home'),
      (Icons.lightbulb_outline,     Icons.lightbulb,    'Insights'),
      (Icons.bolt_outlined,         Icons.bolt,         'Actions'),
      (Icons.receipt_long_outlined, Icons.receipt_long, 'Logs'),
      (Icons.person_outline,        Icons.person,       'Profile'),
    ];

    return Container(
      decoration: BoxDecoration(
        color: surfaceColor,
        border: const Border(
          top: BorderSide(color: borderColor, width: 0.8)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.4),
            blurRadius: 20, offset: const Offset(0, -4)),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8)
        + EdgeInsets.only(bottom: MediaQuery.of(context).padding.bottom),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: items.asMap().entries.map((entry) {
          final i       = entry.key;
          final item    = entry.value;
          final active  = i == currentIndex;

          return GestureDetector(
            onTap: () => onTap(i),
            behavior: HitTestBehavior.opaque,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: active
                  ? primaryColor.withOpacity(0.12)
                  : Colors.transparent,
                borderRadius: BorderRadius.circular(12),
                border: active
                  ? Border.all(color: primaryColor.withOpacity(0.3), width: 0.5)
                  : null,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    active ? item.$2 : item.$1,
                    size: 22,
                    color: active ? primaryColor : text3Color,
                  ),
                  const SizedBox(height: 3),
                  Text(
                    item.$3,
                    style: GoogleFonts.dmSans(
                      fontSize: 10,
                      fontWeight: active ? FontWeight.w600 : FontWeight.w400,
                      color: active ? primaryColor : text3Color,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}
