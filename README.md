# MP3 to MP4 Converter

MP3ファイルをMP4動画に変換するクロスプラットフォームのデスクトップアプリケーション。

## 特徴

- 🎵 **ドラッグ&ドロップ対応** - MP3ファイルを簡単に追加
- ⚡ **並列変換処理** - 複数ファイルを同時に変換
- 📊 **リアルタイム進捗表示** - 変換状態を視覚的に確認
- ⚙️ **カスタマイズ可能** - 出力フォルダ、解像度、ファイル名などを設定
- 🎨 **モダンなUI** - CustomTkinterを使用した見やすいインターフェース
- 🌐 **クロスプラットフォーム** - Windows、macOS、Linuxに対応

## 必要要件

- Python 3.11以上
- FFmpeg（システムにインストール済み）

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd mp3_2_mp4
```

### 2. 依存関係のインストール

#### mise使用の場合（推奨）

```bash
mise install
mise run install-deps
```

#### 手動インストール

```bash
pip install -r requirements.txt
```

### 3. FFmpegのインストール

#### macOS (Homebrew)

```bash
brew install ffmpeg
```

#### Windows (Chocolatey)

```bash
choco install ffmpeg
```

#### Linux (apt)

```bash
sudo apt update
sudo apt install ffmpeg
```

## 実行方法

### 通常実行

```bash
python run.py
```

または

```bash
python src/main.py
```

### デバッグモード

```bash
python run.py --debug
```

## 使い方

1. **アプリケーションを起動**
   ```bash
   python run.py
   ```

2. **ファイルを追加**
   - ドラッグ&ドロップでMP3ファイルを追加
   - または「ファイルを選択」ボタンをクリック

3. **設定を調整**（オプション）
   - 右下の「⋮」メニューから「設定...」を選択
   - 出力フォルダ、ファイル名テンプレート、動画設定を変更

4. **変換開始**
   - 「変換開始」ボタンをクリック
   - 進捗状況がリアルタイムで表示されます

5. **完了**
   - 変換完了後、出力ファイルが指定のフォルダに保存されます

## 設定

設定は以下の場所に保存されます：

- **macOS/Linux**: `~/.mp3_to_mp4/settings.json`
- **Windows**: `%APPDATA%\MP3toMP4Converter\settings.json`

### 設定項目

#### 出力設定
- **出力フォルダ**: MP4ファイルの保存先（未指定の場合は元ファイルと同じ場所）
- **ファイル名テンプレート**: 出力ファイル名の形式
  - `{original_name}` - 元のファイル名
  - `{timestamp}` - タイムスタンプ

#### 動画設定
- **解像度**: 1280x720 (HD)、1920x1080 (Full HD)など
- **フレームレート**: 30 fps、60 fpsなど
- **背景色**: 黒、白、グレーなど

#### 詳細設定
- **同時変換数**: 1〜5（デフォルト: 2）
- **変換完了後に自動的にファイルリストをクリア**
- **変換完了時に通知を表示**

## プロジェクト構造

```
mp3_2_mp4/
├── src/
│   ├── controllers/      # コントローラー層
│   ├── gui/             # GUIコンポーネント
│   │   ├── dialogs/    # ダイアログ
│   │   └── widgets/    # カスタムウィジェット
│   ├── models/          # データモデル
│   ├── services/        # サービス層
│   └── utils/           # ユーティリティ
├── tests/               # テストコード
├── assets/              # アセット（アイコンなど）
├── docs/                # ドキュメント
├── run.py               # 起動スクリプト
└── requirements.txt     # Python依存関係
```

## 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# コード品質チェック
black src tests
flake8 src tests
mypy src

# テスト実行
pytest tests/
```

### mise タスク

```bash
# 利用可能なタスクを確認
mise tasks

# テスト実行
mise run test

# コードフォーマット
mise run format

# リント
mise run lint
```

## トラブルシューティング

### FFmpegが見つからない

```
エラー: FFmpeg が見つかりません。インストールしてください。
```

**解決方法**: FFmpegをインストールしてPATHに追加してください。

### インポートエラー

```
Error: Required modules not found
```

**解決方法**: 依存関係をインストールしてください。

```bash
pip install -r requirements.txt
```

### tkinterdnd2が利用できない

アプリケーションは自動的にファイルブラウザモードにフォールバックします。ドラッグ&ドロップ機能を使用したい場合：

```bash
pip install tkinterdnd2
```

## ライセンス

[ライセンス情報を追加]

## 貢献

[貢献ガイドラインを追加]

## サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。
