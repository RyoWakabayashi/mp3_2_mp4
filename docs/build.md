# Build and Deployment Guide

MP3 to MP4 Converterの実行ファイルをビルドし、配布する手順を説明します。

## 目次

1. [前提条件](#前提条件)
2. [ビルド手順](#ビルド手順)
3. [配布パッケージの作成](#配布パッケージの作成)
4. [テスト](#テスト)
5. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必須

- **Python 3.11以上**
- **PyInstaller** (自動インストールされます)
- **FFmpeg** (開発環境にインストール推奨)

### 推奨

- クリーンなPython仮想環境
- 十分なディスク容量 (500MB以上)

---

## ビルド手順

### 1. 依存関係のインストール

```bash
# 開発依存関係をインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# PyInstallerをインストール（build.pyが自動実行）
pip install pyinstaller
```

### 2. ビルドスクリプトの実行

```bash
# プロジェクトルートから実行
python build.py
```

**ビルドプロセス**:

1. 🧹 既存のビルド成果物をクリーンアップ
2. 🔍 FFmpegの存在確認
3. 📦 PyInstallerのインストール確認
4. 🔨 実行ファイルのビルド
5. 📝 補助ファイルの作成（ランチャースクリプト、README等）
6. 📦 配布パッケージの作成（ZIP）

### 3. 出力ファイル

ビルド成功後、以下のディレクトリが作成されます：

```
dist/
├── MP3toMP4Converter/              # アプリケーションディレクトリ
│   ├── MP3toMP4Converter           # 実行ファイル (macOS)
│   ├── MP3toMP4Converter.exe       # 実行ファイル (Windows)
│   ├── _internal/                  # 依存ライブラリ
│   ├── README.md                   # アプリケーションREADME
│   ├── FFMPEG_REQUIRED.txt         # FFmpegインストール手順
│   └── Launch_MP3toMP4Converter.*  # ランチャースクリプト
└── MP3toMP4Converter-{platform}.zip  # 配布用ZIPファイル
```

---

## 配布パッケージの作成

### Windows向け

```bash
python build.py
```

**生成されるファイル**:
- `dist/MP3toMP4Converter-windows.zip`

**内容**:
- `MP3toMP4Converter.exe` - メイン実行ファイル
- `Launch_MP3toMP4Converter.bat` - 起動用バッチファイル
- `FFMPEG_REQUIRED.txt` - FFmpegインストール手順
- `README.md` - 使用方法

### macOS向け

```bash
python build.py
```

**生成されるファイル**:
- `dist/MP3toMP4Converter-macos.zip`

**オプション: DMG作成**:
```bash
hdiutil create -volname "MP3 to MP4 Converter" \
  -srcfolder dist/MP3toMP4Converter \
  -ov -format UDZO \
  dist/MP3toMP4Converter.dmg
```

---

## FFmpegのバンドル（オプション）

### Windows

1. FFmpegをダウンロード:
   - https://ffmpeg.org/download.html から「Windows builds」を選択
   - ffmpeg-release-essentials.zip をダウンロード

2. FFmpegをバンドル:
```bash
# ffmpeg.exeをコピー
mkdir -p dist/MP3toMP4Converter/ffmpeg
cp path/to/ffmpeg.exe dist/MP3toMP4Converter/ffmpeg/

# 再パッケージ
cd dist
zip -r MP3toMP4Converter-windows-bundled.zip MP3toMP4Converter/
```

### macOS

```bash
# Homebrewでインストール済みのFFmpegをコピー
mkdir -p dist/MP3toMP4Converter/ffmpeg
cp /opt/homebrew/bin/ffmpeg dist/MP3toMP4Converter/ffmpeg/

# 依存ライブラリも必要な場合
# otool -L で確認してコピー

# 再パッケージ
cd dist
zip -r MP3toMP4Converter-macos-bundled.zip MP3toMP4Converter/
```

---

## テスト

### ビルド直後のテスト

```bash
# macOS
./dist/MP3toMP4Converter/MP3toMP4Converter

# Windows
dist\MP3toMP4Converter\MP3toMP4Converter.exe
```

### 配布パッケージのテスト

1. **クリーンなテスト環境を用意**:
   - 別のマシンまたはVM
   - Pythonがインストールされていない環境が理想

2. **ZIPを解凍して実行**:
   ```bash
   unzip MP3toMP4Converter-{platform}.zip
   cd MP3toMP4Converter
   
   # macOS
   ./Launch_MP3toMP4Converter.command
   
   # Windows
   Launch_MP3toMP4Converter.bat
   ```

3. **動作確認項目**:
   - [ ] アプリケーションが起動する
   - [ ] GUIが正常に表示される
   - [ ] MP3ファイルをドラッグ&ドロップできる
   - [ ] FFmpegが見つからない場合、適切なエラーメッセージが表示される
   - [ ] FFmpegインストール後、変換が正常に実行される

---

## トラブルシューティング

### ビルドエラー

#### "ModuleNotFoundError: No module named 'PyInstaller'"

**解決策**:
```bash
pip install pyinstaller
```

#### "Unable to find 'customtkinter'"

**解決策**:
```bash
pip install customtkinter
```

PyInstallerの`--hidden-import`に追加が必要な場合があります。

#### macOSで「開発元が未確認」エラー

**解決策**:
```bash
# コード署名を削除
xattr -cr dist/MP3toMP4Converter/MP3toMP4Converter

# または、システム環境設定で許可
```

### 実行時エラー

#### "FFmpeg not found"

**原因**: FFmpegがシステムにインストールされていない

**解決策**: `FFMPEG_REQUIRED.txt`の手順に従ってFFmpegをインストール

#### "Failed to execute script"

**原因**: 依存ライブラリが不足している

**解決策**:
```bash
# build.pyの--hidden-importに追加
--hidden-import=missing_module_name
```

#### GUIが表示されない

**原因**: tkinkerまたはcustomtkinkerの問題

**解決策**:
1. Pythonがtkinnerサポート付きでビルドされているか確認
2. PyInstallerのログを確認: `--debug=all`

---

## 高度な設定

### アイコンの追加

```bash
# Windows用アイコンを作成
# assets/icons/app.ico

# macOS用アイコンを作成
# assets/icons/app.icns

# build.pyが自動検出してビルドに含めます
```

### ワンファイル配布

`build.py`を編集:
```python
# --onedirを--onefileに変更
"--onefile",  # 単一実行ファイル
```

**メリット**: 配布が簡単
**デメリット**: 起動が遅い、FFmpegのバンドルが困難

### カスタムビルドオプション

```bash
# 直接PyInstallerを実行
pyinstaller \
  --name=MP3toMP4Converter \
  --windowed \
  --onedir \
  --add-data="README.md:." \
  --hidden-import=tkinter \
  --hidden-import=customtkinter \
  run.py
```

---

## 配布チェックリスト

リリース前に確認:

- [ ] ビルドが成功している
- [ ] クリーンな環境でテスト済み
- [ ] README.mdが最新
- [ ] FFMPEG_REQUIRED.txtが含まれている
- [ ] ライセンス情報が記載されている
- [ ] バージョン番号が正しい
- [ ] ZIPファイルサイズが妥当（< 100MB）
- [ ] ウイルススキャン済み（Windows）

---

## サポートとフィードバック

問題が発生した場合:

1. GitHubのIssueを確認
2. `--debug=all`でビルドログを取得
3. Issueを作成（ログを添付）

---

## リファレンス

- [PyInstaller公式ドキュメント](https://pyinstaller.org/)
- [FFmpeg公式サイト](https://ffmpeg.org/)
- [customtkinter GitHub](https://github.com/TomSchimansky/CustomTkinter)
