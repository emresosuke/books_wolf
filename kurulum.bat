@echo off
chcp 65001 >nul
title T Bot — Kurulum
color 0A

echo.
echo  ============================================
echo    T BOT — OTOMATIK KURULUM
echo  ============================================
echo.

REM ── Python kontrolü ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python bulunamadi!
    echo.
    echo  Lutfen Python 3.10 veya uzeri yukleyin:
    echo  https://www.python.org/downloads/
    echo.
    echo  ONEMLI: Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [✓] Python bulundu: %PYVER%
echo.

REM ── pip güncelle ────────────────────────────────────────────────────────────
echo  [i] pip guncelleniyor...
python -m pip install --upgrade pip --quiet
echo  [✓] pip guncellendi
echo.

REM ── Paketleri yükle ─────────────────────────────────────────────────────────
echo  [i] Gerekli Python paketleri yukleniyor...
echo      (Bu islem birka dakika surebilir)
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  [!] Paket yuklemesinde hata olustu!
    echo  Lutfen internet baglantinizi kontrol edin ve tekrar deneyin.
    pause
    exit /b 1
)
echo.
echo  [✓] Python paketleri basariyla yuklendi!
echo.

REM ── FFmpeg kontrolü ─────────────────────────────────────────────────────────
echo  [i] FFmpeg kontrol ediliyor...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  [i] FFmpeg bulunamadi — yukleniyor...
    winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo  [!] FFmpeg otomatik yuklenemedi.
        echo  Manuel olarak yuklemek icin: https://ffmpeg.org/download.html
        echo  veya winget install Gyan.FFmpeg komutunu yonetici olarak calistirin.
        echo.
    ) else (
        echo  [✓] FFmpeg yuklendi!
    )
) else (
    echo  [✓] FFmpeg zaten kurulu!
)
echo.

REM ── Tarayıcı kontrolü ───────────────────────────────────────────────────────
echo  [i] Tarayici kontrol ediliyor...
set BROWSER_FOUND=0

if exist "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" (
    echo  [✓] Brave Browser bulundu!
    set BROWSER_FOUND=1
)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo  [✓] Google Chrome bulundu!
    set BROWSER_FOUND=1
)
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo  [✓] Google Chrome bulundu!
    set BROWSER_FOUND=1
)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo  [✓] Microsoft Edge bulundu!
    set BROWSER_FOUND=1
)

if %BROWSER_FOUND%==0 (
    echo.
    echo  [!] Desteklenen tarayici bulunamadi!
    echo  Asagidakilerden birini yukleyin:
    echo    - Brave:  https://brave.com
    echo    - Chrome: https://www.google.com/chrome/
    echo.
)
echo.

REM ── Sonuç ───────────────────────────────────────────────────────────────────
echo  ============================================
echo    KURULUM TAMAMLANDI!
echo  ============================================
echo.
echo  Botu baslatmak icin: baslat.bat dosyasina cift tiklayin
echo  veya asagidaki komutu calistirin:
echo.
echo    python gui_app.py
echo.
pause
