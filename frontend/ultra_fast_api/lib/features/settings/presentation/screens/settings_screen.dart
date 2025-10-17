import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ultra_fast_api/features/settings/presentation/providers/settings_notifier.dart';
import 'package:ultra_fast_api/shared/widgets/error_view.dart';
import 'package:ultra_fast_api/shared/widgets/loading_indicator.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key, this.showAppBar = true});

  final bool showAppBar;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settingsAsync = ref.watch(settingsProvider);

    final bodyContent = settingsAsync.when(
      loading: () => const LoadingIndicator(message: '設定を読み込み中...'),
      error: (error, stack) => ErrorView(
        message: error.toString(),
        onRetry: () => ref.invalidate(settingsProvider),
      ),
      data: (settings) {
        if (settings == null) {
          return const Center(child: Text('設定がありません'));
        }
        return ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            _buildSettingTile(
              context,
              title: 'テーマ',
              value: settings.theme,
              onTap: () => _showThemeDialog(context, ref, settings.theme),
            ),
            _buildSettingTile(
              context,
              title: 'デフォルトページサイズ',
              value: settings.defaultPageSize.toString(),
              onTap: () =>
                  _showPageSizeDialog(context, ref, settings.defaultPageSize),
            ),
          ],
        );
      },
    );

    // タブナビゲーション内で使用される場合はAppBarなし
    if (!showAppBar) {
      return bodyContent;
    }

    return Scaffold(
      appBar: AppBar(title: const Text('設定')),
      body: bodyContent,
    );
  }

  Widget _buildSettingTile(
    BuildContext context, {
    required String title,
    required String value,
    required VoidCallback onTap,
  }) {
    return ListTile(
      title: Text(title),
      trailing: Text(value, style: Theme.of(context).textTheme.bodyMedium),
      onTap: onTap,
    );
  }

  void _showThemeDialog(
    BuildContext context,
    WidgetRef ref,
    String currentTheme,
  ) {
    showDialog(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('テーマ選択'),
        children: ['light', 'dark'].map((theme) {
          return SimpleDialogOption(
            onPressed: () {
              ref.read(settingsProvider.notifier).updateSettings({
                'theme': theme,
              });
              Navigator.pop(context);
            },
            child: Text(theme == 'light' ? 'ライト' : 'ダーク'),
          );
        }).toList(),
      ),
    );
  }

  void _showPageSizeDialog(
    BuildContext context,
    WidgetRef ref,
    int currentSize,
  ) {
    final controller = TextEditingController(text: currentSize.toString());

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('ページサイズを編集'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: 'ページサイズ (10-100)'),
          keyboardType: TextInputType.number,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('キャンセル'),
          ),
          ElevatedButton(
            onPressed: () {
              final size = int.tryParse(controller.text);
              if (size != null && size >= 10 && size <= 100) {
                ref.read(settingsProvider.notifier).updateSettings({
                  'default_page_size': size,
                });
                Navigator.pop(context);
              }
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }
}
