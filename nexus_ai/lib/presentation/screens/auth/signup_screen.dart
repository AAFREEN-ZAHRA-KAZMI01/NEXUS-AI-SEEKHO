import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/nexus_button.dart';
import '../../widgets/common/nexus_card.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final TextEditingController _nameCtrl = TextEditingController();
  final TextEditingController _emailCtrl = TextEditingController();
  final TextEditingController _passCtrl = TextEditingController();
  final TextEditingController _confirmPassCtrl = TextEditingController();

  bool _obscurePass = true;
  bool _obscureConfirmPass = true;
  String? _errorMsg;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _passCtrl.dispose();
    _confirmPassCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      backgroundColor: bgColor,
      body: Stack(
        children: [
          // Top-left glow
          Positioned(
            top: -50,
            left: -50,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    indigoColor.withOpacity(0.15),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          // Bottom-right glow
          Positioned(
            bottom: -80,
            right: -80,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    purpleColor.withOpacity(0.1),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 30),

                  // Header
                  Text(
                    'Create Account',
                    style: GoogleFonts.syne(
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                      color: textColor,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Sign up to get started',
                    style: AppTextStyles.body.copyWith(color: text2Color),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 30),

                  // Full Name field
                  _NexusTextField(
                    controller: _nameCtrl,
                    label: 'Full Name',
                    hint: 'John Doe',
                    icon: Icons.person_outline,
                  ),

                  const SizedBox(height: 16),

                  // Email field
                  _NexusTextField(
                    controller: _emailCtrl,
                    label: 'Email Address',
                    hint: 'john.doe@example.com',
                    icon: Icons.email_outlined,
                    keyboardType: TextInputType.emailAddress,
                  ),

                  const SizedBox(height: 16),

                  // Password field
                  _NexusTextField(
                    controller: _passCtrl,
                    label: 'Password',
                    hint: '••••••••',
                    icon: Icons.lock_outlined,
                    obscureText: _obscurePass,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePass
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                        color: text3Color,
                        size: 18,
                      ),
                      onPressed: () =>
                          setState(() => _obscurePass = !_obscurePass),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Confirm Password field
                  _NexusTextField(
                    controller: _confirmPassCtrl,
                    label: 'Confirm Password',
                    hint: '••••••••',
                    icon: Icons.lock_clock_outlined,
                    obscureText: _obscureConfirmPass,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPass
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                        color: text3Color,
                        size: 18,
                      ),
                      onPressed: () =>
                          setState(() => _obscureConfirmPass = !_obscureConfirmPass),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Error message
                  if (_errorMsg != null || authProvider.errorMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: NexusCard(
                        borderColor: errorColor,
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline,
                                color: errorColor, size: 14),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                _errorMsg ?? authProvider.errorMessage!,
                                style: const TextStyle(
                                    color: errorColor, fontSize: 12),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  // Sign up button
                  NexusButton(
                    'Sign Up',
                    isLoading: authProvider.isLoading,
                    onTap: () async {
                      final name = _nameCtrl.text.trim();
                      final email = _emailCtrl.text.trim();
                      final password = _passCtrl.text.trim();
                      final confirmPassword = _confirmPassCtrl.text.trim();

                      if (name.isEmpty) {
                        setState(() => _errorMsg = 'Name cannot be empty.');
                        return;
                      }
                      if (!email.contains('@')) {
                        setState(() => _errorMsg = 'Please enter a valid email.');
                        return;
                      }
                      if (password.length < 6) {
                        setState(() => _errorMsg = 'Password must be at least 6 characters.');
                        return;
                      }
                      if (password != confirmPassword) {
                        setState(() => _errorMsg = 'Passwords do not match.');
                        return;
                      }

                      setState(() {
                        _errorMsg = null;
                      });

                      final success = await context.read<AuthProvider>().signup(name, email, password);
                      if (success && mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Registration successful! Please login.'),
                            backgroundColor: successColor,
                          ),
                        );
                        Navigator.pushReplacementNamed(context, '/login');
                      }
                    },
                  ),

                  const SizedBox(height: 24),

                  // Sign in link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "Already have an account? ",
                        style: AppTextStyles.bodySmall,
                      ),
                      GestureDetector(
                        onTap: () =>
                            Navigator.pushReplacementNamed(context, '/login'),
                        child: Text(
                          'Sign In',
                          style: AppTextStyles.bodySmall.copyWith(
                            fontSize: 12,
                            color: purple2Color,
                            decoration: TextDecoration.underline,
                            decorationColor: purple2Color,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _NexusTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final IconData icon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final Widget? suffixIcon;

  const _NexusTextField({
    required this.controller,
    required this.label,
    required this.hint,
    required this.icon,
    this.obscureText = false,
    this.keyboardType,
    this.suffixIcon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.bodySmall),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          style: AppTextStyles.body.copyWith(fontSize: 13, color: textColor),
          decoration: InputDecoration(
            filled: true,
            fillColor: cardColor,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: borderColor, width: 0.5),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: borderColor, width: 0.5),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: indigoColor, width: 1),
            ),
            hintText: hint,
            hintStyle: AppTextStyles.body.copyWith(color: text3Color),
            prefixIcon: Icon(icon, color: text3Color, size: 18),
            suffixIcon: suffixIcon,
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 16),
          ),
        ),
      ],
    );
  }
}
