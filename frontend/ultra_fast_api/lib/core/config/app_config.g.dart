// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AppConfig _$AppConfigFromJson(Map<String, dynamic> json) => AppConfig(
  apiBaseUrl: json['apiBaseUrl'] as String,
  defaultPageLimit: (json['defaultPageLimit'] as num).toInt(),
  connectTimeout: (json['connectTimeout'] as num).toInt(),
  receiveTimeout: (json['receiveTimeout'] as num).toInt(),
  tokenRefreshThreshold: (json['tokenRefreshThreshold'] as num).toInt(),
);

Map<String, dynamic> _$AppConfigToJson(AppConfig instance) => <String, dynamic>{
  'apiBaseUrl': instance.apiBaseUrl,
  'defaultPageLimit': instance.defaultPageLimit,
  'connectTimeout': instance.connectTimeout,
  'receiveTimeout': instance.receiveTimeout,
  'tokenRefreshThreshold': instance.tokenRefreshThreshold,
};
