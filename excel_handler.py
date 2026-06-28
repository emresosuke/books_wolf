import pandas as pd
from datetime import datetime
import os

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    try:
        is_csv = file_path.lower().endswith('.csv')
        if is_csv:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                sep = ';' if ';' in first_line else ','
            df = pd.read_csv(file_path, sep=sep, dtype=str)
        else:
            df = pd.read_excel(file_path, dtype=str)
    except Exception as e:
        print(f"File read error: {e}")
        return []

    students = []
    
    # Handle NaN values by filling with empty string
    df = df.fillna('')

    for _, row in df.iterrows():
        student = {}
        
        # Helper to safely get value from row with stripped keys
        def get_val(key_aliases):
            for key in key_aliases:
                if key in row: return str(row[key]).strip()
                for col in df.columns:
                    if col.strip().lower() == key.lower():
                        return str(row[col]).strip()
            return ''

        student['first_name'] = get_val(['adı', 'ADI','adı', 'ad', 'isim', 'first_name', 'firstname'])
        student['last_name'] = get_val(['soyadı', 'soyadı *','SOYADI', 'soyad', 'last_name', 'lastname'])
        student['phone'] = get_val(['telefon', 'telefon no', 'tel', 'mobilephone', 'phone']).replace('.0', '')
        student['email'] = get_val(['email', 'e-mail', 'eposta', 'e-posta'])
        
        student['gender'] = get_val(['cinsiyet', 'cinsiyet *', 'gender'])
        student['nationality'] = get_val(['uyruk', 'uyruğu', 'nationality'])
        student['tc_no'] = get_val(['t.c.','t.c','T.C', 'T.C.', 't.c. kimlik no', 't.c kimlik no', 'tc kimlik no', 't.c. kimlik', 'tc kimlik', 'tc no', 'tc', 'tc_no', 'kimlik', 'tgv_identificationnumber'])
        
        # Date Parsing
        dob = get_val(['doğum tarihi','DOĞUM TARİHİ', 'dogum tarihi', 'dogum_tarihi', 'doğum_tarihi', 'birthdate', 'birth_date'])
        try:
            if ' ' in dob: dob = dob.split(' ')[0]
            # Convert standard formats to dd.mm.yyyy
            if '/' in dob: 
                dob = dob.replace('/', '.')
            elif '-' in dob: 
                d = datetime.strptime(dob, '%Y-%m-%d')
                dob = d.strftime('%d.%m.%Y')
        except: pass
        student['birth_date'] = dob
        
        student['school_city'] = get_val(['okul ili', 'okul_ili', 'okul ili *', 'school_city'])
        student['school_district'] = get_val(['okul ilçesi', 'okul_ilcesi', 'okul ilçesi *', 'school_district'])
        student['school_name'] = get_val(['okul', 'okul adı', 'okul_adi', 'okul *', 'school_name'])
        student['okul_no'] = ''  # Okul no boş bırakılıyor
        student['sinif'] = get_val(['sınıfı', 'sinifi', 'sınıf', 'sinif', 'durumu', 'durum', 'durumu *', 'durum *', 'class', 'grade'])
        
        student['summer_school_city'] = get_val(['yaz okuluna katılmak istediğiniz il', 'katılmak istediğiniz il', 'yaz okulu ili', 'yaz_okulu_il', 'yaz okuluna katilmak istediginiz il', 'summer_school_city'])
        student['summer_school_district'] = get_val(['yaz okuluna katılmak istediğiniz ilçe', 'katılmak istediğiniz ilçe', 'yaz okulu ilçesi', 'yaz_okulu_ilce', 'yaz okuluna katilmak istediginiz ilce', 'summer_school_district'])
        
        student['hadis_competition'] = get_val(['çizimlerle 40 hadis', 'hadis', 'yarişma', 'yarışma', 'resim yarışması', 'hadis yarışması', 'hadis_competition'])
        student['parent_name'] = get_val(['veli ad soyad', 'veli adı soyadı', 'veli', 'veli_ad_soyad', 'parent_name'])
        
        students.append(student)
        
    return students
