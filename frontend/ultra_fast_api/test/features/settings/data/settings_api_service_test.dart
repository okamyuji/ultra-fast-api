import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/settings/data/settings_api_service.dart';
import 'package:ultra_fast_api/features/settings/domain/models/user_settings_model.dart';

import '../../products/data/products_api_service_test.mocks.dart';

@GenerateMocks([ApiClient])
void main() {
  late SettingsApiService settingsApiService;
  late MockApiClient mockApiClient;

  setUp(() {
    mockApiClient = MockApiClient();
    settingsApiService = SettingsApiService(mockApiClient);
  });

  group('SettingsApiService', () {
    test('getSettings returns UserSettings on success', () async {
      final mockResponse = Response(
        data: {
          'id': '1',
          'user_id': 'user123',
          'theme': 'dark',
          'default_page_size': 20,
          'created_at': '2024-01-01T00:00:00Z',
          'updated_at': '2024-01-01T00:00:00Z',
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/settings'),
      );

      when(
        mockApiClient.get('/settings'),
      ).thenAnswer((_) async => mockResponse);

      final result = await settingsApiService.getSettings();

      expect(result, isA<UserSettings>());
      expect(result.theme, 'dark');
    });

    test('updateSettings returns updated UserSettings', () async {
      final mockResponse = Response(
        data: {
          'id': '1',
          'user_id': 'user123',
          'theme': 'light',
          'default_page_size': 50,
          'created_at': '2024-01-01T00:00:00Z',
          'updated_at': '2024-01-01T01:00:00Z',
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/settings'),
      );

      when(
        mockApiClient.put('/settings', data: anyNamed('data')),
      ).thenAnswer((_) async => mockResponse);

      final result = await settingsApiService.updateSettings({
        'theme': 'light',
      });

      expect(result, isA<UserSettings>());
      expect(result.theme, 'light');
      verify(
        mockApiClient.put('/settings', data: {'theme': 'light'}),
      ).called(1);
    });
  });
}
