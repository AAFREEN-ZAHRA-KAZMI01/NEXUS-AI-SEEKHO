import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/analysis_response.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/results/before_after_widget.dart';

class SimulationScreen extends StatefulWidget {
  const SimulationScreen({super.key});

  @override
  State<SimulationScreen> createState() => _SimulationScreenState();
}

class _SimulationScreenState extends State<SimulationScreen> {
  int _visibleLogCount = 0;
  bool _showResultButton = false;
  Timer? _timer;
  List<Map<String, String>> _logEntries = const [];

  static const List<Map<String, String>> _defaultEntries = [
    {'time': '09:41:02', 'type': 'success', 'msg': 'Campaign record created'},
    {'time': '09:41:03', 'type': 'success', 'msg': 'Discount code generated'},
    {'time': '09:41:04', 'type': 'info',    'msg': 'CRM query — customers matched'},
    {'time': '09:41:05', 'type': 'success', 'msg': 'SMS batch queued'},
    {'time': '09:41:06', 'type': 'success', 'msg': 'Push notifications dispatched'},
    {'time': '09:41:07', 'type': 'warning', 'msg': 'Email delivery rate: 89%'},
    {'time': '09:41:08', 'type': 'info',    'msg': 'Dashboard state updated'},
    {'time': '09:41:09', 'type': 'success', 'msg': 'Simulation complete'},
  ];

  @override
  void initState() {
    super.initState();
    final provider = context.read<AnalysisProvider>();
    final execLog = provider.result?.artifacts?.execLog ?? {};
    _logEntries = _buildEntries(execLog);
    _startTimer();
  }

  List<Map<String, String>> _buildEntries(Map<String, dynamic> execLog) {
    final entries = execLog['entries'];
    if (entries is List && entries.isNotEmpty) {
      return entries
          .whereType<Map>()
          .map<Map<String, String>>((e) => {
                'time': e['time']?.toString() ?? '',
                'type': e['type']?.toString() ?? 'info',
                'msg': e['msg']?.toString() ?? '',
              })
          .toList();
    }
    return _defaultEntries.toList();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(milliseconds: 700), (t) {
      if (!mounted) {
        t.cancel();
        return;
      }
      if (_visibleLogCount < _logEntries.length) {
        setState(() => _visibleLogCount++);
      } else {
        t.cancel();
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) setState(() => _showResultButton = true);
        });
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AnalysisProvider>();
    final result = provider.result;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Simulation', style: AppTextStyles.heading3),
            Text('Action execution in progress',
                style: AppTextStyles.bodySmall),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 0. Action selected card
            if (result != null) ...[
              NexusCard(
                borderColor: indigoColor.withOpacity(0.4),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ACTION SELECTED',
                      style: AppTextStyles.label
                          .copyWith(letterSpacing: 1.2),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: indigoColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: indigoColor.withOpacity(0.4),
                          width: 0.5,
                        ),
                      ),
                      child: Text(
                        formatActionType(result.topAction.actionType),
                        style: const TextStyle(
                          fontSize: 11,
                          color: indigoColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      result.topAction.description.isNotEmpty
                          ? result.topAction.description
                          : 'Executing top-ranked autonomous action',
                      style: AppTextStyles.body.copyWith(height: 1.5),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        Expanded(
                          child: _ScoreChip(
                            'Feasibility',
                            result.topAction.feasibilityScore,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _ScoreChip(
                            'Impact',
                            result.topAction.impactScore,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: _ScoreChip(
                            'Composite',
                            result.topAction.compositeScore,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],

            // 1. Execution log card
            NexusCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.settings,
                          color: text2Color, size: 16),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Execution Log — ${result != null ? formatActionType(result.topAction.actionType) : ''}',
                          style: AppTextStyles.body.copyWith(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: text2Color,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const _RunningBadge(),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Column(
                    children: List.generate(_visibleLogCount, (i) {
                      return _LogEntry(entry: _logEntries[i])
                          .animate()
                          .slideX(begin: 0.3, duration: 300.ms)
                          .fadeIn(duration: 300.ms);
                    }),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 12),

            // 2. Before/after state section
            Text('STATE CHANGE',
                style: AppTextStyles.label.copyWith(letterSpacing: 1.0)),
            const SizedBox(height: 8),
            if (result != null && result.delta.isNotEmpty)
              BeforeAfterWidget(
                delta: result.delta,
                before: result.beforeState,
                after: result.afterState,
              )
            else
              NexusCard(
                child: Row(
                  children: [
                    const Icon(Icons.check_circle_outline,
                        color: successColor, size: 18),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        result != null
                            ? 'State updated — no numeric KPI shift recorded for this action type.'
                            : 'Awaiting analysis result…',
                        style: AppTextStyles.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),

            // 2.1 Email Draft Card
            if (result != null && result.artifacts?.execLog['email_draft'] != null) ...[
              const SizedBox(height: 12),
              NexusCard(
                hasTealAccent: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.email, color: primaryColor, size: 16),
                        const SizedBox(width: 8),
                        Text(
                          'EMAIL GENERATED',
                          style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: successColor.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Text('Sent', style: TextStyle(color: successColor, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color(0xFF060910),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Subject: ${result.artifacts!.execLog['email_draft']['subject']}',
                            style: AppTextStyles.mono.copyWith(fontSize: 11, color: primaryColor),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            result.artifacts!.execLog['email_draft']['preview'],
                            style: AppTextStyles.mono.copyWith(fontSize: 11, color: text2Color, height: 1.5),
                            maxLines: 5,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // 2.2 Workflow Steps Card
            if (result != null && result.artifacts?.execLog['workflow_execution'] != null) ...[
              const SizedBox(height: 12),
              NexusCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('WORKFLOW EXECUTION', style: AppTextStyles.label.copyWith(letterSpacing: 1.2)),
                    const SizedBox(height: 8),
                    Text(
                      '${result.artifacts!.execLog['workflow_execution']['workflow_name']}',
                      style: AppTextStyles.heading4,
                    ),
                    const SizedBox(height: 10),
                    ...((result.artifacts!.execLog['workflow_execution']['steps'] as List?) ?? [])
                        .map((step) => _WorkflowStep(step: step))
                        .toList(),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Text('Total execution time', style: AppTextStyles.bodySmall),
                        const Spacer(),
                        Text(
                          '${result.artifacts!.execLog['workflow_execution']['total_duration_ms']}ms',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: primaryColor),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],

            // 3. Simulated API call card
            if (result != null) ...[
              const SizedBox(height: 12),
              Text(
                'SIMULATED API CALL',
                style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFF080810),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: borderColor, width: 0.5),
                ),
                child: Text(
                  _buildApiCallText(result),
                  style: AppTextStyles.mono.copyWith(
                    color: successColor,
                    fontSize: 11,
                    height: 1.6,
                  ),
                ),
              ),
            ],

            const SizedBox(height: 20),

            // 4. View results button (animated opacity + shimmer)
            AnimatedOpacity(
              opacity: _showResultButton ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 400),
              child: NexusButton(
                'View Results →',
                onTap: _showResultButton
                    ? () => Navigator.pushNamed(context, '/results')
                    : null,
              )
                  .animate(onPlay: (c) => c.repeat())
                  .shimmer(duration: const Duration(seconds: 2)),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

String _buildApiCallText(AnalysisResponse result) {
  final endpoint = result.topAction.apiEndpoint.isNotEmpty
      ? result.topAction.apiEndpoint
      : '/api/actions/execute';
  final payload = result.topAction.apiPayload.isNotEmpty
      ? result.topAction.apiPayload.entries
          .map((e) => '  "${e.key}": "${e.value}"')
          .join(',\n')
      : '  "action": "${result.topAction.actionType}",\n  "domain": "${result.domain}"';
  return 'POST $endpoint\n{\n$payload\n}';
}

// ── Private widgets ───────────────────────────────────────────────────────────

class _ScoreChip extends StatelessWidget {
  final String label;
  final double value;

  const _ScoreChip(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: card2Color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            value.toStringAsFixed(1),
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: primaryColor,
            ),
          ),
          const SizedBox(height: 2),
          Text(label, style: AppTextStyles.bodySmall),
        ],
      ),
    );
  }
}

class _RunningBadge extends StatelessWidget {
  const _RunningBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF2A1A1A),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: errorColor, width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: errorColor,
              shape: BoxShape.circle,
            ),
          )
              .animate(onPlay: (c) => c.repeat(reverse: true))
              .scaleXY(
                  begin: 0.6,
                  end: 1.2,
                  duration: 700.ms,
                  curve: Curves.easeInOut),
          Text(
            ' Running',
            style: AppTextStyles.label.copyWith(
              color: errorColor,
              fontSize: 10,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _LogEntry extends StatelessWidget {
  final Map<String, String> entry;
  const _LogEntry({required this.entry});

  static IconData _logIcon(String type) => switch (type) {
        'success' => Icons.check,
        'warning' => Icons.warning_amber,
        _ => Icons.arrow_forward,
      };

  static Color _logColor(String type) => switch (type) {
        'success' => successColor,
        'warning' => warningColor,
        _ => primaryColor,
      };

  @override
  Widget build(BuildContext context) {
    final type = entry['type'] ?? 'info';
    final color = _logColor(type);
    return Padding(
      padding: const EdgeInsets.only(bottom: 3),
      child: Row(
        children: [
          SizedBox(
            width: 58,
            child: Text(
              entry['time'] ?? '',
              style: AppTextStyles.mono
                  .copyWith(color: text3Color, fontSize: 11),
            ),
          ),
          const SizedBox(width: 4),
          Icon(_logIcon(type), size: 11, color: color),
          const SizedBox(width: 4),
          Expanded(
            child: Text(
              entry['msg'] ?? '',
              style: AppTextStyles.mono
                  .copyWith(color: color, fontSize: 11),
            ),
          ),
        ],
      ),
    );
  }
}

class _WorkflowStep extends StatelessWidget {
  final Map<String, dynamic> step;

  const _WorkflowStep({required this.step});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Container(
            width: 20,
            height: 20,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: successColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              '${step["step"]}',
              style: const TextStyle(fontSize: 10, color: successColor, fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              step["name"]?.toString() ?? '',
              style: const TextStyle(fontSize: 12, color: text2Color),
            ),
          ),
          Text(
            '${step["duration_ms"]}ms',
            style: AppTextStyles.mono.copyWith(fontSize: 10, color: text3Color),
          ),
          const SizedBox(width: 4),
          const Icon(Icons.check_circle, color: successColor, size: 14),
        ],
      ),
    );
  }
}

