import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/agent_progress/live_log_view.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';

class AgentProgressScreen extends StatefulWidget {
  const AgentProgressScreen({super.key});

  @override
  State<AgentProgressScreen> createState() =>
      _AgentProgressScreenState();
}

class _AgentProgressScreenState extends State<AgentProgressScreen> {
  late final AnalysisProvider _provider;
  bool _navigationScheduled = false;

  @override
  void initState() {
    super.initState();
    _provider = context.read<AnalysisProvider>();
    _provider.addListener(_onProviderUpdate);
  }

  void _onProviderUpdate() {
    if (_provider.status == AnalysisStatus.complete &&
        !_navigationScheduled) {
      _navigationScheduled = true;
      Future.delayed(const Duration(milliseconds: 1500), () {
        if (mounted) {
          Navigator.pushReplacementNamed(context, '/insight');
        }
      });
    }
  }

  @override
  void dispose() {
    _provider.removeListener(_onProviderUpdate);
    super.dispose();
  }

  void _showDockerDebugDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.developer_board, color: blue2Color, size: 24),
            const SizedBox(width: 8),
            Text(
              'Docker & Backend Diagnostic',
              style: GoogleFonts.syne(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: textColor,
              ),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Please follow these steps to verify your backend is running:',
                style: AppTextStyles.body.copyWith(fontSize: 13, color: text2Color),
              ),
              const SizedBox(height: 12),
              _buildStepItem('1', 'Check Docker Container Status',
                  'Run "docker ps" to see if newsops-server is running.'),
              _buildStepItem('2', 'Start/Rebuild the Backend',
                  'Run "docker-compose up --build -d" in the project directory.'),
              _buildStepItem('3', 'Verify API Health',
                  'Open http://127.0.0.1:8000/health or http://localhost:8000/docs in your browser.'),
              _buildStepItem('4', 'Verify API Keys',
                  'Ensure OPENAI_API_KEY is correctly set in newsops/.env.'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text(
              'Dismiss',
              style: TextStyle(color: text3Color),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepItem(String num, String title, String detail) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: const BoxDecoration(
              color: blue2Color,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                num,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: textColor,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  detail,
                  style: const TextStyle(
                    fontSize: 11,
                    color: text3Color,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _shortenError(String? msg) {
    if (msg == null) return 'Unknown error occurred.';
    if (msg.contains('pipeline took too long')) {
      return 'Backend timeout — AI pipeline exceeded the time limit.';
    }
    if (msg.contains('Cannot reach backend') || msg.contains('Docker')) {
      return 'Cannot reach backend — is Docker running?';
    }
    const maxLen = 120;
    if (msg.length > maxLen) return '${msg.substring(0, maxLen)}…';
    return msg;
  }

  // step > index → done; step == index → running
  bool _isDone(int index, int step) => step > index;
  bool _isRunning(int index, int step) => step == index;

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AnalysisProvider>();
    final step = provider.agentProgressStep;
    final pct = (step / 6 * 100).round();

    // Build active agents list based on step
    final agents = <({String name, String task, bool isDone})>[];
    if (step >= 1) {
      agents.add((
        name: 'Analyzer Agent',
        task: 'Extracting key insights',
        isDone: step >= 2
      ));
    }
    if (step >= 2) {
      agents.add((
        name: 'Risk Agent',
        task: 'Analyzing potential impact',
        isDone: step >= 3
      ));
    }
    if (step >= 3) {
      agents.add((
        name: 'Planner Agent',
        task: 'Planning best actions',
        isDone: step >= 4
      ));
    }
    if (step >= 4) {
      agents.add((
        name: 'Execution Agent',
        task: 'Simulating execution',
        isDone: step >= 5
      ));
    }

    return PopScope(
      canPop: provider.status != AnalysisStatus.loading,
      child: Scaffold(
        backgroundColor: bgColor,
        appBar: AppBar(
          backgroundColor: bgColor,
          elevation: 0,
          automaticallyImplyLeading: false,
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'AI Agents are Working...',
                style: GoogleFonts.syne(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: textColor,
                ),
              ),
              Text(
                'Please wait while we analyze',
                style: AppTextStyles.bodySmall,
              ),
            ],
          ),
          actions: [
            Container(
              margin: const EdgeInsets.only(right: 12),
              padding: const EdgeInsets.symmetric(
                  vertical: 4, horizontal: 10),
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
                        curve: Curves.easeInOut,
                      ),
                  Text(
                    ' LIVE',
                    style: AppTextStyles.label.copyWith(
                      color: errorColor,
                      fontSize: 10,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        body: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── 1. Processing steps ─────────────────────────────
                  Text(
                    'PROCESSING STEPS',
                    style: AppTextStyles.label
                        .copyWith(letterSpacing: 1.2),
                  ),
                  const SizedBox(height: 10),
                  _ProcessStep(
                    label: 'Parsing Content',
                    isDone: _isDone(0, step),
                    isRunning: _isRunning(0, step),
                  ),
                  _ProcessStep(
                    label: 'Extracting Insights',
                    isDone: _isDone(1, step),
                    isRunning: _isRunning(1, step),
                  ),
                  _ProcessStep(
                    label: 'Impact Analysis',
                    isDone: _isDone(2, step),
                    isRunning: _isRunning(2, step),
                  ),
                  _ProcessStep(
                    label: 'Planning Actions',
                    isDone: _isDone(3, step),
                    isRunning: _isRunning(3, step),
                  ),
                  _ProcessStep(
                    label: 'Executing Simulation',
                    isDone: _isDone(4, step),
                    isRunning: _isRunning(4, step),
                  ),

                  // ── 2. Active agents ────────────────────────────────
                  if (agents.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text(
                      'ACTIVE AGENTS',
                      style: AppTextStyles.label
                          .copyWith(letterSpacing: 1.2),
                    ),
                    const SizedBox(height: 10),
                    ...agents.map((a) => _ActiveAgentRow(
                          name: a.name,
                          task: a.task,
                          isDone: a.isDone,
                        )),
                  ],

                  // ── 3. Overall progress ─────────────────────────────
                  const SizedBox(height: 16),
                  NexusCard(
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Text('Overall Progress',
                                style: AppTextStyles.body),
                            const Spacer(),
                            Text(
                              '$pct%',
                              style: GoogleFonts.syne(
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                                color: primaryColor,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: step / 6.0,
                            backgroundColor: card2Color,
                            valueColor:
                                const AlwaysStoppedAnimation<Color>(
                                    primaryColor),
                            minHeight: 8,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // ── 4. Live log (100 px) ───────────────────────────
                  const SizedBox(height: 16),
                  Text(
                    'LIVE TRACE LOG',
                    style: AppTextStyles.label
                        .copyWith(letterSpacing: 1.2),
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 160,
                    child: LiveLogView(logs: provider.liveLogs),
                  ),

                  // ── 5. Error state ─────────────────────────────────
                  if (provider.status == AnalysisStatus.error) ...[
                    const SizedBox(height: 16),
                    NexusCard(
                      borderColor: errorColor.withOpacity(0.8),
                      gradient: LinearGradient(
                        colors: [
                          errorColor.withOpacity(0.05),
                          errorColor.withOpacity(0.05),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.error_outline, color: errorColor, size: 20),
                              const SizedBox(width: 8),
                              Text(
                                'Pipeline Execution Error',
                                style: GoogleFonts.syne(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                  color: errorColor,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            _shortenError(provider.errorMessage),
                            style: AppTextStyles.body.copyWith(
                              fontSize: 12,
                              color: text2Color,
                            ),
                          ),
                          const SizedBox(height: 16),
                          const Divider(color: borderColor, height: 1),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              const Icon(Icons.help_outline, color: blue2Color, size: 16),
                              const SizedBox(width: 6),
                              Text(
                                'Troubleshooting Guide',
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: textColor,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'The system failed to reach the local analysis microservices. This usually means the dockerized backend API is offline or needs a restart.',
                            style: TextStyle(
                              fontSize: 11,
                              color: text3Color,
                              height: 1.4,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Column(
                            children: [
                              NexusButton(
                                'Back to Input',
                                onTap: () => Navigator.pop(context),
                                padding: const EdgeInsets.symmetric(
                                    vertical: 12, horizontal: 16),
                              ),
                              const SizedBox(height: 8),
                              NexusButton(
                                'Diagnostics & Debug',
                                isOutline: true,
                                onTap: () => _showDockerDebugDialog(context),
                                padding: const EdgeInsets.symmetric(
                                    vertical: 12, horizontal: 16),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],

                  const SizedBox(height: 40),
                ],
              ),
            ),

            // ── Success overlay ─────────────────────────────────────
            if (provider.status == AnalysisStatus.complete)
              Positioned.fill(
                child: Container(
                  color: Colors.black.withOpacity(0.65),
                  child: Center(
                    child: const Icon(
                      Icons.check_circle,
                      color: successColor,
                      size: 60,
                    )
                        .animate()
                        .scale(
                          begin: const Offset(0, 0),
                          end: const Offset(1, 1),
                          duration: 400.ms,
                          curve: Curves.elasticOut,
                        ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

// ─── Processing step row ──────────────────────────────────────────────────────

class _ProcessStep extends StatelessWidget {
  final String label;
  final bool isDone;
  final bool isRunning;

  const _ProcessStep({
    required this.label,
    required this.isDone,
    required this.isRunning,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 10),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: borderColor, width: 0.5),
        ),
      ),
      child: Row(
        children: [
          // Status indicator
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              gradient: isDone ? primaryGrad : null,
              color: isDone
                  ? null
                  : isRunning
                      ? primaryColor.withOpacity(0.2)
                      : card2Color,
              border: isRunning
                  ? Border.all(color: primaryColor, width: 1)
                  : null,
            ),
            child: Center(
              child: isDone
                  ? const Icon(Icons.check,
                      color: Colors.white, size: 16)
                  : isRunning
                      ? const Icon(Icons.hourglass_top,
                              color: primaryColor, size: 16)
                          .animate(onPlay: (c) => c.repeat())
                          .rotate(duration: 1000.ms)
                      : Container(
                          width: 16,
                          height: 16,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                                color: borderColor, width: 0.5),
                          ),
                        ),
            ),
          ),

          const SizedBox(width: 10),

          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: isDone
                    ? textColor
                    : isRunning
                        ? primaryColor
                        : text3Color,
              ),
            ),
          ),

          if (isDone)
            const Icon(Icons.check_circle,
                color: successColor, size: 16)
          else if (isRunning)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(primaryColor),
              ),
            ),
        ],
      ),
    );
  }
}

// ─── Active agent row ─────────────────────────────────────────────────────────

class _ActiveAgentRow extends StatelessWidget {
  final String name;
  final String task;
  final bool isDone;

  const _ActiveAgentRow({
    required this.name,
    required this.task,
    required this.isDone,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: NexusCard(
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    blueColor.withOpacity(0.7),
                    purpleColor.withOpacity(0.7),
                  ],
                ),
              ),
              child: const Center(
                child: Icon(Icons.smart_toy,
                    color: Colors.white, size: 18),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: textColor,
                    ),
                  ),
                  Text(task, style: AppTextStyles.bodySmall),
                ],
              ),
            ),
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: isDone ? successColor : primaryColor,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
