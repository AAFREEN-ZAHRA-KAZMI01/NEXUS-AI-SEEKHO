import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants/app_constants.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/nexus_card.dart';
import '../../../data/services/api_service.dart';
import '../../widgets/common/bottom_nav_bar.dart';
import '../../providers/analysis_provider.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoadingReset = false;
  Map<String, dynamic>? _orgDetails;
  bool _isLoadingOrg = true;

  @override
  void initState() {
    super.initState();
    _loadOrgDetails();
  }

  Future<void> _loadOrgDetails() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final apiKey = prefs.getString(AppConstants.apiKeyPrefKey);
      if (apiKey != null && apiKey.isNotEmpty) {
        final details = await ApiService().getOrgMe();
        setState(() => _orgDetails = details);
      }
    } catch (_) {
      // Ignored
    } finally {
      if (mounted) setState(() => _isLoadingOrg = false);
    }
  }

  Future<void> _resetState() async {
    setState(() => _isLoadingReset = true);
    try {
      final res = await ApiService().resetState();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(res['message'] ?? 'State reset successful')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to reset state: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoadingReset = false);
    }
  }

  void _showLogoutConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(
          'Confirm Logout',
          style: GoogleFonts.syne(color: textColor, fontWeight: FontWeight.w700),
        ),
        content: Text(
          'Are you sure you want to log out of your session?',
          style: AppTextStyles.body.copyWith(color: text2Color),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: text3Color)),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context); // Close dialog
              await context.read<AuthProvider>().logout();
              if (mounted) {
                Navigator.pushNamedAndRemoveUntil(context, '/login', (r) => false);
              }
            },
            child: const Text('Log Out', style: TextStyle(color: errorColor)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final userName = authProvider.currentUser?.name ?? 'User';
    final userEmail = authProvider.currentUser?.email ?? 'user@example.com';
    final userInitial = userName.isNotEmpty ? userName[0].toUpperCase() : 'U';

    return Scaffold(
      backgroundColor: bgColor,
      bottomNavigationBar: Consumer<AnalysisProvider>(
        builder: (_, provider, __) => NexusBottomNav(
          currentIndex: 5,
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
        title: Text('Profile', style: AppTextStyles.heading3),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile header card
            NexusCard(
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      gradient: primaryGrad,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Center(
                      child: Text(
                        userInitial,
                        style: GoogleFonts.syne(
                          fontSize: 24,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(userName, style: AppTextStyles.heading3),
                        Text(
                          userEmail,
                          style: AppTextStyles.bodySmall,
                        ),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: successColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: successColor.withOpacity(0.4),
                              width: 0.5,
                            ),
                          ),
                          child: const Text(
                            'Pro Plan',
                            style: TextStyle(
                              fontSize: 10,
                              color: successColor,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ORGANISATION section
            const _SectionHeader('ORGANISATION'),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: borderColor, width: 0.5),
              ),
              padding: const EdgeInsets.all(14),
              child: _isLoadingOrg
                  ? const Center(child: CircularProgressIndicator())
                  : _orgDetails != null
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Name: ${_orgDetails!['name']}', style: AppTextStyles.body),
                            const SizedBox(height: 4),
                            Text('Plan: ${_orgDetails!['plan']}', style: AppTextStyles.bodySmall),
                            const SizedBox(height: 12),
                            LinearProgressIndicator(
                              value: _orgDetails!['monthly_limit'] > 0 
                                  ? (_orgDetails!['monthly_analysis_count'] / _orgDetails!['monthly_limit']).clamp(0.0, 1.0)
                                  : 0.0,
                            ),
                            const SizedBox(height: 8),
                            Text('${_orgDetails!['monthly_analysis_count']} of ${_orgDetails!['monthly_limit']} analyses used', style: AppTextStyles.bodySmall),
                            const SizedBox(height: 12),
                            _TappableSettingsItem(
                              icon: Icons.key,
                              label: 'Manage API Key',
                              onTap: () => Navigator.pushNamed(context, '/org-setup').then((_) => _loadOrgDetails()),
                            ),
                          ],
                        )
                      : Column(
                          children: [
                            Text('No organisation connected. Running in local mode.', style: AppTextStyles.bodySmall),
                            const SizedBox(height: 12),
                            ElevatedButton(
                              onPressed: () => Navigator.pushNamed(context, '/org-setup').then((_) => _loadOrgDetails()),
                              child: const Text('Connect to Organisation'),
                            ),
                          ],
                        ),
            ),

            const SizedBox(height: 20),

            // GENERAL section
            const _SectionHeader('GENERAL'),
            const SizedBox(height: 8),
            _SettingsGroup(
              items: const [
                _SettingsItem(
                    icon: Icons.person_outline, label: 'Edit Profile'),
                _SettingsItem(
                    icon: Icons.lock_outline, label: 'Change Password'),
                _SettingsItem(
                    icon: Icons.notifications_outlined,
                    label: 'Notifications'),
              ],
            ),

            const SizedBox(height: 20),

            // PREFERENCES section
            const _SectionHeader('PREFERENCES'),
            const SizedBox(height: 8),
            _SettingsGroup(
              items: const [
                _SettingsItem(
                    icon: Icons.language, label: 'Language', trailing: 'English'),
                _SettingsItem(
                    icon: Icons.dark_mode_outlined,
                    label: 'Theme',
                    trailing: 'Dark'),
                _SettingsItem(
                    icon: Icons.domain,
                    label: 'Default Domain',
                    trailing: 'Business'),
              ],
            ),

            const SizedBox(height: 20),

            // HISTORY section
            const _SectionHeader('HISTORY'),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: borderColor, width: 0.5),
              ),
              child: Column(
                children: [
                  _TappableSettingsItem(
                    icon: Icons.history,
                    label: 'Action Outcome History',
                    trailing: null,
                    onTap: () => Navigator.pushNamed(context, '/outcome-history'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // OTHER section
            const _SectionHeader('OTHER'),
            const SizedBox(height: 8),
            _SettingsGroup(
              items: const [
                _SettingsItem(
                    icon: Icons.help_outline, label: 'Help & Support'),
                _SettingsItem(icon: Icons.info_outline, label: 'About'),
                _SettingsItem(
                    icon: Icons.privacy_tip_outlined,
                    label: 'Privacy Policy'),
              ],
            ),

            const SizedBox(height: 24),

            // Reset Domain State button
            GestureDetector(
              onTap: _isLoadingReset ? null : _resetState,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: primaryColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: primaryColor.withOpacity(0.4),
                    width: 0.5,
                  ),
                ),
                child: Center(
                  child: _isLoadingReset
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: primaryColor),
                        )
                      : const Text(
                          'Reset Domain State',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: primaryColor,
                          ),
                        ),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Logout button
            GestureDetector(
              onTap: () => _showLogoutConfirmation(context),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: errorColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: errorColor.withOpacity(0.4),
                    width: 0.5,
                  ),
                ),
                child: const Center(
                  child: Text(
                    'Log Out',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: errorColor,
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // App version footer
            Center(
              child: Text(
                'Nexus AI v1.0.0',
                style: AppTextStyles.bodySmall,
              ),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

// ── Section header ─────────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader(this.title);

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: AppTextStyles.label.copyWith(letterSpacing: 1.2),
    );
  }
}

// ── Settings group ─────────────────────────────────────────────────────────────

class _SettingsGroup extends StatelessWidget {
  final List<_SettingsItem> items;

  const _SettingsGroup({required this.items});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: borderColor, width: 0.5),
      ),
      child: Column(
        children: List.generate(items.length, (i) {
          return Column(
            children: [
              items[i],
              if (i < items.length - 1)
                const Divider(color: borderColor, height: 1, thickness: 0.5),
            ],
          );
        }),
      ),
    );
  }
}

// ── Settings item ──────────────────────────────────────────────────────────────

class _SettingsItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? trailing;

  const _SettingsItem({
    required this.icon,
    required this.label,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      child: Row(
        children: [
          Icon(icon, color: text2Color, size: 18),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: AppTextStyles.body
                  .copyWith(color: textColor, fontSize: 13),
            ),
          ),
          if (trailing != null) ...[
            Text(trailing!, style: AppTextStyles.bodySmall),
            const SizedBox(width: 4),
          ],
          const Icon(Icons.chevron_right, color: text3Color, size: 18),
        ],
      ),
    );
  }
}

// ── Tappable settings item ─────────────────────────────────────────────────────

class _TappableSettingsItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? trailing;
  final VoidCallback? onTap;

  const _TappableSettingsItem({
    required this.icon,
    required this.label,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        child: Row(
          children: [
            Icon(icon, color: text2Color, size: 18),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: AppTextStyles.body.copyWith(color: textColor, fontSize: 13),
              ),
            ),
            if (trailing != null) ...[
              Text(trailing!, style: AppTextStyles.bodySmall),
              const SizedBox(width: 4),
            ],
            const Icon(Icons.chevron_right, color: text3Color, size: 18),
          ],
        ),
      ),
    );
  }
}
