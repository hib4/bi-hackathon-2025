import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:kanca/features/onboarding/onboarding.dart';
import 'package:kanca/l10n/l10n.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        textTheme: GoogleFonts.lexendTextTheme(),
        appBarTheme: AppBarTheme(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        ),
        useMaterial3: true,
      ),
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      debugShowCheckedModeBanner: false,
      home: const OnboardingPage(),
    );
  }
}
