/// アプリケーション全体で使用する定数
class AppConstants {
  AppConstants._();

  /// API Base URL
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  /// JWT Access Token 有効期限 (時間)
  static const int accessTokenExpireHours = 24;

  /// JWT Refresh Token 有効期限 (日数)
  static const int refreshTokenExpireDays = 30;

  /// ページネーション デフォルトページサイズ
  static const int defaultPageSize = 100;

  /// トークン更新タイミング (期限の10分前)
  static const Duration tokenRefreshThreshold = Duration(minutes: 10);

  /// HTTP タイムアウト
  static const Duration httpTimeout = Duration(seconds: 30);

  /// Secure Storage Keys
  static const String storageKeyAccessToken = 'access_token';
  static const String storageKeyRefreshToken = 'refresh_token';
  static const String storageKeyExpiresAt = 'expires_at';
}
