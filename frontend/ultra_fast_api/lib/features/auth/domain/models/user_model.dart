import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

/// ユーザーモデル
@JsonSerializable()
class User {
  final String id;
  final String email;
  final String username;
  @JsonKey(name: 'full_name')
  final String? fullName;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  User({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    required this.isActive,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
