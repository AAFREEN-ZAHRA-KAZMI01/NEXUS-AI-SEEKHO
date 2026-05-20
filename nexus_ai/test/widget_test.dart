// This is a basic Flutter widget test for Nexus AI.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:nexus_ai/main.dart';
import 'package:nexus_ai/presentation/providers/auth_provider.dart';
import 'package:nexus_ai/presentation/providers/analysis_provider.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('App splash screen smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame inside the required MultiProvider parent.
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => AuthProvider()),
          ChangeNotifierProvider(create: (_) => AnalysisProvider()),
        ],
        child: const NexusApp(),
      ),
    );

    // Verify that the splash screen elements exist.
    expect(find.text('NEXUS'), findsOneWidget);
    expect(find.text('AI'), findsOneWidget);

    // Let the animations run and settle completely
    await tester.pumpAndSettle();
  });
}
