import 'package:json_annotation/json_annotation.dart';

part 'register_request.g.dart';

/// 会員登録リクエストモデル
@JsonSerializable()
class RegisterRequest {
  final String email;
  final String password;
  final String username;
  @JsonKey(name: 'full_name')
  final String? fullName;

  RegisterRequest({
    required this.email,
    required this.password,
    required this.username,
    this.fullName,
  });

  factory RegisterRequest.fromJson(Map<String, dynamic> json) =>
      _$RegisterRequestFromJson(json);
  Map<String, dynamic> toJson() => _$RegisterRequestToJson(this);
}
