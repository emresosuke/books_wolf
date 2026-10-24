import os
import re
import pandas as pd
from datetime import datetime

def clean_str(val):
    if val is None or pd.isna(val):
        return ""
    s = str(val).replace('\u200b', '').replace('\ufeff', '').strip()
    return s

def format_tel(tel_str):
    digits = re.sub(r'\D', '', clean_str(tel_str))
    if digits.startswith('90') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return clean_str(tel_str)

def format_date_iso(date_str):
    s = clean_str(date_str)
    if not s:
        return ""
    if ' ' in s:
        s = s.split(' ')[0]
    
    m = re.match(r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$', s)
    if m:
        y, mth, d = m.groups()
        y_int = int(y)
        # Lise sınırları kontrolü (2007 - 2011): 2012+ ise 2011'e çeker
        if 2011 < y_int <= 2015:
            y_int = 2011
        elif 1995 < y_int < 2007:
            y_int = 2008
        return f"{y_int:04d}-{int(mth):02d}-{int(d):02d}"
    
    m = re.match(r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$', s)
    if m:
        d, mth, y = m.groups()
        y_int = int(y)
        if 2011 < y_int <= 2015:
            y_int = 2011
        elif 1995 < y_int < 2007:
            y_int = 2008
        return f"{y_int:04d}-{int(mth):02d}-{int(d):02d}"
    
    return s

# Default High Schools mapped to teams
DEFAULT_SCHOOLS = {
    'A': "Şehit Halit Gülser Kız Anadolu İmam Hatip Lisesi",
    'B': "Gaziler Anadolu Lisesi"
}

DEFAULT_TEACHERS = {
    'A': {
        'name': 'Tuncay Dağdelen',
        'tc': '22099727200',
        'phone': '505-453-1564',
        'email': 'tursunorhan@gmail.com',
        'birthdate': '1982-06-14'
    },
    'B': {
        'name': 'Ömer Teyfik Avcı',
        'tc': '14057014866',
        'phone': '551-634-9498',
        'email': 'omeravc2101@gmail.com',
        'birthdate': '1985-03-22'
    }
}

def load_munazara_data(file_path):
    if not os.path.exists(file_path):
        return {'error': f"Dosya bulunamadı: {file_path}", 'teams': []}

    is_csv = file_path.lower().endswith('.csv')
    
    teacher_info = {
        'name': '',
        'tc': '',
        'phone': '',
        'email': ''
    }
    
    teachers_by_team = dict(DEFAULT_TEACHERS)
    
    df = None
    
    if is_csv:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            raw_lines = [line.rstrip('\r\n') for line in f]

        student_lines = []
        in_teacher_section = False
        
        for line in raw_lines:
            clean_line = line.strip()
            if not clean_line or clean_line.replace(',', '').replace(';', '').strip() == '':
                continue
            if 'DANIŞMAN' in clean_line.upper() or 'DANISMAN' in clean_line.upper():
                in_teacher_section = True
                continue
            
            if in_teacher_section:
                parts = [clean_str(p) for p in re.split(r'[,;]', clean_line) if clean_str(p)]
                if len(parts) >= 3:
                    t_name = parts[0]
                    t_tc = re.sub(r'\D', '', parts[1])
                    t_phone = format_tel(parts[2])
                    t_email = parts[3] if len(parts) >= 4 else ''
                    t_obj = {'name': t_name, 'tc': t_tc, 'phone': t_phone, 'email': t_email}
                    if not teacher_info['name']:
                        teacher_info = t_obj
                    t_team = parts[4].upper().replace('TAKIM', '').strip() if len(parts) >= 5 and parts[4] else ''
                    if t_team:
                        teachers_by_team[t_team] = t_obj
                continue
            
            student_lines.append(line)

        import io
        csv_stream = io.StringIO("\n".join(student_lines))
        try:
            first_l = student_lines[0] if student_lines else ""
            sep = ';' if ';' in first_l else ','
            df = pd.read_csv(csv_stream, sep=sep, dtype=str)
        except Exception as e:
            return {'error': f"Dosya okuma hatası: {e}", 'teams': []}
    else:
        try:
            df = pd.read_excel(file_path, dtype=str)
            def has_expected_cols(cols):
                c_str = " ".join([str(c).lower() for c in cols])
                return ('ad' in c_str or 'isim' in c_str) and ('tc' in c_str or 'kimlik' in c_str)

            if not has_expected_cols(df.columns):
                for row_idx in range(min(10, len(df))):
                    candidate_row = df.iloc[row_idx].values
                    if has_expected_cols(candidate_row):
                        df.columns = [clean_str(c) for c in candidate_row]
                        df = df.iloc[row_idx + 1:].reset_index(drop=True)
                        break
        except Exception as e:
            return {'error': f"Dosya okuma hatası: {e}", 'teams': []}

    df = df.fillna('')
    
    def find_col(aliases):
        for col in df.columns:
            clean_c = re.sub(r'\s+', ' ', str(col).strip().lower())
            for a in aliases:
                if a in clean_c or clean_c == a:
                    return col
        return None

    col_name = find_col(['ad soyad', 'adı soyadı', 'ad_soyad', 'isim soyisim', 'ad'])
    col_tc = find_col(['tc', 't.c.', 'tc no', 'tc kimlik', 'tc_no', 'kimlik'])
    col_dob = find_col(['doğum', 'dogum', 'doğumtarihi', 'dogum_tarihi', 'birthdate'])
    col_tel = find_col(['tel', 'telefon', 'phone', 'cep'])
    col_mail = find_col(['e posta', 'eposta', 'email', 'e-posta', 'mail'])
    col_team = find_col(['takım adı', 'takim adi', 'takım', 'takim', 'team'])
    col_school = find_col(['okul adı', 'okul adi', 'okul', 'lise', 'lise adı', 'lise adi', 'school'])
    col_role = find_col(['rol', 'statü', 'gorev'])

    students = []
    seen_tcs = set()
    warnings = []

    for idx, row in df.iterrows():
        name = clean_str(row.get(col_name, '')) if col_name else ''
        tc = re.sub(r'\D', '', clean_str(row.get(col_tc, ''))) if col_tc else ''
        dob = format_date_iso(row.get(col_dob, '')) if col_dob else ''
        tel = format_tel(row.get(col_tel, '')) if col_tel else ''
        email = clean_str(row.get(col_mail, '')) if col_mail else ''
        team_base = clean_str(row.get(col_team, '')) if col_team else ''
        school = clean_str(row.get(col_school, '')) if col_school else ''
        role = clean_str(row.get(col_role, '')) if col_role else ''

        if not name and not tc:
            continue
        
        # Check if danışman row
        if 'DANIŞMAN' in name.upper() or 'DANIŞMAN' in role.upper() or 'DANISMAN' in role.upper():
            clean_name = re.sub(r'^DANIŞMAN\s*:?\s*', '', name, flags=re.I).strip()
            t_obj = {'name': clean_name or name, 'tc': tc, 'phone': tel, 'email': email}
            clean_t = team_base.upper().replace('TAKIM', '').strip()
            if clean_t:
                teachers_by_team[clean_t] = t_obj
            if not teacher_info['name']:
                teacher_info = t_obj
            continue

        if tc in seen_tcs:
            warnings.append(f"Mükerrer TC tespit edildi: {tc} ({name})")
        seen_tcs.add(tc)

        # Infer school if not explicit
        clean_tb = team_base.upper().replace('TAKIM', '').strip()
        if not school:
            school = DEFAULT_SCHOOLS.get(clean_tb, "Gaziler Anadolu Lisesi")

        students.append({
            'name': name,
            'tc': tc,
            'birthdate': dob,
            'phone': tel,
            'email': email,
            'team_base': team_base or 'Takım',
            'school': school
        })

    # Group students into teams of 2, grouped by team/school
    from collections import OrderedDict
    grouped_students = OrderedDict()
    for s in students:
        tb = s['team_base']
        if tb not in grouped_students:
            grouped_students[tb] = []
        grouped_students[tb].append(s)

    teams = []
    leftover = []
    global_team_counter = 1

    for tb, s_list in grouped_students.items():
        clean_tb = tb.upper().replace('TAKIM', '').strip()
        t_teacher = teachers_by_team.get(clean_tb, DEFAULT_TEACHERS.get(clean_tb, teacher_info))
        t_school = DEFAULT_SCHOOLS.get(clean_tb, "Gaziler Anadolu Lisesi")

        for i in range(0, len(s_list), 2):
            if i + 1 < len(s_list):
                p1 = s_list[i]
                p2 = s_list[i + 1]
                team_num = (i // 2) + 1
                base_name = clean_tb if clean_tb else tb
                team_name = f"{base_name}-{team_num}" if len(base_name) <= 3 else f"{base_name} {team_num}"
                
                school_to_use = p1.get('school') or p2.get('school') or t_school

                teams.append({
                    'team_id': global_team_counter,
                    'team_name': team_name,
                    'school': school_to_use,
                    'p1': p1,
                    'p2': p2,
                    'teacher': t_teacher
                })
                global_team_counter += 1
            else:
                leftover.append(s_list[i])

    if leftover:
        for lo in leftover:
            warnings.append(f"1 öğrenci eşleşmedi (tek kaldı): {lo['name']} (Takım: {lo['team_base']}, TC: {lo['tc']})")

    # Set default top-level teacher if not set
    if not teacher_info['name'] and 'A' in teachers_by_team:
        teacher_info = teachers_by_team['A']

    return {
        'total_students': len(students),
        'teams': teams,
        'teacher': teacher_info,
        'teachers_by_team': teachers_by_team,
        'leftover': leftover,
        'warnings': warnings
    }
