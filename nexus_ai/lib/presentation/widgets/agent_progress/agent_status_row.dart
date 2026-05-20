import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../common/nexus_card.dart';
import '../common/pill_badge.dart';

enum AgentRowStatus { done, running, queued }

class AgentStatusRow extends StatefulWidget {
  final String agentName;
  final String subStatus;
  final AgentRowStatus rowStatus;

  const AgentStatusRow({
    super.key,
    required this.agentName,
    required this.subStatus,
    required this.rowStatus,
  });

  @override
  State<AgentStatusRow> createState() => _AgentStatusRowState();
}

class _AgentStatusRowState extends State<AgentStatusRow>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );
    if (widget.rowStatus == AgentRowStatus.running) _controller.repeat();
  }

  @override
  void didUpdateWidget(AgentStatusRow oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.rowStatus == AgentRowStatus.running) {
      _controller.repeat();
    } else {
      _controller.stop();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final borderC = switch (widget.rowStatus) {
      AgentRowStatus.done    => successColor,
      AgentRowStatus.running => primaryColor,
      AgentRowStatus.queued  => primaryColor.withOpacity(0.2),
    };
    final statusColor = switch (widget.rowStatus) {
      AgentRowStatus.done    => successColor,
      AgentRowStatus.running => primaryColor,
      AgentRowStatus.queued  => text2Color,
    };

    return NexusCard(
      borderColor: borderC,
      padding: const EdgeInsets.all(12),
      child: Row(
        children: [
          _buildStatusIcon(),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.agentName,
                  style: AppTextStyles.body.copyWith(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  widget.subStatus,
                  style: AppTextStyles.bodySmall.copyWith(color: statusColor),
                ),
              ],
            ),
          ),
          _buildPill(),
        ],
      ),
    );
  }

  Widget _buildStatusIcon() {
    final bg = switch (widget.rowStatus) {
      AgentRowStatus.done    => const Color(0xFF0F1F18),
      AgentRowStatus.running => const Color(0xFF1F1A2E),
      AgentRowStatus.queued  => cardColor,
    };
    final Widget icon = switch (widget.rowStatus) {
      AgentRowStatus.done    => const Icon(Icons.check, size: 14, color: successColor),
      AgentRowStatus.running => RotationTransition(
          turns: _controller,
          child: const Icon(Icons.refresh, size: 14, color: primaryColor),
        ),
      AgentRowStatus.queued  => const Icon(Icons.access_time, size: 14, color: text3Color),
    };

    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Center(child: icon),
    );
  }

  PillBadge _buildPill() => switch (widget.rowStatus) {
    AgentRowStatus.done    => const PillBadge('Done',    type: PillType.green),
    AgentRowStatus.running => const PillBadge('Running', type: PillType.blue),
    AgentRowStatus.queued  => const PillBadge('Queued',  type: PillType.grey),
  };
}
