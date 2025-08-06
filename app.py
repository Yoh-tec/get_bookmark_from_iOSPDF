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

def extract_pages_from_pdf(input_path, pages, output_path):
    """指定されたページのみを抽出して新しいPDFを作成"""
    try:
        # ページ番号を文字列に変換
        pages_str = ','.join(map(str, pages))
        
        # qpdfを使用してページを抽出
        result = subprocess.run([
            'qpdf', 
            '--pages', input_path, pages_str,
            '--', input_path, output_path
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, 'ページ抽出がタイムアウトしました'
    except Exception as e:
        return False, str(e)

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

@app.route('/extract_pages', methods=['POST'])
def extract_pages():
    """ブックマークページの抽出"""
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if 'pages' not in request.form:
        return jsonify({'error': 'ページ情報が指定されていません'}), 400
    
    file = request.files['file']
    pages_str = request.form['pages']
    
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'PDFファイルのみアップロード可能です'}), 400
    
    # ページ番号を解析
    try:
        pages = [int(p) for p in pages_str.split(',') if p.strip()]
        if not pages:
            return jsonify({'error': '有効なページ番号が指定されていません'}), 400
    except ValueError:
        return jsonify({'error': '無効なページ番号が含まれています'}), 400
    
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
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        output_filename = f"bookmarks_{filename}"
        output_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{output_filename}")
        
        # ファイルを保存
        file.save(input_path)
        
        # ページ抽出を実行
        success, error = extract_pages_from_pdf(input_path, pages, output_path)
        
        # 入力ファイルを削除
        try:
            os.remove(input_path)
        except:
            pass
        
        if success:
            # ファイルをダウンロード用に送信
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
        else:
            # 出力ファイルを削除
            try:
                os.remove(output_path)
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': error
            }), 500
            
    except Exception as e:
        # クリーンアップ
        try:
            os.remove(input_path)
        except:
            pass
        try:
            os.remove(output_path)
        except:
            pass
        
        return jsonify({'error': f'ページ抽出中にエラーが発生しました: {str(e)}'}), 500

@app.route('/result')
def result():
    """結果表示ページ（リダイレクト用）"""
    return render_template('result.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 