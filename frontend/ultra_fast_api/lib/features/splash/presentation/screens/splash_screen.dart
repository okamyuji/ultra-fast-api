import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_ui/material_ui.dart';
import 'package:ultra_fast_api/core/router/app_router.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_providers.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_state.dart';

/// スプラッシュ画面
/// アプリ起動時に認証状態を確認し、適切な画面に遷移する
class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 認証状態を監視してナビゲーション
    ref.listen<AuthState>(authProvider, (previous, next) {
      debugPrint('🚀 [SplashScreen] Auth state changed: ${next.runtimeType}');
      switch (next) {
        case AuthAuthenticated():
          debugPrint('✅ [SplashScreen] Authenticated -> Navigate to Home');
          context.go(AppRouter.home);
          break;
        case AuthUnauthenticated():
          debugPrint('🔓 [SplashScreen] Unauthenticated -> Navigate to Login');
          context.go(AppRouter.login);
          break;
        case AuthError():
          debugPrint('❌ [SplashScreen] Error -> Navigate to Login');
          context.go(AppRouter.login);
          break;
        case AuthInitial():
          debugPrint('⏳ [SplashScreen] Initial state - waiting...');
          break;
        case AuthLoading():
          debugPrint('⏳ [SplashScreen] Loading - waiting...');
          break;
      }
    });

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Theme.of(context).primaryColor,
              Theme.of(context).primaryColor.withValues(alpha: 0.8),
            ],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // アプリアイコン
              const Icon(Icons.flash_on, size: 100, color: Colors.white),
              const SizedBox(height: 24),
              // アプリ名
              Text(
                'Ultra Fast API',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 48),
              // ローディングインジケーター
              const CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
