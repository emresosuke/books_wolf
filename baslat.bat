@echo off
chcp 65001 >nul
title T Bot — TÜGVA Başvuru Otomasyonu
color 0A

REM ── Python kontrolü ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [!] Python bulunamadi!
    echo  Lutfen once "kurulum.bat" dosyasini calistirin.
    echo.
    pause
    exit /b 1
)

REM ── Kritik paket kontrolü ────────────────────────────────────────────────────
python -c "import customtkinter, selenium, undetected_chromedriver, pandas" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [!] Gerekli paketler eksik!
    echo  "kurulum.bat" calistiriliyor...
    echo.
    call kurulum.bat
)

REM ── Botu başlat ─────────────────────────────────────────────────────────────
echo.
echo  T Bot baslatiliyor...
echo.
python gui_app.py

pause
