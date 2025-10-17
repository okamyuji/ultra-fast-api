import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ultra_fast_api/core/router/app_router.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_notifier.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ホーム'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) {
                context.go(AppRouter.login);
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.inventory),
                title: const Text('商品一覧'),
                subtitle: const Text('商品を検索・閲覧'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () => context.push(AppRouter.products),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: ListTile(
                leading: const Icon(Icons.settings),
                title: const Text('設定'),
                subtitle: const Text('アプリケーション設定'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () => context.push(AppRouter.settings),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
