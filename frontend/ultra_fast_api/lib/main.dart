import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ultra_fast_api/core/router/app_router.dart';
import 'package:ultra_fast_api/features/settings/presentation/providers/settings_notifier.dart';
import 'package:ultra_fast_api/shared/theme/app_theme.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);

    // ユーザー設定からテーマモードを取得
    final themeMode = settingsAsync.maybeWhen(
      data: (settings) {
        if (settings == null) return ThemeMode.system;
        switch (settings.theme) {
          case 'dark':
            return ThemeMode.dark;
          case 'light':
            return ThemeMode.light;
          default:
            return ThemeMode.system;
        }
      },
      orElse: () => ThemeMode.system,
    );

    return MaterialApp.router(
      title: 'UltraFastAPI',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: AppRouter.router,
    );
  }
}
