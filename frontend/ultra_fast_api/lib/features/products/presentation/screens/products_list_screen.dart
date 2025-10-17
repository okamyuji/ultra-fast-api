import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ultra_fast_api/core/router/app_router.dart';
import 'package:ultra_fast_api/features/products/presentation/providers/products_notifier.dart';
import 'package:ultra_fast_api/features/products/presentation/providers/products_state.dart';
import 'package:ultra_fast_api/shared/widgets/error_view.dart';
import 'package:ultra_fast_api/shared/widgets/loading_indicator.dart';

class ProductsListScreen extends ConsumerStatefulWidget {
  /// AppBarを表示するかどうか
  final bool showAppBar;

  const ProductsListScreen({super.key, this.showAppBar = true});

  @override
  ConsumerState<ProductsListScreen> createState() => _ProductsListScreenState();
}

class _ProductsListScreenState extends ConsumerState<ProductsListScreen> {
  final _scrollController = ScrollController();
  String? _selectedCategory;
  String? _selectedStatus;
  String? _searchQuery;

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(productsProvider.notifier).loadProducts(refresh: true);
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent * 0.8) {
      final state = ref.read(productsProvider);
      if (state is ProductsLoaded && state.hasMore) {
        ref
            .read(productsProvider.notifier)
            .loadMore(
              category: _selectedCategory,
              status: _selectedStatus,
              search: _searchQuery,
            );
      }
    }
  }

  void _onSearch(String query) {
    setState(() {
      _searchQuery = query.isEmpty ? null : query;
    });
    ref
        .read(productsProvider.notifier)
        .loadProducts(
          search: _searchQuery,
          category: _selectedCategory,
          status: _selectedStatus,
          refresh: true,
        );
  }

  void _onFilterChanged() {
    ref
        .read(productsProvider.notifier)
        .loadProducts(
          category: _selectedCategory,
          status: _selectedStatus,
          search: _searchQuery,
          refresh: true,
        );
  }

  @override
  Widget build(BuildContext context) {
    final productsState = ref.watch(productsProvider);

    final bodyContent = Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: '商品を検索...',
                    prefixIcon: Icon(Icons.search),
                  ),
                  onSubmitted: _onSearch,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.filter_list),
                onPressed: () => _showFilterDialog(),
                tooltip: 'フィルター',
              ),
            ],
          ),
        ),
        Expanded(child: _buildBody(productsState)),
      ],
    );

    // タブナビゲーション内で使用される場合はAppBarなし
    if (!widget.showAppBar) {
      return bodyContent;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('商品一覧')),
      body: bodyContent,
    );
  }

  Widget _buildBody(ProductsState state) {
    if (state is ProductsLoading) {
      return const LoadingIndicator(message: '商品を読み込み中...');
    } else if (state is ProductsError) {
      return ErrorView(
        message: state.message,
        onRetry: () =>
            ref.read(productsProvider.notifier).loadProducts(refresh: true),
      );
    } else if (state is ProductsLoaded) {
      if (state.products.isEmpty) {
        return const Center(child: Text('商品が見つかりません'));
      }
      return RefreshIndicator(
        onRefresh: () => ref
            .read(productsProvider.notifier)
            .loadProducts(
              category: _selectedCategory,
              status: _selectedStatus,
              search: _searchQuery,
              refresh: true,
            ),
        child: ListView.builder(
          controller: _scrollController,
          itemCount: state.products.length + (state.hasMore ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == state.products.length) {
              return const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(child: CircularProgressIndicator()),
              );
            }
            final product = state.products[index];
            return Card(
              margin: const EdgeInsets.symmetric(
                horizontal: 8.0,
                vertical: 4.0,
              ),
              child: ListTile(
                contentPadding: const EdgeInsets.all(12.0),
                title: Text(
                  product.name,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 4),
                    Text(
                      '¥${product.price.toStringAsFixed(0)}',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Theme.of(context).primaryColor,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _getCategoryLabel(product.category),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () =>
                    context.push('${AppRouter.home}/products/${product.id}'),
              ),
            );
          },
        ),
      );
    }
    return const SizedBox.shrink();
  }

  void _showFilterDialog() {
    String? tempCategory = _selectedCategory;
    String? tempStatus = _selectedStatus;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('フィルター'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('カテゴリ', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: tempCategory,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: null, child: Text('すべて')),
                  DropdownMenuItem(value: 'electronics', child: Text('電化製品')),
                  DropdownMenuItem(value: 'clothing', child: Text('衣類')),
                  DropdownMenuItem(value: 'food', child: Text('食品')),
                ],
                onChanged: (value) {
                  tempCategory = value;
                },
              ),
              const SizedBox(height: 16),
              const Text(
                'ステータス',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: tempStatus,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                ),
                items: const [
                  DropdownMenuItem(value: null, child: Text('すべて')),
                  DropdownMenuItem(value: 'active', child: Text('有効')),
                  DropdownMenuItem(value: 'inactive', child: Text('無効')),
                ],
                onChanged: (value) {
                  tempStatus = value;
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('キャンセル'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _selectedCategory = tempCategory;
                _selectedStatus = tempStatus;
              });
              Navigator.pop(context);
              _onFilterChanged();
            },
            child: const Text('適用'),
          ),
        ],
      ),
    );
  }

  String _getCategoryLabel(String category) {
    switch (category) {
      case 'electronics':
        return '電化製品';
      case 'clothing':
        return '衣類';
      case 'food':
        return '食品';
      default:
        return category;
    }
  }
}
