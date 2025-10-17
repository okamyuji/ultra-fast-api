import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:ultra_fast_api/features/products/domain/models/product_model.dart';

part 'products_state.freezed.dart';

@freezed
sealed class ProductsState with _$ProductsState {
  const factory ProductsState.initial() = ProductsInitial;
  const factory ProductsState.loading() = ProductsLoading;
  const factory ProductsState.loaded({
    required List<Product> products,
    String? nextCursor,
    required int total,
    required bool hasMore,
    @Default(false) bool isLoadMoreError,
  }) = ProductsLoaded;
  const factory ProductsState.error(String message) = ProductsError;
}
