# PDF Bookmark Extractor

macOSのプレビュー.appで追加されたブックマーク情報をPDFファイルから抽出するツールです。

## 🌟 機能

- 📁 **ファイルアップロード**: ブラウザからPDFファイルをアップロード
- 🖱️ **ドラッグ&ドロップ**: ファイルをドラッグ&ドロップでアップロード
- 🔍 **ワンクリック抽出**: ボタン一つでブックマーク情報を抽出
- 📊 **結果表示**: 抽出されたブックマーク情報を美しく表示
- 📱 **レスポンシブ**: スマートフォンやタブレットでも使用可能

## 🚀 デモ

[Live Demo on Render](https://pdf-bookmark-extractor.onrender.com)

## 🛠️ 技術スタック

### バックエンド
- **Python 3.11** + **Flask 3.1.1** (Webフレームワーク)
- **qpdf** (PDF解析・変換)
- **jq** (JSON処理)

### フロントエンド
- **HTML5** + **CSS3** + **JavaScript (ES6+)**
- モダンなUI/UXデザイン
- レスポンシブ対応

## 📦 インストール

### ローカル環境

1. **リポジトリをクローン**
```bash
git clone https://github.com/yourusername/pdf-bookmark-extractor.git
cd pdf-bookmark-extractor
```

2. **依存関係をインストール**
```bash
pip install -r requirements.txt
```

3. **必要なツールをインストール**
```bash
# macOS
brew install qpdf jq

# Ubuntu/Debian
sudo apt-get install qpdf jq

# CentOS/RHEL
sudo yum install qpdf jq
```

4. **シェルスクリプトに実行権限を付与**
```bash
chmod +x extract_bookmarks.sh
```

5. **アプリケーションを起動**
```bash
python app.py
```

6. **ブラウザでアクセス**
```
http://localhost:8000
```

## 🐳 Docker (オプション)

```bash
# Dockerイメージをビルド
docker build -t pdf-bookmark-extractor .

# コンテナを起動
docker run -p 8000:8000 pdf-bookmark-extractor
```

## 📁 プロジェクト構成

```
pdf-bookmark-extractor/
├── app.py                    # Flaskメインアプリケーション
├── extract_bookmarks.sh      # ブックマーク抽出スクリプト
├── requirements.txt          # Python依存関係
├── render.yaml              # Renderデプロイ設定
├── Dockerfile               # Docker設定
├── templates/
│   └── index.html          # HTMLテンプレート
├── static/
│   └── style.css           # CSSスタイル
├── uploads/                # アップロードファイル保存先
├── README.md               # このファイル
├── web_app_README.md       # 詳細な使用方法
├── 技術仕様書.txt          # 技術仕様詳細
├── 主要技術スタック.txt    # 技術スタック概要
└── 技術使用箇所.txt        # 技術使用箇所詳細
```

## 🔧 使用方法

1. **PDFファイルをアップロード**
   - 「ファイルを選択」ボタンをクリック
   - またはPDFファイルをドラッグ&ドロップ

2. **ブックマーク抽出**
   - 「🔍 ブックマークを抽出」ボタンをクリック

3. **結果確認**
   - 抽出されたブックマーク情報が表示されます

## 🔒 セキュリティ

- ファイル形式検証 (PDFのみ許可)
- ファイルサイズ制限 (50MB)
- 安全なファイル名処理
- 一時ファイルの自動削除
- タイムアウト設定 (30秒)

## 🌐 対応ブラウザ

- Chrome (推奨)
- Safari
- Firefox
- Edge
- モバイルブラウザ (レスポンシブ対応)

## 📋 制限事項

- macOSのプレビュー.appで作成されたブックマークのみ対応
- PDFファイルのみ対応
- ファイルサイズ50MB以下
- ローカル環境での実行

## 🤝 貢献

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 👨‍💻 作者

PDF Bookmark Extractor Team

## 🙏 謝辞

- [qpdf](https://github.com/qpdf/qpdf) - PDF処理ライブラリ
- [Flask](https://flask.palletsprojects.com/) - Webフレームワーク
- [Render](https://render.com/) - ホスティングプラットフォーム

## 📞 サポート

問題や質問がある場合は、[Issues](https://github.com/yourusername/pdf-bookmark-extractor/issues)で報告してください。 