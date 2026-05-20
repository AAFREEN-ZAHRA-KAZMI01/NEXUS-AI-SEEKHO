import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/nexus_card.dart';

class WorkflowScreen extends StatefulWidget {
  const WorkflowScreen({super.key});

  @override
  State<WorkflowScreen> createState() => _WorkflowScreenState();
}

class _WorkflowScreenState extends State<WorkflowScreen> {
  int _tab = 0;

  static const List<Map<String, String>> _timelineEntries = [
    {'time': '10:00', 'title': 'Content ingested', 'agent': 'Ingest Agent'},
    {'time': '10:01', 'title': 'Insights extracted', 'agent': 'Analyzer Agent'},
    {'time': '10:02', 'title': 'Risk analysis completed', 'agent': 'Risk Agent'},
    {'time': '10:03', 'title': 'Impact assessment done', 'agent': 'Impact Agent'},
    {'time': '10:04', 'title': 'Actions planned', 'agent': 'Planner Agent'},
    {'time': '10:05', 'title': 'Simulation executed', 'agent': 'Execution Agent'},
    {'time': '10:06', 'title': 'Outcome logged', 'agent': 'Logger Agent'},
  ];

  @override
  Widget build(BuildContext context) {
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
            Text('Decision Flow', style: AppTextStyles.heading3),
            Text('Agent orchestration trace', style: AppTextStyles.bodySmall),
          ],
        ),
      ),
      body: Column(
        children: [
          // Tab switcher
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: borderColor, width: 0.5),
              ),
              child: Row(
                children: [
                  _TabButton(
                    label: 'Timeline',
                    isActive: _tab == 0,
                    onTap: () => setState(() => _tab = 0),
                  ),
                  _TabButton(
                    label: 'Decision Flow',
                    isActive: _tab == 1,
                    onTap: () => setState(() => _tab = 1),
                  ),
                ],
              ),
            ),
          ),

          Expanded(
            child: _tab == 0
                ? _buildTimeline()
                : _buildDecisionFlow(context),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeline() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'AGENT TIMELINE',
            style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
          ),
          const SizedBox(height: 12),
          ..._timelineEntries.asMap().entries.map((e) => _TimelineEntry(
                time: e.value['time']!,
                title: e.value['title']!,
                agent: e.value['agent']!,
                isLast: e.key == _timelineEntries.length - 1,
              )),
        ],
      ),
    );
  }

  Widget _buildDecisionFlow(BuildContext context) {
    final result = context.watch<AnalysisProvider>().result;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _DecisionFlowBox(
            label: 'Insight',
            icon: Icons.search,
            color: blueColor,
          ),
          const _DownArrow(),
          _DecisionFlowBox(
            label: 'Impact',
            icon: Icons.trending_up,
            color: purpleColor,
          ),
          const _DownArrow(),
          _DecisionFlowBox(
            label: 'Action',
            icon: Icons.bolt,
            color: indigoColor,
          ),
          const _DownArrow(),
          _DecisionFlowBox(
            label: 'Execution',
            icon: Icons.play_arrow,
            color: warningColor,
          ),
          const _DownArrow(),
          _DecisionFlowBox(
            label: 'Outcome',
            icon: Icons.check_circle_outline,
            color: successColor,
          ),
          const SizedBox(height: 20),
          NexusCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI REASONING',
                  style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
                ),
                const SizedBox(height: 8),
                Text(
                  result?.topAction.justification.isNotEmpty == true
                      ? result!.topAction.justification
                      : 'The AI agents analyzed the input content and identified key signals. Based on severity and impact scoring, the optimal action was selected and executed autonomously.',
                  style: AppTextStyles.body.copyWith(height: 1.6),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

// ── Tab button ─────────────────────────────────────────────────────────────────

class _TabButton extends StatelessWidget {
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _TabButton({
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isActive ? primaryColor.withOpacity(0.15) : Colors.transparent,
            borderRadius: BorderRadius.circular(9),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: isActive ? primaryColor : text3Color,
            ),
          ),
        ),
      ),
    );
  }
}

// ── Timeline entry ─────────────────────────────────────────────────────────────

class _TimelineEntry extends StatelessWidget {
  final String time;
  final String title;
  final String agent;
  final bool isLast;

  const _TimelineEntry({
    required this.time,
    required this.title,
    required this.agent,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 44,
          child: Padding(
            padding: const EdgeInsets.only(top: 1),
            child: Text(
              time,
              style: AppTextStyles.bodySmall.copyWith(color: text3Color),
            ),
          ),
        ),
        Column(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: const BoxDecoration(
                color: primaryColor,
                shape: BoxShape.circle,
              ),
            ),
            if (!isLast)
              Container(width: 1, height: 46, color: borderColor),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.body.copyWith(
                    color: textColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(agent, style: AppTextStyles.bodySmall),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// ── Decision flow box ──────────────────────────────────────────────────────────

class _DecisionFlowBox extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;

  const _DecisionFlowBox({
    required this.label,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.4), width: 0.8),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(width: 12),
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          const Spacer(),
          Icon(Icons.check_circle, color: color, size: 16),
        ],
      ),
    );
  }
}

// ── Down arrow ─────────────────────────────────────────────────────────────────

class _DownArrow extends StatelessWidget {
  const _DownArrow();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Center(
        child: Icon(Icons.keyboard_arrow_down, color: text3Color, size: 24),
      ),
    );
  }
}
