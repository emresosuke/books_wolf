def normalize_name(s):
    if not s:
        return ""
    s = str(s).strip().upper()
    # Normalize Turkish character mappings
    s = s.replace('İ', 'I').replace('ı', 'I').replace('İ', 'I')
    s = s.replace('Ç', 'C').replace('Ğ', 'G').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U')
    # Remove combining characters (like combining dot) just in case
    import unicodedata
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

male_names = {
    'AHMET', 'MEHMET', 'MUSTAFA', 'ALİ', 'HÜSEYİN', 'HASAN', 'İBRAHİM', 'İSMAİL', 'OSMAN', 'MURAT',
    'ÖMER', 'RAMAZAN', 'YUSUF', 'FATİH', 'HALİL', 'SÜLEYMAN', 'ABDULLAH', 'MAHMUT', 'ADEM', 'KEMAL',
    'YAŞAR', 'EMRE', 'ORHAN', 'SALİH', 'HAKAN', 'MEHMET ALİ', 'SERKAN', 'GÖKHAN', 'METİN', 'UĞUR',
    'MUHAMMED', 'ERKAN', 'YAKUP', 'BURAK', 'YASİN', 'MESUT', 'VOLKAN', 'FERHAT', 'ÖZGÜR', 'SİNAN',
    'ERDEM', 'MUSA', 'CEMAL', 'ONUR', 'BEKİR', 'SELÇUK', 'TUNCAY', 'FARUK', 'SEDAT', 'CELAL', 'TURAN',
    'ŞÜKRÜ', 'ADEM', 'NECATİ', 'MUHARREM', 'ADNAN', 'ŞABAN', 'ŞEVKET', 'CENGİZ', 'VEDAT', 'EYÜP',
    'CAFER', 'BAYRAM', 'ÜMİT', 'EROL', 'HAMZA', 'KADİR', 'SELİM', 'NİHAT', 'KENAN', 'İRFAN', 'BİLAL',
    'SADIK', 'LEVENT', 'HALİT', 'RECEP', 'VEYSEL', 'ZAFER', 'ENGİN', 'ENVER', 'BÜNYAMİN', 'SABRİ',
    'ERCAN', 'SONER', 'İLHAN', 'SAMET', 'ERDAL', 'YUNUS', 'HAYRETTİN', 'AYHAN', 'MÜMİN', 'HAYDAR',
    'MİRAÇ', 'BERAT', 'FURKAN', 'EYMEN', 'ÇINAR', 'KEREM', 'ALPEREN', 'POYRAZ', 'KUZEY', 'MERT',
    'HAMZA', 'METEHAN', 'EMİR', 'EMİRHAN', 'YİĞİT', 'RAVZANUR', 'RÜZGAR', 'ZEYD', 'TOPRAK', 'ARAS',
    'BARAN', 'UMUT', 'KAAN', 'ARDA', 'AYAZ', 'ÖMER ASAF', 'YUSUF ALİ', 'ALİ ASAF', 'MUHAMMED ALİ',
    'MUHAMMED EMİN', 'AHMET YASİN', 'AHMET EMİN', 'MEHMET AKİF', 'MEHMET EMİN', 'MUHAMMED YUSUF',
    'MUHAMMED MİRAÇ', 'MUHAMMED ENES', 'MUHAMMED EREN', 'MUHAMMED MUSTAFA', 'MUHAMMED FURKAN',
    'MUHAMMED HAMZA', 'MUHAMMED TAHA', 'MUHAMMED TALHA', 'MUHAMMED EMİR', 'MUHAMMED ÖMER', 'İSHAK', 'HAMDİ',
    'ABDURRAHMAN', 'ABDULKERİM', 'ABDULSAMET', 'ABDULKADİR', 'SELAHATTİN', 'NURETTİN', 'BAHATTİN',
    'SEBAHATTİN', 'NECMETTİN', 'HİKMET', 'FİKRET', 'NİYAZİ', 'ŞEMSETTİN', 'FAHRETTİN', 'HAYRETTİN',
    'SEYFETTİN', 'CEMİL', 'KERİM', 'AZİZ', 'MÜSLÜM', 'SERVET', 'DURSUN', 'RIZA', 'FEYZULLAH',
    'HAMDULLAH', 'ZİYA', 'RAŞİT', 'HİDAYET', 'RESUL', 'MÜCAHİT', 'MÜRSEL', 'CEVDET', 'MAHİR', 'UĞURCAN', 'BAVER', 'CİHAN', 'GEYLANİ', 'SELAHATTİN',
    'ABDULKADİR', 'MAHMUT', 'BEDİRHAN', 'ABDULBAKİ', 'SEMİH', 'BEDRİ', 'FERİT', 'HALUK',
    'KAMİL', 'TAHSİN', 'TARIK', 'TAYFUN', 'TAYYİP', 'TİMUR', 'TOLGA', 'TUNA', 'TUNCAY', 'TURGAY',
    'TURGUT', 'UFUK', 'UĞUR', 'UMUT', 'ÜNAL', 'VEDAT', 'VELİ', 'VEYSEL', 'YALÇIN', 'YAVUZ',
    'YILDIRIM', 'YILMAZ', 'YUNUS', 'YUSUF', 'ZAFER', 'ZEKİ', 'ZEYNEL', 'ZİYA', 'EZEL', 'AREN', 'ARAT', 'MUSA ENES', 'ALİ RENAS', 'EZMİR SEFA', 'SAİT ALİ', 'EYMEN AYAZ', 'MUHAMMED AGİT', 'MUHAMMED YUSUF', 'MUSTAFA', 'İSHAK', 'HALİM', 'İBRAHİM', 'MUHAMMED ADAR', 'MUHAMMED AGİT', 'MEHMET BAHTİYAR', 'BARAN ADAR', 'YUSUF', 'MEHMET', 'MUHAMMED HASAN', 'HARUN', 'AHMET EMİN', 'ALİ', 'AZAD', 'EMRE', 'BİLAL', 'FERMAN', 'MEHMET SALİH', 'MEHMETCAN', 'MUHAMMED ÖZGÜR', 'ROJHAT', 'SAMET', 'ABDULKERİM', 'YASİN', 'YUSUF', 'MUHAMMED ORHAN', 'FARUK', 'YUNUS', 'BAVER', 'FURKAN EFE', 'ABDULSAMED', 'AYAZ', 'UBEYDULLAH', 'HÜSEYİN', 'HASAN', 'EROL', 'MUHAMMED ENES', 'MUHAMMED EREN', 'MEHMET SAMET', 'MİRAÇ', 'MUHAMMED AYAZ', 'ORHAN BERAT', 'SÜLEYMAN', 'UĞUR', 'UMUT EYMEN', 'YUSUF', 'AHMET', 'MUHAMMED ÇINAR', 'MİRAÇ AYAZ', 'DEVRAN', 'MUHAMMED YUSUF', 'ADAR', 'ALİ AYAZ', 'ALİ', 'MUHAMMED ENES', 'BEHZAT', 'MİRAÇ', 'ENES', 'EREN', 'MUHAMMED HASAN', 'İBRAHİM', 'MEHMET AYBARS', 'VEYSİ', 'OZAN UMUT', 'RAMAZAN', 'ŞERVAN SAİD', 'ABDULLAH', 'ADAR', 'MUHAMMED ENSAR', 'RAMAZAN', 'BEHRAN BERAT', 'ESER', 'EYYÜP YAKUP', 'MUHAMMED', 'HASAN SAİD', 'HOZAN SERHAD', 'MEHMET ALİ', 'SEDAT GEYLANİ', 'YUNUS', 'YUSUF', 'MUHAMMED EREN', 'BERAT', 'MUHAMMED FURKAN', 'UMUT YASİN', 'BAHOZ AMED', 'BÜNYAMİN', 'ALİ FIRAT', 'EYMEN EFE', 'ÖMER', 'ALİ OSMAN', 'MUHAMMED', 'CEMAL MACİT', 'DENİZ', 'KAYRA', 'FATİH', 'MESUT', 'HÜSAMETTİN', 'MİRAÇ ARDA', 'MİRAÇ', 'MUHAMMED YUSUF', 'MUSTAFA', 'ROJAT', 'GEYLANİ', 'BARIŞ', 'CENGİZ', 'NESRULLAH', 'MUHAMMED EFE', 'ALİ EREN', 'AZAD', 'AHMET EMİN', 'MUHAMMED', 'MUHAMMED ADAR', 'RUŞEN', 'EYÜP HAMZA', 'MUHAMMED ENES', 'MEHMET EMİN', 'MEHMET NİDAR', 'MURAT', 'SALİH', 'SİNAN AYAZ', 'MURAD', 'EFRAHİM', 'BERAT', 'MEHMET FATİH', 'MUHAMMED YUSUF', 'MUHAMMED AGİD', 'İBRAHİM HAMZA', 'AHMET YASİN', 'BERAT', 'EYMEN MUSAB', 'HASAN', 'MUHAMMED MUSTAFA', 'MEHMET ALİ', 'CEMİL BARAN', 'SAMET', 'SEMİH', 'ŞEHİD RIYAT', 'TOPRAK', 'UMUT BURAK', 'YAKUP', 'YİĞİT', 'YUSUF AYTAÇ', 'MUHAMMED BERAT', 'MUHAMMED MUAZ', 'MEHMET CAN', 'OKTAY', 'EZGİN', 'ALİ İMRAN', 'BARAN', 'BİLAL', 'ÖZGÜR', 'EYMEN ALİ', 'MUHAMMED EYÜP', 'İBRAHİM', 'MAHİR', 'MİRAÇ', 'MUHAMMED', 'MUHAMMED YUSUF', 'MURAT ALİ', 'MUSTAFA KEMAL', 'ÖMER', 'SEYFULLAH', 'UĞURCAN', 'SAMİ YUSUF', 'ARDA', 'MUHAMMED AMMAR', 'MUHAMMED EMİR', 'ALİ ZENUN', 'MAHİR NEÇİRVAN', 'MEHMET AZİZ', 'YUSUF', 'ALİ ARDA', 'BERAT', 'EMİRHAN', 'ENES', 'EYYÜP SULTAN', 'MEHMET', 'MUHAMMED AGİT', 'MUHAMMED AKİF', 'MUHAMMED ŞEYHMUS', 'MUSTAFA', 'MURAT', 'RONİ', 'RAMAZAN', 'MEHMET ZEKİ', 'SİRACETTİN', 'ŞEYHMUS', 'AYAZ', 'AGİT', 'BERAT', 'HARUN', 'ABDULKADİR GEYLANİ', 'ÖMER TAHA', 'BİLAL', 'MUHAMMED EMİN', 'MUHAMMED EMİR', 'MUHAMMED ENES', 'HAMZA', 'MUHAMMED MUSTAFA', 'MURAT', 'MUSTAFA', 'ÖMER FARUK', 'SEYİD', 'VİYAN', 'YUNUS EMRE', 'MUHAMMED YUSUF', 'BARAN', 'EYYÜP', 'BÜNYAMİN', 'ARDA', 'NURULLAH', 'EBUBEKİR', 'ABDULLAH', 'ARİN', 'BERAT', 'FATİH ATA', 'HALİT', 'HASAN HÜSEYİN', 'KENAN', 'MUHAMMED ABAT', 'MUHAMMED ŞERVAN', 'ÖMER BERAT', 'ENES', 'SEYFULLAH', 'ÜMMET', 'YAHYA', 'MİRAÇ', 'MEHMET', 'SİRACEDDİN', 'FURKAN', 'MUHAMMED EYYÜP', 'MUHAMMED', 'MUHAMMED MUSTAFA', 'BİLAL', 'BURAK', 'CANER', 'ENES', 'MUHAMMED ENES', 'MUHAMMED HAMZA', 'MUHAMMED', 'MUHAMMET EYÜP', 'ÖMER', 'ROHAT', 'YUSUF', 'ZÜLKÜF', 'MEHMET SAİT', 'BURAK', 'MUHAMMED İSA', 'MEHMET', 'ALİ',
    
    # Extra common male names from test output
    'ASAF', 'FIRAT', 'RIDVAN', 'DAVUT', 'MİRZA', 'MİRAN', 'TAHA', 'İSA', 'MERVAN', 'AMMAR', 'YUŞA', 
    'MİHRAÇ', 'EGE', 'ARJEN', 'REBER', 'ARGEŞ', 'BAHOZ', 'ÇİYA', 'GÜNEY', 'ŞİRHAT', 'UMEYR', 'ERAY', 
    'MERDAN', 'ANIL', 'ELYESA', 'ÜVEYS', 'ROHAT', 'ARAM', 'DEVRAN', 'ADAR', 'AGİT', 'VEYSİ', 'ENSAR', 
    'EYYÜP', 'HOZAN', 'SERHAD', 'MACİT', 'ROJAT', 'NESRULLAH', 'RUŞEN', 'NİDAR', 'EFRAHİM', 'AGİD', 
    'MUSAB', 'MUAZ', 'ZENUN', 'NEÇİRVAN', 'RONİ', 'SİRACETTİN', 'ŞEYHMUS', 'ABAT', 'ŞERVAN', 'ÜMMET', 
    'YAHYA', 'SİRACEDDİN', 'ZÜLKÜF', 'SAVAŞ', 'BASRİ', 'DOĞU'
}

female_names = {
    'AYŞE', 'FATMA', 'EMİNE', 'HATİCE', 'ZEYNEP', 'ELİF', 'MERYEM', 'ŞERİFE', 'SULTAN', 'HANİFE',
    'MERVE', 'HAVVA', 'SAKİNE', 'CEMİLE', 'HACER', 'LEYLA', 'SEVİM', 'GÜLŞEN', 'SEVİL', 'GÜL',
    'DÖNDÜ', 'ASİYE', 'KEZBAN', 'FİLİZ', 'YASEMİN', 'HÜLYA', 'SEVGİ', 'GÜLAY', 'AYSEL', 'ZELİHA',
    'REMZİYE', 'GÜLHANIM', 'NAZLI', 'SEVDA', 'NURTEN', 'NURAN', 'HAVVA', 'HACER', 'AYSUN', 'AYTEN',
    'DERYA', 'GAMZE', 'SİBEL', 'ÖZLEM', 'ARZU', 'DİLEK', 'ESRA', 'EBRU', 'BURCU', 'EDA',
    'GİZEM', 'PINAR', 'TUĞBA', 'CANSU', 'SİNEM', 'DAMLA', 'BÜŞRA', 'KÜBRA', 'RABİA', 'BETÜL',
    'ŞEYMA', 'SÜMEYYE', 'ESMA', 'MERVE', 'HİLAL', 'ÖZGE', 'GÜLŞAH', 'YAĞMUR', 'İREM', 'SENA',
    'ZEYNEP', 'ELİF', 'ECRİN', 'HİRANUR', 'MİRAY', 'DEFNE', 'AZRA', 'ZÜMRA', 'ESLEM', 'NİSANUR',
    'EYLÜL', 'NEHİR', 'BELİNAY', 'MİNA', 'ASYA', 'ADA', 'LİNA', 'ELİZ', 'ELSA', 'ALYA', 'ARYA',
    'BEREN', 'DERİN', 'DURU', 'YAREN', 'AYBÜKE', 'AYÇA', 'ASLI', 'BANU', 'BAŞAK', 'BEGÜM',
    'BELGİN', 'BERNA', 'BİLGE', 'BİRSEN', 'BUKET', 'CEYDA', 'CEYLAN', 'ÇAĞLA', 'ÇİĞDEM', 'DEMET',
    'DENİZ', 'DİDEM', 'DİLARA', 'DUYGU', 'ECE', 'ELÇİN', 'FUNDA', 'GÖKÇE', 'GÖZDE', 'GÜLÇİN',
    'GÜLDEN', 'HANDAN', 'HAZAL', 'İCLAL', 'İLKNUR', 'İPEK', 'MELİKE', 'MELİS', 'MELTEM', 'MİNE',
    'MÜJGAN', 'NAGİHAN', 'NALAN', 'NAZAN', 'NESLİHAN', 'NEŞE', 'NİHAN', 'NİLÜFER', 'NUR', 'NURAY',
    'NURCAN', 'NURDAN', 'NURGÜL', 'PELİN', 'PERİHAN', 'REYHAN', 'ROJİN', 'SAADET', 'SABAHAT',
    'SADİYE', 'SEDA', 'SEDEN', 'SEHER', 'SELMA', 'SEMRA', 'SERAP', 'SERPİL', 'SEVAL', 'SEZGİ',
    'SONGÜL', 'SUZAN', 'ŞEBNEM', 'ŞÜKRAN', 'TÜLAY', 'TÜLİN', 'YELİZ', 'YEŞİM', 'YILDIZ', 'ZEHRA', 'ZELAL', 'BERİL', 'BERİL', 
    'BERRİL', 'ELSEM', 'ARİNNA', 'ESLEM NAZLI', 'EYLÜL', 'İREMSU', 'NEHİR ADA', 'SALİHA', 'SELİN SU', 'ZERYA NUR', 'LEYLA', 'SİMA NUR', 'DAMLA', 'HANİFE', 'HAVİN', 'İREM', 'MERVE', 'ROJDA', 'SAKİNE', 'SEMANUR', 'SENA', 'TUBA NUR', 'YEKTA RONAI', 'ASMİN', 'ECRİN AİŞE', 'YELİZ', 'ZEYNEP ALEYNA', 'BEYTA NUR', 'ZÜHRE', 'AYŞEGÜL', 'MAİLE', 'ESMANUR', 'SEMANUR', 'MELEK', 'ÇİÇEK', 'EMİNE HAVİN', 'HAFİZE HİRA', 'HİCRAN', 'KÜRDİSTAN ARİN', 'NİSA', 'ÖZGE', 'SÜMEYYE', 'VETFA NUR', 'RONYA', 'EDANUR', 'ASENAT', 'ELİF', 'SEVİM', 'AMİNE', 'ASMİN', 'DAMLA', 'DARİSTAN', 'ELİF AZRA', 'EYLEM', 'EYLÜL', 'NİSA', 'SEYRAN', 'ŞİRVAN', 'YAĞMUR', 'FATMA', 'BERÇEM ŞURA', 'ZEYNEP', 'GÜLSÜM', 'DELAL', 'ZÜLEYHA', 'ASİYE NUR', 'CEYLİN TUĞBA', 'RABİA', 'AZRA', 'ELİF AZRA', 'BETÜL', 'DENİZ', 'ECRİN', 'ELİF', 'HÜMEYRA', 'IRMAK', 'RABİA BETÜL', 'YAĞMUR DAMLA', 'SİNEM', 'HABİBE', 'MEDİNE', 'EYLEM', 'CEYDA', 'EBRU', 'ELİF', 'ESMANUR', 'EZMİRA', 'HİRANUR', 'NİSANUR', 'REBİHA', 'ROJDA', 'SARYA', 'SİDELYA', 'ŞURA', 'ZEYNEP SU', 'ECRİN', 'YÜSRANUR', 'GÜNEŞ', 'AYŞEGÜL', 'DENİZ', 'DAMLA', 'DİCLE TUANA', 'ECRİN', 'ESMANUR', 'GAMZE', 'LİSA', 'MENESA', 'BERİVAN', 'ÜMRA', 'YEŞİM', 'ZEYNEB', 'ZEYNEP', 'İLANUR', 'HALİME', 'NURGÜL', 'HATUN BELİNAY', 'ECRİN', 'ROZA', 'ZEYNEP', 'NİSANUR', 'ASMİN', 'BAHAR', 'ELÇİN', 'DİCLENUR', 'DOĞA', 'ELİF YAREN', 'EYLÜL', 'HAZİN', 'FATOŞ', 'SEVİM MİRA', 'YAĞMUR', 'DILDA', 'ZERYA', 'ELİF', 'ELA NUR', 'ASMİN', 'BELİNAY', 'BETÜL', 'BUĞLEM', 'BAHAR', 'ECRİN', 'ELA', 'ESLEM', 'MENESA', 'MİRAY', 'BÜŞRA', 'ECRİN', 'AVŞİN', 'BERFİN', 'MERYEM', 'MERYEM ESLİM', 'BERJİN SULTAN', 'SÜMEYE', 'IRMAK', 'ZEYNEP YUSA', 'ASYA', 'EDANUR', 'FATMANUR', 'MELİN SU', 'PELİN', 'ROŞNA', 'SAMİRA', 'HİLDA', 'ASMİN', 'DAMLA', 'ESLİM YAĞMUR', 'ÇİDEM', 'AYLİN', 'AYŞENUR BELİNAY', 'HAZAL', 'BELİNAY SENA', 'BERÇEM', 'PELİN', 'ESİLA', 'ELASU', 'ELİF', 'FATMA', 'HATİCE', 'HİCRAN', 'ECRİN', 'ARYA', 'ZEYNEBŞAH', 'ESMA', 'BEYZA SARYA', 'ARİN', 'ZEHRA', 'NEHİR', 'CENNET', 'DORŞİN', 'ELİFNUR', 'MERVE', 'NESRİN', 'İNCİ AZRA', 'ŞENNUR', 'ŞEVİN', 'ZEYNEP', 'TUĞBA', 'NEHİR ADA', 'BÜŞRA', 'YÜSRA', 'BERFİN', 'SERRA', 'ŞEYMANUR', 'ASMİN', 'ŞEVİN', 'ECRİN AZRA', 'ZERYA', 'İLKNUR', 'NEHİR', 'MELEK NARİN', 'GÜLBAHAR', 'DİCLE', 'FİRDEVS', 'FİLİZ', 'NİLFER',
    
    # Extra common female names from test output
    'CEMRE', 'ESLİN', 'HİRA', 'NAVİN', 'NUJİYAN', 'ÖMÜRNUR', 'RAHİME', 'ŞAMİLE', 'BİRHUDDA', 'ELANUR', 
    'ELİFSU', 'FERHAN', 'GÖKNUR', 'HEVİ', 'DELİLA', 'ROTİNDA', 'BEYZA', 'FATMATÜZEHRA', 'GÜLCİHAN', 
    'SENİHA', 'AVDAR', 'BEHİYE', 'BERRA', 'HEJA', 'NURHAYAT', 'NURSELİN', 'RÜMEYSA', 'ŞEVVAL', 
    'TUANA', 'ZÖHRE', 'AKSANUR', 'ÖYKÜ', 'RANA', 'RÜYA', 'RÜMEYZA', 'ZİŞAN', 'AYNUR', 'ECEM', 
    'FERİDE', 'HELEN', 'AYSİMA'
}

ERKEK_ISIMLERI_FALLBACK = {
    'ahmet','mehmet','ali','mustafa','ibrahim','hüseyin','hasan','murat',
    'ömer','yusuf','ramazan','ismail','halil','kadir','abdullah',
    'recep','osman','mahmut','salih','süleyman','bekir','celal','cem',
    'cengiz','emin','ercan','erhan','erkan','ersen','fehmi','ferhat',
    'furkan','hamza','ilhan','kemal','koray','kürşat','levent',
    'mesut','metin','mikail','muhammed','müslüm','nihat','nuri','okan',
    'orhan','recai','rıza','sami','selim','serkan','serdar','tahir',
    'tarık','tayfun','tolga','turan','turgut','ufuk','uğur','umut',
    'veli','volkan','yasin','yılmaz','yunus','ziya','bilal','bulent',
    'bülent','cahit','emre','enes','eyüp','fuat','gökhan','güven',
    'hamit','hüsamettin','ilyas','kamil','kasım','latif','lütfi',
    'mithat','muammer','münir','necdet','necip','niyazi','nur','nurullah',
    'onur','rifat','rıfat','sait','selahattin','selman','şaban','şahin',
    'şakir','şeref','şükrü','talat','tevfik','tuncay','tuncer','türker',
    'yavuz','yener','yiğit','zafer','zeki','baran','berke','berkay',
    'burak','buğra','çağatay','çağlar','çağrı','egemen','emir','emirhan',
    'enes','erdem','eren','fatih','irmak','kaan','kahraman',
    'mert','sarp','selçuk','sinan','tarik','arda','atilla',
    'alp','alpay','alper','alperen','altan','altay','arif','arman',
    'aşkın','atakan','atila','attila','ayhan','aykut','aytunç',
    'baki','balkan','barış','bartu','başar','batuhan','bayram',
    'yusuf','ahmed','muhammed','ömer','ali','omer',
}

# Pre-normalized sets for O(1) matching
male_names_norm = {normalize_name(x) for x in male_names} | {normalize_name(x) for x in ERKEK_ISIMLERI_FALLBACK}
female_names_norm = {normalize_name(x) for x in female_names}

def guess_gender(name):
    if not name:
        return ""
        
    words = str(name).strip().split()
    if not words:
        return ""
        
    # Check words sequentially
    for word in words:
        norm_word = normalize_name(word)
        if norm_word in male_names_norm:
            return "Erkek"
        if norm_word in female_names_norm:
            return "Kadın"
            
    print(f"      [?] Could not guess gender for '{name}'")
    return ""

if __name__ == "__main__":
    # Quick test
    print(guess_gender("AHMED"))
    print(guess_gender("AYŞE"))
    print(guess_gender("EZEL"))
