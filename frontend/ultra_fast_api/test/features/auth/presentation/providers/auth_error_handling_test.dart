import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Auth Error Handling', () {
    String handleError(Object error) {
      if (error is DioException) {
        switch (error.type) {
          case DioExceptionType.connectionTimeout:
          case DioExceptionType.sendTimeout:
          case DioExceptionType.receiveTimeout:
            return '接続がタイムアウトしました。ネットワーク接続を確認してください。';
          case DioExceptionType.badResponse:
            final statusCode = error.response?.statusCode;
            final data = error.response?.data;

            if (statusCode == 400) {
              if (data is Map && data.containsKey('detail')) {
                final detail = data['detail'];
                if (detail is List) {
                  return detail.map((e) => e['msg'] ?? e.toString()).join('\n');
                }
                return detail.toString();
              }
              return '入力内容に誤りがあります。';
            } else if (statusCode == 401) {
              return 'メールアドレスまたはパスワードが正しくありません。';
            } else if (statusCode == 403) {
              return 'アクセスが拒否されました。';
            } else if (statusCode == 404) {
              return 'リクエストされたリソースが見つかりませんでした。';
            } else if (statusCode == 409) {
              return 'このメールアドレスは既に登録されています。';
            } else if (statusCode == 422) {
              if (data is Map && data.containsKey('detail')) {
                final detail = data['detail'];
                if (detail is List) {
                  return detail
                      .map((e) {
                        final loc = e['loc'] as List?;
                        final msg = e['msg'] as String?;
                        if (loc != null && loc.length > 1 && msg != null) {
                          return '${loc[1]}: $msg';
                        }
                        return msg ?? e.toString();
                      })
                      .join('\n');
                }
              }
              return '入力内容が不正です。';
            } else if (statusCode != null && statusCode >= 500) {
              return 'サーバーエラーが発生しました。しばらくしてから再度お試しください。';
            }
            return 'エラーが発生しました。（ステータスコード: $statusCode）';
          case DioExceptionType.cancel:
            return 'リクエストがキャンセルされました。';
          case DioExceptionType.connectionError:
            return 'ネットワーク接続に失敗しました。インターネット接続を確認してください。';
          case DioExceptionType.badCertificate:
            return 'SSL証明書の検証に失敗しました。';
          case DioExceptionType.unknown:
            if (error.message?.contains('SocketException') ?? false) {
              return 'ネットワークに接続できません。インターネット接続を確認してください。';
            }
            return '予期しないエラーが発生しました。';
        }
      }

      final errorMessage = error.toString();
      if (errorMessage.contains('FormatException')) {
        return 'データの形式が不正です。';
      } else if (errorMessage.contains('TimeoutException')) {
        return '処理がタイムアウトしました。';
      }

      return 'エラーが発生しました: $errorMessage';
    }

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

      final message = handleError(error);
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

      final message = handleError(error);
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

      final message = handleError(error);
      expect(message, contains('email'));
      expect(message, contains('Invalid email format'));
    });

    test('handles connection timeout', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.connectionTimeout,
      );

      final message = handleError(error);
      expect(message, contains('タイムアウト'));
    });

    test('handles connection error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.connectionError,
      );

      final message = handleError(error);
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

      final message = handleError(error);
      expect(message, contains('サーバーエラー'));
    });

    test('handles cancel error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.cancel,
      );

      final message = handleError(error);
      expect(message, contains('キャンセル'));
    });

    test('handles bad certificate error', () {
      final error = DioException(
        requestOptions: RequestOptions(path: '/auth/login'),
        type: DioExceptionType.badCertificate,
      );

      final message = handleError(error);
      expect(message, contains('SSL証明書'));
    });
  });
}
