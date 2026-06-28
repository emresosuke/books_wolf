# Form Config
URL = "https://basvuru.tugva.org/yaz-okulu/"

# ─── 2CAPTCHA API ANAHTARI ────────────────────────────────────────────────────
# https://2captcha.com adresinden ücretsiz hesap açıp API anahtarınızı buraya girin.
# Boş bırakırsanız reCAPTCHA otomatik çözülemez, manuel yapmanız gerekir.
TWOCAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY_HERE"   # ← Buraya kendi API anahtarınızı girin
# ─────────────────────────────────────────────────────────────────────────────

# SESLİ DOĞRULAMA (reCAPTCHA) ──────────────────────────────────────────────
# Sesli doğrulama (Audio Challenge) kullanılsın mı? (True = Evet, False = Hayır)
# Bu yöntem tamamen ücretsiz ve yereldir.
USE_AUDIO_CAPTCHA = True
# ──────────────────────────────────────────────────────────────────────────────

# Field Selectors (By ID or Name)
FIELDS = {
    'firstname': 'firstname', # Name attribute
    'lastname': 'lastname',   # Name attribute
    'gender': 'tgv_gendercode', # Select Name
    'nationality': 'tgv_nationality', # Select Name
    'tc_no': 'tgv_identificationnumber', # Name attribute
    'birthdate': 'tgv_birthdate', # Name attribute
    'school_city': 'tgv_schoolcity', # Name attribute (Lookup)
    'school_district': 'tgv_schoolcounty', # Name attribute (Lookup)
    'school_name': 'tgv_schoolid', # Name attribute (Lookup)
    'summer_school_city': 'tgv_summerschoolcity', # Name attribute (Lookup)
    'summer_school_district': 'tgv_summerschooldistrict', # Name attribute (Lookup)
    'hadis_competition': 'tgv_drawingsfortyhadithattend', # Select Name
    'parent_name': 'tgv_parentnamesurname', # Name attribute
    'phone': 'mobilephone', # Name attribute
    'kvkk': 'kvkkCheckbox', # ID
}

# Default Values (not strictly used, but kept for compatibility)
DEFAULTS = {
    'gender': '', 
    'nationality': '1', # Default: TC Vatandaşı
    'hadis_competition': '2', # Default: Hayır
}
