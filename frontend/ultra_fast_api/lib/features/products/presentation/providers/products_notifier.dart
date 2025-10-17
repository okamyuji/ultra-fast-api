import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ultra_fast_api/core/providers/core_providers.dart';
import 'package:ultra_fast_api/features/products/data/products_api_service.dart';
import 'package:ultra_fast_api/features/products/domain/models/product_model.dart';
import 'package:ultra_fast_api/features/products/presentation/providers/products_state.dart';

part 'products_notifier.g.dart';

@riverpod
ProductsApiService productsApiService(Ref ref) {
  final apiClient = ref.watch(apiClientProvider);
  return ProductsApiService(apiClient);
}

@riverpod
class ProductsNotifier extends _$ProductsNotifier {
  late ProductsApiService _productsApiService;
  List<Product> _allProducts = [];
  String? _nextCursor;
  // 現在のフィルター条件を保持
  String? _currentCategory;
  String? _currentStatus;
  String? _currentSearch;

  @override
  ProductsState build() {
    _productsApiService = ref.watch(productsApiServiceProvider);
    // 初回ロード（フィルターなし）
    Future.microtask(() => loadProducts());
    return const ProductsInitial();
  }

  Future<void> loadProducts({
    String? category,
    String? status,
    String? search,
    bool refresh = false,
  }) async {
    // フィルター条件を更新
    _currentCategory = category;
    _currentStatus = status;
    _currentSearch = search;

    if (!refresh) {
      state = const ProductsState.loading();
    }
    try {
      final response = await _productsApiService.getProducts(
        category: category,
        status: status,
        search: search,
      );
      _allProducts = response.items;
      _nextCursor = response.nextCursor;
      state = ProductsState.loaded(
        products: _allProducts,
        nextCursor: _nextCursor,
        total: response.total,
        hasMore: response.nextCursor != null,
      );
    } catch (e) {
      state = ProductsState.error(e.toString());
    }
  }

  Future<void> loadMore({
    String? category,
    String? status,
    String? search,
  }) async {
    final currentState = state;
    if (currentState is! ProductsLoaded) return;
    if (!currentState.hasMore) return;

    try {
      // 現在のフィルター条件を使用
      final response = await _productsApiService.getProducts(
        cursor: currentState.nextCursor,
        category: _currentCategory,
        status: _currentStatus,
        search: _currentSearch,
      );
      _allProducts.addAll(response.items);
      _nextCursor = response.nextCursor;
      state = ProductsState.loaded(
        products: _allProducts,
        nextCursor: _nextCursor,
        total: response.total,
        hasMore: response.nextCursor != null,
      );
    } catch (e) {
      state = currentState.copyWith(isLoadMoreError: true);
    }
  }
}

@riverpod
class ProductDetailNotifier extends _$ProductDetailNotifier {
  late ProductsApiService _productsApiService;

  @override
  Product? build(String productId) {
    _productsApiService = ref.watch(productsApiServiceProvider);
    _loadProduct(productId);
    return null;
  }

  Future<void> _loadProduct(String id) async {
    try {
      final product = await _productsApiService.getProduct(id);
      state = product;
    } catch (e) {
      state = null;
    }
  }
}
