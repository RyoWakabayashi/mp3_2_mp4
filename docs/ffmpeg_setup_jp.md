# FFmpegセットアップガイド

**最終更新日**: 2025年10月24日  
**対応OS**: Windows 10以降、macOS 12以降

---

## 目次

1. [FFmpegとは](#ffmpegとは)
2. [Windowsへのインストール](#windowsへのインストール)
3. [macOSへのインストール](#macosへのインストール)
4. [インストールの確認](#インストールの確認)
5. [トラブルシューティング](#トラブルシューティング)

---

## FFmpegとは

FFmpegは、音声や動画ファイルを記録、変換、ストリーミングするための完全なクロスプラットフォームソリューションです。MP3 to MP4 Converterは、FFmpegを使用してMP3音声ファイルをMP4動画ファイルに変換します。

### なぜFFmpegが必要なのか

- MP3からMP4への変換処理を実行
- 高品質な音声・動画コーデックのサポート
- 業界標準のマルチメディア処理ツール

---

## Windowsへのインストール

### 方法1: winget を使用(推奨)

wingetは、Windows 10/11に標準搭載されているパッケージマネージャーです。

#### ステップ1: wingetの確認

1. コマンドプロンプトまたはPowerShellを開きます
   - スタートメニューで「cmd」または「PowerShell」を検索

2. 以下のコマンドでwingetが利用可能か確認:

```cmd
winget --version
```

3. バージョン情報が表示されればOKです
   - 表示されない場合は、Windows Updateで最新の状態に更新してください
   - または、Microsoft Storeから「アプリ インストーラー」をインストール

#### ステップ2: FFmpegのインストール

1. コマンドプロンプトまたはPowerShellで以下を実行:

```cmd
winget install Gyan.FFmpeg
```

2. インストールが完了するまで待ちます(通常1-2分程度)

### 方法2: 手動インストール

#### ステップ1: FFmpegのダウンロード

1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)にアクセス
2. 「Windows」セクションの「Windows builds from gyan.dev」リンクをクリック
3. 「ffmpeg-release-essentials.zip」をダウンロード

または、直接以下からダウンロード:
- [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

#### ステップ2: ファイルの展開

1. ダウンロードしたZIPファイルを展開
2. 展開したフォルダを適切な場所に移動（例: `C:\ffmpeg`）

#### ステップ3: 環境変数の設定

1. Windowsの検索バーで「環境変数」と入力
2. 「システム環境変数の編集」を選択
3. 「環境変数」ボタンをクリック
4. 「システム環境変数」セクションで「Path」を選択し、「編集」をクリック
5. 「新規」をクリック
6. FFmpegの`bin`フォルダのパスを追加（例: `C:\ffmpeg\bin`）
7. 「OK」をクリックしてすべてのウィンドウを閉じる

#### ステップ4: 設定の確認

1. 新しいコマンドプロンプトまたはPowerShellウィンドウを開く
2. 以下のコマンドを実行:

```cmd
ffmpeg -version
```

3. バージョン情報が表示されれば成功です

---

## macOSへのインストール

### 方法1: Homebrew を使用（推奨）

Homebrewは、macOSの最も人気のあるパッケージマネージャーです。

#### ステップ1: Homebrewのインストール

1. ターミナルを開きます
   - Finder→「アプリケーション」→「ユーティリティ」→「ターミナル」
   - またはSpotlight検索（Cmd + Space）で「ターミナル」と検索

2. 以下のコマンドを実行:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. プロンプトに従ってインストールを完了します
4. パスワードの入力を求められた場合は、Macのユーザーパスワードを入力

#### ステップ2: FFmpegのインストール

1. ターミナルで以下のコマンドを実行:

```bash
brew install ffmpeg
```

2. インストールが完了するまで待ちます（数分かかる場合があります）

#### ステップ3: インストールの確認

```bash
ffmpeg -version
```

バージョン情報が表示されれば成功です。

### 方法2: MacPorts を使用

MacPortsを使用している場合:

```bash
sudo port install ffmpeg
```

### 方法3: 手動インストール（非推奨）

手動インストールは複雑なため、HomebrewまたはMacPortsの使用を強く推奨します。

---

## インストールの確認

### コマンドラインでの確認

#### Windows (コマンドプロンプトまたはPowerShell)

```cmd
ffmpeg -version
```

#### macOS (ターミナル)

```bash
ffmpeg -version
```

### 期待される出力

以下のような情報が表示されれば、FFmpegは正しくインストールされています:

```
ffmpeg version N-110XXX-XXXXXXXXXXXX
built with gcc X.X.X ...
configuration: --enable-gpl --enable-version3 ...
libavutil      XX. XX.XXX / XX. XX.XXX
libavcodec     XX. XX.XXX / XX. XX.XXX
...
```

### MP3 to MP4 Converter での確認

1. MP3 to MP4 Converter を起動
2. メニューバーから「設定」を開く
3. 「FFmpeg」セクションを確認
4. 「検出済み」または「利用可能」と表示されていればOK

表示されるFFmpegのパス例:
- Windows: `C:\Users\<ユーザー名>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_*\ffmpeg-*\bin\ffmpeg.exe`
- macOS: `/opt/homebrew/bin/ffmpeg` または `/usr/local/bin/ffmpeg`

---

## トラブルシューティング

### Windows: 「ffmpegは内部コマンドまたは外部コマンドとして認識されていません」

**原因**: FFmpegが環境変数PATHに追加されていない

**解決方法**:
1. FFmpegの`bin`フォルダの場所を確認
2. 環境変数PATHに追加（上記「手動インストール」の手順3参照）
3. コマンドプロンプト/PowerShellを再起動
4. 再度 `ffmpeg -version` を実行

### macOS: 「command not found: ffmpeg」

**原因**: FFmpegがインストールされていないか、PATHが通っていない

**解決方法**:
1. Homebrewが正しくインストールされているか確認:
   ```bash
   brew --version
   ```

2. FFmpegを再インストール:
   ```bash
   brew install ffmpeg
   ```

3. Homebrewのパスが通っているか確認:
   ```bash
   echo $PATH
   ```
   `/opt/homebrew/bin` または `/usr/local/bin` が含まれているべき

4. シェル設定ファイルを確認（`~/.zshrc` または `~/.bash_profile`）

### Apple Siliconの場合の追加設定

Apple Silicon (M1/M2) Macで `command not found` エラーが出る場合:

1. `~/.zshrc` を編集:
   ```bash
   nano ~/.zshrc
   ```

2. 以下の行を追加:
   ```bash
   export PATH="/opt/homebrew/bin:$PATH"
   ```

3. ファイルを保存（Ctrl+X, Y, Enter）

4. 設定を再読み込み:
   ```bash
   source ~/.zshrc
   ```

### MP3 to MP4 Converter でFFmpegが検出されない

**症状**: アプリケーションが「FFmpegが見つかりません」と表示する

**解決方法**:

1. ターミナル/コマンドプロンプトでFFmpegが動作するか確認:
   ```bash
   ffmpeg -version
   ```

2. 動作する場合、アプリケーションを再起動

3. それでも検出されない場合、アプリケーションの設定で手動でFFmpegのパスを指定:
   - 設定メニュー→「FFmpeg」→「パスを手動で設定」
   - FFmpegの実行ファイルのフルパスを入力

4. FFmpegのパスを確認:
   - Windows: `where ffmpeg`
   - macOS: `which ffmpeg`

### Chocolatey/Homebrewのインストールに失敗する

**Windows (winget)**:
- wingetが利用できない場合は、Windows Updateで最新の状態に更新
- Microsoft Storeから「アプリ インストーラー」をインストール
- セキュリティソフトが妨害していないか確認

**macOS (Homebrew)**:
- Xcodeコマンドラインツールがインストールされているか確認:
  ```bash
  xcode-select --install
  ```
- インターネット接続を確認
- ディスクの空き容量を確認

### バージョンが古い場合

FFmpegのバージョンが古い場合の更新方法:

#### Windows (winget)

```cmd
winget upgrade Gyan.FFmpeg
```

#### macOS (Homebrew)

```bash
brew upgrade ffmpeg
```

---

## 追加リソース

### 公式ドキュメント

- [FFmpeg公式サイト](https://ffmpeg.org/)
- [FFmpeg公式ドキュメント](https://ffmpeg.org/documentation.html)

### パッケージマネージャー

- [winget公式ドキュメント](https://learn.microsoft.com/ja-jp/windows/package-manager/winget/)
- [Homebrew公式サイト](https://brew.sh/ja/)

### サポート

FFmpegのインストールに関する問題がある場合:

1. MP3 to MP4 Converterの[GitHubリポジトリ](https://github.com/RyoWakabayashi/mp3_2_mp4)でIssueを作成
2. FFmpeg自体の問題の場合は[FFmpegのメーリングリスト](https://ffmpeg.org/contact.html)

---

**関連ドキュメント**:
- [インストールガイド](installation_jp.md)
- [ユーザーマニュアル](manual_jp.md)

---

**注意事項**:
- FFmpegはLGPL/GPLライセンスの下で提供されています
- 商用利用の場合は、ライセンス条件をご確認ください
- MP3 to MP4 Converterは、FFmpegとは独立したプロジェクトです
