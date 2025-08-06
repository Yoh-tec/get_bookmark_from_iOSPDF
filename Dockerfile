# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && apt-get install -y \
    qpdf \
    jq \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# シェルスクリプトに実行権限を付与
RUN chmod +x extract_bookmarks.sh

# アップロードディレクトリの作成
RUN mkdir -p uploads

# ポートの公開
EXPOSE 8000

# 環境変数の設定
ENV FLASK_ENV=production
ENV PORT=8000

# アプリケーションの起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"] 