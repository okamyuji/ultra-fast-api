// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'products_notifier.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(productsApiService)
const productsApiServiceProvider = ProductsApiServiceProvider._();

final class ProductsApiServiceProvider
    extends
        $FunctionalProvider<
          ProductsApiService,
          ProductsApiService,
          ProductsApiService
        >
    with $Provider<ProductsApiService> {
  const ProductsApiServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'productsApiServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$productsApiServiceHash();

  @$internal
  @override
  $ProviderElement<ProductsApiService> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ProductsApiService create(Ref ref) {
    return productsApiService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ProductsApiService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ProductsApiService>(value),
    );
  }
}

String _$productsApiServiceHash() =>
    r'7f8f237d629861ce93952fa219fee3953339823a';

@ProviderFor(ProductsNotifier)
const productsProvider = ProductsNotifierProvider._();

final class ProductsNotifierProvider
    extends $NotifierProvider<ProductsNotifier, ProductsState> {
  const ProductsNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'productsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$productsNotifierHash();

  @$internal
  @override
  ProductsNotifier create() => ProductsNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ProductsState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ProductsState>(value),
    );
  }
}

String _$productsNotifierHash() => r'a557e6b95c1128db9b555637e99aa36b75deda51';

abstract class _$ProductsNotifier extends $Notifier<ProductsState> {
  ProductsState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final created = build();
    final ref = this.ref as $Ref<ProductsState, ProductsState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ProductsState, ProductsState>,
              ProductsState,
              Object?,
              Object?
            >;
    element.handleValue(ref, created);
  }
}

@ProviderFor(ProductDetailNotifier)
const productDetailProvider = ProductDetailNotifierFamily._();

final class ProductDetailNotifierProvider
    extends $NotifierProvider<ProductDetailNotifier, Product?> {
  const ProductDetailNotifierProvider._({
    required ProductDetailNotifierFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'productDetailProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$productDetailNotifierHash();

  @override
  String toString() {
    return r'productDetailProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  ProductDetailNotifier create() => ProductDetailNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Product? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Product?>(value),
    );
  }

  @override
  bool operator ==(Object other) {
    return other is ProductDetailNotifierProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$productDetailNotifierHash() =>
    r'e780f927fc823e0bdc71205e8064f69bf45aee50';

final class ProductDetailNotifierFamily extends $Family
    with
        $ClassFamilyOverride<
          ProductDetailNotifier,
          Product?,
          Product?,
          Product?,
          String
        > {
  const ProductDetailNotifierFamily._()
    : super(
        retry: null,
        name: r'productDetailProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ProductDetailNotifierProvider call(String productId) =>
      ProductDetailNotifierProvider._(argument: productId, from: this);

  @override
  String toString() => r'productDetailProvider';
}

abstract class _$ProductDetailNotifier extends $Notifier<Product?> {
  late final _$args = ref.$arg as String;
  String get productId => _$args;

  Product? build(String productId);
  @$mustCallSuper
  @override
  void runBuild() {
    final created = build(_$args);
    final ref = this.ref as $Ref<Product?, Product?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Product?, Product?>,
              Product?,
              Object?,
              Object?
            >;
    element.handleValue(ref, created);
  }
}
