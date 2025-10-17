import 'package:ultra_fast_api/features/auth/domain/models/user_model.dart';

/// 認証状態
sealed class AuthState {
  const AuthState();
}

/// 初期状態
class AuthInitial extends AuthState {
  const AuthInitial();
}

/// ローディング中
class AuthLoading extends AuthState {
  const AuthLoading();
}

/// 認証済み
class AuthAuthenticated extends AuthState {
  final User user;

  const AuthAuthenticated(this.user);
}

/// 未認証
class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

/// エラー
class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);
}
