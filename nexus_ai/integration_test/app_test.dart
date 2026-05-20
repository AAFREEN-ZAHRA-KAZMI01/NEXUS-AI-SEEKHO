import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:nexus_ai/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Nexus AI — Integration Tests', () {

    testWidgets('Splash screen loads with brand name', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      expect(find.text('NEXUS AI'), findsOneWidget);
      expect(find.text('Get Started →'), findsOneWidget);
    });

    testWidgets('Splash CTA navigates to home screen', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      expect(find.text('Nexus AI'), findsWidgets);
    });

    testWidgets('Home screen shows 4 metric cards', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      expect(find.text('Insights'),       findsOneWidget);
      expect(find.text('Actions'),        findsOneWidget);
      expect(find.text('Revenue Impact'), findsOneWidget);
      expect(find.text('Alerts'),         findsOneWidget);
    });

    testWidgets('Navigate to analyze screen via FAB', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();
      expect(find.text('New Analysis'), findsOneWidget);
    });

    testWidgets('Input tabs switch Text → URL → File', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();
      await tester.tap(find.text('URL'));
      await tester.pumpAndSettle();
      expect(find.byType(TextField), findsOneWidget);
      await tester.tap(find.text('File'));
      await tester.pumpAndSettle();
      expect(find.text('Tap to select file'), findsOneWidget);
    });

    testWidgets('Domain selector tap selects and deselects', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Logistics'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Logistics'));
      await tester.pumpAndSettle();
    });

    testWidgets('Run Analysis button disabled with empty text input', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();
      expect(find.text('▶  Run Analysis'), findsOneWidget);
      await tester.tap(find.text('▶  Run Analysis'));
      await tester.pumpAndSettle();
      // Should still be on analyze screen (button was disabled)
      expect(find.text('New Analysis'), findsOneWidget);
    });

    testWidgets('Bottom nav items exist on home screen', (tester) async {
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 2));
      await tester.tap(find.text('Get Started →'));
      await tester.pumpAndSettle();
      expect(find.text('Home'),    findsOneWidget);
      expect(find.text('Analyze'), findsOneWidget);
      expect(find.text('Actions'), findsWidgets);
    });

  });
}
