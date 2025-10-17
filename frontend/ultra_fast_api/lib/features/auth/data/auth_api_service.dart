import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/auth/domain/models/auth_response.dart';
import 'package:ultra_fast_api/features/auth/domain/models/login_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/register_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/user_model.dart';

/// 認証API サービス
class AuthApiService {
  final ApiClient _apiClient;

  AuthApiService(this._apiClient);

  /// ログイン
  Future<AuthResponse> login(LoginRequest request) async {
    final response = await _apiClient.post(
      '/auth/login',
      data: request.toJson(),
    );
    return AuthResponse.fromJson(response.data);
  }

  /// 会員登録（UserResponseのみ返す）
  Future<User> register(RegisterRequest request) async {
    final response = await _apiClient.post(
      '/auth/register',
      data: request.toJson(),
    );
    return User.fromJson(response.data);
  }

  /// トークンリフレッシュ
  Future<AuthResponse> refreshToken(String refreshToken) async {
    final response = await _apiClient.post(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    return AuthResponse.fromJson(response.data);
  }

  /// ログアウト
  Future<void> logout({String? deviceId}) async {
    await _apiClient.post(
      '/auth/logout',
      data: deviceId != null ? {'device_id': deviceId} : null,
    );
  }

  /// パスワードリセット要求
  Future<void> requestPasswordReset(String email) async {
    await _apiClient.post(
      '/auth/request-password-reset',
      data: {'email': email},
    );
  }

  /// パスワードリセット確認
  Future<void> confirmPasswordReset({
    required String token,
    required String newPassword,
  }) async {
    await _apiClient.post(
      '/auth/confirm-password-reset',
      data: {'token': token, 'new_password': newPassword},
    );
  }

  /// パスワード変更
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _apiClient.post(
      '/auth/change-password',
      data: {'current_password': currentPassword, 'new_password': newPassword},
    );
  }
}
