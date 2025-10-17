import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:ultra_fast_api/core/config/app_config.dart';
import 'package:ultra_fast_api/core/storage/token_manager.dart';

/// API通信を管理するクライアントクラス
class ApiClient {
  final Dio _dio;
  final TokenManager _tokenManager;
  final AppConfig _config;

  ApiClient({required AppConfig config, Dio? dio, TokenManager? tokenManager})
    : _config = config,
      _dio = dio ?? Dio(),
      _tokenManager = tokenManager ?? TokenManager() {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.options.baseUrl = _config.apiBaseUrl;
    _dio.options.connectTimeout = Duration(seconds: _config.connectTimeout);
    _dio.options.receiveTimeout = Duration(seconds: _config.receiveTimeout);

    // 詳細ログ出力
    debugPrint('🌐 [ApiClient] Base URL: ${_config.apiBaseUrl}');
    debugPrint('⏱️  [ApiClient] Connect Timeout: ${_config.connectTimeout}s');
    debugPrint('⏱️  [ApiClient] Receive Timeout: ${_config.receiveTimeout}s');

    // リクエストインターセプター: JWT トークンを自動付与
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          debugPrint('📤 [REQUEST] ${options.method} ${options.uri}');
          debugPrint('   Headers: ${options.headers}');
          if (options.data != null) {
            debugPrint('   Data: ${options.data}');
          }

          final accessToken = await _tokenManager.getAccessToken();
          if (accessToken != null) {
            options.headers['Authorization'] = 'Bearer $accessToken';
            debugPrint('   🔑 Token attached');
          }
          return handler.next(options);
        },
        onResponse: (response, handler) {
          debugPrint(
            '📥 [RESPONSE] ${response.statusCode} ${response.requestOptions.uri}',
          );
          debugPrint('   Data: ${response.data}');
          return handler.next(response);
        },
        onError: (error, handler) async {
          debugPrint('❌ [ERROR] ${error.requestOptions.uri}');
          debugPrint('   Type: ${error.type}');
          debugPrint('   Message: ${error.message}');
          debugPrint('   Status Code: ${error.response?.statusCode}');
          if (error.response?.data != null) {
            debugPrint('   Response Data: ${error.response?.data}');
          }
          // 401または403エラー時、トークンリフレッシュを試行
          if (error.response?.statusCode == 401 ||
              error.response?.statusCode == 403) {
            try {
              final refreshToken = await _tokenManager.getRefreshToken();
              if (refreshToken != null) {
                debugPrint('🔄 [REFRESH] Attempting token refresh...');
                // トークンリフレッシュ
                final response = await _dio.post(
                  '/auth/refresh',
                  data: {'refresh_token': refreshToken},
                );

                if (response.statusCode == 200) {
                  final data = response.data;
                  await _tokenManager.saveTokens(
                    accessToken: data['access_token'],
                    refreshToken: data['refresh_token'],
                    expiresAt: DateTime.now().add(
                      Duration(seconds: data['expires_in'] as int),
                    ),
                  );

                  debugPrint('✅ [REFRESH] Token refreshed successfully');

                  // 元のリクエストを再試行
                  final opts = error.requestOptions;
                  opts.headers['Authorization'] =
                      'Bearer ${data['access_token']}';
                  final retryResponse = await _dio.fetch(opts);
                  return handler.resolve(retryResponse);
                }
              }
            } catch (e) {
              debugPrint('❌ [REFRESH] Token refresh failed: $e');
              // リフレッシュ失敗 -> トークンクリア
              await _tokenManager.clearTokens();
              // 401エラーとして返す（AuthNotifierで処理される）
              return handler.reject(
                DioException(
                  requestOptions: error.requestOptions,
                  response: Response(
                    requestOptions: error.requestOptions,
                    statusCode: 401,
                    statusMessage: 'Token refresh failed',
                  ),
                  type: DioExceptionType.badResponse,
                  message: 'Authentication failed',
                ),
              );
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  /// GET リクエスト
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.get(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// POST リクエスト
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// PUT リクエスト
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.put(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// DELETE リクエスト
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await _dio.delete(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// Dio インスタンスを取得（必要に応じて）
  Dio get dio => _dio;
}
