FROM python:3.9-slim

# 安裝必要的套件
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    fonts-noto-cjk

# 安裝特定版本的 Chromium 和 ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable=114.0.5735.90-1 \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . .

# 安裝 Python 依賴
RUN pip install -r requirements.txt

# 設定環境變數
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV PORT=5000

# 開放端口
EXPOSE 5000

# 啟動應用
CMD ["python", "app.py"]
