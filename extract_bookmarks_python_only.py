#!/usr/bin/env python3
"""
Pythonのみでブックマーク抽出を行うスクリプト
qpdfやjqに依存しない代替実装
"""

import sys
import zlib
import re
import json
from pathlib import Path

def extract_bookmarks_from_binary(pdf_path):
    """バイナリレベルでブックマーク情報を抽出"""
    try:
        with open(pdf_path, 'rb') as file:
            content = file.read()
            
        # macOS Previewのブックマーク情報を探す
        # 複数のパターンを試行
        
        # パターン1: apple-preview:PageIndex
        xml_pattern1 = rb'<apple-preview:PageIndex>(\d+)</apple-preview:PageIndex>'
        matches1 = re.findall(xml_pattern1, content)
        
        if matches1:
            page_numbers = [int(match) + 1 for match in matches1]  # 0ベース→1ベース
            unique_pages = sorted(list(set(page_numbers)))
            page_count = len(unique_pages)
            pages_str = ' '.join(map(str, unique_pages))
            
            print(f"ブックマークが設定されているページ数: {page_count}")
            print(f"ブックマークページ: {pages_str}")
            return True
        
        # パターン2: 圧縮されたXMLデータ
        # zlibで解凍を試行
        try:
            # メタデータオブジェクトを探す
            metadata_pattern = rb'/Metadata\s+\d+\s+\d+\s+R'
            metadata_matches = re.findall(metadata_pattern, content)
            
            for match in metadata_matches:
                # オブジェクト番号を抽出
                obj_match = re.search(rb'(\d+)\s+(\d+)\s+R', match)
                if obj_match:
                    obj_num = obj_match.group(1).decode()
                    # オブジェクトの内容を探す
                    obj_pattern = rb'{} 0 obj.*?endobj'.format(obj_num.encode())
                    obj_matches = re.findall(obj_pattern, content, re.DOTALL)
                    
                    for obj_content in obj_matches:
                        # ストリームデータを探す
                        stream_pattern = rb'stream\s*(.*?)\s*endstream'
                        stream_matches = re.findall(stream_pattern, obj_content, re.DOTALL)
                        
                        for stream_data in stream_matches:
                            try:
                                # zlib解凍を試行
                                decompressed = zlib.decompress(stream_data)
                                xml_content = decompressed.decode('utf-8', errors='ignore')
                                
                                # ページインデックスを探す
                                page_indices = re.findall(r'<apple-preview:PageIndex>(\d+)</apple-preview:PageIndex>', xml_content)
                                
                                if page_indices:
                                    page_numbers = [int(idx) + 1 for idx in page_indices]
                                    unique_pages = sorted(list(set(page_numbers)))
                                    page_count = len(unique_pages)
                                    pages_str = ' '.join(map(str, unique_pages))
                                    
                                    print(f"ブックマークが設定されているページ数: {page_count}")
                                    print(f"ブックマークページ: {pages_str}")
                                    return True
                                    
                            except (zlib.error, UnicodeDecodeError):
                                continue
        
        except Exception as e:
            pass
        
        # パターン3: その他のメタデータ
        # PDFの構造を直接解析
        try:
            # ブックマーク関連のキーワードを探す
            bookmark_patterns = [
                rb'Bookmark',
                rb'Outline',
                rb'PageIndex',
                rb'apple-preview'
            ]
            
            for pattern in bookmark_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"ブックマーク関連のキーワード '{pattern.decode()}' が見つかりました")
                    # より詳細な解析が必要
        
        except Exception as e:
            pass
        
        print("ブックマーク情報が見つかりませんでした。")
        return False
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("使用方法: python extract_bookmarks_python_only.py <PDFファイル名>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    if not Path(pdf_file).exists():
        print(f"エラー: ファイル '{pdf_file}' が見つかりません")
        sys.exit(1)
    
    print(f"PDFファイルを解析中: {pdf_file}")
    extract_bookmarks_from_binary(pdf_file)

if __name__ == "__main__":
    main() 