import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:ultra_fast_api/core/storage/token_manager.dart';

import 'token_manager_test.mocks.dart';

@GenerateMocks([FlutterSecureStorage])
void main() {
  late TokenManager tokenManager;
  late MockFlutterSecureStorage mockStorage;

  setUp(() {
    mockStorage = MockFlutterSecureStorage();
    tokenManager = TokenManager(storage: mockStorage);
  });

  group('TokenManager', () {
    test('saveTokens saves all tokens', () async {
      when(
        mockStorage.write(key: anyNamed('key'), value: anyNamed('value')),
      ).thenAnswer((_) async => {});

      await tokenManager.saveTokens(
        accessToken: 'access123',
        refreshToken: 'refresh123',
        expiresAt: DateTime(2025, 12, 31),
      );

      verify(
        mockStorage.write(key: 'access_token', value: 'access123'),
      ).called(1);
      verify(
        mockStorage.write(key: 'refresh_token', value: 'refresh123'),
      ).called(1);
    });

    test('getAccessToken returns stored token', () async {
      when(
        mockStorage.read(key: 'access_token'),
      ).thenAnswer((_) async => 'access123');

      final result = await tokenManager.getAccessToken();

      expect(result, 'access123');
      verify(mockStorage.read(key: 'access_token')).called(1);
    });

    test('getRefreshToken returns stored token', () async {
      when(
        mockStorage.read(key: 'refresh_token'),
      ).thenAnswer((_) async => 'refresh123');

      final result = await tokenManager.getRefreshToken();

      expect(result, 'refresh123');
      verify(mockStorage.read(key: 'refresh_token')).called(1);
    });

    test('clearTokens deletes all tokens', () async {
      when(
        mockStorage.delete(key: anyNamed('key')),
      ).thenAnswer((_) async => {});

      await tokenManager.clearTokens();

      verify(mockStorage.delete(key: 'access_token')).called(1);
      verify(mockStorage.delete(key: 'refresh_token')).called(1);
      verify(mockStorage.delete(key: 'expires_at')).called(1);
    });

    test('getExpiresAt returns DateTime when stored', () async {
      when(
        mockStorage.read(key: 'expires_at'),
      ).thenAnswer((_) async => '2025-12-31 23:59:59.000');

      final result = await tokenManager.getExpiresAt();

      expect(result, isNotNull);
      expect(result!.year, 2025);
      expect(result.month, 12);
    });

    test('getExpiresAt returns null when not stored', () async {
      when(mockStorage.read(key: 'expires_at')).thenAnswer((_) async => null);

      final result = await tokenManager.getExpiresAt();

      expect(result, null);
    });
  });
}
