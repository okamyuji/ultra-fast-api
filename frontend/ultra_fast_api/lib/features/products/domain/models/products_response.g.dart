// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'products_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PaginationMeta _$PaginationMetaFromJson(Map<String, dynamic> json) =>
    PaginationMeta(
      nextCursor: json['next_cursor'] as String?,
      hasMore: json['has_more'] as bool,
      returnedCount: (json['returned_count'] as num).toInt(),
      totalCountEstimate: (json['total_count_estimate'] as num?)?.toInt(),
    );

Map<String, dynamic> _$PaginationMetaToJson(PaginationMeta instance) =>
    <String, dynamic>{
      'next_cursor': instance.nextCursor,
      'has_more': instance.hasMore,
      'returned_count': instance.returnedCount,
      'total_count_estimate': instance.totalCountEstimate,
    };

ProductsResponse _$ProductsResponseFromJson(Map<String, dynamic> json) =>
    ProductsResponse(
      items: (json['items'] as List<dynamic>)
          .map((e) => Product.fromJson(e as Map<String, dynamic>))
          .toList(),
      pagination: PaginationMeta.fromJson(
        json['pagination'] as Map<String, dynamic>,
      ),
    );

Map<String, dynamic> _$ProductsResponseToJson(ProductsResponse instance) =>
    <String, dynamic>{
      'items': instance.items,
      'pagination': instance.pagination,
    };
