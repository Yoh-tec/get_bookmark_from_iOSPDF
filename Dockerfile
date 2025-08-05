# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージを更新し、必要なツールをインストール
RUN apt-get update && apt-get install -y \
    qpdf \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# シェルスクリプトに実行権限を付与
RUN chmod +x extract_bookmarks.sh

# アップロードディレクトリを作成
RUN mkdir -p uploads

# ポート8000を公開
EXPOSE 8000

# アプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"] 