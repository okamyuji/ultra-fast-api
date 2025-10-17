import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/settings/domain/models/user_settings_model.dart';

class SettingsApiService {
  final ApiClient _apiClient;

  SettingsApiService(this._apiClient);

  /// ユーザー設定を取得
  Future<UserSettings> getSettings() async {
    final response = await _apiClient.get('/settings');
    return UserSettings.fromJson(response.data);
  }

  /// ユーザー設定を更新
  Future<UserSettings> updateSettings(Map<String, dynamic> data) async {
    final response = await _apiClient.put('/settings', data: data);
    return UserSettings.fromJson(response.data);
  }
}
