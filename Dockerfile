FROM python:3.9-slim

# 安裝必要的套件
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    fonts-noto-cjk \
    chromium \
    chromium-driver \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libgbm1

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
ENV DISPLAY=:99

# 開放端口
EXPOSE 5000

# 使用 xvfb-run 啟動應用
CMD xvfb-run --server-args="-screen 0 1280x720x24" python app.py
