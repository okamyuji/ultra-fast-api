import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ultra_fast_api/core/providers/core_providers.dart';
import 'package:ultra_fast_api/core/storage/token_manager.dart';
import 'package:ultra_fast_api/features/auth/data/auth_api_service.dart';
import 'package:ultra_fast_api/features/auth/domain/models/login_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/register_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/user_model.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_state.dart';

part 'auth_notifier.g.dart';

/// AuthApiService プロバイダー
@riverpod
AuthApiService authApiService(Ref ref) {
  final apiClient = ref.watch(apiClientProvider);
  return AuthApiService(apiClient);
}

/// 認証 Notifier
@riverpod
class AuthNotifier extends _$AuthNotifier {
  late AuthApiService _authApiService;
  late TokenManager _tokenManager;

  @override
  AuthState build() {
    _tokenManager = ref.watch(tokenManagerProvider);
    _authApiService = ref.watch(authApiServiceProvider);
    _checkAuthStatus();
    return const AuthInitial();
  }

  /// 認証状態をチェック
  Future<void> _checkAuthStatus() async {
    try {
      final isAuthenticated = await _tokenManager.isAuthenticated();
      if (!isAuthenticated) {
        state = const AuthUnauthenticated();
        return;
      }

      // トークンが有効な場合、ユーザー情報を取得
      final accessToken = await _tokenManager.getAccessToken();
      if (accessToken == null) {
        state = const AuthUnauthenticated();
        return;
      }

      // JWTペイロードをデコードしてユーザー情報を取得
      final userInfo = _decodeJwtPayload(accessToken);
      if (userInfo == null) {
        await _tokenManager.clearTokens();
        state = const AuthUnauthenticated();
        return;
      }

      // ユーザー情報で状態を更新
      state = AuthAuthenticated(userInfo);
    } catch (e) {
      // エラー時はトークンをクリアして未認証状態に
      await _tokenManager.clearTokens();
      state = const AuthUnauthenticated();
    }
  }

  /// JWTペイロードからユーザー情報をデコード
  User? _decodeJwtPayload(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;

      // Base64URLデコード
      String payload = parts[1];
      // Base64URL -> Base64変換
      payload = payload.replaceAll('-', '+').replaceAll('_', '/');
      // パディング追加
      switch (payload.length % 4) {
        case 2:
          payload += '==';
          break;
        case 3:
          payload += '=';
          break;
      }

      final decoded = utf8.decode(base64.decode(payload));
      final Map<String, dynamic> payloadData = json.decode(decoded);

      // JWTペイロードからユーザー情報を構築
      return User(
        id: payloadData['sub'] ?? '',
        email: payloadData['email'] ?? '',
        username: payloadData['username'] ?? '',
        fullName: payloadData['full_name'],
        isActive: payloadData['is_active'] ?? true,
        createdAt:
            DateTime.tryParse(payloadData['created_at'] ?? '') ??
            DateTime.now(),
        updatedAt:
            DateTime.tryParse(payloadData['updated_at'] ?? '') ??
            DateTime.now(),
      );
    } catch (e) {
      return null;
    }
  }

  /// ログイン
  Future<void> login({required String email, required String password}) async {
    try {
      state = const AuthLoading();

      final request = LoginRequest(email: email, password: password);
      final response = await _authApiService.login(request);

      // トークンを保存
      await _tokenManager.saveTokens(
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        expiresAt: response.expiresAt,
      );

      state = AuthAuthenticated(response.user);
    } catch (e) {
      state = AuthError(_handleError(e));
    }
  }

  /// 会員登録
  Future<void> register({
    required String email,
    required String password,
    required String username,
    String? fullName,
  }) async {
    try {
      state = const AuthLoading();

      // 1. ユーザー登録
      final request = RegisterRequest(
        email: email,
        password: password,
        username: username,
        fullName: fullName,
      );
      await _authApiService.register(request);

      // 2. 登録成功後、自動的にログイン
      await login(email: email, password: password);
    } catch (e) {
      state = AuthError(_handleError(e));
    }
  }

  /// ログアウト
  Future<void> logout() async {
    try {
      state = const AuthLoading();

      // APIにログアウトリクエスト
      await _authApiService.logout();

      // トークンをクリア
      await _tokenManager.clearTokens();

      state = const AuthUnauthenticated();
    } catch (e) {
      // ログアウト失敗でもトークンはクリア
      await _tokenManager.clearTokens();
      state = const AuthUnauthenticated();
    }
  }

  /// パスワード変更
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      await _authApiService.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// パスワードリセット要求
  Future<void> requestPasswordReset(String email) async {
    try {
      await _authApiService.requestPasswordReset(email);
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// エラーハンドリング
  String _handleError(Object error) {
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
            // バリデーションエラー
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
            // FastAPIのバリデーションエラー
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

    // その他のエラー
    final errorMessage = error.toString();
    if (errorMessage.contains('FormatException')) {
      return 'データの形式が不正です。';
    } else if (errorMessage.contains('TimeoutException')) {
      return '処理がタイムアウトしました。';
    }

    return 'エラーが発生しました: $errorMessage';
  }
}
