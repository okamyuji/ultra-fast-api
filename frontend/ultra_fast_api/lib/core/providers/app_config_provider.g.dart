// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_config_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(appConfig)
const appConfigProvider = AppConfigProvider._();

final class AppConfigProvider
    extends
        $FunctionalProvider<
          AsyncValue<AppConfig>,
          AppConfig,
          FutureOr<AppConfig>
        >
    with $FutureModifier<AppConfig>, $FutureProvider<AppConfig> {
  const AppConfigProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'appConfigProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$appConfigHash();

  @$internal
  @override
  $FutureProviderElement<AppConfig> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<AppConfig> create(Ref ref) {
    return appConfig(ref);
  }
}

String _$appConfigHash() => r'6e3c984bbb64ae648a386a1a54df652201c46e0d';
