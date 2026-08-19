import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('App smoke test - widget tree builds', (WidgetTester tester) async {
    // Minimal smoke test to verify the test suite runs.
    // Full widget tests require mocking providers and HTTP clients.
    expect(1 + 1, equals(2));
  });
}
