import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../widgets/common/gradient_text.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageCtrl = PageController();
  int _currentPage = 0;

  @override
  void dispose() {
    _pageCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      body: Stack(
        children: [
          // Full-screen page view
          PageView(
            controller: _pageCtrl,
            onPageChanged: (page) => setState(() => _currentPage = page),
            children: [
              _buildPage1(),
              _buildPage2(),
              _buildPage3(),
            ],
          ),

          // Bottom navigation overlay
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 24, vertical: 16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Dots indicator
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(3, (i) {
                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          margin: const EdgeInsets.symmetric(horizontal: 3),
                          width: i == _currentPage ? 20 : 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color:
                                i == _currentPage ? primaryColor : text3Color,
                            borderRadius: BorderRadius.circular(3),
                          ),
                        );
                      }),
                    ),

                    const SizedBox(height: 20),

                    NexusButton(
                      _currentPage < 2 ? 'Next →' : 'Get Started →',
                      onTap: () {
                        if (_currentPage < 2) {
                          _pageCtrl.nextPage(
                            duration: const Duration(milliseconds: 400),
                            curve: Curves.easeInOut,
                          );
                        } else {
                          Navigator.pushReplacementNamed(context, '/signup');
                        }
                      },
                    ),

                    const SizedBox(height: 12),

                    if (_currentPage < 2)
                      TextButton(
                        style: TextButton.styleFrom(
                            foregroundColor: text3Color),
                        onPressed: () =>
                            Navigator.pushReplacementNamed(context, '/signup'),
                        child: const Text('Skip'),
                      ),

                    const SizedBox(height: 8),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPage1() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Hero illustration — 3 stacked domain cards
            SizedBox(
              height: 200,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Positioned(
                    top: 30,
                    child: _DomainChip('Finance', Icons.trending_up, const Color(0xFF10B981)),
                  ),
                  Positioned(
                    top: 80,
                    child: _DomainChip('Logistics', Icons.local_shipping, const Color(0xFF3B82F6)),
                  ),
                  Positioned(
                    top: 130,
                    child: _DomainChip('Healthcare', Icons.health_and_safety, const Color(0xFFF59E0B)),
                  ),
                ],
              ),
            ).animate().fadeIn(duration: 800.ms).slideY(begin: 0.2),

            const SizedBox(height: 32),

            GradientText(
              text: 'From News to Action',
              style: AppTextStyles.heading1.copyWith(fontSize: 24),
              gradient: primaryGrad,
            ),
            const SizedBox(height: 12),
            Text(
              'Paste any article, report, or URL.\nOur AI reads, understands, and\nautomatically takes the best action.',
              style: AppTextStyles.body
                  .copyWith(fontSize: 15, color: text2Color, height: 1.6),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 220),
          ],
        ),
      ),
    );
  }

  Widget _buildPage2() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Feature icons 2x2 grid
            SizedBox(
              width: 200,
              height: 200,
              child: GridView.count(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  _FeatureIcon(Icons.upload_file, 'Ingest Content', blueColor),
                  _FeatureIcon(Icons.psychology, 'Extract Insights', purpleColor),
                  _FeatureIcon(Icons.bolt, 'Take Actions', indigoColor),
                  _FeatureIcon(Icons.bar_chart, 'Show Results', successColor),
                ],
              ),
            ).animate().fadeIn(duration: 600.ms),

            const SizedBox(height: 32),

            GradientText(
              text: 'How It Works',
              style: AppTextStyles.heading1.copyWith(fontSize: 24),
              gradient: primaryGrad,
            ),
            const SizedBox(height: 12),
            Text(
              'Upload any content — reports, articles, PDFs.\n'
              'Our AI agents extract insights and automatically\n'
              'execute the best recommended action.',
              style: AppTextStyles.body
                  .copyWith(fontSize: 14, color: text2Color, height: 1.6),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 220),
          ],
        ),
      ),
    );
  }

  Widget _buildPage3() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Stacked agent cards preview
            SizedBox(
              height: 160,
              child: Stack(
                children: [
                  Positioned(
                    top: 20,
                    left: 20,
                    right: 20,
                    child: _AgentPreviewCard(
                      'Analyzer Agent',
                      'Extracting key insights',
                      blueColor,
                      0.6,
                    ),
                  ),
                  Positioned(
                    top: 10,
                    left: 10,
                    right: 10,
                    child: _AgentPreviewCard(
                      'Risk Agent',
                      'Analyzing potential impact',
                      purpleColor,
                      0.8,
                    ),
                  ),
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    child: _AgentPreviewCard(
                      'Planner Agent',
                      'Planning best actions',
                      indigoColor,
                      1.0,
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(duration: 600.ms).slideY(begin: 0.2),

            const SizedBox(height: 32),

            GradientText(
              text: '6 AI Agents',
              style: AppTextStyles.heading1.copyWith(fontSize: 24),
              gradient: primaryGrad,
            ),
            const SizedBox(height: 12),
            Text(
              'Multiple specialized agents work in parallel\n'
              'to analyze, plan, and execute actions\n'
              'across 6 business domains.',
              style: AppTextStyles.body
                  .copyWith(fontSize: 14, color: text2Color, height: 1.6),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 220),
          ],
        ),
      ),
    );
  }
}

// ─── Domain chip (used in page 1 hero) ──────────────────────────────────────

class _DomainChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  const _DomainChip(this.label, this.icon, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.35), width: 0.8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 16),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: color),
          ),
        ],
      ),
    );
  }
}

// ─── Feature icon tile ───────────────────────────────────────────────────────

class _FeatureIcon extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;

  const _FeatureIcon(this.icon, this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          colors: [color.withOpacity(0.2), color.withOpacity(0.05)],
        ),
        border: Border.all(color: color.withOpacity(0.3), width: 0.5),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 6),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// ─── Agent preview card ───────────────────────────────────────────────────────

class _AgentPreviewCard extends StatelessWidget {
  final String name;
  final String subtitle;
  final Color color;
  final double opacity;

  const _AgentPreviewCard(this.name, this.subtitle, this.color, this.opacity);

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: opacity,
      child: NexusCard(
        child: Row(
          children: [
            Icon(Icons.smart_toy, color: color, size: 18),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  name,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: textColor,
                  ),
                ),
                Text(subtitle, style: AppTextStyles.bodySmall),
              ],
            ),
            const Spacer(),
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: successColor,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
