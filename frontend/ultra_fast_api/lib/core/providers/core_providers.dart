import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/core/config/app_config.dart';
import 'package:ultra_fast_api/core/providers/app_config_provider.dart';
import 'package:ultra_fast_api/core/storage/token_manager.dart';

/// TokenManager プロバイダー
final tokenManagerProvider = Provider<TokenManager>((ref) {
  return TokenManager();
});

/// ApiClient プロバイダー
final apiClientProvider = Provider<ApiClient>((ref) {
  // AppConfigを同期的に取得（エラー時はデフォルト値を使用）
  final configAsync = ref.watch(appConfigProvider);
  final config = configAsync.maybeWhen(
    data: (config) => config,
    orElse: () => const AppConfig(
      apiBaseUrl: 'http://192.168.0.15:8000',
      defaultPageLimit: 20,
      connectTimeout: 30,
      receiveTimeout: 30,
      tokenRefreshThreshold: 10,
    ),
  );

  final tokenManager = ref.watch(tokenManagerProvider);
  return ApiClient(config: config, tokenManager: tokenManager);
});
