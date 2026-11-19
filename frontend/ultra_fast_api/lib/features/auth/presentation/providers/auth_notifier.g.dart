// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_notifier.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// AuthApiService プロバイダー

@ProviderFor(authApiService)
final authApiServiceProvider = AuthApiServiceProvider._();

/// AuthApiService プロバイダー

final class AuthApiServiceProvider
    extends $FunctionalProvider<AuthApiService, AuthApiService, AuthApiService>
    with $Provider<AuthApiService> {
  /// AuthApiService プロバイダー
  AuthApiServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authApiServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authApiServiceHash();

  @$internal
  @override
  $ProviderElement<AuthApiService> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  AuthApiService create(Ref ref) {
    return authApiService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthApiService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthApiService>(value),
    );
  }
}

String _$authApiServiceHash() => r'2fa6578a04d8b1fc18facbc9c46cadf9ca237903';

/// 認証 Notifier

@ProviderFor(AuthNotifier)
final authProvider = AuthNotifierProvider._();

/// 認証 Notifier
final class AuthNotifierProvider
    extends $NotifierProvider<AuthNotifier, AuthState> {
  /// 認証 Notifier
  AuthNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authNotifierHash();

  @$internal
  @override
  AuthNotifier create() => AuthNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AuthState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AuthState>(value),
    );
  }
}

String _$authNotifierHash() => r'd78da7d03f0f60a19aaf3a800d9ae53900de920e';

/// 認証 Notifier

abstract class _$AuthNotifier extends $Notifier<AuthState> {
  AuthState build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref = this.ref as $Ref<AuthState, AuthState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AuthState, AuthState>,
              AuthState,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}
