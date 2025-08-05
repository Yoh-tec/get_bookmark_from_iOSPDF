from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
import subprocess
import tempfile
import shutil
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション管理用

# 設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# アップロードフォルダの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """ファイル拡張子の検証"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_bookmarks_from_pdf(file_path):
    """PDFファイルからブックマーク情報を抽出"""
    try:
        # シェルスクリプトを実行
        result = subprocess.run(
            ['./extract_bookmarks.sh', file_path],
            capture_output=True,
            text=True,
            timeout=30  # 30秒のタイムアウト
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout,
                'error': None
            }
        else:
            return {
                'success': False,
                'output': None,
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': None,
            'error': '処理がタイムアウトしました'
        }
    except Exception as e:
        return {
            'success': False,
            'output': None,
            'error': str(e)
        }

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """ファイルアップロード処理"""
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'PDFファイルのみアップロード可能です'}), 400
    
    # ファイルサイズチェック
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'ファイルサイズが大きすぎます（最大50MB）'}), 400
    
    try:
        # 安全なファイル名を生成
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # ファイルを保存
        file.save(file_path)
        
        # ブックマーク抽出を実行
        result = extract_bookmarks_from_pdf(file_path)
        
        # 一時ファイルを削除
        try:
            os.remove(file_path)
        except:
            pass
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': filename,
                'result': result['output']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'ファイル処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/result')
def result():
    """結果表示ページ（リダイレクト用）"""
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 