#!/bin/bash

# PDFファイルのブックマーク情報を抽出するスクリプト
# 使用方法: ./extract_bookmarks.sh <PDFファイル名>

if [ $# -eq 0 ]; then
    echo "使用方法: $0 <PDFファイル名>"
    exit 1
fi

PDF_FILE="$1"

if [ ! -f "$PDF_FILE" ]; then
    echo "エラー: ファイル '$PDF_FILE' が見つかりません"
    exit 1
fi

echo "PDFファイルを解析中: $PDF_FILE"

# メタデータオブジェクトを特定（最後のオブジェクトのみを取得）
METADATA_OBJECTS=$(qpdf --json "$PDF_FILE" | jq -r '.qpdf[1] | to_entries[] | select(.value.stream.dict."/Type" == "/Metadata" and .value.stream.dict."/Subtype" == "/XML") | .key' 2>/dev/null | tail -1)

if [ -z "$METADATA_OBJECTS" ]; then
    echo "ブックマーク情報が見つかりませんでした。"
    exit 0
fi

BOOKMARK_PAGES=""

# 最新のメタデータオブジェクトのみを処理
for obj in $METADATA_OBJECTS; do
    # オブジェクトIDから数値を抽出（例: "obj:100 0 R" -> "100 0 R"）
    obj_id=$(echo "$obj" | sed 's/obj://')
    
    # 一時ファイル名を生成
    temp_file=$(mktemp)
    
    # メタデータを抽出・解凍
    if qpdf --show-object="$obj_id" --raw-stream-data "$PDF_FILE" > "$temp_file" 2>/dev/null; then
        # zlib解凍してブックマークページを抽出
        pages=$(python3 -c "
import zlib
import sys
try:
    with open('$temp_file', 'rb') as f:
        data = f.read()
    xml_content = zlib.decompress(data).decode('utf-8', errors='ignore')
    
    # ページインデックスを抽出
    import re
    page_indices = re.findall(r'<apple-preview:PageIndex>(\d+)</apple-preview:PageIndex>', xml_content)
    
    # 0ベースのインデックスを1ベースのページ番号に変換
    page_numbers = [str(int(idx) + 1) for idx in page_indices]
    print(' '.join(page_numbers))
except Exception as e:
    pass
" 2>/dev/null)
        
        if [ ! -z "$pages" ]; then
            BOOKMARK_PAGES="$pages"
        fi
    fi
    
    # 一時ファイルを削除
    rm -f "$temp_file"
done

# 結果を整理・表示
if [ ! -z "$BOOKMARK_PAGES" ]; then
    # 重複を除去してソート
    UNIQUE_PAGES=$(echo $BOOKMARK_PAGES | tr ' ' '\n' | sort -nu | tr '\n' ' ')
    PAGE_COUNT=$(echo $UNIQUE_PAGES | wc -w)
    
    echo "ブックマークが設定されているページ数: $PAGE_COUNT"
    echo "ブックマークページ: $UNIQUE_PAGES"
else
    echo "ブックマークは設定されていません。"
fi 