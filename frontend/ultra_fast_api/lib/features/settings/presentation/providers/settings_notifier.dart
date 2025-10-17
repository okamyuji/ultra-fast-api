import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ultra_fast_api/core/providers/core_providers.dart';
import 'package:ultra_fast_api/features/settings/data/settings_api_service.dart';
import 'package:ultra_fast_api/features/settings/domain/models/user_settings_model.dart';

part 'settings_notifier.g.dart';

@riverpod
SettingsApiService settingsApiService(Ref ref) {
  final apiClient = ref.watch(apiClientProvider);
  return SettingsApiService(apiClient);
}

@riverpod
class SettingsNotifier extends _$SettingsNotifier {
  late SettingsApiService _settingsApiService;

  @override
  AsyncValue<UserSettings?> build() {
    _settingsApiService = ref.watch(settingsApiServiceProvider);
    _loadSettings();
    return const AsyncValue.loading();
  }

  Future<void> _loadSettings() async {
    try {
      final settings = await _settingsApiService.getSettings();
      state = AsyncValue.data(settings);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> updateSettings(Map<String, dynamic> data) async {
    try {
      final updated = await _settingsApiService.updateSettings(data);
      state = AsyncValue.data(updated);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
