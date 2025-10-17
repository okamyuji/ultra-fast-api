import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/products/data/products_api_service.dart';
import 'package:ultra_fast_api/features/products/domain/models/product_model.dart';
import 'package:ultra_fast_api/features/products/domain/models/products_response.dart';

import 'products_api_service_test.mocks.dart';

@GenerateMocks([ApiClient])
void main() {
  late ProductsApiService productsApiService;
  late MockApiClient mockApiClient;

  setUp(() {
    mockApiClient = MockApiClient();
    productsApiService = ProductsApiService(mockApiClient);
  });

  group('ProductsApiService', () {
    test('getProducts returns ProductsResponse on success', () async {
      final mockResponse = Response(
        data: {
          'items': [
            {
              'id': '1',
              'name': 'Test Product',
              'description': 'Test Description',
              'price': 1000.0,
              'category': 'electronics',
              'status': 'active',
              'stock': 10,
              'user_id': 'user123',
              'created_at': '2024-01-01T00:00:00Z',
              'updated_at': '2024-01-01T00:00:00Z',
            },
          ],
          'pagination': {
            'next_cursor': 'cursor123',
            'has_more': true,
            'returned_count': 1,
            'total_count_estimate': 100,
          },
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/products'),
      );

      when(
        mockApiClient.get(
          '/products',
          queryParameters: anyNamed('queryParameters'),
        ),
      ).thenAnswer((_) async => mockResponse);

      final result = await productsApiService.getProducts();

      expect(result, isA<ProductsResponse>());
      expect(result.items.length, 1);
      expect(result.items[0].name, 'Test Product');
      expect(result.nextCursor, 'cursor123');
      expect(result.total, 100);
    });

    test('getProduct returns Product on success', () async {
      final mockResponse = Response(
        data: {
          'id': '1',
          'name': 'Test Product',
          'description': 'Test Description',
          'price': 1000.0,
          'category': 'electronics',
          'status': 'active',
          'stock': 10,
          'user_id': 'user123',
          'created_at': '2024-01-01T00:00:00Z',
          'updated_at': '2024-01-01T00:00:00Z',
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/products/1'),
      );

      when(
        mockApiClient.get('/products/1'),
      ).thenAnswer((_) async => mockResponse);

      final result = await productsApiService.getProduct('1');

      expect(result, isA<Product>());
      expect(result.id, '1');
      expect(result.name, 'Test Product');
    });

    test('getProducts with filters applies query parameters', () async {
      final mockResponse = Response(
        data: {
          'items': [],
          'pagination': {
            'next_cursor': null,
            'has_more': false,
            'returned_count': 0,
            'total_count_estimate': null,
          },
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/products'),
      );

      when(
        mockApiClient.get(
          '/products',
          queryParameters: anyNamed('queryParameters'),
        ),
      ).thenAnswer((_) async => mockResponse);

      await productsApiService.getProducts(
        limit: 50,
        cursor: 'cursor123',
        category: 'electronics',
        status: 'active',
        search: 'test',
      );

      verify(
        mockApiClient.get(
          '/products',
          queryParameters: {
            'limit': 50,
            'cursor': 'cursor123',
            'category': 'electronics',
            'status': 'active',
            'search': 'test',
          },
        ),
      ).called(1);
    });
  });
}
