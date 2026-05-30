import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/constants/app_constants.dart';
import '../../../data/services/api_service.dart';
import '../../../data/models/watchlist_alert.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _apiService = ApiService();
  
  List<WatchlistAlert> _alerts = [];
  List<AlertHistoryItem> _history = [];
  
  bool _isLoadingAlerts = true;
  bool _isLoadingHistory = true;
  String? _alertsError;
  String? _historyError;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadAllData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadAllData() async {
    _loadAlerts();
    _loadHistory();
  }

  Future<void> _loadAlerts() async {
    setState(() {
      _isLoadingAlerts = true;
      _alertsError = null;
    });
    try {
      final alerts = await _apiService.getAlerts(AppConstants.deviceId);
      setState(() {
        _alerts = alerts;
        _isLoadingAlerts = false;
      });
    } catch (e) {
      setState(() {
        _alertsError = e.toString();
        _isLoadingAlerts = false;
      });
    }
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoadingHistory = true;
      _historyError = null;
    });
    try {
      final history = await _apiService.getAlertHistory(AppConstants.deviceId);
      setState(() {
        _history = history;
        _isLoadingHistory = false;
      });
    } catch (e) {
      setState(() {
        _historyError = e.toString();
        _isLoadingHistory = false;
      });
    }
  }

  Future<void> _toggleAlert(WatchlistAlert alert) async {
    try {
      final updated = await _apiService.toggleAlert(alert.id);
      setState(() {
        final index = _alerts.indexWhere((element) => element.id == alert.id);
        if (index != -1) {
          _alerts[index] = updated;
        }
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Alert "${alert.label}" is now ${updated.isActive ? 'Active' : 'Inactive'}',
            style: AppTextStyles.bodyMedium.copyWith(color: Colors.black),
          ),
          backgroundColor: primaryColor,
          duration: const Duration(seconds: 2),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to toggle alert: $e', style: AppTextStyles.bodyMedium),
          backgroundColor: errorColor,
        ),
      );
    }
  }

  Future<void> _deleteAlert(WatchlistAlert alert) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: surfaceColor,
        title: Text('Delete Alert', style: AppTextStyles.heading3),
        content: Text(
          'Are you sure you want to delete "${alert.label}"?',
          style: AppTextStyles.body,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('Cancel', style: AppTextStyles.bodyMedium.copyWith(color: text3Color)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text('Delete', style: AppTextStyles.bodyMedium.copyWith(color: errorColor)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _apiService.deleteAlert(alert.id);
        setState(() {
          _alerts.removeWhere((element) => element.id == alert.id);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Alert deleted successfully', style: AppTextStyles.bodyMedium.copyWith(color: Colors.black)),
            backgroundColor: primaryColor,
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete alert: $e', style: AppTextStyles.bodyMedium),
            backgroundColor: errorColor,
          ),
        );
      }
    }
  }

  Color _getDomainColor(String domain) {
    switch (domain.toLowerCase()) {
      case 'logistics':
        return Colors.orange;
      case 'business':
        return Colors.blue;
      case 'finance':
        return successColor;
      case 'policy':
        return Colors.purple;
      case 'healthcare':
        return errorColor;
      case 'urban':
        return Colors.teal;
      default:
        return primaryColor;
    }
  }

  String _getConditionDescription(WatchlistAlert alert) {
    switch (alert.conditionType) {
      case 'severity_above':
        return 'Notify when ${alert.domain} severity > ${alert.conditionValue}';
      case 'kpi_change':
        return 'Notify when ${alert.domain} KPI changes > ${alert.conditionValue}%';
      case 'domain_keyword':
        final kw = alert.keyword ?? alert.conditionValue;
        return 'Notify when keyword "$kw" appears in ${alert.domain} insight';
      default:
        return 'Custom trigger on ${alert.domain}';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 0,
        title: Text('Watchlist', style: AppTextStyles.brandLarge.copyWith(fontSize: 22)),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: primaryColor,
          labelColor: primaryColor,
          unselectedLabelColor: text3Color,
          labelStyle: AppTextStyles.heading4,
          indicatorSize: TabBarIndicatorSize.tab,
          tabs: const [
            Tab(text: 'Active Alerts', icon: Icon(Icons.notifications_active, size: 20)),
            Tab(text: 'Trigger History', icon: Icon(Icons.history, size: 20)),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.pushNamed(context, '/alerts/create');
          if (result == true) {
            _loadAlerts();
          }
        },
        backgroundColor: Colors.transparent,
        elevation: 8,
        child: Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: primaryGrad,
            boxShadow: [
              BoxShadow(
                color: primaryColor.withOpacity(0.4),
                blurRadius: 12,
                spreadRadius: 2,
              )
            ],
          ),
          child: const Icon(Icons.add, color: Colors.black, size: 28),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAlertsTab(),
          _buildHistoryTab(),
        ],
      ),
    );
  }

  Widget _buildAlertsTab() {
    if (_isLoadingAlerts) {
      return const Center(child: CircularProgressIndicator(color: primaryColor));
    }

    if (_alertsError != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, color: errorColor, size: 48),
              const SizedBox(height: 16),
              Text('Failed to load watchlist', style: AppTextStyles.heading3),
              const SizedBox(height: 8),
              Text(_alertsError!, style: AppTextStyles.bodySmall, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadAlerts,
                style: ElevatedButton.styleFrom(backgroundColor: cardColor),
                child: const Text('Try Again'),
              )
            ],
          ),
        ),
      );
    }

    if (_alerts.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: cardColor,
                  border: Border.all(color: borderColor, width: 2),
                ),
                child: Icon(Icons.notifications_none_outlined, color: text3Color, size: 48),
              ),
              const SizedBox(height: 24),
              Text('No Alerts Set', style: AppTextStyles.heading2),
              const SizedBox(height: 12),
              Text(
                'No alerts set — tap + to create your first watchlist',
                style: AppTextStyles.body,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadAlerts,
      color: primaryColor,
      backgroundColor: cardColor,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        itemCount: _alerts.length,
        itemBuilder: (ctx, index) {
          final alert = _alerts[index];
          final domColor = _getDomainColor(alert.domain);

          return Card(
            margin: const EdgeInsets.bottom: 16,
            color: cardColor,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: alert.isActive ? tealBorder : borderColor, width: 1.5),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: domColor.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: domColor.withOpacity(0.3)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              AppConstants.domainIcons[alert.domain.toLowerCase()] ?? '🔔',
                              style: const TextStyle(fontSize: 12),
                            ),
                            const SizedBox(width: 6),
                            Text(
                              alert.domain.toUpperCase(),
                              style: AppTextStyles.label.copyWith(
                                color: domColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          Switch(
                            value: alert.isActive,
                            onChanged: (_) => _toggleAlert(alert),
                            activeColor: primaryColor,
                            activeTrackColor: primaryColor.withOpacity(0.3),
                            inactiveThumbColor: text3Color,
                            inactiveTrackColor: Colors.black26,
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: errorColor, size: 22),
                            onPressed: () => _deleteAlert(alert),
                          )
                        ],
                      )
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    alert.label,
                    style: AppTextStyles.heading3.copyWith(
                      color: alert.isActive ? textColor : text3Color,
                      decoration: alert.isActive ? null : TextDecoration.lineThrough,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _getConditionDescription(alert),
                    style: AppTextStyles.body.copyWith(
                      color: alert.isActive ? text2Color : text4Color,
                    ),
                  ),
                  const Divider(color: borderColor, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Triggered ${alert.triggerCount} times',
                        style: AppTextStyles.bodySmall.copyWith(
                          color: alert.triggerCount > 0 ? warningColor : text3Color,
                          fontWeight: alert.triggerCount > 0 ? FontWeight.bold : null,
                        ),
                      ),
                      if (alert.lastTriggeredAt != null)
                        Text(
                          'Last: ${alert.lastTriggeredAt!.substring(0, 10)}',
                          style: AppTextStyles.bodySmall,
                        )
                      else
                        Text(
                          'Never triggered',
                          style: AppTextStyles.bodySmall.copyWith(fontStyle: FontStyle.italic),
                        ),
                    ],
                  )
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHistoryTab() {
    if (_isLoadingHistory) {
      return const Center(child: CircularProgressIndicator(color: primaryColor));
    }

    if (_historyError != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, color: errorColor, size: 48),
              const SizedBox(height: 16),
              Text('Failed to load history', style: AppTextStyles.heading3),
              const SizedBox(height: 8),
              Text(_historyError!, style: AppTextStyles.bodySmall, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadHistory,
                style: ElevatedButton.styleFrom(backgroundColor: cardColor),
                child: const Text('Try Again'),
              )
            ],
          ),
        ),
      );
    }

    if (_history.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: cardColor,
                  border: Border.all(color: borderColor, width: 2),
                ),
                child: Icon(Icons.history_toggle_off_outlined, color: text3Color, size: 48),
              ),
              const SizedBox(height: 24),
              Text('No Triggers Yet', style: AppTextStyles.heading2),
              const SizedBox(height: 12),
              Text(
                'When your alerts detect issues during pipeline execution, they will show up here.',
                style: AppTextStyles.body,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadHistory,
      color: primaryColor,
      backgroundColor: cardColor,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        itemCount: _history.length,
        itemBuilder: (ctx, index) {
          final item = _history[index];
          final domColor = _getDomainColor(item.domain);

          return Container(
            margin: const EdgeInsets.bottom: 12,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderColor),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: domColor.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    AppConstants.domainIcons[item.domain.toLowerCase()] ?? '🔔',
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              item.alertLabel,
                              style: AppTextStyles.heading4.copyWith(color: textColor),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 8),
                          if (item.triggeredAt != null)
                            Text(
                              item.triggeredAt!.substring(11, 16), // HH:MM
                              style: AppTextStyles.bodySmall,
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        item.triggerReason,
                        style: AppTextStyles.body.copyWith(color: text2Color, fontSize: 13),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          GestureDetector(
                            onTap: () {
                              Navigator.pushNamed(context, '/results', arguments: item.sessionId);
                            },
                            child: Row(
                              children: [
                                const Icon(Icons.analytics_outlined, color: primaryColor, size: 14),
                                const SizedBox(width: 4),
                                Text(
                                  'View Session',
                                  style: AppTextStyles.tealAccent.copyWith(fontSize: 12),
                                ),
                              ],
                            ),
                          ),
                          Text(
                            item.triggeredAt != null ? item.triggeredAt!.substring(0, 10) : '',
                            style: AppTextStyles.bodySmall.copyWith(fontSize: 10),
                          ),
                        ],
                      )
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
