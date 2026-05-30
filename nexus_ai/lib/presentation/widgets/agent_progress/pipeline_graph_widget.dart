import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../../core/theme/app_colors.dart';

class PipelineGraphWidget extends StatelessWidget {
  final Map<String, String> agentStatuses;
  final Map<String, double?> agentTimes;

  const PipelineGraphWidget({
    super.key,
    required this.agentStatuses,
    required this.agentTimes,
  });

  bool _isAgentActive(String? status) {
    return status == 'running' || status == 'done' || status == 'failed';
  }

  @override
  Widget build(BuildContext context) {
    // Determine active states of downstream agents to animate connecting lines
    final bool ingestionActive = _isAgentActive(agentStatuses['ingestion']);
    final bool researchActive = _isAgentActive(agentStatuses['research']);
    final bool analysisActive = _isAgentActive(agentStatuses['analysis']);
    final bool decisionActive = _isAgentActive(agentStatuses['decision']);
    final bool executionActive = _isAgentActive(agentStatuses['execution']);

    return Center(
      child: SizedBox(
        width: 320,
        height: 480,
        child: Stack(
          children: [
            // Background line animations
            Positioned.fill(
              child: _PipelineLinesPainterWidget(
                ingestionActive: ingestionActive,
                researchActive: researchActive,
                analysisActive: analysisActive,
                decisionActive: decisionActive,
                executionActive: executionActive,
              ),
            ),
            // Orchestrator Node (Top, X: 160, Y: 40)
            Positioned(
              left: 120, // 160 - 80/2
              top: 10,   // 40 - 60/2
              child: _AgentNode(
                name: 'Orchestrator',
                status: agentStatuses['orchestrator'] ?? 'done',
                elapsedSeconds: agentTimes['orchestrator'],
                isOrchestrator: true,
              ),
            ),
            // Ingestion Agent Node (X: 80, Y: 140)
            Positioned(
              left: 40,  // 80 - 80/2
              top: 110,  // 140 - 60/2
              child: _AgentNode(
                name: 'Ingestion',
                status: agentStatuses['ingestion'] ?? 'pending',
                elapsedSeconds: agentTimes['ingestion'],
              ),
            ),
            // Research Agent Node (X: 240, Y: 140)
            Positioned(
              left: 200, // 240 - 80/2
              top: 110,  // 140 - 60/2
              child: _AgentNode(
                name: 'Research',
                status: agentStatuses['research'] ?? 'pending',
                elapsedSeconds: agentTimes['research'],
              ),
            ),
            // Analysis Agent Node (X: 160, Y: 240)
            Positioned(
              left: 120, // 160 - 80/2
              top: 210,  // 240 - 60/2
              child: _AgentNode(
                name: 'Analysis',
                status: agentStatuses['analysis'] ?? 'pending',
                elapsedSeconds: agentTimes['analysis'],
              ),
            ),
            // Decision Agent Node (X: 160, Y: 340)
            Positioned(
              left: 120, // 160 - 80/2
              top: 310,  // 340 - 60/2
              child: _AgentNode(
                name: 'Decision',
                status: agentStatuses['decision'] ?? 'pending',
                elapsedSeconds: agentTimes['decision'],
              ),
            ),
            // Execution Agent Node (X: 160, Y: 440)
            Positioned(
              left: 120, // 160 - 80/2
              top: 410,  // 440 - 60/2
              child: _AgentNode(
                name: 'Execution',
                status: agentStatuses['execution'] ?? 'pending',
                elapsedSeconds: agentTimes['execution'],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AgentNode extends StatelessWidget {
  final String name;
  final String status;
  final double? elapsedSeconds;
  final bool isOrchestrator;

  const _AgentNode({
    required this.name,
    required this.status,
    this.elapsedSeconds,
    this.isOrchestrator = false,
  });

  @override
  Widget build(BuildContext context) {
    // Build different card styles depending on status
    final bool isPending = status == 'pending';
    final bool isRunning = status == 'running';
    final bool isDone = status == 'done';
    final bool isFailed = status == 'failed';

    // Base card color and border color
    Color cardBg = cardColor;
    Color borderCol = borderColor;
    List<BoxShadow> glowEffects = const [];

    if (isOrchestrator) {
      // Orchestrator is always active and styled in grey
      borderCol = text3Color;
    } else if (isPending) {
      borderCol = borderColor;
    } else if (isFailed) {
      borderCol = errorColor;
      glowEffects = [
        BoxShadow(
          color: errorColor.withValues(alpha: 0.15),
          blurRadius: 6,
          spreadRadius: 1,
        )
      ];
    } else if (isDone) {
      borderCol = successColor;
    }

    Widget cardChild = Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Text(
            name,
            style: GoogleFonts.syne(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isPending ? text3Color : textColor,
            ),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(height: 4),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildStatusIcon(),
            if ((isDone || isFailed) && elapsedSeconds != null) ...[
              const SizedBox(width: 4),
              Text(
                '${elapsedSeconds!.toStringAsFixed(1)}s',
                style: GoogleFonts.syne(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: isFailed ? errorColor : successColor,
                ),
              ),
            ],
          ],
        ),
      ],
    );

    Widget nodeCard = Container(
      width: 80,
      height: 60,
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: borderCol, width: 1.5),
        boxShadow: glowEffects,
      ),
      child: cardChild,
    );

    // Apply animations depending on current state change
    if (isRunning && !isOrchestrator) {
      nodeCard = nodeCard
          .animate(onPlay: (controller) => controller.repeat(reverse: true))
          .custom(
            duration: 1000.ms,
            builder: (context, value, child) {
              return Container(
                width: 80,
                height: 60,
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: Color.lerp(borderColor, blueColor, value)!,
                    width: 1.5,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: blueColor.withValues(alpha: 0.3 * value),
                      blurRadius: 8 * value,
                      spreadRadius: 1 * value,
                    )
                  ],
                ),
                child: child,
              );
            },
          );
    } else if (isDone) {
      nodeCard = nodeCard
          .animate(key: ValueKey(status))
          .scale(
            begin: const Offset(0.85, 0.85),
            end: const Offset(1.0, 1.0),
            duration: 350.ms,
            curve: Curves.elasticOut,
          );
    }

    return nodeCard;
  }

  Widget _buildStatusIcon() {
    switch (status) {
      case 'running':
        return Container(
          width: 8,
          height: 8,
          decoration: const BoxDecoration(
            color: blueColor,
            shape: BoxShape.circle,
          ),
        )
            .animate(onPlay: (c) => c.repeat(reverse: true))
            .scaleXY(begin: 0.7, end: 1.3, duration: 600.ms);
      case 'done':
        return const Icon(
          Icons.check_circle_rounded,
          color: successColor,
          size: 12,
        );
      case 'failed':
        return const Icon(
          Icons.cancel_rounded,
          color: errorColor,
          size: 12,
        );
      case 'pending':
      default:
        return Container(
          width: 8,
          height: 8,
          decoration: const BoxDecoration(
            color: text4Color,
            shape: BoxShape.circle,
          ),
        );
    }
  }
}

class _PipelineLinesPainterWidget extends StatefulWidget {
  final bool ingestionActive;
  final bool researchActive;
  final bool analysisActive;
  final bool decisionActive;
  final bool executionActive;

  const _PipelineLinesPainterWidget({
    required this.ingestionActive,
    required this.researchActive,
    required this.analysisActive,
    required this.decisionActive,
    required this.executionActive,
  });

  @override
  State<_PipelineLinesPainterWidget> createState() => _PipelineLinesPainterWidgetState();
}

class _PipelineLinesPainterWidgetState extends State<_PipelineLinesPainterWidget>
    with TickerProviderStateMixin {
  late final AnimationController _ingestionController;
  late final AnimationController _researchController;
  late final AnimationController _analysisController;
  late final AnimationController _decisionController;
  late final AnimationController _executionController;

  @override
  void initState() {
    super.initState();
    _ingestionController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _researchController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _analysisController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _decisionController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _executionController = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));

    _updateControllers();
  }

  @override
  void didUpdateWidget(covariant _PipelineLinesPainterWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    _updateControllers();
  }

  void _updateControllers() {
    _toggleController(_ingestionController, widget.ingestionActive);
    _toggleController(_researchController, widget.researchActive);
    _toggleController(_analysisController, widget.analysisActive);
    _toggleController(_decisionController, widget.decisionActive);
    _toggleController(_executionController, widget.executionActive);
  }

  void _toggleController(AnimationController controller, bool active) {
    if (active) {
      controller.forward();
    } else {
      controller.reverse();
    }
  }

  @override
  void dispose() {
    _ingestionController.dispose();
    _researchController.dispose();
    _analysisController.dispose();
    _decisionController.dispose();
    _executionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        _ingestionController,
        _researchController,
        _analysisController,
        _decisionController,
        _executionController,
      ]),
      builder: (context, _) {
        return CustomPaint(
          painter: _PipelineLinesPainter(
            ingestionProgress: _ingestionController.value,
            researchProgress: _researchController.value,
            analysisProgress: _analysisController.value,
            decisionProgress: _decisionController.value,
            executionProgress: _executionController.value,
          ),
        );
      },
    );
  }
}

class _PipelineLinesPainter extends CustomPainter {
  final double ingestionProgress;
  final double researchProgress;
  final double analysisProgress;
  final double decisionProgress;
  final double executionProgress;

  _PipelineLinesPainter({
    required this.ingestionProgress,
    required this.researchProgress,
    required this.analysisProgress,
    required this.decisionProgress,
    required this.executionProgress,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final Paint bgPaint = Paint()
      ..color = borderColor.withValues(alpha: 0.4)
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke;

    final Paint activePaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke;

    // Node locations
    const Offset orchestratorBottom = Offset(160, 70);
    const Offset ingestionTop = Offset(80, 110);
    const Offset ingestionBottom = Offset(80, 170);
    const Offset researchTop = Offset(240, 110);
    const Offset researchBottom = Offset(240, 170);
    const Offset analysisTop = Offset(160, 210);
    const Offset analysisBottom = Offset(160, 270);
    const Offset decisionTop = Offset(160, 310);
    const Offset decisionBottom = Offset(160, 370);
    const Offset executionTop = Offset(160, 410);

    // 1. Orchestrator -> Ingestion line
    _drawLine(canvas, orchestratorBottom, ingestionTop, bgPaint, activePaint, ingestionProgress);

    // 2. Orchestrator -> Research line
    _drawLine(canvas, orchestratorBottom, researchTop, bgPaint, activePaint, researchProgress);

    // 3. Ingestion -> Analysis line
    _drawLine(canvas, ingestionBottom, analysisTop, bgPaint, activePaint, analysisProgress);

    // 4. Research -> Analysis line
    _drawLine(canvas, researchBottom, analysisTop, bgPaint, activePaint, analysisProgress);

    // 5. Analysis -> Decision line
    _drawLine(canvas, analysisBottom, decisionTop, bgPaint, activePaint, decisionProgress);

    // 6. Decision -> Execution line
    _drawLine(canvas, decisionBottom, executionTop, bgPaint, activePaint, executionProgress);
  }

  void _drawLine(Canvas canvas, Offset start, Offset end, Paint inactivePaint, Paint activePaint, double progress) {
    // Draw full inactive line
    canvas.drawLine(start, end, inactivePaint);

    // Draw active portion based on progress
    if (progress > 0) {
      final Offset activeEnd = Offset(
        start.dx + (end.dx - start.dx) * progress,
        start.dy + (end.dy - start.dy) * progress,
      );
      canvas.drawLine(start, activeEnd, activePaint);
    }
  }

  @override
  bool shouldRepaint(covariant _PipelineLinesPainter oldDelegate) {
    return oldDelegate.ingestionProgress != ingestionProgress ||
        oldDelegate.researchProgress != researchProgress ||
        oldDelegate.analysisProgress != analysisProgress ||
        oldDelegate.decisionProgress != decisionProgress ||
        oldDelegate.executionProgress != executionProgress;
  }
}
