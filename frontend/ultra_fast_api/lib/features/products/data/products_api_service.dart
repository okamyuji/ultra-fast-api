import 'package:ultra_fast_api/core/api/api_client.dart';
import 'package:ultra_fast_api/features/products/domain/models/product_model.dart';
import 'package:ultra_fast_api/features/products/domain/models/products_response.dart';

class ProductsApiService {
  final ApiClient _apiClient;

  ProductsApiService(this._apiClient);

  Future<ProductsResponse> getProducts({
    int limit = 20,
    String? cursor,
    String? category,
    String? status,
    String? search,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      if (cursor != null) 'cursor': cursor,
      if (category != null) 'category': category,
      if (status != null) 'status': status,
      if (search != null) 'search': search,
    };

    final response = await _apiClient.get(
      '/products',
      queryParameters: queryParams,
    );
    return ProductsResponse.fromJson(response.data);
  }

  Future<Product> getProduct(String id) async {
    final response = await _apiClient.get('/products/$id');
    return Product.fromJson(response.data);
  }
}
