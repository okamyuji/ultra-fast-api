import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ultra_fast_api/features/products/presentation/providers/products_notifier.dart';
import 'package:ultra_fast_api/shared/widgets/loading_indicator.dart';

class ProductDetailScreen extends ConsumerWidget {
  final String productId;

  const ProductDetailScreen({super.key, required this.productId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final product = ref.watch(productDetailProvider(productId));

    return Scaffold(
      appBar: AppBar(title: const Text('商品詳細')),
      body: product == null
          ? const LoadingIndicator(message: '商品を読み込み中...')
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.name,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '¥${product.price.toStringAsFixed(0)}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Chip(label: Text(product.category)),
                      const SizedBox(width: 8),
                      Chip(label: Text(product.status)),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text('商品説明', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(product.description ?? '説明なし'),
                  const SizedBox(height: 24),
                  Text(
                    '在庫: ${product.stock}個',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    '登録日: ${product.createdAt.toLocal()}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  Text(
                    '更新日: ${product.updatedAt.toLocal()}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
    );
  }
}
