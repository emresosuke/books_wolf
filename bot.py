import time
import random
from datetime import datetime
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    import undetected_chromedriver as uc
except ImportError:
    print("Selenium not found. Please run 'pip install selenium webdriver-manager'")
    exit()

import config
import excel_handler
import gender_guesser
import os

# Global logger callback
STOP_BOT = False

# Rastgele veli adı için Türkçe isim listesi
RASTGELE_ADLAR = [
    "Ahmet", "Mehmet", "Ali", "Mustafa", "İbrahim", "Hüseyin", "Hasan",
    "Fatma", "Ayşe", "Emine", "Hatice", "Zeynep", "Elif", "Merve",
    "Murat", "Ömer", "Yusuf", "Ramazan", "İsmail", "Halil",
    "Havva", "Şükran", "Gülay", "Nesrin", "Selma", "Nurten"
]

def random_phone():
    """5xx-xxx-xxxx formatında rastgele Türk cep telefonu numarası üretir."""
    prefix = random.choice(['530', '531', '532', '533', '535', '536', '537',
                            '538', '539', '541', '542', '543', '544', '545',
                            '546', '551', '552', '553', '554', '555'])
    mid   = str(random.randint(100, 999))
    end   = str(random.randint(1000, 9999))
    return f"{prefix}-{mid}-{end}"

def random_parent_name(soyad):
    """Rastgele bir Türkçe ad + veriden gelen soyadı döndürür."""
    return f"{random.choice(RASTGELE_ADLAR)} {soyad}"

# Sınıf → doğum yılı aralığı haritası (2025-2026 eğitim yılına göre)
SINIF_YIL = {
    '5': [2014, 2015],
    '6': [2013, 2014],
    '7': [2012, 2013],
    '8': [2011, 2012],
}

def random_birthdate(sinif_str):
    """
    Sınıfa göre rastgele doğum tarihi üretir (GG.AA.YYYY formatı).
    Gün ve ay tamamen rastgele; yıl sınıfa göre belirlenir.
    Sınıf bilinmiyorsa yıl 2011-2015 aralığından seçilir.
    """
    import re
    # "5. Sınıf", "5.sınıf", "5", "Durumu:5" gibi formatlardan ilk rakamı al
    match = re.search(r'\b(\d)\b', str(sinif_str))   # tek basamaklı kelime önce
    if not match:
        match = re.search(r'(\d)', str(sinif_str))    # en az bir rakam
    sinif_num = match.group(1) if match else ''
    if sinif_num in SINIF_YIL:
        year = random.choice(SINIF_YIL[sinif_num])
    else:
        year = random.randint(2011, 2015)             # Bilinmiyorsa geniş aralık
    month = random.randint(1, 12)
    # Ay gün sayısını hesapla (28'i aşmamak için 28 kullaınılır)
    max_day = 28 if month == 2 else (30 if month in [4, 6, 9, 11] else 31)
    day = random.randint(1, max_day)
    return f"{day:02d}.{month:02d}.{year}"

def log(msg, callback=None):
    if callback:
        try:
            callback(str(msg))
        except: pass
    print(msg)

def _find_browser():
    """
    Bilgisayarda kurulu Chromium tabanlı tarayıcıyı otomatik olarak bulur.
    Sırasıyla dener: Brave → Chrome → Edge
    Bulamazsa None döndürür (undetected_chromedriver kendi bulur).
    """
    import sys
    
    if sys.platform.startswith('win'):
        candidates = [
            # Brave
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            # Chrome
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            # Edge
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif sys.platform == 'darwin':
        home = os.path.expanduser("~")
        candidates = [
            # Brave
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            os.path.join(home, "Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
            # Chrome
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            os.path.join(home, "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            # Edge
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            os.path.join(home, "Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
    else:
        candidates = [
            "/usr/bin/brave-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/microsoft-edge",
        ]

    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def get_browser_major_version(browser_path):
    """
    Tarayıcı exe dosyasının sürüm bilgisini (major version) alır.
    Windows'ta PowerShell aracılığıyla, diğer sistemlerde CLI parametresiyle.
    """
    import subprocess
    import sys
    import re
    if not browser_path or not os.path.exists(browser_path):
        return None
    if sys.platform.startswith('win'):
        try:
            cmd = ['powershell', '-NoProfile', '-Command', f'(Get-Item "{browser_path}").VersionInfo.ProductVersion']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            out = result.stdout.strip()
            match = re.match(r"^(\d+)", out)
            if match:
                return int(match.group(1))
        except Exception:
            pass
    try:
        result = subprocess.run([browser_path, "--version"], capture_output=True, text=True, timeout=5)
        out = result.stdout.strip() or result.stderr.strip()
        match = re.search(r"(\d+)\.\d+\.\d+\.\d+", out)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def init_driver(log_callback=None):
    """
    Tarayıcıyı otomatik tespit edip başlatır.
    Brave → Chrome → Edge sırasıyla arar; bulduğunu kullanır.
    """
    import re
    options = uc.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--lang=en-US")

    # Sabit profil klasörü yolu (Proje dizini altında 'chrome_profile')
    project_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(project_dir, "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")

    log(f"   [i] Kalıcı tarayıcı profili kullanılıyor: {profile_dir}", log_callback)
    log("   [i] İPUCU: Açılan tarayıcıda bir kez Google/Gmail hesabınıza giriş yaparsanız captcha engellerini çok daha kolay aşarsınız.", log_callback)

    browser_path = _find_browser()
    major_version = None

    if browser_path:
        browser_name = os.path.basename(browser_path).replace('.exe', '').title()
        log(f"   [i] Tarayıcı bulundu: {browser_name} ({browser_path})", log_callback)
        major_version = get_browser_major_version(browser_path)
        if major_version:
            log(f"   [i] Tespit edilen tarayıcı ana sürümü: {major_version}", log_callback)
    else:
        log("   [i] Tarayıcı yolu bulunamadı — sistem varsayılanı denenecek.", log_callback)

    try:
        kwargs = {"options": options}
        if browser_path:
            kwargs["browser_executable_path"] = browser_path
        if major_version:
            kwargs["version_main"] = major_version
        driver = uc.Chrome(**kwargs)
        driver.maximize_window()
        return driver
    except Exception as e:
        log(f"   [!] Tarayıcı başlatılamadı: {e}", log_callback)
        
        # Check for version mismatch error
        err_msg = str(e)
        match = re.search(r"Current browser version is (\d+)", err_msg)
        if match:
            major_version = int(match.group(1))
            log(f"   [i] Sürüm uyumsuzluğu tespit edildi. Tarayıcı sürümü: {major_version}. Bu sürümle tekrar deneniyor...", log_callback)
            try:
                retry_options = uc.ChromeOptions()
                retry_options.add_argument("--disable-popup-blocking")
                retry_options.add_argument("--lang=en-US")
                kwargs = {"options": retry_options, "version_main": major_version}
                if browser_path:
                    kwargs["browser_executable_path"] = browser_path
                driver = uc.Chrome(**kwargs)
                driver.maximize_window()
                return driver
            except Exception as e_retry:
                log(f"   [!] Sürüm {major_version} ile de başlatılamadı: {e_retry}", log_callback)

        log("   [i] undetected_chromedriver ile varsayılan tarayıcı deneniyor...", log_callback)
        try:
            default_options = uc.ChromeOptions()
            default_options.add_argument("--disable-popup-blocking")
            default_options.add_argument("--lang=en-US")
            driver = uc.Chrome(options=default_options)
            driver.maximize_window()
            return driver
        except Exception as e2:
            log(f"   [!] Varsayılan tarayıcı başlatılamadı: {e2}", log_callback)
            
            # Check version mismatch on the default driver too
            err_msg2 = str(e2)
            match2 = re.search(r"Current browser version is (\d+)", err_msg2)
            if match2:
                major_version2 = int(match2.group(1))
                log(f"   [i] Varsayılan tarayıcıda sürüm uyumsuzluğu. Tarayıcı sürümü: {major_version2}. Bu sürümle tekrar deneniyor...", log_callback)
                try:
                    default_retry_options = uc.ChromeOptions()
                    default_retry_options.add_argument("--disable-popup-blocking")
                    default_retry_options.add_argument("--lang=en-US")
                    driver = uc.Chrome(options=default_retry_options, version_main=major_version2)
                    driver.maximize_window()
                    return driver
                except Exception as e2_retry:
                    log(f"   [X] Sürüm {major_version2} ile varsayılan tarayıcı başlatılamadı: {e2_retry}", log_callback)
            
            return None


def format_phone(phone_str):
    """Format phone to 5xx-xxx-xxxx format"""
    if not phone_str:
        return phone_str
    # Strip all non-digit chars
    digits = ''.join(ch for ch in str(phone_str) if ch.isdigit())
    # Remove leading 0 or 90 country code
    if digits.startswith('90') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    # Format as 5xx-xxx-xxxx
    if len(digits) == 10:
        return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
    return phone_str

# ─── DİYARBAKIR YENİŞEHİR ORTAOKUL LİSTESİ ─────────────────────────────────────────────
YENISEHIR_ORTAOKULLAR = [
"Şehit Yüzbaşı Bahtiyar Er İmam Hatip Ortaokulu",
"Şair Sirri Hanim Ortaokulu",
"Şehit Albay Güner Ekici İmam Hatip Ortaokulu",
"Şehit Başkomiser Fatih Özdil İmam Hatip Ortaokulu",
"Kesikağaç Ortaokulu",
"Tanışık Ortaokulu",
"Şehit Mehmet Hüseyin Balta Ortaokulu",
"Hamravat Ortaokulu",
"Hasanpaşa Ortaokulu",
"Dimer Yaytaş Ortaokulu",
"Seyrantepe Ortaokulu",
"Gazi Ortaokulu",
]
# ───────────────────────────────────────────────────────────────────────────────

# ─── SABİT DEĞERLER ───────────────────────────────────────────────────────────
# Aşağıdaki değerler her öğrenci için sabit olarak uygulanır:
SABIT = {
    'okul_ili'            : 'Diyarbakır',
    'okul_ilcesi'         : 'Kayapınar',
    'yaz_okulu_ili'       : 'Diyarbakır',
    'yaz_okulu_ilcesi'    : 'Kayapınar',
    'nationality_val'     : '1',          # 1 = TC Vatandaşı
    'hadis_val'           : '2',          # 2 = Hayır
    # Cinsiyet alanı DOLDURULMAYACAK (formda zorunlu ama tahmin ihtimali yanlış)
}
# ─────────────────────────────────────────────────────────────────────────────

def format_date_for_input(date_str):
    """Convert yyyy-mm-dd (y.a.g) to dd.mm.yyyy (g.a.y) for the form input"""
    if not date_str:
        return date_str
    try:
        # Check if it's separated by hyphen
        if '-' in date_str:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            return d.strftime('%d.%m.%Y')  # g.a.y formatı
        # Check if it's separated by dot
        elif '.' in date_str:
            parts = date_str.split('.')
            if len(parts[0]) == 4:  # yyyy.mm.dd ise
                d = datetime.strptime(date_str, '%Y.%m.%d')
                return d.strftime('%d.%m.%Y')
            return date_str # Zaten dd.mm.yyyy ise dokunma
        # Check if it's separated by slash
        elif '/' in date_str:
            parts = date_str.split('/')
            if len(parts[0]) == 4:  # yyyy/mm/dd ise
                d = datetime.strptime(date_str, '%Y/%m/%d')
                return d.strftime('%d.%m.%Y')
        return date_str
    except Exception:
        return date_str

def fill_select_by_value(driver, selector, value, log_callback=None):
    """Fill a select element by value (numeric string)"""
    time.sleep(random.uniform(0.1, 0.3))
    try:
        wait = WebDriverWait(driver, 5)
        element = wait.until(EC.element_to_be_clickable((By.NAME, selector)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.15)
        select = Select(element)
        select.select_by_value(str(value))
        log(f"      [✓] Selected value '{value}' for {selector}", log_callback)
    except Exception as e:
        log(f"      [X] Failed to select '{value}' in {selector}: {e}", log_callback)

def clean_val(s):
    return str(s).strip().lower().replace('ı', 'i').replace('i̇', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')

def fill_lookup(driver, name_selector, value, log_callback=None):
    """Fill a lookup-behavior autocomplete field with character-by-character typing and suggestion clicking"""
    if not value:
        return
    
    time.sleep(random.uniform(0.1, 0.2))
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.NAME, name_selector)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.15)
        element.click()
        element.clear()
        time.sleep(0.15)
        
        # Send keys character-by-character to trigger autocomplete reliably
        for char in value:
            element.send_keys(char)
            time.sleep(random.uniform(0.04, 0.08))
            
        # Poll for suggestions list elements to appear and become visible
        suggestions = []
        start_time = time.time()
        while time.time() - start_time < 4.0:
            found_elements = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item-wrapper")
            suggestions = [el for el in found_elements if el.is_displayed() and el.text.strip()]
            if suggestions:
                break
            time.sleep(0.15)
            
        clicked = False
        target_clean = clean_val(value)
        
        # 1. Look for an exact match (ignoring Turkish casing/accents)
        for item in suggestions:
            item_text = item.text.strip()
            if clean_val(item_text) == target_clean:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", item)
                time.sleep(0.08)
                item.click()
                clicked = True
                log(f"      [✓] Lookup selected: {item_text}", log_callback)
                break
                
        # 2. Look for a substring match
        if not clicked:
            for item in suggestions:
                item_text = item.text.strip()
                if target_clean in clean_val(item_text) or clean_val(item_text) in target_clean:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", item)
                    time.sleep(0.08)
                    item.click()
                    clicked = True
                    log(f"      [✓] Lookup selected (partial match): {item_text}", log_callback)
                    break
                    
        # 3. Fallback: click the first suggestion if any are present
        if not clicked and suggestions:
            item_text = suggestions[0].text.strip()
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", suggestions[0])
            time.sleep(0.08)
            suggestions[0].click()
            clicked = True
            log(f"      [✓] Lookup selected (fallback first): {item_text}", log_callback)
            
        if not clicked:
            element.send_keys(Keys.TAB)
            log(f"      [i] Lookup typed '{value}' (no suggestion clicked)", log_callback)
            
        time.sleep(0.15)
    except Exception as e:
        log(f"      [X] Failed to fill lookup '{name_selector}': {e}", log_callback)
def fill_school_from_dropdown(driver, name_selector, search_text='Yeni', log_callback=None):
    """
    Okul alanına kısa bir arama terimi yazar, gelen önerilerden
    rastgele birini seçer. Sayfadaki gerçek okul listesini kullanır.
    """
    time.sleep(random.uniform(0.1, 0.2))
    selected_name = None
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.NAME, name_selector)))
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", element)
        time.sleep(0.15)
        element.click()
        element.clear()
        time.sleep(0.1)

        # Arama kelimesini karakter karakter yaz
        for char in search_text:
            element.send_keys(char)
            time.sleep(random.uniform(0.04, 0.08))

        # Önerilerin yüklenmesini bekle (max 5sn)
        suggestions = []
        start_time = time.time()
        while time.time() - start_time < 5.0:
            found = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item-wrapper")
            suggestions = [el for el in found if el.is_displayed() and el.text.strip()]
            if suggestions:
                break
            time.sleep(0.15)

        if not suggestions:
            log(f"      [!] '{search_text}' için öneri gelmedi, listedeki ilk okul deneniyor...", log_callback)
            # Yedek: hardcoded listeden rastgele seç
            fallback = random.choice(YENISEHIR_ORTAOKULLAR)
            element.clear()
            for char in fallback:
                element.send_keys(char)
                time.sleep(random.uniform(0.04, 0.08))
            time.sleep(0.5)
            found = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item-wrapper")
            suggestions = [el for el in found if el.is_displayed() and el.text.strip()]

        if suggestions:
            # Rastgele bir okul seç
            chosen = random.choice(suggestions)
            selected_name = chosen.text.strip()
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior:'instant',block:'center'});", chosen)
            time.sleep(0.1)
            chosen.click()
            log(f"      [✓] Okul seçildi (dropdown'dan): {selected_name}", log_callback)
        else:
            element.send_keys(Keys.TAB)
            log(f"      [!] Okul önerisi bulunamadı, alan boş bırakıldı.", log_callback)

        time.sleep(0.15)
    except Exception as e:
        log(f"      [X] Okul seçim hatası: {e}", log_callback)

    return selected_name

def fill_field(driver, field_key, value, by_method=By.NAME, hit_enter=False, log_callback=None, max_retries=3):
    """Helper to fill a simple text/email/tel field safely with retry logic."""
    if not value:
        return
    
    selector = config.FIELDS.get(field_key)
    if not selector: return

    log(f"   -> Filling {field_key} with '{value}'...", log_callback)
    
    for attempt in range(max_retries):
        time.sleep(random.uniform(0.1, 0.3))

        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((by_method, selector)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.15)
            
            element = wait.until(EC.element_to_be_clickable((by_method, selector)))
            
            element.click()
            element.clear()
            element.send_keys(value)
            time.sleep(0.1)
            
            current_val = element.get_attribute('value')
            if current_val and len(current_val.strip()) > 0:
                log(f"      [✓] {field_key} filled successfully (attempt {attempt+1})", log_callback)
                return
            else:
                log(f"      [!] {field_key} boş kaldı, JS ile dolduruluyor... (attempt {attempt+1})", log_callback)
                driver.execute_script("""
                    var el = arguments[0];
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, arguments[1]);
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                """, element, value)
                time.sleep(0.1)
                current_val = element.get_attribute('value')
                if current_val and len(current_val.strip()) > 0:
                    log(f"      [✓] {field_key} filled via JS (attempt {attempt+1})", log_callback)
                    return
                    
        except Exception as e:
            log(f"      [!] {field_key} attempt {attempt+1}/{max_retries} failed: {e}", log_callback)
            time.sleep(0.3)
    
    log(f"      [X] Failed to fill {field_key} after {max_retries} attempts", log_callback)

def wait_for_page_ready(driver, log_callback=None, timeout=15):
    """Sayfanın tamamen yüklenmiş olduğundan emin ol"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.NAME, config.FIELDS['firstname']))
        )
        time.sleep(0.8)
        log("   [✓] Sayfa tamamen yüklendi", log_callback)
    except Exception as e:
        log(f"   [!] Sayfa yükleme bekleme hatası: {e}", log_callback)

def solve_recaptcha_2captcha(driver, log_callback=None):
    """
    2captcha servisi aracılığıyla reCAPTCHA v2'yi çözer.
    Site anahtarını sayfadan alır, API'ye gönderir ve token döndürür.
    Token alınca sayfaya enjekte eder.
    """
    api_key = config.TWOCAPTCHA_API_KEY
    if not api_key:
        log("      [!] 2captcha API anahtarı config.py'de boş. Otomatik çözüm devre dışı.", log_callback)
        return False

    try:
        import urllib.request
        import urllib.parse
        import json

        page_url = driver.current_url

        # 1. Sayfadan reCAPTCHA site anahtarını bul
        site_key = None
        # Yöntem 1: data-sitekey attribute
        try:
            el = driver.find_element(By.CSS_SELECTOR, '[data-sitekey]')
            site_key = el.get_attribute('data-sitekey')
        except: pass

        # Yöntem 2: Sayfa kaynağında ara
        if not site_key:
            page_src = driver.page_source
            import re
            m = re.search(r'["\']sitekey["\']\s*:\s*["\']([^"\']+)["\']', page_src)
            if not m:
                m = re.search(r'data-sitekey=["\']([^"\']+)["\']', page_src)
            if m:
                site_key = m.group(1)

        if not site_key:
            log("      [!] reCAPTCHA site anahtarı bulunamadı", log_callback)
            return False

        log(f"      [i] Site anahtarı: {site_key[:20]}...", log_callback)
        log("      [i] 2captcha'ya gönderiliyor... (20-60 sn sürebilir)", log_callback)

        # 2. 2captcha'ya gönder
        submit_url = "https://2captcha.com/in.php"
        params = urllib.parse.urlencode({
            'key': api_key,
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': 1,
        })
        req = urllib.request.Request(
            submit_url,
            data=params.encode('utf-8'),
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        if result.get('status') != 1:
            log(f"      [!] 2captcha gönderim hatası: {result.get('request')}", log_callback)
            return False

        captcha_id = result['request']
        log(f"      [i] CAPTCHA ID: {captcha_id} — çözüm bekleniyor...", log_callback)

        # 3. Çözümü bekle (her 5 saniyede bir sorgula, max 120 sn)
        token = None
        result_url = f"https://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1"
        for attempt in range(24):  # max 120 saniye
            time.sleep(5)
            with urllib.request.urlopen(result_url, timeout=15) as resp:
                res = json.loads(resp.read().decode())
            if res.get('status') == 1:
                token = res['request']
                break
            elif res.get('request') == 'CAPCHA_NOT_READY':
                log(f"      [i] Çözüm bekleniyor... ({(attempt+1)*5}sn)", log_callback)
            else:
                log(f"      [!] 2captcha hata: {res.get('request')}", log_callback)
                return False

        if not token:
            log("      [!] 2captcha: Token alınamadı (timeout)", log_callback)
            return False

        log(f"      [✓] Token alındı! Sayfaya enjekte ediliyor...", log_callback)

        # 4. Token'ı sayfaya enjekte et
        driver.execute_script("""
            // g-recaptcha-response textarea'sına token yaz
            var el = document.getElementById('g-recaptcha-response');
            if (!el) {
                // Tüm textarea'ları dene
                var all = document.querySelectorAll('textarea[name="g-recaptcha-response"]');
                if (all.length > 0) el = all[0];
            }
            if (el) {
                el.style.display = 'block';
                el.value = arguments[0];
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
            // Bazı siteler callback fonksiyonu kullanır
            try {
                var cb = document.querySelector('[data-callback]');
                if (cb) {
                    var fn = cb.getAttribute('data-callback');
                    if (fn && typeof window[fn] === 'function') window[fn](arguments[0]);
                }
            } catch(e) {}
            // ___grecaptcha_cfg callback'i çağır
            try {
                if (typeof ___grecaptcha_cfg !== 'undefined') {
                    var clients = ___grecaptcha_cfg.clients;
                    for (var key in clients) {
                        var client = clients[key];
                        for (var cb_key in client) {
                            var node = client[cb_key];
                            if (node && typeof node.callback === 'function') {
                                try { node.callback(arguments[0]); } catch(e) {}
                            }
                        }
                    }
                }
            } catch(e) {}
        """, token)

        time.sleep(1.0)
        log("      [✓] reCAPTCHA token enjekte edildi!", log_callback)
        return True

    except Exception as e:
        log(f"      [!] 2captcha çözüm hatası: {e}", log_callback)
        return False


def _find_recaptcha_anchor_frame(driver):
    """Sayfa üzerindeki reCAPTCHA anchor (checkbox) iframe'ini bulur."""
    try:
        driver.switch_to.default_content()
        for iframe in driver.find_elements(By.TAG_NAME, 'iframe'):
            src   = (iframe.get_attribute('src') or '').lower()
            title = (iframe.get_attribute('title') or '').lower()
            if ('recaptcha' in src or 'robot' in title or 'anchor' in src) and 'bframe' not in src:
                return iframe
    except:
        pass
    return None


def _find_recaptcha_challenge_frame(driver):
    """reCAPTCHA challenge (resim/ses) iframe'ini bulur."""
    try:
        driver.switch_to.default_content()
        for iframe in driver.find_elements(By.TAG_NAME, 'iframe'):
            src   = (iframe.get_attribute('src') or '').lower()
            title = (iframe.get_attribute('title') or '').lower()
            if 'bframe' in src or 'challenge' in src or 'challenge' in title or 'sınama' in title:
                return iframe
    except:
        pass
    return None


def is_recaptcha_solved(driver):
    """reCAPTCHA'nın çözülüp çözülmediğini (token veya yeşil tik) kontrol eder."""
    try:
        driver.switch_to.default_content()
        token = driver.execute_script(
            "var el = document.getElementById('g-recaptcha-response') || "
            "document.querySelector('textarea[name=\"g-recaptcha-response\"]'); "
            "return (el && el.value && el.value.length > 20) ? el.value : '';"
        )
        if token:
            return True
        anchor = _find_recaptcha_anchor_frame(driver)
        if anchor:
            driver.switch_to.frame(anchor)
            checked = driver.find_elements(
                By.CSS_SELECTOR, '.recaptcha-checkbox-checked, [aria-checked="true"]')
            driver.switch_to.default_content()
            if checked:
                return True
    except:
        try:
            driver.switch_to.default_content()
        except:
            pass
    return False


def wait_for_manual_recaptcha(driver, timeout=45, log_callback=None):
    """
    Kullanıcının reCAPTCHA'yı ekrandan manuel olarak çözmesini bekler.
    Her 1 saniyede bir token veya yeşil tik kontrolü yapar.
    """
    try:
        import bot_munazara
        munazara_stop = getattr(bot_munazara, 'STOP_MUNAZARA_BOT', False)
    except:
        munazara_stop = False

    log(f"      [!] Otomatik reCAPTCHA tamamlanamadı (Google engeli veya ses kısıtlaması).", log_callback)
    log(f"      [i] 👉 Lütfen ekrandaki reCAPTCHA'yı manuel tıklayarak çözün! (En fazla {timeout} sn bekleniyor...)", log_callback)
    start = time.time()
    last_log = 0
    while time.time() - start < timeout:
        if STOP_BOT:
            log("      [i] Bot kullanıcı tarafından durduruldu.", log_callback)
            return False

        try:
            import bot_munazara
            if getattr(bot_munazara, 'STOP_MUNAZARA_BOT', False):
                log("      [i] Bot kullanıcı tarafından durduruldu.", log_callback)
                return False
        except: pass

        if is_recaptcha_solved(driver):
            log("      [✓] reCAPTCHA başarıyla çözüldü (Manuel onay algılandı)!", log_callback)
            return True

        elapsed = int(time.time() - start)
        remaining = timeout - elapsed
        if remaining > 0 and elapsed - last_log >= 10:
            log(f"      [i] reCAPTCHA çözümü bekleniyor... (Kalan süre: {remaining} sn)", log_callback)
            last_log = elapsed

        time.sleep(1.0)

    log("      [!] reCAPTCHA bekleme süresi doldu.", log_callback)
    return False


def is_valid_audio_response(text):
    """reCAPTCHA ses çözümünün geçerli bir yanıt (sayı veya kelime grubu) olduğunu doğrular."""
    if not text:
        return False
    clean_text = text.lower().strip()
    words = clean_text.split()
    if not words:
        return False
    for w in words:
        w_clean = ''.join(ch for ch in w if ch.isalnum())
        if w_clean:
            return True
    return False


def normalize_audio_response(text):
    """reCAPTCHA ses çözümündeki sayı sözcüklerini (İngilizce/Türkçe) rakamlara dönüştürür."""
    if not text:
        return ""
    num_map = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'sıfır': '0', 'sifir': '0', 'bir': '1', 'iki': '2', 'üç': '3', 'uc': '3',
        'dört': '4', 'dort': '4', 'beş': '5', 'bes': '5', 'altı': '6', 'alti': '6',
        'yedi': '7', 'sekiz': '8', 'dokuz': '9'
    }
    words = text.lower().replace('-', ' ').replace(',', ' ').split()
    converted = []
    has_converted_digit = False
    for w in words:
        if w in num_map:
            converted.append(num_map[w])
            has_converted_digit = True
        elif w.isdigit():
            converted.append(w)
            has_converted_digit = True
        else:
            converted.append(w)
    if has_converted_digit:
        return " ".join(converted)
    return text.strip()


def solve_recaptcha_audio(driver, log_callback=None):
    """
    reCAPTCHA v2 Sesli Doğrulama (Audio Challenge) çözücü.
    ─────────────────────────────────────────────────────
    Adımlar:
      1. Anchor iframe → checkbox tıkla
      2. Challenge iframe görünürse → Ses simgesine tıkla
      3. Tarayıcı içi JS Fetch veya urllib ile ses dosyasını indir
      4. pydub ile ses dosyasını WAV'a dönüştür
      5. SpeechRecognition ile metin al (en-US / tr-TR fallback)
      6. Yanıtı forma yaz → "Doğrula" butonuna tıkla
    """
    try:
        import urllib.request
        import tempfile
        import os as _os
        import base64

        # ── Kütüphane varlık kontrolü ──────────────────────────────────────
        try:
            import speech_recognition as sr
        except ImportError:
            log("      [!] 'SpeechRecognition' yüklü değil. Kurmak için: pip install SpeechRecognition", log_callback)
            return False

        try:
            from pydub import AudioSegment
        except ImportError:
            log("      [!] 'pydub' yüklü değil. Kurmak için: pip install pydub", log_callback)
            return False

        # ── 1. Anchor iframe → checkbox tıkla ─────────────────────────────
        driver.switch_to.default_content()
        anchor = _find_recaptcha_anchor_frame(driver)
        if not anchor:
            log("      [!] reCAPTCHA anchor iframe bulunamadı", log_callback)
            return False

        # Zaten çözülmüş mü?
        try:
            driver.switch_to.frame(anchor)
            already_checked = driver.find_elements(
                By.CSS_SELECTOR, '.recaptcha-checkbox-checked, [aria-checked="true"]')
            if already_checked:
                log("      [✓] reCAPTCHA zaten doğrulanmış (tik yeşil)!", log_callback)
                driver.switch_to.default_content()
                return True
        except:
            driver.switch_to.default_content()

        driver.switch_to.default_content()
        anchor = _find_recaptcha_anchor_frame(driver)
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", anchor)
        time.sleep(0.5)
        driver.switch_to.frame(anchor)

        wait = WebDriverWait(driver, 8)
        checkbox = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             '.recaptcha-checkbox-border, #recaptcha-anchor, .rc-anchor-checkbox')
        ))
        time.sleep(random.uniform(0.3, 0.6))
        try:
            checkbox.click()
        except Exception:
            driver.execute_script("arguments[0].click();", checkbox)
        log("      [✓] reCAPTCHA checkbox tıklandı", log_callback)
        time.sleep(random.uniform(1.5, 2.5))

        # Checkbox başarılıysa (yeşil tik) direkt dön
        try:
            checked = driver.find_elements(
                By.CSS_SELECTOR, '.recaptcha-checkbox-checked, [aria-checked="true"]')
            if checked:
                log("      [✓] reCAPTCHA tek tıkla doğrulandı (tik yeşil)!", log_callback)
                driver.switch_to.default_content()
                return True
        except:
            pass
        driver.switch_to.default_content()

        # ── 2. Challenge iframe'ini bekle ─────────────────────────────────
        log("      [i] Challenge ekranı bekleniyor...", log_callback)
        challenge_frame = None
        for _ in range(10):  # max 10 × 0.5 sn = 5.0 sn
            challenge_frame = _find_recaptcha_challenge_frame(driver)
            if challenge_frame:
                break
            time.sleep(0.5)

        if not challenge_frame:
            if is_recaptcha_solved(driver):
                log("      [✓] reCAPTCHA doğrulandı!", log_callback)
                return True
            log("      [i] Challenge açılmadı — checkbox yeterli olabilir.", log_callback)
            return True

        driver.switch_to.frame(challenge_frame)
        log("      [i] Challenge iframe'i içinde, ses butonu aranıyor...", log_callback)

        # ── 3. Ses butonunu veya doscaptcha uyarısını bekle ────────────────
        audio_btn = None
        doscaptcha_blocked = False
        start_wait = time.time()
        while time.time() - start_wait < 5.0:
            if STOP_BOT:
                driver.switch_to.default_content()
                return False

            try:
                doscaptcha = driver.find_elements(By.CSS_SELECTOR, '.rc-doscaptcha-header, .rc-doscaptcha-body, .rc-doscaptcha-footer')
                if doscaptcha and any(d.is_displayed() for d in doscaptcha):
                    doscaptcha_blocked = True
                    break
                btext = driver.find_element(By.TAG_NAME, 'body').text.lower()
                if 'automated queries' in btext or 'otomatik sorgular' in btext:
                    doscaptcha_blocked = True
                    break
            except:
                pass

            for sel in [
                '#recaptcha-audio-button',
                'button.rc-button-audio',
                'button[id*="audio"]',
                'button[title*="ses"]',
                'button[title*="audio"]',
            ]:
                try:
                    btn = driver.find_element(By.CSS_SELECTOR, sel)
                    if btn.is_displayed():
                        audio_btn = btn
                        break
                except:
                    pass

            if audio_btn:
                break
            time.sleep(0.4)

        if doscaptcha_blocked:
            log("      [!] Google bu IP/oturum için sesli doğrulamayı kısıtladı ('Automated queries' engeli).", log_callback)
            log("      [i] İPUCU: Açılan tarayıcıda bir kez Google/Gmail hesabınıza giriş yaparak bu engeli aşabilirsiniz.", log_callback)
            driver.switch_to.default_content()
            return False

        if not audio_btn:
            log("      [!] Ses butonu bulunamadı — resim challenge veya kısıtlama olabilir.", log_callback)
            driver.switch_to.default_content()
            return False

        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", audio_btn)
        time.sleep(0.4)
        try:
            audio_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", audio_btn)
        log("      [✓] Sesli doğrulama butonuna tıklandı", log_callback)
        time.sleep(1.5)

        # Butona tıklandıktan hemen sonra Google engeli ("Automated queries") geldi mi kontrol et
        try:
            doscaptcha = driver.find_elements(By.CSS_SELECTOR, '.rc-doscaptcha-header, .rc-doscaptcha-body, .rc-doscaptcha-footer')
            if doscaptcha and any(d.is_displayed() for d in doscaptcha):
                log("      [!] Google sesli doğrulamayı kısıtladı ('Automated queries' engeli tespit edildi).", log_callback)
                log("      [i] İPUCU: Açılan tarayıcıda bir Gmail/Google hesabına giriş yaparsanız bu kısıtlama kalkar.", log_callback)
                driver.switch_to.default_content()
                return False
            btext = driver.find_element(By.TAG_NAME, 'body').text.lower()
            if 'automated queries' in btext or 'otomatik sorgular' in btext:
                log("      [!] Google sesli doğrulamayı kısıtladı ('Automated queries' engeli tespit edildi).", log_callback)
                driver.switch_to.default_content()
                return False
        except:
            pass

        # ── 4. Ses dosyası URL'ini al ve döngü ────────────────────────────
        text = None
        for attempt in range(1, 4):
            if STOP_BOT:
                driver.switch_to.default_content()
                return False

            log(f"      [i] Sesli doğrulama çözülüyor... Deneme {attempt}/3", log_callback)
            audio_src = None

            # Ses URL'inin DOM'a gelmesini bekle (max 5 sn)
            s_start = time.time()
            while time.time() - s_start < 5.0:
                try:
                    doscaptcha = driver.find_elements(By.CSS_SELECTOR, '.rc-doscaptcha-header, .rc-doscaptcha-body')
                    if doscaptcha and any(d.is_displayed() for d in doscaptcha):
                        log("      [!] Google sesli doğrulamayı kısıtladı ('Automated queries').", log_callback)
                        driver.switch_to.default_content()
                        return False
                except:
                    pass

                for sel in [
                    'a.rc-audiochallenge-download-link',
                    'a.rc-audiochallenge-tdownload-link',
                    '.rc-audiochallenge-download-link',
                    '.rc-audiochallenge-tdownload-link',
                    'a[href*="/payload"]',
                    'a[href*="payload"]',
                    'audio#audio-source',
                    'audio source',
                    'a[href*="audio"]',
                ]:
                    try:
                        el = driver.find_element(By.CSS_SELECTOR, sel)
                        val = el.get_attribute('src') or el.get_attribute('href')
                        if val and ('payload' in val or 'audio' in val or val.startswith('http')):
                            audio_src = val
                            break
                    except:
                        pass

                if audio_src:
                    break

                try:
                    audio_el = driver.find_element(By.TAG_NAME, 'audio')
                    src = audio_el.get_attribute('src')
                    if src and src.startswith('http'):
                        audio_src = src
                        break
                except:
                    pass

                time.sleep(0.5)

            if not audio_src:
                log("      [!] Ses dosyası URL'i bulunamadı.", log_callback)
                if attempt < 3:
                    try:
                        reload_btn = None
                        for r_sel in ['#recaptcha-reload-button', 'button.rc-button-reload', 'button[id*="reload"]']:
                            try:
                                el = driver.find_element(By.CSS_SELECTOR, r_sel)
                                if el.is_displayed():
                                    reload_btn = el
                                    break
                            except: pass
                        if reload_btn:
                            try: reload_btn.click()
                            except: driver.execute_script('arguments[0].click();', reload_btn)
                            log("      [i] Yeni reCAPTCHA sesi talep ediliyor...", log_callback)
                            time.sleep(2.0)
                            continue
                    except: pass
                driver.switch_to.default_content()
                return False

            log(f"      [i] Ses dosyası indiriliyor (Deneme {attempt})...", log_callback)

            # ── 5. Ses dosyasını indir (Önce Tarayıcı JS Fetch, sonra urllib) ──
            tmp_dir = tempfile.gettempdir()
            ts = int(time.time() * 1000)
            raw_path = _os.path.join(tmp_dir, f'captcha_audio_{ts}.raw')
            wav_path = _os.path.join(tmp_dir, f'captcha_audio_{ts}.wav')

            download_ok = False
            # Yöntem A: Tarayıcı içi Fetch (Tarayıcının kendi oturumuyla indirme - en güvenli)
            try:
                driver.set_script_timeout(10)
                b64_data = driver.execute_async_script("""
                    var done = arguments[arguments.length - 1];
                    var url = arguments[0];
                    fetch(url)
                        .then(function(r) { return r.blob(); })
                        .then(function(b) {
                            var reader = new FileReader();
                            reader.onloadend = function() { done(reader.result); };
                            reader.onerror = function() { done(null); };
                            reader.readAsDataURL(b);
                        })
                        .catch(function(err) { done(null); });
                """, audio_src)

                if b64_data and ',' in b64_data:
                    b64_str = b64_data.split(',', 1)[1]
                    raw_bytes = base64.b64decode(b64_str)
                    if len(raw_bytes) > 500:
                        with open(raw_path, 'wb') as f:
                            f.write(raw_bytes)
                        download_ok = True
            except Exception as e:
                pass

            # Yöntem B: urllib fallback
            if not download_ok:
                try:
                    headers = {
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/124.0.0.0 Safari/537.36'
                        )
                    }
                    req = urllib.request.Request(audio_src, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        with open(raw_path, 'wb') as f:
                            f.write(resp.read())
                    download_ok = True
                except Exception as e:
                    log(f"      [!] Ses dosyası indirme hatası: {e}", log_callback)

            if not download_ok:
                if attempt < 3:
                    try:
                        reload_btn = None
                        for r_sel in ['#recaptcha-reload-button', 'button.rc-button-reload', 'button[id*="reload"]']:
                            try:
                                el = driver.find_element(By.CSS_SELECTOR, r_sel)
                                if el.is_displayed():
                                    reload_btn = el
                                    break
                            except: pass
                        if reload_btn:
                            try: reload_btn.click()
                            except: driver.execute_script('arguments[0].click();', reload_btn)
                            log("      [i] Yeni reCAPTCHA sesi talep ediliyor...", log_callback)
                            time.sleep(2.0)
                            continue
                    except: pass
                driver.switch_to.default_content()
                return False

            # Ses dosyasını WAV formatına dönüştür (pydub + FFmpeg)
            convert_ok = False
            try:
                sound = AudioSegment.from_file(raw_path)
                sound.export(wav_path, format='wav')
                convert_ok = True
            except Exception as e:
                log(f"      [!] Ses dönüşüm hatası (FFmpeg): {e}", log_callback)

            if not convert_ok:
                try: _os.remove(raw_path)
                except: pass
                if attempt < 3:
                    try:
                        reload_btn = None
                        for r_sel in ['#recaptcha-reload-button', 'button.rc-button-reload', 'button[id*="reload"]']:
                            try:
                                el = driver.find_element(By.CSS_SELECTOR, r_sel)
                                if el.is_displayed():
                                    reload_btn = el
                                    break
                            except: pass
                        if reload_btn:
                            try: reload_btn.click()
                            except: driver.execute_script('arguments[0].click();', reload_btn)
                            log("      [i] Yeni reCAPTCHA sesi talep ediliyor...", log_callback)
                            time.sleep(2.0)
                            continue
                    except: pass
                driver.switch_to.default_content()
                return False

            # ── 6. SpeechRecognition (Google STT) ile metne çevir ─────────────
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            stt_ok = False
            raw_text = None

            try:
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)

                # Önce en-US ile dene
                try:
                    raw_text = recognizer.recognize_google(audio_data, language='en-US')
                    stt_ok = True
                except sr.UnknownValueError:
                    # Türkçe olarak tekrar dene
                    try:
                        raw_text = recognizer.recognize_google(audio_data, language='tr-TR')
                        stt_ok = True
                    except:
                        pass
                except Exception as e:
                    log(f"      [!] STT hatası: {e}", log_callback)

                if stt_ok and raw_text:
                    normalized_text = normalize_audio_response(raw_text)
                    log(f"      [✓] Ses Tanıma Başarılı: '{normalized_text}'", log_callback)
                    text = normalized_text
                else:
                    log(f"      [!] Ses tanınamadı (Deneme {attempt}/3)", log_callback)

            except Exception as e:
                log(f"      [!] STT dosya okuma hatası: {e}", log_callback)
            finally:
                for p in [raw_path, wav_path]:
                    try:
                        if _os.path.exists(p): _os.remove(p)
                    except: pass

            if stt_ok and text and is_valid_audio_response(text):
                break
            else:
                stt_ok = False
                if attempt < 3:
                    try:
                        reload_btn = None
                        for r_sel in ['#recaptcha-reload-button', 'button.rc-button-reload', 'button[id*="reload"]']:
                            try:
                                el = driver.find_element(By.CSS_SELECTOR, r_sel)
                                if el.is_displayed():
                                    reload_btn = el
                                    break
                            except: pass
                        if reload_btn:
                            try: reload_btn.click()
                            except: driver.execute_script('arguments[0].click();', reload_btn)
                            log("      [i] Yeni reCAPTCHA sesi talep ediliyor...", log_callback)
                            time.sleep(2.0)
                            continue
                    except: pass
                else:
                    driver.switch_to.default_content()
                    return False

        # ── 7. Yanıtı forma yaz ve doğrula ───────────────────────────────
        try:
            response_input = driver.find_element(
                By.CSS_SELECTOR,
                '#audio-response, input[id*="audio"], input.rc-audiochallenge-response'
            )
            try:
                response_input.click()
            except Exception:
                driver.execute_script("arguments[0].click();", response_input)
            response_input.clear()
            time.sleep(0.1)
            response_input.send_keys(text.lower())
            log("      [✓] Sesli doğrulama yanıtı yazıldı", log_callback)
            time.sleep(0.5)

            # Doğrula butonuna tıkla
            verify_clicked = False
            try:
                verify_btn = driver.find_element(
                    By.CSS_SELECTOR,
                    '#recaptcha-verify-button, button[id*="verify"], button.rc-button-default'
                )
                try:
                    verify_btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", verify_btn)
                log("      [✓] 'Doğrula' butonuna tıklandı", log_callback)
                verify_clicked = True
            except:
                pass

            if not verify_clicked:
                response_input.send_keys(Keys.ENTER)
                log("      [✓] Yanıt alanında Enter tuşuna basıldı", log_callback)

        except Exception as e:
            log(f"      [!] Yanıt alanı bulunamadı veya değer yazılamadı: {e}", log_callback)
            driver.switch_to.default_content()
            return False

        # ── 8. g-recaptcha-response alanını kontrol et ───────────────────
        log("      [i] reCAPTCHA doğrulama sonucu bekleniyor...", log_callback)
        solved = False
        start_time = time.time()

        while time.time() - start_time < 6.0:
            try:
                driver.switch_to.default_content()
                response_val = driver.execute_script(
                    "var el = document.getElementById('g-recaptcha-response'); "
                    "return el ? el.value : '';"
                )
                if response_val and len(response_val.strip()) > 30:
                    log("      [✓] reCAPTCHA başarıyla çözüldü! Token algılandı.", log_callback)
                    solved = True
                    break
            except:
                pass

            try:
                driver.switch_to.default_content()
                anchor = _find_recaptcha_anchor_frame(driver)
                if anchor:
                    driver.switch_to.frame(anchor)
                    checked_el = driver.find_elements(By.CSS_SELECTOR, '.recaptcha-checkbox-checked, [aria-checked="true"]')
                    if checked_el:
                        log("      [✓] reCAPTCHA başarıyla çözüldü! (Yeşil tik algılandı)", log_callback)
                        solved = True
                        break
            except:
                pass

            time.sleep(0.5)

        try:
            driver.switch_to.default_content()
        except:
            pass

        if solved:
            return True
        else:
            log("      [!] Sesli doğrulama tamamlanamadı (Yanıt hatalı veya ek sınama istendi).", log_callback)
            return False

    except Exception as e:
        log(f"      [!] Audio CAPTCHA genel hata: {e}", log_callback)
        try:
            driver.switch_to.default_content()
        except: pass
        return False


def click_recaptcha(driver, log_callback=None, use_audio_captcha=True, use_token_captcha=False):
    """
    reCAPTCHA'yı çözer (öncelik sırası):
    1. Zaten çözülmüş mü kontrolü
    2. Ücretsiz Sesli Doğrulama (Audio Challenge) - ÖNCELİKLİ (Eğer etkinse)
    3. 2captcha token enjeksiyonu (config.py'de anahtar varsa otomatik devreye girer)
    4. CapSolver token enjeksiyonu (config.py'de anahtar varsa)
    5. Salt checkbox tıklama (Challenge ekranı açık değilse ve henüz tıklanmadıysa)
    6. Manuel çözüm bekleme (Challenge açık kalmışsa)
    """
    # 0. Zaten çözülmüş mü?
    if is_recaptcha_solved(driver):
        log("      [✓] reCAPTCHA zaten çözülmüş durumda.", log_callback)
        return True

    # Sayfadaki engelleyici backdrop overlay varsa pointer-events kapat
    try:
        driver.switch_to.default_content()
        driver.execute_script("""
            document.querySelectorAll('div[style*="opacity: 0.05"], div[style*="2000000000"]').forEach(function(d) {
                if (d.style.position === 'fixed' && d.tagName === 'DIV' && !d.querySelector('iframe')) {
                    d.style.pointerEvents = 'none';
                }
            });
        """)
    except:
        pass

    # Yöntem 1: Sesli doğrulama (Audio Challenge)
    if use_audio_captcha:
        log("      [i] Öncelikli yöntem: Ücretsiz Sesli Doğrulama (Audio Challenge) deneniyor...", log_callback)
        try:
            if solve_recaptcha_audio(driver, log_callback):
                return True
        except Exception as e:
            log(f"      [!] Sesli doğrulama çalıştırılırken hata: {e}", log_callback)

    # Sesli doğrulama sonrası çözüldü mü?
    if is_recaptcha_solved(driver):
        return True

    # Yöntem 2: 2captcha token enjeksiyonu (Anahtar tanımlıysa otomatik devreye girer)
    two_key = getattr(config, 'TWOCAPTCHA_API_KEY', '').strip()
    if (use_token_captcha or two_key) and two_key:
        log("      [i] 2captcha API anahtarı devrede, otomatik token çözümü deneniyor...", log_callback)
        result = solve_recaptcha_2captcha(driver, log_callback)
        if result:
            return True

    # Yöntem 3: CapSolver token enjeksiyonu
    capsolver_key = getattr(config, 'CAPSOLVER_API_KEY', '').strip() if hasattr(config, 'CAPSOLVER_API_KEY') else ''
    if (use_token_captcha or capsolver_key) and capsolver_key:
        log("      [i] CapSolver API anahtarı devrede, otomatik token çözümü deneniyor...", log_callback)
        result = solve_recaptcha_capsolver(driver, log_callback)
        if result:
            return True

    # Yöntem 4: Salt checkbox tıklama (Challenge ekranı açık değilse ve henüz tıklanmadıysa)
    challenge_frame = _find_recaptcha_challenge_frame(driver)
    if not challenge_frame:
        log("      [i] Doğrudan checkbox tıklanıyor...", log_callback)
        try:
            driver.switch_to.default_content()
            anchor = _find_recaptcha_anchor_frame(driver)
            if not anchor:
                log("      [!] reCAPTCHA iframe bulunamadı", log_callback)
                return False

            driver.execute_script(
                "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", anchor)
            time.sleep(0.5)
            driver.switch_to.frame(anchor)

            wait = WebDriverWait(driver, 8)
            checkbox = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.recaptcha-checkbox-border, #recaptcha-anchor, .rc-anchor-checkbox')
            ))
            time.sleep(random.uniform(0.3, 0.7))
            try:
                checkbox.click()
            except Exception:
                driver.execute_script("arguments[0].click();", checkbox)
            log("      [✓] reCAPTCHA checkbox tıklandı", log_callback)
            time.sleep(random.uniform(1.5, 2.5))
            driver.switch_to.default_content()

            if is_recaptcha_solved(driver):
                log("      [✓] reCAPTCHA tek tıkla doğrulandı!", log_callback)
                return True

        except Exception as e:
            log(f"      [!] reCAPTCHA checkbox hatası: {e}", log_callback)
            try:
                driver.switch_to.default_content()
            except: pass

    # Yöntem 5: reCAPTCHA çözülemediyse ve challenge ekranda açıksa manuel bekle
    if not is_recaptcha_solved(driver):
        return wait_for_manual_recaptcha(driver, timeout=45, log_callback=log_callback)

    return True

def click_submit(driver, log_callback=None):
    """
    Submit butonunu bulup tıklar.
    Disabled olsa bile JS ile tıklar; buton yoksa formu JS ile submit eder.
    """
    try:
        submit_btn = None

        # Görünür submit butonu ara (disabled olsa da)
        for xpath in [
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'GÖNDER')]",
            "//button[contains(text(), 'Gönder')]",
            "//button[contains(text(), 'GONDER')]",
            "//button[contains(text(), 'Gonder')]",
            "//button[contains(@class,'submit')]",
            "//input[@value='GÖNDER' or @value='Gönder' or @value='Submit']",
        ]:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                if btn.is_displayed():   # is_enabled() kontrolü KALDIRILDI
                    submit_btn = btn
                    break
            except:
                pass

        if submit_btn:
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});",
                submit_btn)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", submit_btn)
            log("      [✓] GÖNDER butonuna tıklandı!", log_callback)
            return True

        # Buton bulunamadıysa: form'u doğrudan JS ile gönder
        log("      [i] GÖNDER butonu bulunamadı — form JS ile submit ediliyor...", log_callback)
        submitted = driver.execute_script("""
            var forms = document.querySelectorAll('form');
            if (forms.length > 0) {
                forms[forms.length - 1].submit();
                return true;
            }
            return false;
        """)
        if submitted:
            log("      [✓] Form JS ile gönderildi!", log_callback)
            return True
        else:
            log("      [!] Form bulunamadı — manuel gönder gerekiyor.", log_callback)
            return False

    except Exception as e:
        log(f"      [!] GÖNDER hatası: {e}", log_callback)
        return False

def verify_and_fix_fields(driver, student, log_callback=None):
    """Doldurulmuş alanları kontrol et; boş kalan varsa veya hatalıysa yeniden doldur."""
    text_fields = {
        'firstname'  : student.get('form_firstname', ''),
        'lastname'   : student.get('form_lastname', ''),
        'tc_no'      : student.get('form_tc_no', ''),
        'parent_name': student.get('form_parent_name', ''),
        'phone'      : student.get('form_phone', ''),
        'birthdate'  : student.get('form_birthdate', ''),
    }

    any_fixed = False
    
    # 1. Text alanlarını doğrula
    for field_key, expected_value in text_fields.items():
        if not expected_value:
            continue
        selector = config.FIELDS.get(field_key)
        if not selector:
            continue
        try:
            element = driver.find_element(By.NAME, selector)
            current_val = element.get_attribute('value')
            if not current_val or len(current_val.strip()) == 0:
                log(f"   [!!] {field_key} BOŞ KALDI - tekrar dolduruluyor!", log_callback)
                fill_field(driver, field_key, expected_value, By.NAME, log_callback=log_callback)
                any_fixed = True
        except Exception as e:
            log(f"   [!] {field_key} doğrulama hatası: {e}", log_callback)

    # 2. Select alanlarını doğrula
    select_fields = {
        'gender'      : (config.FIELDS['gender'], student.get('form_gender_val', '')),
        'nationality' : (config.FIELDS['nationality'], SABIT['nationality_val']),
        'hadis'       : (config.FIELDS['hadis_competition'], SABIT['hadis_val'])
    }
    
    for field_key, (selector, expected_value) in select_fields.items():
        if not expected_value:
            continue
        try:
            element = driver.find_element(By.NAME, selector)
            select = Select(element)
            current_val = select.first_selected_option.get_attribute('value')
            if not current_val or current_val != expected_value:
                log(f"   [!!] Select {field_key} BOŞ/YANLIŞ KALDI ({current_val}) - tekrar dolduruluyor!", log_callback)
                fill_select_by_value(driver, selector, expected_value, log_callback=log_callback)
                any_fixed = True
        except Exception as e:
            pass

    # 3. Lookup alanlarını doğrula
    lookup_fields = {
        'school_city'            : (config.FIELDS['school_city'], SABIT['okul_ili']),
        'school_district'        : (config.FIELDS['school_district'], SABIT['okul_ilcesi']),
        'school_name'            : (config.FIELDS['school_name'], student.get('form_school_name', random.choice(YENISEHIR_ORTAOKULLAR))),
        'summer_school_city'     : (config.FIELDS['summer_school_city'], SABIT['yaz_okulu_ili']),
        'summer_school_district' : (config.FIELDS['summer_school_district'], SABIT['yaz_okulu_ilcesi'])
    }
    
    for field_key, (selector, expected_value) in lookup_fields.items():
        try:
            element = driver.find_element(By.NAME, selector)
            current_val = element.get_attribute('value')
            if not current_val or len(current_val.strip()) == 0:
                log(f"   [!!] Lookup {field_key} ({selector}) BOŞ KALDI - tekrar dolduruluyor!", log_callback)
                fill_lookup(driver, selector, expected_value, log_callback=log_callback)
                any_fixed = True
        except Exception as e:
            log(f"   [!] Lookup {field_key} doğrulama hatası: {e}", log_callback)

    if any_fixed:
        log("   [i] Eksik/hatalı alanlar tekrar dolduruldu", log_callback)
    else:
        log("   [✓] Tüm alanlar dolu ve doğrulanmış durumda", log_callback)
        
    return any_fixed

def fill_form(driver, student, log_callback=None, use_audio_captcha=True, use_token_captcha=False):
    """
    ─── ALAN EŞLEMESİ ─────────────────────────────────────────────────────────
    Sitedeki Alan          ← Excel Sütunu / Sabit Değer
    ─────────────────────────────────────────────────────
    TC Kimlik / Pasaport   ← tc_no sütunu (tc kimlik no)
    Adı   (firstname)      ← first_name sütunu (adı)
    Soyadı (lastname)      ← last_name sütunu (soyadı)
    Cinsiyet               ← excel sütunundan / tahmin
    Uyruk                  ← SABİT: TC Vatandaşı
    Okul İli               ← SABİT: Diyarbakır
    Okul İlçesi            ← SABİT: Yenişehir
    Okul                   ← SABİT: Ali Emiri Ortaokulu
    Yaz Okulu İli          ← SABİT: Diyarbakır
    Yaz Okulu İlçesi       ← SABİT: Yenişehir
    Hadis Yarışması        ← SABİT: Hayır
    Veli Ad Soyad          ← Rastgele ad + soyadı sütunundan soyad
    Telefon                ← Rastgele üretilir
    KVKK                   ← Otomatik işaretlenir
    ──────────────────────────────────────────────────────────────────────────
    """
    try:
        wait_for_page_ready(driver, log_callback)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.2)

        # ── Değerleri önceden hesapla ────────────────────────────────────────
        # Sitedeki "TC Kimlik" kutusuna → verideki tc_no sütunu
        form_tc_no     = student.get('tc_no', '')              # tc_no → TC Kimlik
        # Sitedeki "Adı" kutusuna → verideki first_name (adı) sütunu
        form_firstname = student.get('first_name', '')         # adı → Adı
        # Sitedeki "Soyadı" kutusuna → verideki last_name (soyadı) sütunu
        form_lastname  = student.get('last_name', '')          # soyadı → Soyadı
        # Veli: rastgele Türkçe ad + soyadı
        form_parent    = random_parent_name(form_lastname if form_lastname else '')
        # Telefon: rastgele
        form_phone     = random_phone()

        # Verify/fix için student dict'e ekle
        student['form_firstname']   = form_firstname
        student['form_lastname']    = form_lastname
        student['form_tc_no']       = form_tc_no
        student['form_parent_name'] = form_parent
        student['form_phone']       = form_phone

        log(f"   [i] TC={form_tc_no} | Adı={form_firstname} | Soyadı={form_lastname}", log_callback)
        log(f"   [i] Veli={form_parent} | Tel={form_phone}", log_callback)

        # 1. Adı → adı sütunu
        fill_field(driver, 'firstname', form_firstname, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 2. Soyadı → soyadı sütunu
        fill_field(driver, 'lastname', form_lastname, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 3. Cinsiyet — form_firstname (gerçek adı) üzerinden tahmin
        gender_raw = str(student.get('gender', '')).strip().lower()
        gender_val = ''
        if gender_raw in ['1', '2']:
            gender_val = gender_raw
        elif 'erkek' in gender_raw or 'male' in gender_raw or gender_raw in ['e', 'm']:
            gender_val = '1'
        elif 'kadın' in gender_raw or 'kadin' in gender_raw or 'kız' in gender_raw or 'female' in gender_raw or gender_raw in ['k', 'f']:
            gender_val = '2'

        if not gender_val:
            # Gerçek adı üzerinden cinsiyet tahmini yap
            gender_text = gender_guesser.guess_gender(form_firstname) if form_firstname else ''
            if gender_text == "Erkek":
                gender_val = '1'
            elif gender_text == "Kadın":
                gender_val = '2'
            else:
                # Hâlâ bilinmiyorsa erkek varsayılan ('1')
                gender_val = '1'
            
            gender_label = 'Erkek' if gender_val == '1' else 'Kadın'
            log(f"   [i] Cinsiyet tahmini: '{form_firstname}' → {gender_label}", log_callback)

        fill_select_by_value(driver, config.FIELDS['gender'], gender_val, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))


        # 4. Uyruk → SABİT: TC Vatandaşı (1)
        fill_select_by_value(driver, config.FIELDS['nationality'], SABIT['nationality_val'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 5. TC Kimlik No → ad sütunu
        fill_field(driver, 'tc_no', form_tc_no, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 6. Doğum Tarihi → veriden al (birth_date sütunu); boşsa sınıfa göre rastgele üret
        sinif_val = student.get('sinif', '')
        birth_date_from_data = student.get('birth_date', '').strip()
        if birth_date_from_data:
            birth_date_formatted = format_date_for_input(birth_date_from_data)
            log(f"   [i] Doğum tarihi (veriden): {birth_date_formatted}", log_callback)
        else:
            birth_date_formatted = random_birthdate(sinif_val)
            log(f"   [i] Doğum tarihi (rastgele, {sinif_val}. Sınıf): {birth_date_formatted}", log_callback)
        
        # Verify/fix doğrulaması için ekle
        student['form_gender_val'] = gender_val
        student['form_birthdate'] = birth_date_formatted
        
        fill_field(driver, 'birthdate', birth_date_formatted, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 7. Okul İli → SABİT: Diyarbakır
        fill_lookup(driver, config.FIELDS['school_city'], SABIT['okul_ili'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 8. Okul İlçesi → SABİT: Yenişehir
        fill_lookup(driver, config.FIELDS['school_district'], SABIT['okul_ilcesi'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 9. Okul → Sitedeki Yenişehir okulları listesinden rastgele biri
        secilen_okul = random.choice(YENISEHIR_ORTAOKULLAR)
        student['form_school_name'] = secilen_okul
        log(f"   [i] Seçilen okul: {secilen_okul}", log_callback)
        fill_lookup(driver, config.FIELDS['school_name'], secilen_okul, log_callback=log_callback)
        time.sleep(random.uniform(0.2, 0.4))

        # 10. Yaz Okulu İli → SABİT: Diyarbakır
        fill_lookup(driver, config.FIELDS['summer_school_city'], SABIT['yaz_okulu_ili'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 11. Yaz Okulu İlçesi → SABİT: Yenişehir
        fill_lookup(driver, config.FIELDS['summer_school_district'], SABIT['yaz_okulu_ilcesi'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 12. Hadis Yarışması → SABİT: Hayır (2)
        fill_select_by_value(driver, config.FIELDS['hadis_competition'], SABIT['hadis_val'], log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 13. Veli Ad Soyad → rastgele ad + okul_no
        fill_field(driver, 'parent_name', form_parent, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 14. Telefon → rastgele
        fill_field(driver, 'phone', form_phone, By.NAME, log_callback=log_callback)
        time.sleep(random.uniform(0.1, 0.2))

        # 15. Son kontrol
        log("\n   [i] Son kontrol: Tüm alanlar doğrulanıyor...", log_callback)
        verify_and_fix_fields(driver, student, log_callback)
        time.sleep(0.2)

        # 16. KVKK → Otomatik işaretle
        try:
            checkbox = driver.find_element(By.ID, config.FIELDS['kvkk'])
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
            time.sleep(0.2)
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)
            log("      [✓] KVKK işaretlendi", log_callback)
        except Exception as e:
            try:
                kvkk_label = driver.find_element(By.XPATH, "//label[@for='kvkkCheckbox']")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", kvkk_label)
                time.sleep(0.15)
                kvkk_label.click()
                log("      [✓] KVKK (label) işaretlendi", log_callback)
            except Exception as e2:
                log(f"      [!] KVKK işaretlenemedi: {e2}", log_callback)

        # 17. reCAPTCHA → 2captcha / Sesli / Checkbox
        log("   [i] reCAPTCHA kontrol ediliyor...", log_callback)
        time.sleep(0.5)
        captcha_ok = click_recaptcha(driver, log_callback=log_callback, use_audio_captcha=use_audio_captcha, use_token_captcha=use_token_captcha)

        # 18. reCAPTCHA sonrası bekleme + GÖNDER
        # 2captcha token enjekte edildikten sonra sayfanın callback'i işlemesi
        # için yeterli süre bekliyoruz, ardından GÖNDER'e basıyoruz.
        wait_secs = 3.0 if captcha_ok else 1.5
        log(f"   [i] reCAPTCHA sonrası {wait_secs:.0f}sn bekleniyor...", log_callback)
        time.sleep(wait_secs)

        submitted = click_submit(driver, log_callback=log_callback)
        if not submitted:
            # Son çare: 1 sn daha bekle ve tekrar dene
            time.sleep(1.0)
            click_submit(driver, log_callback=log_callback)

    except Exception as e:
        log(f"Error in main form fill: {e}", log_callback)

def run_bot(data_file_path, log_callback=None, use_audio_captcha=None, use_token_captcha=False):
    global STOP_BOT
    STOP_BOT = False
    
    if use_audio_captcha is None:
        use_audio_captcha = getattr(config, 'USE_AUDIO_CAPTCHA', True)
    
    log("\n" + "="*40, log_callback)
    log("      YAZ OKULU BOT VERSION 3.0", log_callback)
    log("="*40 + "\n", log_callback)
    
    log(f"Reading {data_file_path}...", log_callback)
    students = excel_handler.load_data(data_file_path)
    
    if not students:
        log(f"ERROR: Could not read '{data_file_path}'.", log_callback)
        return
 
    log(f"Loaded {len(students)} students from file.", log_callback)
    
    # Load completed tracker
    completed_tckns = set()
    if os.path.exists('completed.txt'):
         with open('completed.txt', 'r') as f:
             completed_tckns = {line.strip() for line in f if line.strip()}
    log(f"Loaded {len(completed_tckns)} previously completed records.", log_callback)

    driver = init_driver(log_callback)
    if not driver: return

    try:
        total_students = len(students)
        
        for i, student in enumerate(students, 1):
            if STOP_BOT:
                log("Bot stopped by user.", log_callback)
                break
                
            # Mapping: tc_no=TC Kimlik, first_name=Adı, last_name=Soyadı
            tc_no_from_data   = student.get('tc_no', '').strip()       # tc_no sütunu = TC Kimlik
            ad_from_data      = student.get('first_name', '').strip()  # adı sütunu
            soyad_from_data   = student.get('last_name', '').strip()   # soyadı sütunu
            display_name = f"{ad_from_data} {soyad_from_data}"

            # Skip header or completely invalid rows
            if not tc_no_from_data or not tc_no_from_data.isdigit() or len(tc_no_from_data) != 11:
                log(f"Skipping {i}/{total_students}: Geçersiz TC Kimlik '{tc_no_from_data}' (Boş veya Başlık satırı)", log_callback)
                continue

            # Takip kimliği olarak TC No kullan
            tracking_id = tc_no_from_data
            if tracking_id in completed_tckns:
                log(f"Skipping {i}/{total_students}: {display_name} (Zaten tamamlandı)", log_callback)
                continue

            log(f"\nProcessing {i}/{total_students}: {display_name} [TC={tc_no_from_data}]", log_callback)
            driver.get(config.URL)
            time.sleep(1.5)
            
            fill_form(driver, student, log_callback, use_audio_captcha=use_audio_captcha, use_token_captcha=use_token_captcha)
            
            log("\n>> Form filled. CAPTCHA focused.", log_callback)
            log(">> ACTION REQUIRED: Type CAPTCHA and Click 'GÖNDER' (Submit).", log_callback)
            log(">> Bot is watching for 'Başvurunuz başarıyla alınmıştır' message...", log_callback)

            # Wait for success message or user skip
            success_detected = False
            start_wait = time.time()
            retried = False
            
            while time.time() - start_wait < 60:
                if STOP_BOT: break
                    
                try:
                    success_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Başvurunuz başarıyla alınmıştır')]")
                    for elem in success_elements:
                        if elem.is_displayed():
                            log(f"   [+] SUCCESS:{ad_from_data} {soyad_from_data}:{tracking_id}", log_callback)
                            log(f"   [+] Başarı! {display_name} tamamlandı.", log_callback)
                            success_detected = True
                            
                            # Save to completed tracking
                            if tracking_id:
                                with open('completed.txt', 'a') as f:
                                    f.write(tracking_id + '\n')
                                completed_tckns.add(tracking_id)
                            break
                    
                    if success_detected: break
                    
                    # Eğer 7 saniye geçtiyse ve form hâlâ başarılı olmadıysa,
                    # boş veya hatalı doldurulmuş alanları kontrol et, doldur ve tekrar gönder
                    if not retried and (time.time() - start_wait > 7.0):
                        log("   [!] Form gönderimi gecikti. Boş/hatalı alanlar kontrol ediliyor...", log_callback)
                        any_empty = verify_and_fix_fields(driver, student, log_callback)
                        if any_empty:
                            log("   [!] Eksik alanlar dolduruldu. Tekrar GÖNDER deneniyor...", log_callback)
                            try:
                                checkbox = driver.find_element(By.ID, config.FIELDS['kvkk'])
                                if not checkbox.is_selected():
                                    driver.execute_script("arguments[0].click();", checkbox)
                            except: pass
                            
                            click_submit(driver, log_callback=log_callback)
                            start_wait = time.time() # Süreyi sıfırla
                            retried = True
                        else:
                            log("   [i] Tüm alanlar dolu görünüyor. Lütfen CAPTCHA çözün veya manuel gönderin.", log_callback)
                            retried = True
                            
                except Exception as e:
                    pass
                
                if not driver.window_handles: 
                    return
                
                time.sleep(1)

            if success_detected:
                log("   [i] Success confirmed. Waiting 1.5 seconds before next student...", log_callback)
                time.sleep(0.8)
            else:
                log(f"   [!] {display_name} için form başarı onayı alınamadı (Zaman aşımı). Sonraki kayda geçiliyor...", log_callback)
            
    except KeyboardInterrupt:
        log("\nStopped.", log_callback)
    except Exception as e:
        log(f"Critical Error: {e}", log_callback)
    finally:
        if driver: driver.quit()
        log("Bot Finished/Stopped.", log_callback)

if __name__ == "__main__":
    # Default behavior for CLI
    run_bot("33.csv")
