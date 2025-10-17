import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ultra_fast_api/features/auth/presentation/screens/login_screen.dart';
import 'package:ultra_fast_api/features/auth/presentation/screens/register_screen.dart';
import 'package:ultra_fast_api/features/home/presentation/screens/home_screen_with_tabs.dart';
import 'package:ultra_fast_api/features/products/presentation/screens/product_detail_screen.dart';
import 'package:ultra_fast_api/features/splash/presentation/screens/splash_screen.dart';

/// アプリケーションのルーティング設定
class AppRouter {
  AppRouter._();

  /// ルートパス
  static const String splash = '/';
  static const String login = '/login';
  static const String register = '/register';
  static const String home = '/home';
  static const String products = '/products';
  static const String productDetail = '/products/:id';
  static const String settings = '/settings';

  /// GoRouter インスタンス
  static final GoRouter router = GoRouter(
    initialLocation: splash,
    routes: [
      GoRoute(path: splash, builder: (context, state) => const SplashScreen()),
      GoRoute(path: login, builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: home,
        builder: (context, state) => const HomeScreenWithTabs(),
        routes: [
          GoRoute(
            path: 'products/:id',
            builder: (context, state) {
              final id = state.pathParameters['id']!;
              return ProductDetailScreen(productId: id);
            },
          ),
        ],
      ),
      GoRoute(
        path: productDetail,
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return ProductDetailScreen(productId: id);
        },
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(title: const Text('エラー')),
      body: Center(child: Text('ページが見つかりません: ${state.uri}')),
    ),
  );
}
