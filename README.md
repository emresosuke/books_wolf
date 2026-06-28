# T Bot — TÜGVA Yaz Okulu Kayıt Otomasyonu

Excel dosyasındaki öğrenci bilgilerini okuyarak TÜGVA Yaz Okulu başvuru formunu otomatik dolduran bot.

---

## 🚀 Kurulum (Kurulum ve Çalıştırma)

### 🖥️ Windows İçin

1. **Python Kur:** Python 3.10 veya üzeri gereklidir. [python.org/downloads](https://www.python.org/downloads/) adresinden indirin. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretlemeyi unutmayın!
2. **Kurulum Scriptini Çalıştır:** `kurulum.bat` dosyasına çift tıklayarak çalıştırın. (Bağımlılıkları ve FFmpeg'i yükler).
3. **Botu Başlat:** `baslat.bat` dosyasına çift tıklayın.

---

### 🍎 macOS (Macbook) İçin

1. **Terminal'i Açın:** Macbook'unuzda **Terminal** uygulamasını açın.
2. **Homebrew, Python ve FFmpeg Kurun:** Terminal'de aşağıdaki komutları çalıştırarak gerekli araçları kurun:
   ```bash
   # Homebrew kurulu değilse kurun (https://brew.sh)
   # Ardından python3, ffmpeg ve tkinter'ı yükleyin:
   brew install python ffmpeg python-tk
   ```
3. **Proje Klasörüne Gidin:** Terminal'den indirdiğiniz klasöre gidin:
   ```bash
   cd /path/to/books_wolf-main
   ```
4. **Kurulumu Çalıştırın:** Script'e izin verip çalıştırın:
   ```bash
   chmod +x kurulum.sh baslat.sh
   ./kurulum.sh
   ```
5. **Botu Başlatın:**
   ```bash
   ./baslat.sh
   ```

---

## ⚙️ Yapılandırma

`config.py` dosyasını açın ve API anahtarınızı girin:

```python
TWOCAPTCHA_API_KEY = "buraya_api_anahtarinizi_girin"
```

> 2captcha API anahtarı için: [2captcha.com](https://2captcha.com)

---

## 🌐 Desteklenen Tarayıcılar

Bot aşağıdaki tarayıcıları otomatik tespit eder (öncelik sırasıyla):

| # | Tarayıcı | İndirme Linki |
|---|---|---|
| 1 | **Brave** (önerilen) | [brave.com](https://brave.com) |
| 2 | Google Chrome | [google.com/chrome](https://www.google.com/chrome/) |
| 3 | Microsoft Edge | Windows'ta yerleşik gelir |

---

## 📋 Gereksinimler

| Gereksinim | Versiyon |
|---|---|
| Python | 3.10 veya üzeri |
| Tarayıcı | Brave / Chrome / Edge |
| FFmpeg | Herhangi (winget ile otomatik kurulur) |
| 2captcha Kredisi | ~$1.5 / 1000 başvuru |

---

## 📂 Dosya Yapısı

```
books_wolf-main/
├── baslat.bat          ← Botu başlatır
├── kurulum.bat         ← İlk kurulum (bir kez çalıştırın)
├── requirements.txt    ← Python bağımlılıkları
├── config.py           ← API anahtarı ve ayarlar
├── bot.py              ← Ana bot kodu
├── gui_app.py          ← Arayüz
├── excel_handler.py    ← Excel okuma
└── completed.txt       ← Tamamlanan kayıtlar (otomatik oluşur)
```

---

## ❓ Sık Sorulan Sorular

**Bot hangi Excel sütunlarını okur?**  
`AD`, `SOYAD`, `T.C.`, `DOĞUM TARİHİ` sütunları okunur.

**Yarıda kesilirse ne olur?**  
`completed.txt` dosyasında tamamlanan TC numaraları tutulur. Bot yeniden başlatıldığında kaldığı yerden devam eder.

**Okul nasıl seçiliyor?**  
Diyarbakır Yenişehir'deki 27 ortaokuldan rastgele biri seçilir.

**CAPTCHA otomatik çözülüyor mu?**  
Evet, `config.py`'ye 2captcha API anahtarı girilmişse tam otomatik çözülür.
