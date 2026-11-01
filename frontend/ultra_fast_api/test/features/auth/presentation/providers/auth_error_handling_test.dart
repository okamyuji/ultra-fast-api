import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_notifier.dart';

void main() {
  group('Auth Error Handling', () {
    test('handles 401 Unauthorized error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        response: Response(
          requestOptions: RequestOptions(path: '/auth/login'),
          statusCode: 401,
          data: {'detail': 'Invalid credentials'},
        ),
        type: DioExceptionType.badResponse,
      );

      final message = authErrorMessage(error);
      expect(message, contains('メールアドレスまたはパスワードが正しくありません'));
    });

    test('handles 409 Conflict error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/register'),
        response: Response(
          requestOptions: RequestOptions(path: '/auth/register'),
          statusCode: 409,
          data: {'detail': 'Email already exists'},
        ),
        type: DioExceptionType.badResponse,
      );

      final message = authErrorMessage(error);
      expect(message, contains('このメールアドレスは既に登録されています'));
    });

    test('handles 422 Validation error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        response: Response(
          requestOptions: RequestOptions(path: '/auth/login'),
          statusCode: 422,
          data: {
            'detail': [
              {
                'loc': ['body', 'email'],
                'msg': 'Invalid email format',
                'type': 'value_error',
              },
            ],
          },
        ),
        type: DioExceptionType.badResponse,
      );

      final message = authErrorMessage(error);
      expect(message, contains('email'));
      expect(message, contains('Invalid email format'));
    });

    test('handles connection timeout', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.connectionTimeout,
      );

      final message = authErrorMessage(error);
      expect(message, contains('タイムアウト'));
    });

    test('handles connection error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.connectionError,
      );

      final message = authErrorMessage(error);
      expect(message, contains('ネットワーク接続に失敗'));
    });

    test('handles 500 server error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        response: Response(
          requestOptions: RequestOptions(path: '/auth/login'),
          statusCode: 500,
          data: {'detail': 'Internal server error'},
        ),
        type: DioExceptionType.badResponse,
      );

      final message = authErrorMessage(error);
      expect(message, contains('サーバーエラー'));
    });

    test('handles cancel error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.cancel,
      );

      final message = authErrorMessage(error);
      expect(message, contains('キャンセル'));
    });

    test('handles bad certificate error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.badCertificate,
      );

      final message = authErrorMessage(error);
      expect(message, contains('SSL証明書'));
    });
  });
}
