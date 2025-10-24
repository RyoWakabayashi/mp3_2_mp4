# MP3 to MP4 Converter - インストールガイド

**バージョン**: 1.0  
**最終更新日**: 2025年10月24日  
**対応OS**: Windows 10以降、macOS 12以降

---

## 目次

1. [システム要件](#システム要件)
2. [Windowsへのインストール](#windowsへのインストール)
3. [macOSへのインストール](#macosへのインストール)
4. [FFmpegのインストール](#ffmpegのインストール)
5. [インストールの確認](#インストールの確認)
6. [アップデート](#アップデート)
7. [アンインストール](#アンインストール)
8. [トラブルシューティング](#トラブルシューティング)

---

## システム要件

### 必須要件

#### Windows

- **OS**: Windows 10 (64-bit) 以降
- **CPU**: Intel Core i3 相当以上
- **メモリ**: 4GB RAM 以上
- **ディスク空き容量**: 500MB以上（インストール用）
- **追加容量**: 変換する音声ファイルの約2倍の空き容量を推奨
- **その他**: FFmpeg（インストール手順は後述）

#### macOS

- **OS**: macOS 12 (Monterey) 以降
- **CPU**: Intel Core i3 または Apple Silicon (M1/M2)
- **メモリ**: 4GB RAM 以上
- **ディスク空き容量**: 500MB以上（インストール用）
- **追加容量**: 変換する音声ファイルの約2倍の空き容量を推奨
- **その他**: FFmpeg（インストール手順は後述）

### 推奨要件

- **CPU**: Intel Core i5 / AMD Ryzen 5 相当以上
- **メモリ**: 8GB RAM 以上
- **ディスク**: SSD推奨
- **ディスプレイ**: 1280x720以上の解像度

---

## Windowsへのインストール

### ステップ1: アプリケーションのダウンロード

1. [リリースページ](https://github.com/RyoWakabayashi/mp3_2_mp4/releases)にアクセスします
2. 最新バージョンの `MP3toMP4Converter-Windows.zip` をダウンロードします
3. ダウンロードしたファイルを任意のフォルダに保存します

### ステップ2: ファイルの解凍

1. ダウンロードした `MP3toMP4Converter-Windows.zip` を右クリックします
2. 「すべて展開」を選択します
3. 展開先を選択します（例: `C:\Program Files\MP3toMP4Converter`）
4. 「展開」ボタンをクリックします

### ステップ3: アプリケーションの起動

1. 解凍したフォルダを開きます
2. `MP3toMP4Converter.exe` をダブルクリックして起動します
3. Windows Defenderの警告が表示される場合:
   - 「詳細情報」をクリック
   - 「実行」をクリック

### ステップ4: FFmpegのインストール

アプリケーションの初回起動時にFFmpegが必要です。詳細は[FFmpegセットアップガイド](ffmpeg_setup_jp.md)をご参照ください。

### オプション: デスクトップショートカットの作成

1. `MP3toMP4Converter.exe` を右クリック
2. 「送る」→「デスクトップ（ショートカットを作成）」を選択

---

## macOSへのインストール

### ステップ1: アプリケーションのダウンロード

1. [リリースページ](https://github.com/RyoWakabayashi/mp3_2_mp4/releases)にアクセスします
2. 最新バージョンの `MP3toMP4Converter-macOS.zip` をダウンロードします
3. ダウンロードしたファイルを任意のフォルダに保存します

### ステップ2: ファイルの解凍とインストール

1. ダウンロードした `MP3toMP4Converter-macOS.zip` をダブルクリックして解凍します
2. 解凍されたフォルダ `MP3toMP4Converter` の名前を `MP3toMP4Converter.app` に変更します
3. `MP3toMP4Converter.app` を「アプリケーション」フォルダにコピーします
   - Finderで「移動」→「アプリケーション」を選択
   - `MP3toMP4Converter.app` をドラッグ&ドロップ

### ステップ3: 初回起動

1. Finderで「アプリケーション」フォルダを開きます
2. `MP3toMP4Converter` を探してダブルクリックします
3. 「開発元を確認できません」という警告が表示された場合:
   - アプリケーションを右クリック（またはControlキー + クリック）
   - 「開く」を選択
   - 「開く」ボタンをクリック

### ステップ4: FFmpegのインストール

アプリケーションの初回起動時にFFmpegが必要です。詳細は[FFmpegセットアップガイド](ffmpeg_setup_jp.md)をご参照ください。

### オプション: Dockへの追加

1. 「アプリケーション」フォルダで `MP3toMP4Converter` を見つけます
2. アイコンをDockにドラッグ&ドロップします

---

## FFmpegのインストール

MP3 to MP4 Converterは動画変換にFFmpegを使用します。FFmpegのインストール方法については、[FFmpegセットアップガイド](ffmpeg_setup_jp.md)をご参照ください。

### 簡易手順

#### Windows（wingetを使用）

```powershell
winget install Gyan.FFmpeg
```

#### macOS（Homebrewを使用）

```bash
brew install ffmpeg
```

詳細な手順とトラブルシューティングについては、[FFmpegセットアップガイド](ffmpeg_setup_jp.md)をご確認ください。

---

## インストールの確認

### アプリケーションの起動確認

1. アプリケーションを起動します
2. メインウィンドウが正常に表示されることを確認します
3. エラーメッセージが表示されないことを確認します

### FFmpegの確認

1. アプリケーションの「設定」メニューを開きます
2. 「FFmpeg」セクションで状態を確認します
3. 「検出済み」または「利用可能」と表示されていればOKです

または、ターミナル/コマンドプロンプトで以下を実行:

#### Windows

```cmd
ffmpeg -version
```

#### macOS

```bash
ffmpeg -version
```

FFmpegのバージョン情報が表示されれば正常にインストールされています。

---

## アップデート

### 手動アップデート

1. [リリースページ](https://github.com/RyoWakabayashi/mp3_2_mp4/releases)で最新バージョンを確認します
2. 新しいバージョンをダウンロードします
3. 既存のアプリケーションを新しいバージョンで上書きします
   - Windows: 新しいファイルを同じフォルダに解凍して上書き
   - macOS: 古いアプリケーションを削除し、新しいDMGからインストール

### 設定の保持

設定ファイルは以下の場所に保存されており、アップデート後も保持されます:

- **Windows**: `%APPDATA%\MP3toMP4Converter\settings.json`
- **macOS**: `~/Library/Application Support/MP3toMP4Converter/settings.json`

---

## アンインストール

### Windows

1. アプリケーションを終了します
2. インストールフォルダ全体を削除します
3. （オプション）設定ファイルを削除:
   - `%APPDATA%\MP3toMP4Converter` フォルダを削除

### macOS

1. アプリケーションを終了します
2. 「アプリケーション」フォルダから `MP3toMP4Converter` をゴミ箱に移動します
3. ゴミ箱を空にします
4. （オプション）設定ファイルを削除:
   - `~/Library/Application Support/MP3toMP4Converter` フォルダを削除

---

## トラブルシューティング

### アプリケーションが起動しない

#### Windows

- **症状**: ダブルクリックしても何も起こらない
- **対処法**:
  1. Windows Defenderやウイルス対策ソフトがブロックしていないか確認
  2. 管理者として実行を試す（右クリック→「管理者として実行」）
  3. Visual C++ Redistributableがインストールされているか確認

#### macOS

- **症状**: 「開発元を確認できません」エラー
- **対処法**:
  1. 右クリック→「開く」で起動を試す
  2. システム環境設定→「セキュリティとプライバシー」→「一般」タブで「このまま開く」をクリック

### FFmpegが見つからない

- **症状**: 「FFmpegが見つかりません」というエラー
- **対処法**:
  1. [FFmpegセットアップガイド](ffmpeg_setup_jp.md)に従ってFFmpegをインストール
  2. 環境変数PATHにFFmpegのパスが含まれているか確認
  3. アプリケーションを再起動

### 変換が開始できない

- **症状**: ファイルをドロップしても変換が始まらない
- **対処法**:
  1. ファイルがMP3形式であることを確認
  2. ファイルが破損していないか確認
  3. ディスクに十分な空き容量があるか確認
  4. アプリケーションのログを確認（メニュー→「ログを表示」）

### その他の問題

その他の問題については、[メインマニュアル](manual_jp.md)の「トラブルシューティング」セクションをご参照ください。

---

## サポート

インストールに関する問題やご質問がある場合は、以下からお問い合わせください:

- **GitHub Issues**: [https://github.com/RyoWakabayashi/mp3_2_mp4/issues](https://github.com/RyoWakabayashi/mp3_2_mp4/issues)
- **Email**: （プロジェクトのREADMEを参照）

---

**関連ドキュメント**:

- [ユーザーマニュアル](manual_jp.md)
- [FFmpegセットアップガイド](ffmpeg_setup_jp.md)
