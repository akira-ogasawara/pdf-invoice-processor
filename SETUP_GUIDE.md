# セットアップガイド

PDF請求書自動処理システムの詳細なセットアップ手順です。

## 前提条件

- macOS 10.14 以降
- Python 3.9 以降がインストール済み
- 管理者権限でのコマンド実行が可能

## 1. 環境確認

### Python バージョン確認
```bash
python3 --version
# Python 3.9.0 以降であることを確認
```

### Python パス確認
```bash
which python3
# 出力例: /usr/bin/python3 または /Library/Frameworks/Python.framework/Versions/3.x/bin/python3
```

## 2. 依存関係のインストール

### pdfplumber のインストール
```bash
# システムのPython3を使用する場合
/usr/bin/python3 -m pip install pdfplumber

# または、通常のpip3コマンド
pip3 install pdfplumber
```

### インストール確認
```bash
python3 -c "import pdfplumber; print('pdfplumber インストール成功')"
```

## 3. スクリプトの配置と設定

### 3.1 ディレクトリ作成
```bash
mkdir -p ~/scripts
cd ~/scripts
```

### 3.2 スクリプトファイルの取得
```bash
# GitHubからダウンロード
curl -O https://raw.githubusercontent.com/[USERNAME]/pdf-invoice-processor/main/invoice_processor.py

# または、手動でファイルを作成・コピー
```

### 3.3 実行権限の付与
```bash
chmod +x ~/scripts/invoice_processor.py
```

### 3.4 設定の変更

`invoice_processor.py` をテキストエディタで開き、以下の設定を変更：

```python
# 移動先フォルダパス
DEST_FOLDER = "/Users/[あなたのユーザー名]/Library/CloudStorage/GoogleDrive-[あなたのメール]/共有ドライブ/経理/請求書/"

# 取引先名変換ルール（必要に応じて追加）
COMPANY_MAPPING = {
    "Amazon": "amazon",
    "アマゾン": "amazon",
    "アマゾンジャパン": "amazon",
    # 追加したい取引先があれば記述
}
```

## 4. 動作テスト

### 4.1 基本動作確認
```bash
python3 ~/scripts/invoice_processor.py --help
```

### 4.2 サンプルPDFでのテスト
```bash
# テスト用PDFファイルで実行
python3 ~/scripts/invoice_processor.py "/path/to/sample_invoice.pdf"
```

## 5. Automator設定

### 5.1 アプリケーション形式の作成

1. **Automator.app** を起動
2. **新規書類** をクリック
3. **アプリケーション** を選択

#### アクションの追加

1. **「選択されたFinder項目を取得」** を検索してドラッグ
2. **「シェルスクリプトを実行」** を検索してドラッグ

#### シェルスクリプトの設定

- **シェル**: `/bin/bash`
- **入力の引き渡し方法**: 引数として
- **スクリプト内容**:

```bash
# Python のパスを確認して適切なものを使用
/usr/bin/python3 ~/scripts/invoice_processor.py "$@"

# もしくは、which python3 の結果に基づいて
# /Library/Frameworks/Python.framework/Versions/3.x/bin/python3 ~/scripts/invoice_processor.py "$@"
```

#### 保存

- **ファイル** → **保存**
- **名前**: `請求書リネーム処理`
- **場所**: `アプリケーション` フォルダ
- **フォーマット**: アプリケーション

### 5.2 サービス（クイックアクション）形式の作成

1. **Automator.app** を起動
2. **新規書類** をクリック
3. **クイックアクション** を選択

#### 設定

- **ワークフローが受け取る現在の項目**: ファイルまたはフォルダ
- **検索対象**: Finder
- **ファイルタイプ**: PDF（オプション）

#### アクションの追加

**「シェルスクリプトを実行」** を検索してドラッグ

#### シェルスクリプトの設定

- **シェル**: `/bin/bash`
- **入力の引き渡し方法**: 引数として
- **スクリプト内容**:

```bash
/usr/bin/python3 ~/scripts/invoice_processor.py "$@"
```

#### 保存

- **ファイル** → **保存**
- **名前**: `請求書リネーム処理`
- 自動的に `~/Library/Services/` に保存される

## 6. 権限設定

### 6.1 プライバシー設定

**システム環境設定** → **セキュリティとプライバシー** → **プライバシー**

#### フルディスクアクセス
- **Automator** を追加
- **ターミナル** を追加（デバッグ用）

#### ファイルとフォルダ
- **デスクトップ フォルダ** - Automator に許可
- **書類フォルダ** - Automator に許可
- **ダウンロード フォルダ** - Automator に許可

### 6.2 Google Drive アクセス確認

```bash
# Google Drive フォルダにアクセス可能か確認
ls "/Users/$(whoami)/Library/CloudStorage/"
```

## 7. 使用方法

### 7.1 アプリケーション形式

1. **Finder** でPDFファイルを選択
2. **アプリケーション** フォルダの `請求書リネーム処理.app` にドラッグ&ドロップ

### 7.2 サービス形式

1. **Finder** でPDFファイルを右クリック
2. **サービス** → **請求書リネーム処理** を選択

### 7.3 Dock への追加

`請求書リネーム処理.app` を **Dock** にドラッグして追加

## 8. トラブルシューティング

### 8.1 よくあるエラー

#### `ModuleNotFoundError: No module named 'pdfplumber'`

**原因**: pdfplumber がインストールされていない、または異なるPython環境にインストールされている

**解決方法**:
```bash
# 使用するPythonと同じ環境にインストール
/usr/bin/python3 -m pip install pdfplumber

# または
pip3 install pdfplumber
```

#### `FileNotFoundError: [Errno 2] No such file or directory`

**原因**: 移動先フォルダパス（`DEST_FOLDER`）が間違っている

**解決方法**:
1. Google Drive が正常にマウントされているか確認
2. `DEST_FOLDER` のパスを正確に設定
3. フォルダの存在確認:
   ```bash
   ls -la "/Users/$(whoami)/Library/CloudStorage/"
   ```

#### 印刷エラー

**原因**: プリンター設定またはlprコマンドの問題

**解決方法**:
1. システム環境設定でプリンターが正常に設定されているか確認
2. lprコマンドのテスト:
   ```bash
   echo "test" | lpr
   ```

### 8.2 デバッグ方法

#### ターミナルから直接実行
```bash
# 詳細なエラー情報を表示
python3 ~/scripts/invoice_processor.py "/path/to/invoice.pdf"
```

#### ログの確認
```bash
# システムログでAutomatorのエラーを確認
log show --predicate 'subsystem == "com.apple.automator"' --last 1h
```

### 8.3 設定の確認

#### Python パスの確認
```bash
# Automatorで使用するPythonパスを確認
which python3
```

#### 権限の確認
```bash
# スクリプトファイルの権限確認
ls -la ~/scripts/invoice_processor.py
```

## 9. カスタマイズ

### 9.1 新しい取引先の追加

`COMPANY_MAPPING` に新しい取引先を追加:

```python
COMPANY_MAPPING = {
    # 既存の設定...
    "新しい取引先名": "short_name",
}
```

### 9.2 金額抽出パターンの追加

`amount_patterns` リストに新しい正規表現パターンを追加:

```python
amount_patterns = [
    # 既存のパターン...
    r'新しいパターン[\s:：]*([0-9,]+)',
]
```

### 9.3 印刷設定の変更

`print_pdf()` 関数内の `lpr` コマンドオプションを変更:

```python
cmd = [
    "lpr",
    "-o", "sides=one-sided",        # 片面印刷
    "-o", "ColorModel=RGB",         # カラー印刷
    "-o", "media=Letter",           # 用紙サイズ
    pdf_path
]
```

## 10. 更新とメンテナンス

### 10.1 スクリプトの更新

```bash
# 最新版の取得
cd ~/scripts
curl -O https://raw.githubusercontent.com/[USERNAME]/pdf-invoice-processor/main/invoice_processor.py
chmod +x invoice_processor.py
```

### 10.2 依存関係の更新

```bash
pip3 install --upgrade pdfplumber
```

### 10.3 設定のバックアップ

```bash
# 設定をバックアップ
cp ~/scripts/invoice_processor.py ~/scripts/invoice_processor.py.backup
```

以上で、PDF請求書自動処理システムのセットアップが完了です。
