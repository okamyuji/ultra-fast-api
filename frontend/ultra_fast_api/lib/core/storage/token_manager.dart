import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:ultra_fast_api/core/constants/app_constants.dart';

/// JWT トークンを安全に保存・管理するクラス
class TokenManager {
  final FlutterSecureStorage _storage;

  TokenManager({FlutterSecureStorage? storage})
    : _storage = storage ?? const FlutterSecureStorage();

  /// アクセストークンを取得
  Future<String?> getAccessToken() async {
    return await _storage.read(key: AppConstants.storageKeyAccessToken);
  }

  /// リフレッシュトークンを取得
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: AppConstants.storageKeyRefreshToken);
  }

  /// トークンの有効期限を取得
  Future<DateTime?> getExpiresAt() async {
    final expiresAtStr = await _storage.read(
      key: AppConstants.storageKeyExpiresAt,
    );
    if (expiresAtStr == null) return null;
    return DateTime.tryParse(expiresAtStr);
  }

  /// トークンを保存
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
    required DateTime expiresAt,
  }) async {
    await Future.wait([
      _storage.write(
        key: AppConstants.storageKeyAccessToken,
        value: accessToken,
      ),
      _storage.write(
        key: AppConstants.storageKeyRefreshToken,
        value: refreshToken,
      ),
      _storage.write(
        key: AppConstants.storageKeyExpiresAt,
        value: expiresAt.toIso8601String(),
      ),
    ]);
  }

  /// トークンを削除（ログアウト時）
  Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: AppConstants.storageKeyAccessToken),
      _storage.delete(key: AppConstants.storageKeyRefreshToken),
      _storage.delete(key: AppConstants.storageKeyExpiresAt),
    ]);
  }

  /// トークンが期限切れかチェック
  Future<bool> isTokenExpired() async {
    final expiresAt = await getExpiresAt();
    if (expiresAt == null) return true;

    final now = DateTime.now();
    final threshold = now.add(AppConstants.tokenRefreshThreshold);

    return threshold.isAfter(expiresAt);
  }

  /// 認証済みかチェック
  Future<bool> isAuthenticated() async {
    final accessToken = await getAccessToken();
    if (accessToken == null) return false;

    return !(await isTokenExpired());
  }
}
