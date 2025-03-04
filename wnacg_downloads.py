from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import os
from PIL import Image
import time
from urllib.parse import urljoin

def fix_url(url, base_url):
    if url.startswith('data:'):
        return None
    if url.startswith('//'):
        return 'https:' + url
    if not url.startswith(('http://', 'https://')):
        return urljoin(base_url, url)
    return url

def is_valid_image(url):
    if not url:
        return False
    # 只下載這些格式的圖片
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    return url.lower().endswith(valid_extensions)

def get_manga_images(url, download_folder):
    # 設定 Selenium 瀏覽器
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，不開啟瀏覽器
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    # 模擬滾動頁面以加載所有圖片
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待加載
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # 取得 HTML 內容
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    # 找到所有圖片連結並修正URL
    image_tags = soup.find_all('img')
    image_urls = []
    for img in image_tags:
        if 'src' in img.attrs:
            fixed_url = fix_url(img['src'], url)
            if fixed_url and is_valid_image(fixed_url):
                image_urls.append(fixed_url)
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    downloaded_images = []
    for index, img_url in enumerate(image_urls):
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()  # 檢查請求是否成功
            
            # 修改檔案命名，確保順序正確（補零到4位數）
            img_path = os.path.join(download_folder, f"page_{index+1:04d}.jpg")
            with open(img_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            downloaded_images.append(img_path)
            print(f"下載成功: {img_url}")
        except Exception as e:
            print(f"下載失敗 {img_url}: {str(e)}")
    
    return downloaded_images

def cleanup_images(folder_path, image_paths):
    """清理下載的圖片文件"""
    try:
        # 刪除所有下載的圖片
        for img_path in image_paths:
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"已刪除: {img_path}")
        
        # 如果資料夾為空，則刪除資料夾
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)
            print(f"已刪除空資料夾: {folder_path}")
    except Exception as e:
        print(f"清理文件時發生錯誤: {e}")

def natural_sort_key(s):
    """實現自然排序的鍵值函數"""
    import re
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def images_to_pdf(image_paths, output_pdf):
    try:
        # 檢查是否有圖片可供轉換
        valid_images = []
        # 使用自然排序來排序檔案
        for img_path in sorted(image_paths, key=natural_sort_key):  # 確保圖片順序
            if os.path.exists(img_path):
                try:
                    with Image.open(img_path) as img:
                        # 轉換為 RGB 模式（去除透明通道）
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        valid_images.append(img.copy())  # 建立副本以避免資源釋放問題
                except Exception as e:
                    print(f"無法處理圖片 {img_path}: {e}")
                    continue
            else:
                print(f"找不到圖片: {img_path}")

        if valid_images:
            # 確保輸出目錄存在
            output_dir = os.path.dirname(output_pdf)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 儲存為PDF
            valid_images[0].save(
                output_pdf,
                "PDF",
                save_all=True,
                append_images=valid_images[1:],
                resolution=100.0,
                quality=95
            )
            print(f"成功建立 PDF: {output_pdf}")
            print(f"共處理 {len(valid_images)} 張圖片")
            return True  # 表示PDF轉換成功
        else:
            print("沒有有效的圖片可轉換！")
            return False
    except Exception as e:
        print(f"PDF 轉換失敗: {e}")
        return False
    finally:
        # 清理記憶體
        if 'valid_images' in locals():
            for img in valid_images:
                img.close()

if __name__ == "__main__":
    while True:
        manga_url = input("請輸入漫畫網址 (直接按Enter離開程式): ").strip()
        if not manga_url:  # 如果使用者直接按Enter，則結束程式
            print("程式結束")
            break
            
        save_folder = "manga_downloads"
        pdf_output = input("請輸入PDF檔案名稱 (預設為manga.pdf): ").strip()
        if not pdf_output:  # 如果使用者沒有輸入，使用預設值
            pdf_output = "manga.pdf"
        elif not pdf_output.endswith('.pdf'):  # 確保檔案名稱有.pdf副檔名
            pdf_output += '.pdf'
        
        try:
            print(f"開始下載: {manga_url}")
            image_files = get_manga_images(manga_url, save_folder)
            if image_files:
                print(f"開始轉換 {len(image_files)} 張圖片為 PDF...")
                if images_to_pdf(image_files, pdf_output):
                    print("開始清理下載的圖片...")
                    cleanup_images(save_folder, image_files)
                    print("清理完成！")
            else:
                print("沒有下載到任何圖片")
                
            print("\n" + "="*50 + "\n")  # 分隔線
        except Exception as e:
            print(f"處理過程發生錯誤: {e}")
            print("\n" + "="*50 + "\n")  # 分隔線
