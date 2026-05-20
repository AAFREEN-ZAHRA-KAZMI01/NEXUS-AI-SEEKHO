import 'dart:math' show min;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:shimmer/shimmer.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/constants/api_constants.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/session_trace.dart';
import '../../../data/services/api_service.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';
import '../../widgets/common/pill_badge.dart';
import '../../widgets/common/bottom_nav_bar.dart';

class TraceScreen extends StatefulWidget {
  const TraceScreen({super.key});

  @override
  State<TraceScreen> createState() => _TraceScreenState();
}

class _TraceScreenState extends State<TraceScreen> {
  SessionTrace? _trace;
  bool _loading = true;
  String? _error;
  String? _sessionId;

  @override
  void initState() {
    super.initState();
    _loadTrace();
  }

  Future<void> _loadTrace() async {
    // Give context a tick to build so ModalRoute is available
    await Future.delayed(Duration.zero);
    
    if (!mounted) return;
    
    final argId = ModalRoute.of(context)?.settings.arguments as String?;
    final provider = context.read<AnalysisProvider>();
    _sessionId = argId ?? provider.currentSessionId;

    if (_sessionId == null) {
      if (!mounted) return;
      setState(() {
        _error = 'No session ID — run an analysis first';
        _loading = false;
      });
      return;
    }

    try {
      final trace = await ApiService().getSessionTrace(_sessionId!);
      if (!mounted) return;
      setState(() {
        _trace = trace;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  Future<void> _exportTrace() async {
    final url =
        '${ApiConstants.baseUrl}/api/session/$_sessionId/trace';
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
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
        title: Text('Agent Reasoning Trace',
            style: AppTextStyles.heading3),
        actions: [
          TextButton(
            onPressed: _sessionId != null ? _exportTrace : null,
            child: Text(
              'Export',
              style: AppTextStyles.body
                  .copyWith(color: blue2Color, fontSize: 13),
            ),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 5,
        itemBuilder: (_, __) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Shimmer.fromColors(
            baseColor: cardColor,
            highlightColor: card2Color,
            child: Container(
              height: 80,
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(14),
              ),
            ),
          ),
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.wifi_off, color: text3Color, size: 40),
              const SizedBox(height: 8),
              Text(_error!, style: AppTextStyles.body,
                  textAlign: TextAlign.center),
              const SizedBox(height: 16),
              NexusButton(
                'Retry',
                onTap: () {
                  setState(() {
                    _loading = true;
                    _error = null;
                    _trace = null;
                  });
                  _loadTrace();
                },
              ),
            ],
          ),
        ),
      );
    }

    final artifacts = _trace!.artifacts;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Full decision trail — every reasoning step recorded by Nexus AI',
            style: AppTextStyles.body.copyWith(color: text3Color),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ...List.generate(artifacts.length, (i) {
            final artifact = artifacts[i];
            final isLast = i == artifacts.length - 1;
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Timeline column
                  SizedBox(
                    width: 32,
                    child: Column(
                      children: [
                        Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: _agentDotBg(artifact.agentName),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Center(
                            child: Text(
                              _agentEmoji(artifact.agentName),
                              style:
                                  const TextStyle(fontSize: 13),
                            ),
                          ),
                        ),
                        if (!isLast)
                          Container(
                            width: 1,
                            height: 20,
                            color: borderColor,
                          ),
                      ],
                    ),
                  ),

                  const SizedBox(width: 10),

                  // Content card
                  Expanded(
                    child: NexusCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                  child: Text(
                                    _getAgentDisplayName(artifact.agentName),
                                    style: GoogleFonts.syne(
                                      fontSize: 13, fontWeight: FontWeight.w600, color: textColor),
                                  ),
                                ),
                                const SizedBox(width: 6),
                                PillBadge(
                                  _getAgentModel(artifact),
                                type: PillType.indigo,
                              ),
                              const SizedBox(width: 6),
                              Text(
                                formatTimestamp(artifact.createdAt),
                                style: AppTextStyles.bodySmall,
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          _ArtifactPreview(artifact: artifact),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              const Icon(Icons.check,
                                  color: successColor, size: 11),
                              const SizedBox(width: 4),
                              Text(
                                '✓ ${artifact.artifactType}.json',
                                style: AppTextStyles.label.copyWith(
                                  fontSize: 10,
                                  color: successColor,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

Color _agentDotBg(String name) {
  if (name.contains('orchestrator')) return const Color(0xFF1F1A2E);
  if (name.contains('execution')) return const Color(0xFF2A1A0F);
  return const Color(0xFF0F1F18);
}

String _agentEmoji(String name) {
  if (name.contains('orchestrator')) return '🎯';
  if (name.contains('ingestion')) return '📥';
  if (name.contains('analysis')) return '🔬';
  if (name.contains('decision')) return '⚖️';
  if (name.contains('research')) return '🔍';
  if (name.contains('execution')) return '⚡';
  return '🤖';
}

String _getAgentDisplayName(String agentName) {
  final key = agentName.replaceAll('_agent', '').trim().toLowerCase();
  const names = {
    'orchestrator': '🎯  Orchestrator Agent',
    'ingestion':    '📥  Ingestion Agent',
    'analysis':     '🔬  Analysis Agent',
    'decision':     '⚖️  Decision Agent',
    'research':     '🔍  Research Agent',
    'execution':    '⚡  Execution Agent',
  };
  return names[key] 
      ?? '🤖  ${formatAgentName(agentName)}';
}

String _getAgentModel(AgentArtifactItem artifact) {
  final contentModel = artifact.content['orchestrator_model']
      ?? artifact.content['model_used'];
  if (contentModel != null) return contentModel.toString();
  
  final key = artifact.agentName.replaceAll('_agent', '').trim();
  return AppConstants.agentModels[key] ?? 'Gemini 1.5 Pro';
}

// ── Private widgets ───────────────────────────────────────────────────────────

class _ArtifactPreview extends StatelessWidget {
  final AgentArtifactItem artifact;
  const _ArtifactPreview({required this.artifact});

  @override
  Widget build(BuildContext context) {
    final c = artifact.content;
    switch (artifact.artifactType) {
      case 'task_plan':
        final agents = (c['agents_to_spawn'] as List?)?.join(', ') ?? '';
        final domain = c['domain'] ?? '';
        final model  = c['orchestrator_model'] ?? 'Gemini 1.5 Pro';
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Domain detected: $domain', style: AppTextStyles.body),
          Text('Agents spawned: $agents', style: AppTextStyles.body),
          Text('Model: $model', style: AppTextStyles.bodySmall),
          Text('Parallel execution: ${c['parallel_execution']}', 
            style: AppTextStyles.bodySmall),
        ]);

      case 'signals':
        final facts = c['facts'] as List? ?? [];
        final confidence = c['confidence'] ?? 'medium';
        final entities = c['entities'] as Map? ?? {};
        final orgs = (entities['organizations'] as List?)?.join(', ') ?? 'None';
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${facts.length} facts extracted:', style: AppTextStyles.bodyMedium),
          ...facts.take(3).map((f) => Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('• ', style: AppTextStyles.body.copyWith(color: Colors.tealAccent)),
              Expanded(child: Text((f as Map)['text']?.toString() ?? '', style: AppTextStyles.bodySmall)),
            ]),
          )),
          const SizedBox(height: 6),
          Row(children: [
            Text('Confidence: ', style: AppTextStyles.bodySmall),
            PillBadge(confidence.toString().toUpperCase(),
              type: confidence == 'high' ? PillType.green
                  : confidence == 'medium' ? PillType.blue
                  : PillType.grey),
            const SizedBox(width: 8),
            Text('Orgs: $orgs', style: AppTextStyles.bodySmall),
          ]),
        ]);

      case 'impact':
        final severity = c['severity'] ?? 0;
        final label    = c['severity_label'] ?? '';
        final kpis     = c['kpis_affected'] as List? ?? [];
        final reasoning = c['reasoning_chain'] as List? ?? [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text('Severity: ', style: AppTextStyles.body),
            Text('$severity/10 — $label',
              style: GoogleFonts.syne(fontSize:13, fontWeight:FontWeight.w700,
                color: (severity as num)>=7 ? errorColor : severity>=5 ? warningColor : successColor)),
          ]),
          const SizedBox(height: 6),
          Text('KPIs affected: ${kpis.length}', style: AppTextStyles.bodySmall),
          if (reasoning.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text('Reasoning chain:', style: AppTextStyles.bodyMedium),
            Text(reasoning.first.toString(), style: AppTextStyles.bodySmall,
              maxLines: 2, overflow: TextOverflow.ellipsis),
          ],
        ]);

      case 'actions':
        final actions = c['actions'] as List? ?? [];
        final topAction = actions.isNotEmpty && actions.first is Map ? actions.first as Map : {};
        final summary = c['reasoning_summary'] ?? '';
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('${actions.length} actions ranked', style: AppTextStyles.body),
          if (topAction.isNotEmpty) ...[
            const SizedBox(height: 6),
            Row(children: [
              Text('#1: ', style: AppTextStyles.body.copyWith(color: Colors.tealAccent)),
              Expanded(child: Text(
                formatActionType(topAction['action_type']?.toString() ?? ''),
                style: AppTextStyles.bodyMedium)),
              Text('${(topAction['composite_score'] as num?)?.toStringAsFixed(1) ?? '0.0'}/10',
                style: const TextStyle(color: successColor, fontSize:12, fontWeight:FontWeight.w600)),
            ]),
          ],
          if (summary.toString().isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(summary.toString(), style: AppTextStyles.bodySmall,
              maxLines: 2, overflow: TextOverflow.ellipsis),
          ],
        ]);

      case 'context':
        final corroboration = c['corroboration'] ?? 'unconfirmed';
        final contextText = c['additional_context'] ?? '';
        final sources = c['recommended_sources'] as List? ?? [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text('Verification: ', style: AppTextStyles.body),
            PillBadge(corroboration.toString(),
              type: corroboration == 'confirmed' ? PillType.green
                  : corroboration.toString().contains('partial') ? PillType.orange
                  : PillType.grey),
          ]),
          if (contextText.toString().isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(contextText.toString(), style: AppTextStyles.bodySmall,
              maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
          if (sources.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text('Sources: ${sources.take(2).join(', ')}', style: AppTextStyles.bodySmall),
          ],
        ]);

      case 'master_brief':
        final insight   = c['insight'] ?? '';
        final severity  = c['severity'] ?? 0;
        final domain    = c['domain'] ?? '';
        final corroboration = c['corroboration'] ?? '';
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Domain: ${formatDomain(domain.toString())}', style: AppTextStyles.bodyMedium),
          const SizedBox(height: 4),
          Text(insight.toString(), style: AppTextStyles.body,
            maxLines: 3, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 6),
          Row(children: [
            Text('Severity: $severity/10  ', style: AppTextStyles.bodySmall),
            Text('Corroboration: $corroboration', style: AppTextStyles.bodySmall),
          ]),
        ]);

      case 'exec_log':
        final status  = c['execution_status'] ?? '';
        final actions = c['actions_taken'] as List? ?? [];
        final delta   = c['delta'] as Map? ?? {};
        final notifs  = c['notifications_sent'] as List? ?? [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text('Status: ', style: AppTextStyles.body),
            PillBadge(status == 'success' ? 'SUCCESS' : status.toString().toUpperCase(),
              type: status == 'success' ? PillType.green : PillType.red),
          ]),
          if (actions.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text('Actions taken:', style: AppTextStyles.bodyMedium),
            ...actions.map((a) => Text('• $a', style: AppTextStyles.bodySmall)),
          ],
          const SizedBox(height: 4),
          Text('State changes: ${delta.length} fields updated',
            style: AppTextStyles.bodySmall),
          Text('Notifications sent: ${notifs.length}',
            style: AppTextStyles.bodySmall),
        ]);

      default:
        final keys = c.keys.take(3).join(', ');
        return Text(keys, style: AppTextStyles.bodySmall);
    }
  }
}
