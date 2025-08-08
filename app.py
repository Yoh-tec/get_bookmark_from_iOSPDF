from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
import os
import subprocess
import tempfile
import shutil
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # セッション管理用

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

def check_dependencies():
    """依存関係の確認"""
    dependencies = {}
    
    # qpdfの確認
    try:
        result = subprocess.run(['qpdf', '--version'], capture_output=True, text=True, timeout=10)
        dependencies['qpdf'] = {
            'installed': result.returncode == 0,
            'version': result.stdout.strip() if result.returncode == 0 else 'Not found',
            'error': result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        dependencies['qpdf'] = {
            'installed': False,
            'version': 'Error',
            'error': str(e)
        }
    
    # jqの確認
    try:
        result = subprocess.run(['jq', '--version'], capture_output=True, text=True, timeout=10)
        dependencies['jq'] = {
            'installed': result.returncode == 0,
            'version': result.stdout.strip() if result.returncode == 0 else 'Not found',
            'error': result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        dependencies['jq'] = {
            'installed': False,
            'version': 'Error',
            'error': str(e)
        }
    
    # Pythonの確認
    try:
        import sys
        dependencies['python'] = {
            'installed': True,
            'version': sys.version,
            'error': None
        }
    except Exception as e:
        dependencies['python'] = {
            'installed': False,
            'version': 'Error',
            'error': str(e)
        }
    
    return dependencies

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

@app.route('/health')
def health():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '2025-08-07T00:00:00Z'
    })

@app.route('/debug/dependencies')
def debug_dependencies():
    """依存関係の確認エンドポイント"""
    dependencies = check_dependencies()
    return jsonify({
        'dependencies': dependencies,
        'environment': {
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not set'),
            'PORT': os.environ.get('PORT', 'Not set'),
            'PYTHON_VERSION': os.environ.get('PYTHON_VERSION', 'Not set')
        }
    })

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
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 