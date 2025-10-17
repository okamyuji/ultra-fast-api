import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/auth/data/auth_api_service.dart';
import 'package:ultra_fast_api/features/auth/domain/models/auth_response.dart';
import 'package:ultra_fast_api/features/auth/domain/models/login_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/register_request.dart';
import 'package:ultra_fast_api/features/auth/domain/models/user_model.dart';

import 'auth_api_service_test.mocks.dart';

@GenerateMocks([ApiClient])
void main() {
  late AuthApiService authApiService;
  late MockApiClient mockApiClient;

  setUp(() {
    mockApiClient = MockApiClient();
    authApiService = AuthApiService(mockApiClient);
  });

  group('AuthApiService', () {
    test('login returns AuthResponse on success', () async {
      final request = LoginRequest(
        email: 'test@example.com',
        password: 'password123',
      );
      final mockResponse = Response(
        data: {
          'access_token': 'token123',
          'refresh_token': 'refresh123',
          'token_type': 'bearer',
          'expires_in': 86400,
          'user': {
            'id': '1',
            'email': 'test@example.com',
            'username': 'testuser',
            'is_active': true,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
          },
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/auth/login'),
      );

      when(
        mockApiClient.post('/auth/login', data: anyNamed('data')),
      ).thenAnswer((_) async => mockResponse);

      final result = await authApiService.login(request);

      expect(result, isA<AuthResponse>());
      expect(result.accessToken, 'token123');
      expect(result.user.email, 'test@example.com');
    });

    test('register returns User on success', () async {
      final request = RegisterRequest(
        email: 'new@example.com',
        password: 'password123',
        username: 'newuser',
      );
      final mockResponse = Response(
        data: {
          'id': '2',
          'email': 'new@example.com',
          'username': 'newuser',
          'is_active': true,
          'created_at': '2024-01-01T00:00:00Z',
          'updated_at': '2024-01-01T00:00:00Z',
        },
        statusCode: 201,
        requestOptions: RequestOptions(path: '/auth/register'),
      );

      when(
        mockApiClient.post('/auth/register', data: anyNamed('data')),
      ).thenAnswer((_) async => mockResponse);

      final result = await authApiService.register(request);

      expect(result, isA<User>());
      expect(result.username, 'newuser');
      expect(result.email, 'new@example.com');
    });

    test('logout calls API endpoint', () async {
      when(mockApiClient.post('/auth/logout', data: null)).thenAnswer(
        (_) async => Response(
          statusCode: 200,
          requestOptions: RequestOptions(path: '/auth/logout'),
        ),
      );

      await authApiService.logout();

      verify(mockApiClient.post('/auth/logout', data: null)).called(1);
    });
  });
}
