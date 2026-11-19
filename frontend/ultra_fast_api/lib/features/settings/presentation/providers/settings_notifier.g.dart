// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settings_notifier.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(settingsApiService)
final settingsApiServiceProvider = SettingsApiServiceProvider._();

final class SettingsApiServiceProvider
    extends
        $FunctionalProvider<
          SettingsApiService,
          SettingsApiService,
          SettingsApiService
        >
    with $Provider<SettingsApiService> {
  SettingsApiServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'settingsApiServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$settingsApiServiceHash();

  @$internal
  @override
  $ProviderElement<SettingsApiService> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  SettingsApiService create(Ref ref) {
    return settingsApiService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SettingsApiService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SettingsApiService>(value),
    );
  }
}

String _$settingsApiServiceHash() =>
    r'7b0a6c3bd021621d70da7e849d8e209298abd08a';

@ProviderFor(SettingsNotifier)
final settingsProvider = SettingsNotifierProvider._();

final class SettingsNotifierProvider
    extends $NotifierProvider<SettingsNotifier, AsyncValue<UserSettings?>> {
  SettingsNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'settingsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$settingsNotifierHash();

  @$internal
  @override
  SettingsNotifier create() => SettingsNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AsyncValue<UserSettings?> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AsyncValue<UserSettings?>>(value),
    );
  }
}

String _$settingsNotifierHash() => r'a1d1881bb82eede1434a1a9fd0447aa9f7a5faba';

abstract class _$SettingsNotifier extends $Notifier<AsyncValue<UserSettings?>> {
  AsyncValue<UserSettings?> build();
  @$mustCallSuper
  @override
  WhenComplete runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<UserSettings?>, AsyncValue<UserSettings?>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<UserSettings?>, AsyncValue<UserSettings?>>,
              AsyncValue<UserSettings?>,
              Object?,
              Object?
            >;
    return element.handleCreate(ref, build);
  }
}
