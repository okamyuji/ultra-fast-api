/// バリデーションユーティリティ
class Validators {
  Validators._();

  /// メールアドレスバリデーション
  static String? email(String? value) {
    if (value == null || value.isEmpty) {
      return 'メールアドレスを入力してください';
    }

    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );

    if (!emailRegex.hasMatch(value)) {
      return '有効なメールアドレスを入力してください';
    }

    return null;
  }

  /// パスワードバリデーション
  static String? password(String? value) {
    if (value == null || value.isEmpty) {
      return 'パスワードを入力してください';
    }

    if (value.length < 8) {
      return 'パスワードは8文字以上である必要があります';
    }

    if (value.length > 255) {
      return 'パスワードは255文字以下である必要があります';
    }

    // 英数字混在チェック
    final hasLetter = RegExp(r'[a-zA-Z]').hasMatch(value);
    final hasDigit = RegExp(r'[0-9]').hasMatch(value);

    if (!hasLetter || !hasDigit) {
      return 'パスワードは英字と数字を含む必要があります';
    }

    return null;
  }

  /// 必須フィールドバリデーション
  static String? required(String? value, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return '${fieldName ?? 'この項目'}を入力してください';
    }
    return null;
  }

  /// 最小文字数バリデーション
  static String? minLength(String? value, int minLength, {String? fieldName}) {
    if (value == null || value.isEmpty) {
      return '${fieldName ?? 'この項目'}を入力してください';
    }

    if (value.length < minLength) {
      return '${fieldName ?? 'この項目'}は$minLength文字以上である必要があります';
    }

    return null;
  }

  /// 最大文字数バリデーション
  static String? maxLength(String? value, int maxLength, {String? fieldName}) {
    if (value != null && value.length > maxLength) {
      return '${fieldName ?? 'この項目'}は$maxLength文字以下である必要があります';
    }

    return null;
  }
}
