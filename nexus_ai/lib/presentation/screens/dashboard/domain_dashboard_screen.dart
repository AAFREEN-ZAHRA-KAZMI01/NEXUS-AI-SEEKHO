import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_text_styles.dart';
import '../../../../data/services/api_service.dart';
import '../../../../data/models/domain_state_summary.dart';
import '../../../widgets/common/nexus_card.dart';

class DomainDashboardScreen extends StatefulWidget {
  const DomainDashboardScreen({super.key});

  @override
  State<DomainDashboardScreen> createState() => _DomainDashboardScreenState();
}

class _DomainDashboardScreenState extends State<DomainDashboardScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  String? _error;
  List<DomainStateSummary> _domains = [];

  @override
  void initState() {
    super.initState();
    _loadStates();
  }

  Future<void> _loadStates() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await _apiService.getAllDomainStates();
      final List<DomainStateSummary> loaded = [];
      data.forEach((key, value) {
        if (value is Map<String, dynamic>) {
          loaded.add(DomainStateSummary.fromJson(key, value));
        }
      });
      setState(() {
        _domains = loaded;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  IconData _getIcon(String domain) {
    switch (domain.toLowerCase()) {
      case 'logistics':
        return Icons.local_shipping;
      case 'finance':
        return Icons.bar_chart;
      case 'business':
        return Icons.business_center;
      case 'healthcare':
        return Icons.favorite;
      case 'policy':
        return Icons.description;
      case 'urban':
        return Icons.apartment;
      default:
        return Icons.help_outline;
    }
  }

  Color _getIconColor(String domain) {
    switch (domain.toLowerCase()) {
      case 'logistics':
        return blueColor;
      case 'finance':
        return successColor;
      case 'business':
        return primaryColor;
      case 'healthcare':
        return errorColor;
      case 'policy':
        return purpleColor;
      case 'urban':
        return warningColor;
      default:
        return Colors.white;
    }
  }

  String _formatMetricKey(String key) {
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .map((str) => str.isNotEmpty ? '${str[0].toUpperCase()}${str.substring(1)}' : '')
        .join(' ');
  }

  String _formatMetricValue(String key, dynamic value) {
    if (value == null) return '—';
    if (value is num) {
      String result = '';
      double numVal = value.toDouble();
      if (numVal.abs() >= 1000000) {
        result = '${(numVal / 1000000).toStringAsFixed(1)}M';
      } else if (numVal.abs() >= 1000) {
        result = '${(numVal / 1000).toStringAsFixed(1)}K';
      } else {
        result = value.toString();
        if (value is double) {
          result = value.toStringAsFixed(1);
        }
      }

      if (key.endsWith('_pct') || key.endsWith('_rate')) {
        result = '$result%';
      }
      if (key.endsWith('_pkr') || key.startsWith('pkr_') || key.contains('_revenue_')) {
        result = '₨$result';
      }
      return result;
    }
    return value.toString();
  }

  Color _getIndicatorColor(DomainStateSummary summary) {
    final domain = summary.domain.toLowerCase();
    final metrics = summary.metrics;

    if (domain == 'healthcare') {
      final shortages = metrics['critical_drug_shortage_count'] ?? 0;
      if (shortages > 0) return errorColor;
    } else if (domain == 'logistics') {
      final delayed = metrics['delayed_shipments'] ?? 0;
      if (delayed > 5) return errorColor;
      if (delayed > 2) return warningColor;
    } else if (domain == 'urban') {
      final faults = metrics['active_faults'] ?? 0;
      if (faults > 3) return errorColor;
      if (faults > 0) return warningColor;
    }

    // Default Amber logic: let's flag if any percentage metrics are low or high anomalies
    for (var entry in metrics.entries) {
      final k = entry.key.toLowerCase();
      final v = entry.value;
      if (v is num) {
        if (k.contains('compliance') && v < 85) return warningColor;
        if (k.contains('rate') && k.contains('on_time') && v < 90) return warningColor;
        if (k.contains('churn') && v > 5) return warningColor;
      }
    }

    return successColor;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        title: Text(
          'Domain States',
          style: GoogleFonts.syne(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadStates,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: primaryColor))
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('Error: $_error', style: const TextStyle(color: errorColor), textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadStates,
                          child: const Text('Retry'),
                        )
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  color: primaryColor,
                  backgroundColor: surfaceColor,
                  onRefresh: _loadStates,
                  child: GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 0.85,
                    ),
                    itemCount: _domains.length,
                    itemBuilder: (context, index) {
                      final item = _domains[index];
                      final topMetrics = item.metrics.entries.take(3).toList();
                      final indicatorColor = _getIndicatorColor(item);

                      return NexusCard(
                        onTap: () {
                          Navigator.pushNamed(
                            context,
                            '/dashboard/detail',
                            arguments: item,
                          );
                        },
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  _getIcon(item.domain),
                                  color: _getIconColor(item.domain),
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    item.domain.toUpperCase(),
                                    style: GoogleFonts.syne(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w700,
                                      color: Colors.white,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: indicatorColor,
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: indicatorColor.withOpacity(0.5),
                                        blurRadius: 4,
                                        spreadRadius: 1,
                                      )
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const Divider(color: borderColor, height: 16),
                            Expanded(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: topMetrics.map((m) {
                                  return Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        _formatMetricKey(m.key),
                                        style: AppTextStyles.bodySmall.copyWith(
                                          color: text3Color,
                                          fontSize: 10,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        _formatMetricValue(m.key, m.value),
                                        style: GoogleFonts.dmSans(
                                          fontSize: 13,
                                          fontWeight: FontWeight.bold,
                                          color: textColor,
                                        ),
                                      ),
                                    ],
                                  );
                                }).toList(),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
