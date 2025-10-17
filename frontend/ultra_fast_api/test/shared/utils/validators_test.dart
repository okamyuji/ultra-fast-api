import 'package:flutter_test/flutter_test.dart';
import 'package:ultra_fast_api/shared/utils/validators.dart';

void main() {
  group('Validators', () {
    group('email', () {
      test('returns null for valid email', () {
        expect(Validators.email('test@example.com'), null);
        expect(Validators.email('user.name@domain.co.jp'), null);
      });

      test('returns error for invalid email', () {
        expect(Validators.email(''), isNotNull);
        expect(Validators.email('invalid'), isNotNull);
        expect(Validators.email('test@'), isNotNull);
        expect(Validators.email('@example.com'), isNotNull);
      });
    });

    group('password', () {
      test('returns null for valid password', () {
        expect(Validators.password('password123'), null);
        expect(Validators.password('Test1234'), null);
      });

      test('returns error for too short password', () {
        expect(Validators.password('pass1'), isNotNull);
      });

      test('returns error for missing letter or digit', () {
        expect(Validators.password('password'), isNotNull);
        expect(Validators.password('12345678'), isNotNull);
      });
    });

    group('required', () {
      test('returns null for non-empty value', () {
        expect(Validators.required('value'), null);
      });

      test('returns error for empty value', () {
        expect(Validators.required(''), isNotNull);
        expect(Validators.required(null), isNotNull);
      });
    });
  });
}
