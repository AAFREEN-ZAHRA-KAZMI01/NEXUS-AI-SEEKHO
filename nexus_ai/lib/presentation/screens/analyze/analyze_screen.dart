import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/services/file_service.dart';
import '../../providers/analysis_provider.dart';
import '../../widgets/analyze/domain_selector.dart';
import '../../widgets/analyze/file_upload_button.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';

class AnalyzeScreen extends StatefulWidget {
  const AnalyzeScreen({super.key});

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen> {
  late final TextEditingController _textCtrl;
  late final TextEditingController _urlCtrl;

  static const List<Map<String, String>> _samples = [
    {
      'domain':  'finance',
      'emoji':   '📈',
      'label':   'KSE-100 Crash',
      'text':
          'KSE-100 index dropped 847 points today as foreign investors pulled \$200M '
          'out of Pakistani equities following IMF loan uncertainty. The index closed '
          'at 71,243 — its lowest since March. SECP has called an emergency board '
          'meeting. Trading volume collapsed to 180M shares vs a 30-day average of '
          '420M. Foreign portfolio outflow reached \$200M in a single session.',
    },
    {
      'domain':  'policy',
      'emoji':   '🏛️',
      'label':   'OGRA Fuel Notification',
      'text':
          'OGRA has issued emergency notification ref. OGRA/S(Pricing)/2024-847 '
          'increasing petrol price by PKR 12.74 per litre and HSD diesel by PKR 9.50 '
          'per litre effective midnight tonight. The notification cites global crude '
          'oil movement and PKR depreciation as primary drivers. All logistics '
          'operators must revise freight contracts within 48 hours or face '
          'regulatory penalties under the Petroleum Act 1934.',
    },
    {
      'domain':  'logistics',
      'emoji':   '🚢',
      'label':   'KPT Port Congestion',
      'text':
          'Karachi Port Trust (KPT) reports 47 vessels awaiting berth as port '
          'congestion reaches a 3-year high. Average container dwell time is now '
          '11.2 days vs the target of 4 days. Container throughput dropped 22% this '
          'week to 18,400 TEUs. Freight costs surged 18% since last month. '
          'Auto manufacturers report production line stoppages due to CKD kit delays. '
          'NLC and Fauji Foundation fleets are being redirected to Gwadar port.',
    },
    {
      'domain':  'healthcare',
      'emoji':   '🏥',
      'label':   'DRAP Drug Shortage',
      'text':
          'DRAP has confirmed a critical shortage of Insulin Glargine 100IU/ml at '
          '14 public hospitals across Lahore and Rawalpindi. An estimated 12,000 '
          'insulin-dependent diabetic patients are at immediate risk. Three '
          'pharmaceutical manufacturers — Getz Pharma, Searle, and Highnoon — '
          'suspended production citing raw material (API) import restrictions. '
          'WHO Pakistan office has been formally notified. Emergency procurement '
          'authorisation is required from NHSRC.',
    },
    {
      'domain':  'urban',
      'emoji':   '⚡',
      'label':   'LESCO Grid Fault',
      'text':
          'LESCO reports an 18-hour unplanned power outage affecting zones DHA-4, '
          'Gulberg-3, Model Town, and Johar Town in Lahore. An estimated 340,000 '
          'households and 4,200 commercial units are impacted. Grid fault identified '
          'at 132kV Kot Lakhpat substation — feeder 6 breaker failure. '
          'Repair ETA: 6 hours. Industrial estates report PKR 45M/hour production loss. '
          'Backup generator fuel demand has spiked 300% at Lahore fuel stations.',
    },
    {
      'domain':  'business',
      'emoji':   '🏪',
      'label':   'Regional Sales Decline',
      'text':
          'Q3 regional sales report for Karachi division shows revenue down 31% versus '
          'Q2 — from PKR 8.5M to PKR 5.87M. Monthly order volume fell from 1,240 to '
          '856. Customer churn rate spiked to 18.4% (benchmark: 5%). Top 3 churned '
          'SKUs: SKU-1042 (Premium Basmati), SKU-2287 (Cooking Oil 5L), SKU-3391 '
          '(Detergent Bulk). CRM data shows 47 high-value accounts have gone silent '
          'in the last 30 days.',
    },
  ];

  @override
  void initState() {
    super.initState();
    _textCtrl = TextEditingController();
    _urlCtrl = TextEditingController();
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    _urlCtrl.dispose();
    super.dispose();
  }

  void _showBackendOfflineDialog() {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: cardColor,
        title: Text('Backend Offline', style: AppTextStyles.heading3),
        content: Text(
          'Cannot reach backend. Please start Docker and ensure the server is running.',
          style: AppTextStyles.body,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(
              'OK',
              style: AppTextStyles.buttonLabel.copyWith(color: blue2Color),
            ),
          ),
        ],
      ),
    );
  }

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
            Text('Upload or Add Content',
                style: AppTextStyles.heading3),
            Text('Choose input type',
                style: AppTextStyles.bodySmall),
          ],
        ),
      ),
      body: Consumer<AnalysisProvider>(
        builder: (context, provider, _) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── 1. Input type grid ─────────────────────────────────
                Text('CHOOSE INPUT TYPE',
                    style: AppTextStyles.label),
                const SizedBox(height: 12),
                GridView.count(
                  crossAxisCount: 2,
                  childAspectRatio: 1.6,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  children: [
                    _InputTypeCard(
                      icon: Icons.picture_as_pdf,
                      label: 'Upload PDF',
                      type: 'pdf',
                      color: blueColor,
                      isSelected:
                          provider.selectedInputType == 'pdf',
                      onTap: () => provider.setInputType('pdf'),
                    ),
                    _InputTypeCard(
                      icon: Icons.article_outlined,
                      label: 'Paste Article',
                      type: 'text',
                      color: purpleColor,
                      isSelected:
                          provider.selectedInputType == 'text',
                      onTap: () => provider.setInputType('text'),
                    ),
                    _InputTypeCard(
                      icon: Icons.language_outlined,
                      label: 'Website URL',
                      type: 'url',
                      color: indigoColor,
                      isSelected:
                          provider.selectedInputType == 'url',
                      onTap: () => provider.setInputType('url'),
                    ),
                    _InputTypeCard(
                      icon: Icons.dashboard_outlined,
                      label: 'Dashboard Data',
                      type: 'excel',
                      color: const Color(0xFF06B6D4),
                      isSelected:
                          provider.selectedInputType == 'excel',
                      onTap: () => provider.setInputType('excel'),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // ── 2. Input preview ───────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('INPUT PREVIEW', style: AppTextStyles.label),
                    GestureDetector(
                      onTap: () => _showSamplePicker(context, provider),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.lightbulb_outline,
                              size: 14, color: blue2Color),
                          const SizedBox(width: 4),
                          Text(
                            'Try a sample',
                            style: AppTextStyles.label.copyWith(
                                color: blue2Color,
                                decoration: TextDecoration.underline),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 250),
                  child: _buildInputPreview(provider, context),
                ),

                const SizedBox(height: 20),

                // ── 3. AI Analysis options ─────────────────────────────
                Text('AI ANALYSIS OPTIONS',
                    style: AppTextStyles.label),
                const SizedBox(height: 10),
                Container(
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(14),
                    border:
                        Border.all(color: borderColor, width: 0.5),
                  ),
                  child: Column(
                    children: const [
                      _AnalysisOption(
                        label: 'Business Impact',
                        icon: Icons.trending_up,
                        defaultOn: true,
                        subtitle: 'Analyzing business effects',
                      ),
                      Divider(
                          color: borderColor,
                          height: 1,
                          thickness: 0.5),
                      _AnalysisOption(
                        label: 'Risk Analysis',
                        icon: Icons.shield_outlined,
                        defaultOn: true,
                        subtitle: 'Identifying potential risks',
                      ),
                      Divider(
                          color: borderColor,
                          height: 1,
                          thickness: 0.5),
                      _AnalysisOption(
                        label: 'Financial Impact',
                        icon: Icons.account_balance,
                        defaultOn: false,
                        subtitle: 'Calculating financial changes',
                      ),
                      Divider(
                          color: borderColor,
                          height: 1,
                          thickness: 0.5),
                      _AnalysisOption(
                        label: 'Policy Analysis',
                        icon: Icons.gavel_outlined,
                        defaultOn: false,
                        subtitle: 'Checking compliance factors',
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // ── 4. Domain selector ────────────────────────────────
                DomainSelector(
                  selected: provider.selectedDomain,
                  onSelect: (d) => provider.setDomain(d),
                ),

                const SizedBox(height: 16),

                // ── 5. Run AI Analysis button ─────────────────────────
                NexusButton(
                  'Run AI Analysis',
                  onTap: provider.hasValidInput
                      ? () {
                          context
                              .read<AnalysisProvider>()
                              .runAnalysis();
                          Navigator.pushNamed(context, '/progress');
                        }
                      : null,
                ),

                const SizedBox(height: 32),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildInputPreview(
      AnalysisProvider provider, BuildContext context) {
    final type = provider.selectedInputType;

    if (type == 'text') {
      return TextField(
        key: const ValueKey('text'),
        controller: _textCtrl,
        maxLines: 8,
        minLines: 5,
        style: AppTextStyles.body.copyWith(color: textColor),
        onChanged: (v) =>
            context.read<AnalysisProvider>().setTextContent(v),
        decoration: InputDecoration(
          filled: true,
          fillColor: cardColor,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: borderColor, width: 0.5),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: borderColor, width: 0.5),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: indigoColor, width: 1),
          ),
          hintText: 'Paste news article, report, or any text...',
          hintStyle:
              AppTextStyles.body.copyWith(color: text3Color),
          contentPadding: const EdgeInsets.all(14),
        ),
      );
    }

    if (type == 'url') {
      return TextField(
        key: const ValueKey('url'),
        controller: _urlCtrl,
        style: AppTextStyles.body.copyWith(color: textColor),
        onChanged: (v) =>
            context.read<AnalysisProvider>().setUrlContent(v),
        decoration: InputDecoration(
          filled: true,
          fillColor: cardColor,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: borderColor, width: 0.5),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: borderColor, width: 0.5),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide:
                const BorderSide(color: indigoColor, width: 1),
          ),
          prefixIcon:
              const Icon(Icons.link, color: text3Color, size: 18),
          hintText: 'https://',
          hintStyle:
              AppTextStyles.body.copyWith(color: text3Color),
          contentPadding: const EdgeInsets.all(14),
        ),
      );
    }

    // pdf / docx / excel / csv
    if (provider.selectedFileName != null) {
      return Column(
        key: ValueKey('file_selected_$type'),
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          NexusCard(
            borderColor: blue2Color.withOpacity(0.4),
            child: Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: card2Color,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Center(
                    child: Icon(Icons.description,
                        color: blue2Color, size: 20),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        provider.selectedFileName!,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: textColor,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        FileService.formatFileSize(
                            provider.selectedFileSize ?? 0),
                        style: AppTextStyles.bodySmall,
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close,
                      size: 18, color: text3Color),
                  onPressed: () =>
                      context.read<AnalysisProvider>().reset(),
                ),
              ],
            ),
          ),
        ],
      );
    }

    return FileUploadButton(
      key: ValueKey('file_upload_$type'),
      onFilePicked: (name, bytes, fileType) {
        context.read<AnalysisProvider>().setFile(name, bytes);
      },
      fileName: null,
      fileSize: null,
      onClear: () => context.read<AnalysisProvider>().reset(),
    );
  }

  // ─── Sample picker bottom sheet ───────────────────────────────────────────

  void _showSamplePicker(BuildContext context, AnalysisProvider provider) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (_) => DraggableScrollableSheet(
        initialChildSize: 0.75,
        minChildSize: 0.5,
        maxChildSize: 0.92,
        expand: false,
        builder: (_, scrollCtrl) => Column(
          children: [
            // Handle bar
            Container(
              margin: const EdgeInsets.symmetric(vertical: 10),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: borderColor,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
              child: Row(
                children: [
                  const Icon(Icons.lightbulb_outline, color: blue2Color, size: 20),
                  const SizedBox(width: 8),
                  Text('Pakistani Scenario Samples',
                      style: AppTextStyles.heading3),
                ],
              ),
            ),
            const Divider(color: borderColor, height: 1),
            Expanded(
              child: ListView.separated(
                controller: scrollCtrl,
                padding: const EdgeInsets.symmetric(vertical: 8),
                itemCount: _samples.length,
                separatorBuilder: (_, __) =>
                    const Divider(color: borderColor, height: 1),
                itemBuilder: (_, i) {
                  final s = _samples[i];
                  return ListTile(
                    leading: Text(s['emoji']!,
                        style: const TextStyle(fontSize: 26)),
                    title: Text(s['label']!,
                        style: AppTextStyles.body
                            .copyWith(color: textColor, fontWeight: FontWeight.w600)),
                    subtitle: Text(
                      s['text']!.length > 80
                          ? '${s['text']!.substring(0, 80)}…'
                          : s['text']!,
                      style: AppTextStyles.bodySmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: blue2Color.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                            color: blue2Color.withOpacity(0.4), width: 0.5),
                      ),
                      child: Text(s['domain']!,
                          style: AppTextStyles.bodySmall
                              .copyWith(color: blue2Color)),
                    ),
                    onTap: () {
                      provider
                        ..setInputType('text')
                        ..setDomain(s['domain'])
                        ..setTextContent(s['text']!);
                      _textCtrl.text = s['text']!;
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Input type card ──────────────────────────────────────────────────────────

class _InputTypeCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String type;
  final Color color;
  final bool isSelected;
  final VoidCallback onTap;

  const _InputTypeCard({
    required this.icon,
    required this.label,
    required this.type,
    required this.color,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: NexusCard(
        borderColor: isSelected ? color : borderColor,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color:
                    color.withOpacity(isSelected ? 0.25 : 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Icon(icon, color: color, size: 24),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isSelected ? textColor : text2Color,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Analysis option toggle ───────────────────────────────────────────────────

class _AnalysisOption extends StatefulWidget {
  final String label;
  final IconData icon;
  final bool defaultOn;
  final String subtitle;

  const _AnalysisOption({
    required this.label,
    required this.icon,
    required this.defaultOn,
    required this.subtitle,
  });

  @override
  State<_AnalysisOption> createState() => _AnalysisOptionState();
}

class _AnalysisOptionState extends State<_AnalysisOption> {
  late bool _isOn;

  @override
  void initState() {
    super.initState();
    _isOn = widget.defaultOn;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
          horizontal: 14, vertical: 12),
      child: Row(
        children: [
          Icon(
            widget.icon,
            color: _isOn ? blue2Color : text3Color,
            size: 18,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.label,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: _isOn ? textColor : text2Color,
                  ),
                ),
                Text(widget.subtitle,
                    style: AppTextStyles.bodySmall),
              ],
            ),
          ),
          Switch(
            value: _isOn,
            onChanged: (v) => setState(() => _isOn = v),
            activeColor: blueColor,
            inactiveThumbColor: text3Color,
          ),
        ],
      ),
    );
  }
}
