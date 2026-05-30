import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'presentation/providers/analysis_provider.dart';
import 'presentation/screens/splash/splash_screen.dart';
import 'presentation/screens/onboarding/onboarding_screen.dart';
import 'presentation/screens/auth/login_screen.dart';
import 'presentation/screens/home/home_screen.dart';
import 'presentation/screens/analyze/analyze_screen.dart';
import 'presentation/screens/agent_progress/agent_progress_screen.dart';
import 'presentation/screens/insight/insight_screen.dart';
import 'presentation/screens/actions/actions_screen.dart';
import 'presentation/screens/simulation/simulation_screen.dart';
import 'presentation/screens/results/results_screen.dart';
import 'presentation/screens/trace/trace_screen.dart';
import 'presentation/screens/workflow/workflow_screen.dart';
import 'presentation/screens/profile/profile_screen.dart';
import 'presentation/screens/history/history_screen.dart';
import 'presentation/screens/state_diff/state_diff_screen.dart';
import 'presentation/screens/alerts/alerts_screen.dart';
import 'presentation/screens/alerts/create_alert_screen.dart';
import 'presentation/screens/history/outcome_history_screen.dart';
import 'presentation/screens/dashboard/domain_dashboard_screen.dart';
import 'presentation/screens/dashboard/domain_detail_screen.dart';
import 'presentation/screens/org/org_setup_screen.dart';

import 'presentation/providers/auth_provider.dart';
import 'presentation/screens/auth/signup_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  GoogleFonts.config.allowRuntimeFetching = true;
  
  final prefs = await SharedPreferences.getInstance();
  String? devId = prefs.getString('device_id');
  if (devId == null || devId.isEmpty) {
    devId = DateTime.now().millisecondsSinceEpoch.toString();
    await prefs.setString('device_id', devId);
  }
  AppConstants.deviceId = devId;

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => AnalysisProvider()),
      ],
      child: const NexusApp(),
    ),
  );
}

class NexusApp extends StatelessWidget {
  const NexusApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      initialRoute: '/splash',
      routes: {
        '/splash':      (_) => const SplashScreen(),
        '/onboarding':  (_) => const OnboardingScreen(),
        '/login':       (_) => const LoginScreen(),
        '/signup':      (_) => const SignupScreen(),
        '/auth/login':  (_) => const LoginScreen(),
        '/home':        (_) => const HomeScreen(),
        '/analyze':     (_) => const AnalyzeScreen(),
        '/progress':    (_) => const AgentProgressScreen(),
        '/insight':     (_) => const InsightScreen(),
        '/actions':     (_) => const ActionsScreen(),
        '/simulate':    (_) => const SimulationScreen(),
        '/results':     (_) => const ResultsScreen(),
        '/trace':       (_) => const TraceScreen(),
        '/workflow':    (_) => const WorkflowScreen(),
        '/profile':     (_) => const ProfileScreen(),
        '/history':     (_) => const HistoryScreen(),
        '/state-diff':  (_) => const StateDiffScreen(),
        '/alerts':      (_) => const AlertsScreen(),
        '/alerts/create': (_) => const CreateAlertScreen(),
        '/outcome-history': (_) => const OutcomeHistoryScreen(),
        '/dashboard':   (_) => const DomainDashboardScreen(),
        '/dashboard/detail': (_) => const DomainDetailScreen(),
        '/org-setup':   (_) => const OrgSetupScreen(),
      },
    );
  }
}
