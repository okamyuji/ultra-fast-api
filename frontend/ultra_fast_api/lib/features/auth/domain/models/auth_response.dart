import 'package:json_annotation/json_annotation.dart';
import 'package:ultra_fast_api/features/auth/domain/models/user_model.dart';

part 'auth_response.g.dart';

/// 認証レスポンスモデル
@JsonSerializable()
class AuthResponse {
  @JsonKey(name: 'access_token')
  final String accessToken;
  @JsonKey(name: 'refresh_token')
  final String refreshToken;
  @JsonKey(name: 'token_type')
  final String tokenType;
  @JsonKey(name: 'expires_in')
  final int expiresIn;
  final User user;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  /// トークンの有効期限を計算
  DateTime get expiresAt => DateTime.now().add(Duration(seconds: expiresIn));

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AuthResponseToJson(this);
}
