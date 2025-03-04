FROM python:3.9-slim

# 安裝必要的套件
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    fonts-noto-cjk \
    chromium \
    chromium-driver

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . .

# 安裝 Python 依賴
RUN pip install -r requirements.txt

# 設定環境變數
ENV CHROME_BINARY_LOCATION=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# 開放端口
EXPOSE 5000

# 啟動應用
CMD ["python", "app.py"]
