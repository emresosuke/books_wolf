import time
import random
import os
import re
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import config_munazara
import excel_munazara
import bot

STOP_MUNAZARA_BOT = False

def log(msg, callback=None):
    if callback:
        try:
            callback(str(msg))
        except:
            pass
    print(msg)

def wait_for_munazara_form(driver, timeout=25, log_callback=None):
    """Waits for Dynamics 365 FormLoader to render the Münazara form elements."""
    log("   [i] Form bileşenlerinin yüklenmesi bekleniyor...", log_callback)
    end_time = time.time() + timeout
    while time.time() < end_time:
        if STOP_MUNAZARA_BOT:
            return False
        try:
            # Check for bolge select or first player input
            el = driver.find_elements(By.NAME, "tgv_tmybolge")
            if el and el[0].is_displayed():
                return True
        except:
            pass
        time.sleep(0.5)
    log("   [!] Form yüklenemedi veya zaman aşımı oluştu.", log_callback)
    return False

def fill_input(driver, name, value, log_callback=None):
    if not value:
        return
    try:
        wait = WebDriverWait(driver, 8)
        el = wait.until(EC.element_to_be_clickable((By.NAME, name)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", el)
        time.sleep(0.1)
        el_type = el.get_attribute('type')
        if el_type == 'date':
            fill_date_input(driver, name, value, log_callback)
            return
        el.click()
        el.clear()
        time.sleep(0.05)
        el.send_keys(str(value))
        time.sleep(0.05)
    except Exception as e:
        log(f"   [!] Input '{name}' doldurulamadı: {e}", log_callback)

def fill_date_input(driver, name, value, log_callback=None):
    if not value:
        return
    try:
        s = str(value).strip()
        d = None
        m = re.match(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$', s)
        if m:
            y, mth, day = m.groups()
            y_int = int(y)
            # Lise yaş sınırları güvenliği (2007 - 2011)
            if 2011 < y_int <= 2015:
                y_int = 2011
            elif 1995 < y_int < 2007:
                y_int = 2008
            d = datetime(y_int, int(mth), int(day))
        else:
            m = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$', s)
            if m:
                day, mth, y = m.groups()
                y_int = int(y)
                if 2011 < y_int <= 2015:
                    y_int = 2011
                elif 1995 < y_int < 2007:
                    y_int = 2008
                d = datetime(y_int, int(mth), int(day))
        
        iso_val = d.strftime('%Y-%m-%d') if d else s
        ddmmyyyy = d.strftime('%d%m%Y') if d else s

        wait = WebDriverWait(driver, 8)
        el = wait.until(EC.presence_of_element_located((By.NAME, name)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", el)
        time.sleep(0.1)

        # 1. HTML5 standard value assignment via JS
        driver.execute_script("""
            var el = arguments[0];
            el.value = arguments[1];
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, el, iso_val)
        time.sleep(0.1)

        # 2. Check if set properly. If not (e.g. custom text mask), send keys as DDMMYYYY
        cur = el.get_attribute('value')
        if not cur or cur == '':
            el.click()
            el.clear()
            el.send_keys(ddmmyyyy)
            time.sleep(0.05)
    except Exception as e:
        log(f"   [!] Date input '{name}' doldurulamadı: {e}", log_callback)

LISE_SEARCH_TERMS = ['Anadolu', 'Lise', 'Fen', 'İmam', 'Meslek', 'Kolej', 'Sosyal']

DIYARBAKIR_LISELER = [
    "Gaziler Anadolu Lisesi",
    "Şehit Halit Gülser Kız Anadolu İmam Hatip Lisesi",
    "Diyarbakır Anadolu Lisesi",
    "Rekabet Kurumu Cumhuriyet Fen Lisesi",
    "Sezai Karakoç Anadolu Lisesi",
    "Ali Emiri Anadolu Lisesi",
    "Diyarbakır Rekabet Kurumu Anadolu Lisesi",
    "Diyarbakır Sosyal Bilimler Lisesi",
    "Gaffar Okkan Anadolu Lisesi",
    "Fatih Anadolu Lisesi",
    "Ziya Gökalp Anadolu Lisesi"
]

def select_random_lise(driver, log_callback=None):
    """
    tgv_highscoolname lookup alanına arama terimi yazıp gelen dropdown önerilerinden
    gerçek ve geçerli bir liseyi rastgele seçer.
    """
    time.sleep(random.uniform(0.15, 0.25))
    selected_name = None
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.NAME, "tgv_highscoolname")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.15)
        element.click()
        element.clear()
        time.sleep(0.1)

        search_term = random.choice(LISE_SEARCH_TERMS)
        for char in search_term:
            element.send_keys(char)
            time.sleep(random.uniform(0.04, 0.08))

        suggestions = []
        start_time = time.time()
        while time.time() - start_time < 4.5:
            found = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item-wrapper")
            suggestions = [el for el in found if el.is_displayed() and el.text.strip()]
            if suggestions:
                break
            time.sleep(0.15)

        if not suggestions:
            fallback = random.choice(DIYARBAKIR_LISELER)
            element.clear()
            for char in fallback[:8]:
                element.send_keys(char)
                time.sleep(random.uniform(0.04, 0.08))
            time.sleep(0.5)
            found = driver.find_elements(By.CSS_SELECTOR, ".ui-menu-item-wrapper")
            suggestions = [el for el in found if el.is_displayed() and el.text.strip()]

        if suggestions:
            chosen = random.choice(suggestions)
            selected_name = chosen.text.strip()
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", chosen)
            time.sleep(0.1)
            chosen.click()
            log(f"      [✓] Lise rastgele seçildi: {selected_name}", log_callback)
        else:
            fallback = random.choice(DIYARBAKIR_LISELER)
            element.clear()
            element.send_keys(fallback)
            element.send_keys(Keys.TAB)
            selected_name = fallback
            log(f"      [i] Öneri listesi açılamadı, lise yazıldı: {selected_name}", log_callback)

        time.sleep(0.15)
    except Exception as e:
        log(f"   [!] Rastgele lise seçiminde hata: {e}", log_callback)

    return selected_name

def fill_select(driver, name, value, log_callback=None):
    if not value:
        return
    try:
        wait = WebDriverWait(driver, 8)
        el = wait.until(EC.presence_of_element_located((By.NAME, name)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", el)
        time.sleep(0.1)
        sel = Select(el)
        # Try by value first, then visible text
        try:
            sel.select_by_value(str(value))
        except:
            sel.select_by_visible_text(str(value))
        time.sleep(0.1)
    except Exception as e:
        log(f"   [!] Select '{name}' seçilemedi: {e}", log_callback)

def fill_munazara_form(driver, team, school_info, log_callback=None, use_audio_captcha=True, use_token_captcha=False):
    """
    Fills one team application for Türkiye Münazara Yarışması.
    """
    try:
        ready = wait_for_munazara_form(driver, timeout=20, log_callback=log_callback)
        if not ready:
            return False

        # 1. Bölge Seçimi
        bolge_val = school_info.get('bolge_val', '5') # Default: Güneydoğu Anadolu (5)
        fill_select(driver, "tgv_tmybolge", bolge_val, log_callback)
        time.sleep(0.2)

        # 2. Okul İli
        city = school_info.get('city', 'Diyarbakır')
        bot.fill_lookup(driver, "tgv_schoolcity", city, log_callback)
        time.sleep(0.2)

        # 3. Okul İlçe
        district = school_info.get('district', 'Kayapınar')
        bot.fill_lookup(driver, "tgv_schoolcounty", district, log_callback)
        time.sleep(0.2)

        # 4. Lise Seçimi / Okul
        team_school = team.get('school', '')
        user_school = school_info.get('school', '').strip()
        school_name = user_school or team_school

        if not school_name or school_name.lower() in ['random', 'rastgele', 'otomatik', 'hepsi']:
            if team['team_name'].startswith('A') or 'A' in str(team.get('p1', {}).get('team_base', '')):
                school_name = "Şehit Halit Gülser Kız Anadolu İmam Hatip Lisesi"
            else:
                school_name = "Gaziler Anadolu Lisesi"

        school_exists = school_info.get('school_in_list', True)

        if school_exists and school_name:
            log(f"   [i] Lise seçiliyor: {school_name}", log_callback)
            res = bot.fill_lookup(driver, "tgv_highscoolname", school_name, log_callback)
            if not res:
                short_term = "Halit Gülser" if "Halit" in school_name else ("Gaziler" if "Gaziler" in school_name else school_name[:8])
                bot.fill_lookup(driver, "tgv_highscoolname", short_term, log_callback)
        else:
            try:
                radio_no = driver.find_element(By.CSS_SELECTOR, "input[name='tgv_existschool'][value='1']")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio_no)
                time.sleep(0.1)
                driver.execute_script("arguments[0].click();", radio_no)
                time.sleep(0.2)
                if school_name:
                    fill_input(driver, "tgv_unknownschool", school_name, log_callback)
            except Exception as e:
                log(f"   [!] Okul listede yok seçeneği işaretlenemedi: {e}", log_callback)

        time.sleep(0.2)

        # 5. Takım Adı
        fill_input(driver, "tgv_teamname", team['team_name'], log_callback)
        time.sleep(0.15)

        # 6. 1. Yarışmacı Bilgileri
        p1 = team['p1']
        fill_input(driver, "tgv_firstplayernamesurname", p1['name'], log_callback)
        fill_input(driver, "tgv_firstplayertcnumber", p1['tc'], log_callback)
        fill_date_input(driver, "tgv_firstplayerbirthdate", p1['birthdate'], log_callback)
        fill_input(driver, "tgv_firstplayerphonenumber", p1['phone'], log_callback)
        fill_input(driver, "tgv_firstplayeremail", p1['email'], log_callback)
        time.sleep(0.15)

        # 7. 2. Yarışmacı Bilgileri
        p2 = team['p2']
        fill_input(driver, "tgv_secondplayernamesurname", p2['name'], log_callback)
        fill_input(driver, "tgv_secondplayertcnumber", p2['tc'], log_callback)
        fill_date_input(driver, "tgv_secondplayerdateofbirth", p2['birthdate'], log_callback)
        fill_input(driver, "tgv_secondplayerphonenumber", p2['phone'], log_callback)
        fill_input(driver, "tgv_secondplayeremail", p2['email'], log_callback)
        time.sleep(0.15)

        # 8. Danışman Hoca Bilgileri
        teacher = team.get('teacher') or school_info.get('teacher') or {}
        fill_input(driver, "tgv_refetanceteachername", teacher.get('name', ''), log_callback)
        fill_input(driver, "tgv_teacheridentificationnumber", teacher.get('tc', ''), log_callback)
        fill_input(driver, "tgv_referancemobilenumber", teacher.get('phone', ''), log_callback)
        fill_input(driver, "tgv_mentorteachermail", teacher.get('email', ''), log_callback)
        time.sleep(0.2)

        # 9. KVKK Aydınlatma Metni
        try:
            kvkk = driver.find_element(By.ID, "kvkkCheckbox")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", kvkk)
            time.sleep(0.1)
            if not kvkk.is_selected():
                driver.execute_script("arguments[0].click();", kvkk)
            log("      [✓] KVKK onaylandı", log_callback)
        except Exception as e:
            log(f"      [!] KVKK işaretlenemedi: {e}", log_callback)

        time.sleep(0.3)

        # 10. reCAPTCHA
        log("   [i] reCAPTCHA kontrol ediliyor...", log_callback)
        captcha_ok = bot.click_recaptcha(driver, log_callback=log_callback,
                                         use_audio_captcha=use_audio_captcha,
                                         use_token_captcha=use_token_captcha)

        if not captcha_ok:
            log("   [!] reCAPTCHA doğrulanamadı, form gönderilemiyor!", log_callback)
            return False

        time.sleep(2.0)

        # 11. Gönder (Submit) Butonu
        submitted = bot.click_submit(driver, log_callback=log_callback)
        if not submitted:
            time.sleep(1.0)
            bot.click_submit(driver, log_callback=log_callback)

        return True

    except Exception as e:
        log(f"Form doldurma hatası: {e}", log_callback)
        return False

def run_munazara_bot(data_file_path, school_info, log_callback=None, use_audio_captcha=True, use_token_captcha=False):
    """
    Main orchestration loop for Türkiye Münazara Yarışması.
    """
    global STOP_MUNAZARA_BOT
    STOP_MUNAZARA_BOT = False

    log("\n" + "="*50, log_callback)
    log("    TÜRKİYE MÜNAZARA YARIŞMASI BAŞVURU BOTU", log_callback)
    log("="*50 + "\n", log_callback)

    log(f"Dosya okunuyor: {data_file_path}...", log_callback)
    data = excel_munazara.load_munazara_data(data_file_path)

    if 'error' in data:
        log(f"HATA: {data['error']}", log_callback)
        return

    teams = data['teams']
    total_teams = len(teams)
    log(f"Toplam {data['total_students']} öğrenci bulundu. {total_teams} takım oluşturuldu.", log_callback)

    if data['warnings']:
        log("UYARILAR:", log_callback)
        for w in data['warnings']:
            log(f"  [!] {w}", log_callback)

    # Danışman Hoca
    teacher = data.get('teacher') or {}
    if not teacher.get('name') and school_info.get('teacher', {}).get('name'):
        teacher = school_info['teacher']
    log(f"Danışman Hoca: {teacher.get('name', 'Belirtilmedi')} (TC: {teacher.get('tc', 'Belirtilmedi')})", log_callback)

    # Completed tracker
    completed_file = 'completed_munazara.txt'
    completed_ids = set()
    if os.path.exists(completed_file):
        with open(completed_file, 'r', encoding='utf-8') as f:
            completed_ids = {line.strip() for line in f if line.strip()}
    log(f"Daha önce tamamlanan takım sayısı: {len(completed_ids)}", log_callback)

    driver = bot.init_driver(log_callback)
    if not driver:
        log("HATA: Tarayıcı başlatılamadı.", log_callback)
        return

    try:
        for idx, team in enumerate(teams, 1):
            if STOP_MUNAZARA_BOT:
                log("Bot kullanıcı tarafından durduruldu.", log_callback)
                break

            team_name = team['team_name']
            p1_tc = team['p1']['tc']
            p2_tc = team['p2']['tc']
            tracking_id = f"{team_name}_{p1_tc}_{p2_tc}"

            if tracking_id in completed_ids:
                log(f"Atlanıyor [{idx}/{total_teams}]: {team_name} ({team['p1']['name']} & {team['p2']['name']}) - Zaten tamamlandı.", log_callback)
                continue

            log(f"\nİşleniyor [{idx}/{total_teams}]: Takım '{team_name}' | 1: {team['p1']['name']} | 2: {team['p2']['name']}", log_callback)
            driver.get(config_munazara.URL)
            time.sleep(2.0)

            team['teacher'] = teacher
            form_ok = fill_munazara_form(driver, team, school_info, log_callback, use_audio_captcha, use_token_captcha)
            if not form_ok:
                log(f"   [!] Takım '{team_name}' için form gönderilemedi (reCAPTCHA doğrulanamadı). Sonraki takıma geçiliyor...", log_callback)
                continue

            log(">> Form gönderildi. Başarı mesajı ('Başvurunuz başarıyla alınmıştır.') bekleniyor...", log_callback)

            success_detected = False
            start_wait = time.time()

            while time.time() - start_wait < 60:
                if STOP_MUNAZARA_BOT:
                    break

                try:
                    # Check for success message
                    success_elems = driver.find_elements(By.XPATH, "//*[contains(text(), 'Başvurunuz başarıyla alınmıştır') or contains(text(), 'başarıyla alınmıştır')]")
                    for elem in success_elems:
                        if elem.is_displayed():
                            log(f"   [+] SUCCESS:{team_name}:{tracking_id}", log_callback)
                            log(f"   [+] BAŞARILI! Takım '{team_name}' kaydı alındı.", log_callback)
                            success_detected = True

                            with open(completed_file, 'a', encoding='utf-8') as f:
                                f.write(tracking_id + '\n')
                            completed_ids.add(tracking_id)
                            break

                    if success_detected:
                        break
                except:
                    pass

                time.sleep(1)

            if success_detected:
                log("   [i] Sonraki takıma geçmeden önce 2 saniye bekleniyor...", log_callback)
                time.sleep(2)
            else:
                log(f"   [!] Takım '{team_name}' için başarı onayı alınamadı. Manuel kontrol gerekebilir.", log_callback)

    except KeyboardInterrupt:
        log("\nBot durduruldu.", log_callback)
    except Exception as e:
        log(f"Kritik Hata: {e}", log_callback)
    finally:
        if driver:
            driver.quit()
        log("Münazara Botu Tamamlandı / Durdu.", log_callback)
