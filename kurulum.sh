#!/bin/bash

echo "============================================"
echo "   T BOT — MAC OTO KURULUM"
echo "============================================"
echo ""

# Python 3 Kontrolü
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[!] Python 3 bulunamadı!"
    echo "Macbook'ta Python 3 kurmak için lütfen Terminal'de şu komutu çalıştırın:"
    echo "  brew install python"
    echo ""
    echo "Eğer Homebrew kurulu değilse, önce https://brew.sh adresindeki adımları izleyin."
    exit 1
fi

echo "[✓] Python 3 bulundu."

# pip güncelle
echo "[i] pip güncelleniyor..."
python3 -m pip install --upgrade pip --quiet

# Paketleri yükleme
echo "[i] Gerekli Python paketleri yükleniyor..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[!] Paket yüklemesinde hata oluştu!"
    exit 1
fi
echo "[✓] Python paketleri başarıyla yüklendi."

# Tkinter Kontrolü
python3 -c "import tkinter" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[!] tkinter bulunamadı! Arayüz (customtkinter) hata verebilir."
    echo "Çözmek için şu komutu çalıştırın:"
    echo "  brew install python-tk"
    echo ""
fi

# FFmpeg Kontrolü
ffmpeg -version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[i] FFmpeg bulunamadı. Kuruluyor (Homebrew gerekir)..."
    brew install ffmpeg
    if [ $? -ne 0 ]; then
        echo "[!] FFmpeg otomatik kurulamadı. Lütfen 'brew install ffmpeg' komutunu manuel çalıştırın veya sesli captcha çözümünü kapatın."
    else
        echo "[✓] FFmpeg başarıyla kuruldu!"
    fi
else
    echo "[✓] FFmpeg zaten kurulu."
fi

# Tarayıcı Kontrolü
BROWSER_FOUND=0
if [ -d "/Applications/Brave Browser.app" ] || [ -d "$HOME/Applications/Brave Browser.app" ]; then
    echo "[✓] Brave Browser bulundu!"
    BROWSER_FOUND=1
fi
if [ -d "/Applications/Google Chrome.app" ] || [ -d "$HOME/Applications/Google Chrome.app" ]; then
    echo "[✓] Google Chrome bulundu!"
    BROWSER_FOUND=1
fi
if [ -d "/Applications/Microsoft Edge.app" ] || [ -d "$HOME/Applications/Microsoft Edge.app" ]; then
    echo "[✓] Microsoft Edge bulundu!"
    BROWSER_FOUND=1
fi

if [ $BROWSER_FOUND -eq 0 ]; then
    echo "[!] UYARI: Brave, Chrome veya Edge tarayıcılarından biri kurulu değil."
    echo "Lütfen botu çalıştırmadan önce bunlardan birini yükleyin."
fi

echo ""
echo "============================================"
echo "   KURULUM TAMAMLANDI!"
echo "============================================"
echo "Botu başlatmak için: ./baslat.sh komutunu çalıştırın."
echo ""
