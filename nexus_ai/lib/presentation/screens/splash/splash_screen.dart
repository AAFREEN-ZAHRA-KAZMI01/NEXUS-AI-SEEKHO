import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/gradient_text.dart';
import '../../widgets/common/pill_badge.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _progressCtrl;
  late final Animation<double> _progressAnim;

  @override
  void initState() {
    super.initState();
    _progressCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );
    _progressAnim = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _progressCtrl, curve: Curves.easeInOut),
    );
    _progressCtrl.addStatusListener((status) async {
      if (status == AnimationStatus.completed) {
        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        await authProvider.checkAuthStatus();
        if (!mounted) return;
        if (authProvider.isAuthenticated) {
          Navigator.pushReplacementNamed(context, '/home');
        } else {
          Navigator.pushReplacementNamed(context, '/onboarding');
        }
      }
    });
    _progressCtrl.forward();
  }

  @override
  void dispose() {
    _progressCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgColor,
      body: Stack(
        children: [
          // Radial glow background
          Align(
            alignment: const Alignment(0, -0.2),
            child: Container(
              width: 300,
              height: 300,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [Color(0x33634AB7), Colors.transparent],
                ),
              ),
            ),
          ),

          SafeArea(
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 28),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(height: 80),

                    // Logo with particle/glow effect
                    Stack(
                      alignment: Alignment.center,
                      children: [
                        // Glow ring behind logo
                        Container(
                          width: 200,
                          height: 200,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: RadialGradient(
                              colors: [
                                primaryColor.withOpacity(0.3),
                                Colors.transparent,
                              ],
                            ),
                          ),
                        ),
                        // Logo — large N
                        Container(
                          width: 88,
                          height: 88,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(28),
                            gradient: primaryGrad,
                            boxShadow: [
                              BoxShadow(
                                color: primaryColor.withOpacity(0.4),
                                blurRadius: 30,
                              ),
                            ],
                          ),
                          child: Center(
                            child: Text(
                              'N',
                              style: GoogleFonts.syne(
                                fontSize: 48,
                                fontWeight: FontWeight.w800,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ),
                      ],
                    )
                        .animate()
                        .fadeIn(duration: 400.ms)
                        .slideY(begin: 0.3, duration: 400.ms),

                    const SizedBox(height: 20),

                    // NEXUS
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        GradientText(
                          text: 'NEXUS',
                          style: AppTextStyles.brandLarge.copyWith(fontSize: 28),
                          gradient: primaryGrad,
                        ),
                      ],
                    )
                        .animate(delay: 200.ms)
                        .fadeIn(duration: 400.ms)
                        .slideY(begin: 0.3, duration: 400.ms),

                    const SizedBox(height: 2),

                    // AI
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'AI',
                          style: GoogleFonts.syne(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: text2Color,
                            letterSpacing: 4,
                          ),
                        ),
                      ],
                    )
                        .animate(delay: 300.ms)
                        .fadeIn(duration: 400.ms),

                    const SizedBox(height: 12),

                    // Tagline
                    Text(
                      'Transforming Insights into Actions',
                      style: AppTextStyles.body.copyWith(
                        fontSize: 13,
                        color: text2Color,
                      ),
                      textAlign: TextAlign.center,
                    )
                        .animate(delay: 400.ms)
                        .fadeIn(duration: 400.ms)
                        .slideY(begin: 0.3, duration: 400.ms),

                    const SizedBox(height: 20),

                    // Tag pills
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      alignment: WrapAlignment.center,
                      children: const [
                        PillBadge('Insight Extraction', type: PillType.teal),
                        PillBadge('Action Simulation', type: PillType.blue),
                        PillBadge('6 Domains', type: PillType.teal),
                      ],
                    )
                        .animate(delay: 600.ms)
                        .fadeIn(duration: 400.ms)
                        .slideY(begin: 0.3, duration: 400.ms),

                    const SizedBox(height: 48),

                    // Animated progress bar
                    AnimatedBuilder(
                      animation: _progressAnim,
                      builder: (context, _) => ClipRRect(
                        borderRadius: BorderRadius.circular(3),
                        child: LinearProgressIndicator(
                          value: _progressAnim.value,
                          backgroundColor: card2Color,
                          valueColor:
                              const AlwaysStoppedAnimation<Color>(primaryColor),
                          minHeight: 3,
                        ),
                      ),
                    ).animate(delay: 800.ms).fadeIn(duration: 400.ms),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}


class _PulsingDot extends StatefulWidget {
  final Color color;
  const _PulsingDot({required this.color});

  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    _anim = Tween<double>(begin: 0.3, end: 1.0).animate(_ctrl);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _anim,
      child: Container(
        width: 8,
        height: 8,
        decoration: BoxDecoration(color: widget.color, shape: BoxShape.circle),
      ),
    );
  }
}
