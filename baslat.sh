#!/bin/bash

# Python kontrolü
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[!] Python 3 bulunamadı!"
    echo "Lütfen önce './kurulum.sh' scriptini çalıştırın."
    exit 1
fi

# Kritik paket kontrolü
python3 -c "import customtkinter, selenium, undetected_chromedriver, pandas" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[!] Gerekli paketler eksik! Kurulum başlatılıyor..."
    chmod +x kurulum.sh
    ./kurulum.sh
fi

echo ""
echo "T Bot başlatılıyor..."
echo ""
python3 gui_app.py
