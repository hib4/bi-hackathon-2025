import 'package:flutter/material.dart';
import 'package:kanca/core/theme/app_theme.dart';
import 'package:kanca/features/onboarding/onboarding.dart';
import 'package:kanca/l10n/l10n.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Kanca',
      theme: AppThemeData.themeData().themeData,
      darkTheme: AppThemeData.themeData().themeData,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      debugShowCheckedModeBanner: false,
      home: const OnboardingPage(),
    );
  }
}
