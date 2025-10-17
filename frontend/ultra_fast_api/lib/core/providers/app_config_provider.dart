import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ultra_fast_api/core/config/app_config.dart';

part 'app_config_provider.g.dart';

@Riverpod(keepAlive: true)
Future<AppConfig> appConfig(Ref ref) async {
  // 環境変数から環境を取得（デフォルトは本番設定）
  const environment = String.fromEnvironment('ENV', defaultValue: 'default');
  return await AppConfig.load(environment: environment);
}
