import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ultra_fast_api/core/router/app_router.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_notifier.dart';
import 'package:ultra_fast_api/features/auth/presentation/providers/auth_state.dart';
import 'package:ultra_fast_api/shared/utils/validators.dart';
import 'package:ultra_fast_api/shared/widgets/loading_indicator.dart';

/// ログイン画面
class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final notifier = ref.read(authProvider.notifier);
    await notifier.login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    // 認証成功時にホーム画面へ遷移
    ref.listen<AuthState>(authProvider, (previous, next) {
      if (next is AuthAuthenticated) {
        context.go(AppRouter.home);
      } else if (next is AuthError) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(next.message)));
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('ログイン')),
      body: authState is AuthLoading
          ? const LoadingIndicator(message: 'ログイン中...')
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 32),
                    // ロゴまたはタイトル
                    Text(
                      'UltraFastAPI',
                      style: Theme.of(context).textTheme.headlineLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 48),
                    // メールアドレス
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(
                        labelText: 'メールアドレス',
                        prefixIcon: Icon(Icons.email),
                      ),
                      keyboardType: TextInputType.emailAddress,
                      validator: Validators.email,
                    ),
                    const SizedBox(height: 16),
                    // パスワード
                    TextFormField(
                      controller: _passwordController,
                      decoration: InputDecoration(
                        labelText: 'パスワード',
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility
                                : Icons.visibility_off,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      obscureText: _obscurePassword,
                      validator: (value) =>
                          Validators.required(value, fieldName: 'パスワード'),
                    ),
                    const SizedBox(height: 24),
                    // ログインボタン
                    ElevatedButton(
                      onPressed: _handleLogin,
                      child: const Text('ログイン'),
                    ),
                    const SizedBox(height: 16),
                    // 会員登録リンク
                    TextButton(
                      onPressed: () => context.push(AppRouter.register),
                      child: const Text('アカウントをお持ちでない方はこちら'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
