from flask import Flask, render_template, request, jsonify, send_file
from wnacg_downloads import get_manga_images, images_to_pdf, cleanup_images
import os
import socket
import tempfile
import shutil

app = Flask(__name__)

# 建立一個臨時資料夾管理器
class TempFolderManager:
    def __init__(self):
        self.base_path = os.path.join(tempfile.gettempdir(), 'manga_downloader')
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def get_temp_folder(self):
        # 建立唯一的臨時資料夾
        temp_folder = tempfile.mkdtemp(dir=self.base_path)
        return temp_folder
    
    def cleanup(self, folder_path):
        # 清理臨時資料夾
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)

# 建立臨時資料夾管理器實例
temp_manager = TempFolderManager()

def get_ip_addresses():
    """獲取本機所有可用的IP地址"""
    hostname = socket.gethostname()
    addresses = []
    try:
        # 獲取主機名對應的IP
        host_ip = socket.gethostbyname(hostname)
        addresses.append(host_ip)
        
        # 獲取所有網路介面的IP
        for interface in socket.getaddrinfo(socket.gethostname(), None):
            ip = interface[4][0]
            if ip not in addresses and not ip.startswith('127.') and ':' not in ip:
                addresses.append(ip)
    except:
        pass
    return addresses

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    temp_folder = None
    try:
        manga_url = request.form['url']
        pdf_name = request.form['pdf_name']
        
        if not pdf_name.endswith('.pdf'):
            pdf_name += '.pdf'
        
        # 使用臨時資料夾
        temp_folder = temp_manager.get_temp_folder()
        pdf_path = os.path.join(temp_folder, pdf_name)
        
        # 開始下載過程
        image_files = get_manga_images(manga_url, temp_folder)
        if not image_files:
            return jsonify({'status': 'error', 'message': '沒有找到可下載的圖片'})
        
        # 轉換為PDF
        if images_to_pdf(image_files, pdf_path):
            cleanup_images(temp_folder, image_files)
            # 傳送PDF檔案
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=pdf_name,
                mimetype='application/pdf'
            )
        else:
            return jsonify({'status': 'error', 'message': 'PDF轉換失敗'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        # 清理臨時資料夾
        if temp_folder:
            temp_manager.cleanup(temp_folder)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # 使用環境變數的 PORT，如果沒有則使用 5000
    port = int(os.environ.get('PORT', 5000))
    
    # 在本地開發時顯示 IP 資訊
    if os.environ.get('RAILWAY_STATIC_URL') is None:
        addresses = get_ip_addresses()
        print("\n=== 漫畫下載器服務已啟動 ===")
        print("你可以使用以下位址訪問：")
        print(f"本機訪問: http://localhost:{port}")
        for ip in addresses:
            print(f"局域網訪問: http://{ip}:{port}")
        print("="*30 + "\n")
    
    # 啟動應用
    app.run(host='0.0.0.0', port=port)
