import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/models/action_outcome.dart';
import '../../../data/services/api_service.dart';
import '../../widgets/common/bottom_nav_bar.dart';
import '../../providers/analysis_provider.dart';
import 'package:provider/provider.dart';

class OutcomeHistoryScreen extends StatefulWidget {
  const OutcomeHistoryScreen({super.key});

  @override
  State<OutcomeHistoryScreen> createState() => _OutcomeHistoryScreenState();
}

class _OutcomeHistoryScreenState extends State<OutcomeHistoryScreen> {
  String? _selectedDomain;
  List<ActionOutcome> _outcomes = [];
  OutcomeSummary? _summary;
  bool _loading = true;
  String? _error;

  static const List<String> _domainFilters = [
    'All',
    'Finance',
    'Logistics',
    'Healthcare',
    'Retail',
    'Energy',
    'Agriculture',
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final domain =
          (_selectedDomain == null || _selectedDomain == 'All') ? null : _selectedDomain!.toLowerCase();
      final results = await Future.wait([
        ApiService().getOutcomes(domain: domain),
        ApiService().getOutcomeSummary(),
      ]);
      if (!mounted) return;
      setState(() {
        _outcomes = results[0] as List<ActionOutcome>;
        _summary = results[1] as OutcomeSummary;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _loading = false;
      });
    }
  }

  void _onFilterChanged(String domain) {
    setState(() => _selectedDomain = domain == 'All' ? null : domain);
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      bottomNavigationBar: Consumer<AnalysisProvider>(
        builder: (_, provider, __) => NexusBottomNav(
          currentIndex: 3,
          onTap: (i) => handleBottomNavTap(context, i, provider),
        ),
      ),
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('Action History', style: AppTextStyles.heading3),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: textColor),
            tooltip: 'Refresh',
            onPressed: _load,
          ),
        ],
      ),
      body: RefreshIndicator(
        color: primaryColor,
        backgroundColor: cardColor,
        onRefresh: _load,
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(color: primaryColor),
              )
            : _error != null
                ? _ErrorState(message: _error!, onRetry: _load)
                : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // ── Summary cards ────────────────────────────────────
                      if (_summary != null) _SummaryRow(summary: _summary!),

                      const SizedBox(height: 20),

                      // ── Filter chips ─────────────────────────────────────
                      Text(
                        'FILTER BY DOMAIN',
                        style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
                      ),
                      const SizedBox(height: 10),
                      SizedBox(
                        height: 36,
                        child: ListView.separated(
                          scrollDirection: Axis.horizontal,
                          itemCount: _domainFilters.length,
                          separatorBuilder: (_, __) => const SizedBox(width: 8),
                          itemBuilder: (_, i) {
                            final d = _domainFilters[i];
                            final active = (_selectedDomain == null && d == 'All') ||
                                _selectedDomain == d;
                            return _FilterChip(
                              label: d,
                              active: active,
                              onTap: () => _onFilterChanged(d),
                            );
                          },
                        ),
                      ),

                      const SizedBox(height: 20),

                      // ── List ─────────────────────────────────────────────
                      if (_outcomes.isEmpty)
                        _EmptyState()
                      else
                        ...List.generate(_outcomes.length, (i) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: _OutcomeCard(
                              outcome: _outcomes[i],
                              onOutcomeRecorded: _load,
                            ),
                          );
                        }),

                      const SizedBox(height: 32),
                    ],
                  ),
      ),
    );
  }
}

// ── Summary row ──────────────────────────────────────────────────────────────

class _SummaryRow extends StatelessWidget {
  final OutcomeSummary summary;

  const _SummaryRow({required this.summary});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _SummaryCard(
            icon: Icons.bolt_outlined,
            iconColor: const Color(0xFF818CF8),
            value: '${summary.totalActionsRecommended}',
            label: 'Recommended',
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _SummaryCard(
            icon: Icons.check_circle_outline,
            iconColor: const Color(0xFF34D399),
            value: '${summary.totalConfirmed}',
            label: 'Confirmed',
            sub: '${summary.confirmationRatePct.toStringAsFixed(0)}%',
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _SummaryCard(
            icon: Icons.bar_chart_outlined,
            iconColor: const Color(0xFF60A5FA),
            value: '${summary.outcomesRecorded}',
            label: 'Outcomes',
          ),
        ),
      ],
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String value;
  final String label;
  final String? sub;

  const _SummaryCard({
    required this.icon,
    required this.iconColor,
    required this.value,
    required this.label,
    this.sub,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: borderColor, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: iconColor, size: 20),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                value,
                style: GoogleFonts.syne(
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: textColor,
                ),
              ),
              if (sub != null) ...[
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 3),
                  child: Text(
                    sub!,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Color(0xFF34D399),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ],
          ),
          Text(label, style: AppTextStyles.bodySmall),
        ],
      ),
    );
  }
}

// ── Filter chip ──────────────────────────────────────────────────────────────

class _FilterChip extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _FilterChip({
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: active ? const Color(0xFF6366F1) : cardColor,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: active ? const Color(0xFF6366F1) : borderColor,
            width: 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: active ? Colors.white : text2Color,
          ),
        ),
      ),
    );
  }
}

// ── Outcome card ─────────────────────────────────────────────────────────────

class _OutcomeCard extends StatelessWidget {
  final ActionOutcome outcome;
  final VoidCallback onOutcomeRecorded;

  const _OutcomeCard({
    required this.outcome,
    required this.onOutcomeRecorded,
  });

  @override
  Widget build(BuildContext context) {
    final statusInfo = _statusInfo(outcome);

    return Container(
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: borderColor, width: 0.5),
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row: domain chip + status badge
          Row(
            children: [
              _DomainChip(domain: outcome.domain),
              const SizedBox(width: 8),
              if (outcome.actionType.isNotEmpty)
                Expanded(
                  child: Text(
                    _formatActionType(outcome.actionType),
                    style: AppTextStyles.bodySmall.copyWith(color: text2Color),
                    overflow: TextOverflow.ellipsis,
                  ),
                )
              else
                const Spacer(),
              _StatusBadge(
                label: statusInfo['label']!,
                color: Color(int.parse(statusInfo['color']!)),
              ),
            ],
          ),

          const SizedBox(height: 10),

          // Recommended delta
          if (outcome.recommendedDelta.isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFF0F0F14),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.trending_up, color: Color(0xFF818CF8), size: 14),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      outcome.recommendedDelta,
                      style: AppTextStyles.body.copyWith(
                        fontSize: 13,
                        color: const Color(0xFFE0E0FF),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Actual outcome note
          if (outcome.hasOutcomeRecorded && outcome.actualOutcomeNote != null) ...[
            const SizedBox(height: 8),
            Text(
              '"${outcome.actualOutcomeNote}"',
              style: AppTextStyles.bodySmall.copyWith(
                fontStyle: FontStyle.italic,
                color: const Color(0xFF6B7280),
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ],

          // KPI + actual value row
          if (outcome.kpiName != null || outcome.actualValue != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                if (outcome.kpiName != null) ...[
                  const Icon(Icons.bar_chart, color: Color(0xFF60A5FA), size: 13),
                  const SizedBox(width: 4),
                  Text(
                    outcome.kpiName!,
                    style: AppTextStyles.bodySmall,
                  ),
                ],
                if (outcome.projectedValue != null) ...[
                  const SizedBox(width: 8),
                  Text(
                    'Projected: ${outcome.projectedValue!.toStringAsFixed(1)}',
                    style: AppTextStyles.bodySmall.copyWith(color: text2Color),
                  ),
                ],
                if (outcome.actualValue != null) ...[
                  const SizedBox(width: 8),
                  Text(
                    '→ Actual: ${outcome.actualValue!.toStringAsFixed(1)}',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: const Color(0xFF34D399),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ],
            ),
          ],

          // Record outcome button
          if (outcome.userConfirmed && !outcome.hasOutcomeRecorded) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => _showRecordSheet(context),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  side: const BorderSide(color: Color(0xFF60A5FA), width: 1),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child: const Text(
                  'Record Outcome',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF60A5FA),
                  ),
                ),
              ),
            ),
          ],

          // Timestamp
          const SizedBox(height: 8),
          Text(
            _formatDate(outcome.createdAt),
            style: AppTextStyles.bodySmall.copyWith(
              color: const Color(0xFF4B5563),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  Map<String, String> _statusInfo(ActionOutcome o) {
    if (o.hasOutcomeRecorded) {
      return {'label': 'Outcome recorded', 'color': '0xFF3B82F6'};
    } else if (o.userConfirmed) {
      return {'label': 'Confirmed', 'color': '0xFF34D399'};
    }
    return {'label': 'Skipped', 'color': '0xFF6B7280'};
  }

  String _formatActionType(String s) =>
      s.replaceAll('_', ' ').split(' ').map((w) {
        if (w.isEmpty) return w;
        return w[0].toUpperCase() + w.substring(1);
      }).join(' ');

  String _formatDate(String? iso) {
    if (iso == null) return '';
    try {
      final dt = DateTime.parse(iso).toLocal();
      return '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}  '
          '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return iso;
    }
  }

  void _showRecordSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _RecordOutcomeSheet(
        outcome: outcome,
        onSaved: () {
          Navigator.pop(context);
          onOutcomeRecorded();
        },
      ),
    );
  }
}

// ── Domain chip ──────────────────────────────────────────────────────────────

class _DomainChip extends StatelessWidget {
  final String domain;

  const _DomainChip({required this.domain});

  @override
  Widget build(BuildContext context) {
    final color = _domainColor(domain);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.4), width: 1),
      ),
      child: Text(
        domain[0].toUpperCase() + domain.substring(1),
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }

  Color _domainColor(String d) {
    switch (d.toLowerCase()) {
      case 'finance':
        return const Color(0xFF34D399);
      case 'logistics':
        return const Color(0xFF60A5FA);
      case 'healthcare':
        return const Color(0xFFF472B6);
      case 'retail':
        return const Color(0xFFFBBF24);
      case 'energy':
        return const Color(0xFFF97316);
      case 'agriculture':
        return const Color(0xFFA3E635);
      default:
        return const Color(0xFF818CF8);
    }
  }
}

// ── Status badge ─────────────────────────────────────────────────────────────

class _StatusBadge extends StatelessWidget {
  final String label;
  final Color color;

  const _StatusBadge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5), width: 1),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }
}

// ── Record outcome bottom sheet ───────────────────────────────────────────────

class _RecordOutcomeSheet extends StatefulWidget {
  final ActionOutcome outcome;
  final VoidCallback onSaved;

  const _RecordOutcomeSheet({required this.outcome, required this.onSaved});

  @override
  State<_RecordOutcomeSheet> createState() => _RecordOutcomeSheetState();
}

class _RecordOutcomeSheetState extends State<_RecordOutcomeSheet> {
  final _noteCtrl = TextEditingController();
  final _valueCtrl = TextEditingController();
  bool _saving = false;
  String? _saveError;

  @override
  void dispose() {
    _noteCtrl.dispose();
    _valueCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final note = _noteCtrl.text.trim();
    if (note.isEmpty) {
      setState(() => _saveError = 'Please describe what happened.');
      return;
    }
    setState(() {
      _saving = true;
      _saveError = null;
    });
    try {
      final raw = _valueCtrl.text.trim();
      final actualValue = raw.isEmpty ? null : double.tryParse(raw);
      await ApiService().recordOutcome(
        widget.outcome.id,
        note,
        actualValue: actualValue,
      );
      widget.onSaved();
    } catch (e) {
      setState(() {
        _saving = false;
        _saveError = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 28,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: const Color(0xFF374151),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          Text('Record Outcome', style: AppTextStyles.heading3),
          const SizedBox(height: 4),
          Text(
            'What actually happened after you applied this action?',
            style: AppTextStyles.bodySmall,
          ),

          const SizedBox(height: 20),

          // Note field
          TextField(
            controller: _noteCtrl,
            style: AppTextStyles.body.copyWith(fontSize: 13),
            maxLines: 3,
            decoration: InputDecoration(
              labelText: 'What actually happened?',
              labelStyle: AppTextStyles.bodySmall,
              filled: true,
              fillColor: const Color(0xFF0F0F14),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF2D2D3A)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF2D2D3A)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // Actual value field
          TextField(
            controller: _valueCtrl,
            style: AppTextStyles.body.copyWith(fontSize: 13),
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: InputDecoration(
              labelText: 'Actual value (optional)',
              labelStyle: AppTextStyles.bodySmall,
              hintText: 'e.g. 12.5',
              hintStyle: AppTextStyles.bodySmall.copyWith(color: const Color(0xFF4B5563)),
              filled: true,
              fillColor: const Color(0xFF0F0F14),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF2D2D3A)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF2D2D3A)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFF6366F1), width: 1.5),
              ),
            ),
          ),

          if (_saveError != null) ...[
            const SizedBox(height: 8),
            Text(
              _saveError!,
              style: const TextStyle(color: errorColor, fontSize: 12),
            ),
          ],

          const SizedBox(height: 20),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _saving ? null : _save,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6366F1),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _saving
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text(
                      'Save Outcome',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Empty / Error states ─────────────────────────────────────────────────────

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [
          const SizedBox(height: 40),
          const Icon(Icons.history_toggle_off, color: text3Color, size: 48),
          const SizedBox(height: 16),
          Text(
            'No actions tracked yet',
            style: AppTextStyles.body.copyWith(color: text2Color),
          ),
          const SizedBox(height: 8),
          Text(
            'After running an analysis, use the\n"Did you apply this action?" card to start tracking.',
            style: AppTextStyles.bodySmall.copyWith(color: text3Color),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorState({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [
          const SizedBox(height: 40),
          const Icon(Icons.error_outline, color: errorColor, size: 48),
          const SizedBox(height: 16),
          Text(message,
              style: AppTextStyles.bodySmall.copyWith(color: text2Color),
              textAlign: TextAlign.center),
          const SizedBox(height: 16),
          TextButton(
            onPressed: onRetry,
            child: const Text('Retry', style: TextStyle(color: primaryColor)),
          ),
        ],
      ),
    );
  }
}
