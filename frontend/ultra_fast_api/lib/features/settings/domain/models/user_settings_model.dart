import 'package:json_annotation/json_annotation.dart';

part 'user_settings_model.g.dart';

@JsonSerializable()
class UserSettings {
  final String id;
  @JsonKey(name: 'user_id')
  final String userId;
  final String theme;
  @JsonKey(name: 'default_page_size')
  final int defaultPageSize;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  UserSettings({
    required this.id,
    required this.userId,
    required this.theme,
    required this.defaultPageSize,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserSettings.fromJson(Map<String, dynamic> json) =>
      _$UserSettingsFromJson(json);
  Map<String, dynamic> toJson() => _$UserSettingsToJson(this);
}
