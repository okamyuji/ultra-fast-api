import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_notifier.dart';
import 'package:ultra_fast_api/features/products/presentation/screens/products_list_screen.dart';
import 'package:ultra_fast_api/features/settings/presentation/screens/settings_screen.dart';

/// タブナビゲーション付きホーム画面
class HomeScreenWithTabs extends ConsumerStatefulWidget {
  const HomeScreenWithTabs({super.key});

  @override
  ConsumerState<HomeScreenWithTabs> createState() => _HomeScreenWithTabsState();
}

class _HomeScreenWithTabsState extends ConsumerState<HomeScreenWithTabs> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    ProductsListScreen(showAppBar: false),
    SettingsScreen(showAppBar: false),
  ];

  final List<String> _titles = const ['商品一覧', '設定'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_currentIndex]),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            tooltip: 'メニュー',
            onSelected: (value) async {
              if (value == 'logout') {
                final navigator = Navigator.of(context);
                await ref.read(authProvider.notifier).logout();
                // ログアウト後はSplashScreen経由で自動的にログイン画面へ遷移
                if (context.mounted) {
                  navigator.pushNamedAndRemoveUntil('/', (route) => false);
                }
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout),
                    SizedBox(width: 8),
                    Text('ログアウト'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.inventory), label: '商品一覧'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: '設定'),
        ],
      ),
    );
  }
}
