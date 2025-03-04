document.addEventListener('DOMContentLoaded', function() {
    const downloadBtn = document.getElementById('download-btn');
    const mangaUrl = document.getElementById('manga-url');
    const pdfName = document.getElementById('pdf-name');
    const statusMessage = document.getElementById('status-message');
    const progress = document.querySelector('.progress');

    downloadBtn.addEventListener('click', async function() {
        if (!mangaUrl.value) {
            showMessage('請輸入漫畫網址', 'error');
            return;
        }

        // 禁用按鈕和輸入
        downloadBtn.disabled = true;
        mangaUrl.disabled = true;
        pdfName.disabled = true;

        // 顯示進度
        showProgress(true);
        showMessage('開始下載...', '');

        try {
            const formData = new FormData();
            formData.append('url', mangaUrl.value);
            formData.append('pdf_name', pdfName.value || 'manga.pdf');

            const response = await fetch('/download', {
                method: 'POST',
                body: formData
            });

            // 檢查回應類型
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/pdf')) {
                // 處理PDF下載
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = pdfName.value || 'manga.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                showMessage('下載完成！', 'success');
            } else {
                // 處理錯誤回應
                const data = await response.json();
                showMessage(data.message, 'error');
            }
        } catch (error) {
            showMessage('下載過程發生錯誤', 'error');
        } finally {
            // 重置表單狀態
            downloadBtn.disabled = false;
            mangaUrl.disabled = false;
            pdfName.disabled = false;
            showProgress(false);
        }
    });

    function showMessage(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = type;
    }

    function showProgress(show) {
        if (show) {
            progress.style.width = '100%';
        } else {
            progress.style.width = '0%';
        }
    }
});
