import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:json_annotation/json_annotation.dart';

part 'app_config.g.dart';

@JsonSerializable()
class AppConfig {
  final String apiBaseUrl;
  final int defaultPageLimit;
  final int connectTimeout;
  final int receiveTimeout;
  final int tokenRefreshThreshold;

  const AppConfig({
    required this.apiBaseUrl,
    required this.defaultPageLimit,
    required this.connectTimeout,
    required this.receiveTimeout,
    required this.tokenRefreshThreshold,
  });

  factory AppConfig.fromJson(Map<String, dynamic> json) =>
      _$AppConfigFromJson(json);

  Map<String, dynamic> toJson() => _$AppConfigToJson(this);

  /// 環境に応じた設定ファイルを読み込む
  static Future<AppConfig> load({String environment = 'default'}) async {
    String configPath;
    switch (environment) {
      case 'dev':
        configPath = 'config/app_config.dev.json';
        break;
      case 'prod':
        configPath = 'config/app_config.prod.json';
        break;
      default:
        configPath = 'config/app_config.json';
    }

    try {
      final configString = await rootBundle.loadString(configPath);
      final configJson = json.decode(configString) as Map<String, dynamic>;
      return AppConfig.fromJson(configJson);
    } catch (e) {
      // デフォルト設定にフォールバック
      return const AppConfig(
        apiBaseUrl: 'http://192.168.0.15:8000',
        defaultPageLimit: 20,
        connectTimeout: 30,
        receiveTimeout: 30,
        tokenRefreshThreshold: 10,
      );
    }
  }
}
