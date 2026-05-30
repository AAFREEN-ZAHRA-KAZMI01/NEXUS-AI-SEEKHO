import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/services/api_service.dart';
import '../../../data/services/websocket_service.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/agent_progress/pipeline_graph_widget.dart';

// ─── Agent step data ──────────────────────────────────────────────────────────

enum _StepState { pending, running, done, failed }

class _AgentStep {
  final String name;
  final String description;
  final IconData icon;
  _StepState state;
  double? elapsedSeconds; // set when transitioning to done/failed

  _AgentStep({
    required this.name,
    required this.description,
    required this.icon,
    this.state = _StepState.pending,
    this.elapsedSeconds,
  });
}

// Maps backend status string → index of the currently RUNNING agent (0-based).
// -1 means none running yet (pending), 5 means all done (complete).
const _kStatusToRunning = <String, int>{
  'pending':     -1,
  'ingesting':    0,  // agent 1 running
  'researching':  1,  // agent 1 done, agent 2 running
  'analysing':    2,  // 1+2 done, 3 running
  'deciding':     3,  // 1+2+3 done, 4 running
  'executing':    4,  // 1+2+3+4 done, 5 running
  'complete':     5,  // all done
  'failed':       5,  // treat as all done (error shown separately)
};

// ─── Screen ───────────────────────────────────────────────────────────────────

class AgentProgressScreen extends StatefulWidget {
  const AgentProgressScreen({super.key});

  @override
  State<AgentProgressScreen> createState() => _AgentProgressScreenState();
}

class _AgentProgressScreenState extends State<AgentProgressScreen> {
  late final AnalysisProvider _provider;
  bool _navigationScheduled = false;

  // Polling
  Timer? _pollTimer;
  String _lastStatus = '';

  // WebSocket
  final WebSocketService _webSocketService = WebSocketService();
  StreamSubscription? _wsSubscription;
  final List<Map<String, dynamic>> _wsLogs = [];

  // Per-agent step tracking
  late final List<_AgentStep> _steps;

  // Timestamps: when did each agent start?
  final List<DateTime?> _startedAt = List.filled(5, null);

  // Overall progress percentage (0.0 – 1.0)
  double _progressFraction = 0.0;

  @override
  void initState() {
    super.initState();
    _provider = context.read<AnalysisProvider>();
    _provider.addListener(_onProviderUpdate);

    _steps = [
      _AgentStep(
        name: 'Ingestion Agent',
        description: 'Parsing and extracting key facts',
        icon: Icons.input_rounded,
      ),
      _AgentStep(
        name: 'Research Agent',
        description: 'Gathering domain context',
        icon: Icons.travel_explore,
      ),
      _AgentStep(
        name: 'Analysis Agent',
        description: 'Quantifying KPI impact',
        icon: Icons.bar_chart_rounded,
      ),
      _AgentStep(
        name: 'Decision Agent',
        description: 'Ranking action candidates',
        icon: Icons.account_tree_outlined,
      ),
      _AgentStep(
        name: 'Execution Agent',
        description: 'Applying recommended action',
        icon: Icons.rocket_launch_outlined,
      ),
    ];

    // Start polling as soon as we have a session ID
    _startPolling();
    _startWebSocket();
  }

  void _startWebSocket() {
    final sessionId = _provider.currentSessionId;
    if (sessionId != null) {
      _wsSubscription = _webSocketService.connect(sessionId).listen((data) {
        if (mounted) {
          setState(() {
            _wsLogs.add(data);
          });
        }
      });
    }
  }

  // ── Polling ────────────────────────────────────────────────────────────

  void _startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 2), (_) => _poll());
    // Run first tick immediately
    _poll();
  }

  Future<void> _poll() async {
    final sessionId = _provider.currentSessionId;
    if (sessionId == null) return;

    try {
      final data = await ApiService().getSessionStatus(sessionId);
      final status = data['status'] as String? ?? 'pending';
      if (status == _lastStatus) return; // nothing changed
      _lastStatus = status;
      _applyStatus(status);
    } catch (_) {
      // Transient errors — ignore, keep polling
    }
  }

  void _applyStatus(String status) {
    final runningIdx = _kStatusToRunning[status] ?? -1;
    final now = DateTime.now();

    setState(() {
      for (int i = 0; i < _steps.length; i++) {
        if (i < runningIdx) {
          // Done
          if (_steps[i].state != _StepState.done) {
            if (_startedAt[i] != null) {
              _steps[i].elapsedSeconds =
                  now.difference(_startedAt[i]!).inMilliseconds / 1000.0;
            }
            _steps[i].state = _StepState.done;
          }
        } else if (i == runningIdx) {
          // Running
          if (_steps[i].state != _StepState.running) {
            _startedAt[i] = now;
            _steps[i].state = _StepState.running;
          }
        } else {
          // Still pending
          if (_steps[i].state == _StepState.pending) {
            // stay pending
          }
        }
      }

      // Handle terminal states
      if (status == 'complete') {
        for (int i = 0; i < _steps.length; i++) {
          if (_steps[i].state != _StepState.done) {
            if (_startedAt[i] != null) {
              _steps[i].elapsedSeconds =
                  now.difference(_startedAt[i]!).inMilliseconds / 1000.0;
            }
            _steps[i].state = _StepState.done;
          }
        }
        _progressFraction = 1.0;
        _pollTimer?.cancel();
      } else if (status == 'failed') {
        // Mark running agent as failed; rest stay pending
        for (int i = 0; i < _steps.length; i++) {
          if (_steps[i].state == _StepState.running) {
            _steps[i].state = _StepState.failed;
            if (_startedAt[i] != null) {
              _steps[i].elapsedSeconds =
                  now.difference(_startedAt[i]!).inMilliseconds / 1000.0;
            }
          }
        }
        _pollTimer?.cancel();
      } else {
        // Partial progress — runningIdx is 0-based, total 5 steps
        _progressFraction =
            runningIdx < 0 ? 0.0 : (runningIdx / 5.0).clamp(0.0, 1.0);
      }
    });
  }

  // ── Provider listener (handles overall complete/error from the API call) ──

  void _onProviderUpdate() {
    if (_provider.status == AnalysisStatus.complete && !_navigationScheduled) {
      // Make sure all steps are marked done
      _applyStatus('complete');
      _navigationScheduled = true;
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) Navigator.pushReplacementNamed(context, '/insight');
      });
    }
    if (_provider.status == AnalysisStatus.error && !_navigationScheduled) {
      _applyStatus('failed');
    }
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _wsSubscription?.cancel();
    _webSocketService.dispose();
    _provider.removeListener(_onProviderUpdate);
    super.dispose();
  }

  // ── Error helpers ─────────────────────────────────────────────────────

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

  void _showDockerDebugDialog() {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.developer_board, color: blue2Color, size: 22),
            const SizedBox(width: 8),
            Text('Backend Diagnostic',
                style: GoogleFonts.syne(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: textColor)),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _debugStep('1', 'Check Docker', 'Run "docker ps" — newsops-server must be listed.'),
              _debugStep('2', 'Start backend', '"docker-compose up --build -d" in the newsops/ dir.'),
              _debugStep('3', 'Verify health', 'Open http://localhost:8000/health in a browser.'),
              _debugStep('4', 'Check API key', 'Ensure GEMINI_API_KEY is set in newsops/.env.'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Dismiss', style: TextStyle(color: text3Color)),
          ),
        ],
      ),
    );
  }

  Widget _debugStep(String num, String title, String detail) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20, height: 20,
            decoration: const BoxDecoration(color: blue2Color, shape: BoxShape.circle),
            child: Center(
              child: Text(num,
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.white)),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: textColor)),
              const SizedBox(height: 2),
              Text(detail, style: const TextStyle(fontSize: 11, color: text3Color)),
            ]),
          ),
        ],
      ),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AnalysisProvider>();
    final isError = provider.status == AnalysisStatus.error;
    final isComplete = provider.status == AnalysisStatus.complete;
    final isQueued = provider.status == AnalysisStatus.queued;
    final pct = (_progressFraction * 100).round();

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
                isComplete
                    ? 'Analysis Complete'
                    : isError
                        ? 'Pipeline Failed'
                        : isQueued
                            ? 'Analysis Queued'
                            : 'AI Agents Working…',
                style: GoogleFonts.syne(
                    fontSize: 16, fontWeight: FontWeight.w700, color: textColor),
              ),
              Text(
                isComplete
                    ? 'Navigating to insights…'
                    : isError
                        ? 'An error occurred'
                        : isQueued
                            ? 'Processing will begin shortly'
                            : 'Please wait while we analyse',
                style: AppTextStyles.bodySmall,
              ),
            ],
          ),
          actions: [
            // LIVE pulse badge
            if (!isComplete && !isError && !isQueued)
              Container(
                margin: const EdgeInsets.only(right: 12),
                padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFF2A1A1A),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: errorColor, width: 0.5),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 6, height: 6,
                      decoration: const BoxDecoration(color: errorColor, shape: BoxShape.circle),
                    )
                        .animate(onPlay: (c) => c.repeat(reverse: true))
                        .scaleXY(begin: 0.6, end: 1.2, duration: 700.ms, curve: Curves.easeInOut),
                    Text(' LIVE',
                        style: AppTextStyles.label.copyWith(
                            color: errorColor, fontSize: 10, fontWeight: FontWeight.w500)),
                  ],
                ),
              ),
          ],
        ),

        body: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 40),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Overall progress bar ─────────────────────────────
                  NexusCard(
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Text('Overall Progress', style: AppTextStyles.body),
                            const Spacer(),
                            Text(
                              '$pct%',
                              style: GoogleFonts.syne(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                  color: isComplete ? successColor : primaryColor),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(6),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 600),
                            curve: Curves.easeOut,
                            child: LinearProgressIndicator(
                              value: _progressFraction,
                              backgroundColor: card2Color,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                  isComplete ? successColor : primaryColor),
                              minHeight: 8,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  if (isQueued) ...[
                    NexusCard(
                      borderColor: Colors.orangeAccent.withOpacity(0.5),
                      child: Row(
                        children: [
                          const Icon(Icons.access_time_filled, color: Colors.orangeAccent),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Your analysis is queued — processing will begin shortly.',
                              style: AppTextStyles.body.copyWith(color: Colors.orangeAccent),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // ── Agent pipeline steps ─────────────────────────────
                  Text('PIPELINE AGENTS',
                      style: AppTextStyles.label.copyWith(letterSpacing: 1.2)),
                  const SizedBox(height: 12),

                   PipelineGraphWidget(
                     agentStatuses: {
                       'orchestrator': 'done',
                       'ingestion': _steps[0].state.name,
                       'research': _steps[1].state.name,
                       'analysis': _steps[2].state.name,
                       'decision': _steps[3].state.name,
                       'execution': _steps[4].state.name,
                     },
                     agentTimes: {
                       'orchestrator': null,
                       'ingestion': _steps[0].elapsedSeconds,
                       'research': _steps[1].elapsedSeconds,
                       'analysis': _steps[2].elapsedSeconds,
                       'decision': _steps[3].elapsedSeconds,
                       'execution': _steps[4].elapsedSeconds,
                     },
                   ),

                  // ── WebSocket Live log ─────────────────────────────────────────
                  if (_wsLogs.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text('LIVE AGENT COMMENTARY',
                        style: AppTextStyles.label.copyWith(letterSpacing: 1.2)),
                    const SizedBox(height: 8),
                    Container(
                      height: 200,
                      decoration: BoxDecoration(
                        color: cardColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: borderColor, width: 0.5),
                      ),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(10),
                        reverse: true, // Auto-scrolls to bottom if we insert at 0
                        itemCount: _wsLogs.length,
                        itemBuilder: (_, i) {
                          final log = _wsLogs[_wsLogs.length - 1 - i];
                          final agent = log['agent'] ?? 'System';
                          final message = log['message'] ?? '';
                          final timestampStr = log['timestamp'] as String?;
                          String time = '';
                          if (timestampStr != null) {
                            try {
                              final dt = DateTime.parse(timestampStr).toLocal();
                              time = '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}:${dt.second.toString().padLeft(2, '0')}';
                            } catch (_) {}
                          }
                          
                          Color agentColor = text3Color;
                          switch (agent) {
                            case 'ingestion': agentColor = Colors.blue; break;
                            case 'research': agentColor = Colors.purple; break;
                            case 'analysis': agentColor = Colors.orange; break;
                            case 'decision': agentColor = Colors.teal; break;
                            case 'execution': agentColor = Colors.redAccent; break;
                          }

                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('[$time]', style: const TextStyle(fontSize: 10, color: text3Color, fontFamily: 'monospace')),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: agentColor.withOpacity(0.15),
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(color: agentColor.withOpacity(0.4), width: 0.5),
                                  ),
                                  child: Text(agent.toString().toUpperCase(), style: TextStyle(fontSize: 9, color: agentColor, fontWeight: FontWeight.bold)),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(message, style: const TextStyle(fontSize: 12, color: textColor)),
                                ),
                              ],
                            ).animate().fadeIn(duration: 300.ms),
                          );
                        },
                      ),
                    ),
                  ],

                  // ── Error card ───────────────────────────────────────
                  if (isError) ...[
                    const SizedBox(height: 20),
                    NexusCard(
                      borderColor: errorColor.withOpacity(0.8),
                      gradient: LinearGradient(colors: [
                        errorColor.withOpacity(0.06),
                        errorColor.withOpacity(0.06),
                      ]),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(children: [
                            const Icon(Icons.error_outline, color: errorColor, size: 20),
                            const SizedBox(width: 8),
                            Text('Pipeline Execution Error',
                                style: GoogleFonts.syne(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    color: errorColor)),
                          ]),
                          const SizedBox(height: 10),
                          Text(_shortenError(provider.errorMessage),
                              style: AppTextStyles.body.copyWith(
                                  fontSize: 12, color: text2Color)),
                          const SizedBox(height: 16),
                          const Divider(color: borderColor, height: 1),
                          const SizedBox(height: 12),
                          Column(children: [
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
                              onTap: _showDockerDebugDialog,
                              padding: const EdgeInsets.symmetric(
                                  vertical: 12, horizontal: 16),
                            ),
                          ]),
                        ],
                      ),
                    ),
                  ],

                  // ── Live log ─────────────────────────────────────────
                  if (provider.liveLogs.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    Text('LIVE TRACE LOG',
                        style: AppTextStyles.label.copyWith(letterSpacing: 1.2)),
                    const SizedBox(height: 8),
                    Container(
                      height: 140,
                      decoration: BoxDecoration(
                        color: cardColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: borderColor, width: 0.5),
                      ),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(10),
                        reverse: true,
                        itemCount: provider.liveLogs.length,
                        itemBuilder: (_, i) {
                          final log = provider.liveLogs[
                              provider.liveLogs.length - 1 - i];
                          return Text(
                            log,
                            style: const TextStyle(
                              fontSize: 10,
                              fontFamily: 'monospace',
                              color: text3Color,
                              height: 1.6,
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // ── Success overlay ──────────────────────────────────────
            if (isComplete)
              Positioned.fill(
                child: Container(
                  color: Colors.black.withOpacity(0.6),
                  child: Center(
                    child: const Icon(Icons.check_circle,
                            color: successColor, size: 64)
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

// ─── Individual agent step row ────────────────────────────────────────────────

class _AgentStepRow extends StatelessWidget {
  final _AgentStep step;
  final bool isLast;
  final int index;

  const _AgentStepRow({
    required this.step,
    required this.isLast,
    required this.index,
  });

  @override
  Widget build(BuildContext context) {
    const double iconBoxSize = 40.0;
    const double lineWidth   = 2.0;

    final Color stateColor = switch (step.state) {
      _StepState.done    => successColor,
      _StepState.running => primaryColor,
      _StepState.failed  => errorColor,
      _StepState.pending => borderColor,
    };

    final Color textCol = switch (step.state) {
      _StepState.done    => textColor,
      _StepState.running => primaryColor,
      _StepState.failed  => errorColor,
      _StepState.pending => text3Color,
    };

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Left column: icon + connector line ────────────────────
        SizedBox(
          width: iconBoxSize,
          child: Column(
            children: [
              // Icon box
              _buildIcon(stateColor),
              // Connector line
              if (!isLast)
                AnimatedContainer(
                  duration: const Duration(milliseconds: 400),
                  width: lineWidth,
                  height: 52,
                  decoration: BoxDecoration(
                    color: step.state == _StepState.done
                        ? successColor.withOpacity(0.5)
                        : borderColor.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(1),
                  ),
                ),
            ],
          ),
        ),

        const SizedBox(width: 12),

        // ── Right column: name, description, timer ────────────────
        Expanded(
          child: Padding(
            padding: EdgeInsets.only(bottom: isLast ? 0 : 12),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: step.state == _StepState.running
                    ? primaryColor.withOpacity(0.07)
                    : cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: step.state == _StepState.running
                      ? primaryColor.withOpacity(0.35)
                      : step.state == _StepState.done
                          ? successColor.withOpacity(0.2)
                          : borderColor.withOpacity(0.5),
                  width: 0.8,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Parallel badge for agents 1+2
                        if (index < 2 && step.state == _StepState.running)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: indigoColor.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(4),
                                border: Border.all(
                                    color: indigoColor.withOpacity(0.4),
                                    width: 0.5),
                              ),
                              child: const Text(
                                '⚡ PARALLEL',
                                style: TextStyle(
                                  fontSize: 9,
                                  fontWeight: FontWeight.w700,
                                  color: indigoColor,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ),
                          ),
                        Text(
                          step.name,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: textCol,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          step.description,
                          style: AppTextStyles.bodySmall.copyWith(
                            fontSize: 11,
                            color: step.state == _StepState.pending
                                ? text3Color
                                : text2Color,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Right-side status indicator
                  if (step.state == _StepState.running)
                    const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor:
                            AlwaysStoppedAnimation<Color>(primaryColor),
                      ),
                    )
                  else if (step.state == _StepState.done &&
                      step.elapsedSeconds != null)
                    Text(
                      '${step.elapsedSeconds!.toStringAsFixed(1)}s',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: successColor,
                      ),
                    )
                  else if (step.state == _StepState.failed &&
                      step.elapsedSeconds != null)
                    Text(
                      '${step.elapsedSeconds!.toStringAsFixed(1)}s',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: errorColor,
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildIcon(Color stateColor) {
    const double size = 40;

    if (step.state == _StepState.running) {
      return SizedBox(
        width: size,
        height: size,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Animated ring
            const SizedBox(
              width: size,
              height: size,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(primaryColor),
              ),
            ),
            Icon(step.icon, color: primaryColor, size: 18),
          ],
        ),
      );
    }

    if (step.state == _StepState.done) {
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [successColor, Color(0xFF059669)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: successColor.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: const Icon(Icons.check, color: Colors.white, size: 20),
      );
    }

    if (step.state == _StepState.failed) {
      return Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: errorColor.withOpacity(0.15),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: errorColor, width: 1),
        ),
        child: const Icon(Icons.close, color: errorColor, size: 20),
      );
    }

    // Pending
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: card2Color,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor, width: 0.6),
      ),
      child: Icon(step.icon, color: text3Color, size: 18),
    );
  }
}
