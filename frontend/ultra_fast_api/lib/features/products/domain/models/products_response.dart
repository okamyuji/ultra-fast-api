import 'package:json_annotation/json_annotation.dart';
import 'package:ultra_fast_api/features/products/domain/models/product_model.dart';

part 'products_response.g.dart';

@JsonSerializable()
class PaginationMeta {
  @JsonKey(name: 'next_cursor')
  final String? nextCursor;
  @JsonKey(name: 'has_more')
  final bool hasMore;
  @JsonKey(name: 'returned_count')
  final int returnedCount;
  @JsonKey(name: 'total_count_estimate')
  final int? totalCountEstimate;

  PaginationMeta({
    this.nextCursor,
    required this.hasMore,
    required this.returnedCount,
    this.totalCountEstimate,
  });

  factory PaginationMeta.fromJson(Map<String, dynamic> json) =>
      _$PaginationMetaFromJson(json);
  Map<String, dynamic> toJson() => _$PaginationMetaToJson(this);
}

@JsonSerializable()
class ProductsResponse {
  final List<Product> items;
  final PaginationMeta pagination;

  ProductsResponse({required this.items, required this.pagination});

  /// 互換性のために追加
  String? get nextCursor => pagination.nextCursor;
  int get total => pagination.totalCountEstimate ?? pagination.returnedCount;

  factory ProductsResponse.fromJson(Map<String, dynamic> json) =>
      _$ProductsResponseFromJson(json);
  Map<String, dynamic> toJson() => _$ProductsResponseToJson(this);
}
