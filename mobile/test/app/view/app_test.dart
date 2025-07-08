import 'package:flutter_test/flutter_test.dart';
import 'package:kanca/app/app.dart';
import 'package:kanca/features/onboarding/onboarding.dart';

void main() {
  group('App', () {
    testWidgets('renders OnboardingPage', (tester) async {
      await tester.pumpWidget(const App());
      expect(find.byType(OnboardingPage), findsOneWidget);
    });
  });
}
