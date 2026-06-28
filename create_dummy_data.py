import pandas as pd

data = {
    'ad': ['Ahmet', 'Ayşe'],
    'soyad': ['Yılmaz', 'Demir'],
    'cinsiyet': ['Erkek', 'Kadın'],
    'uyruk': ['TC Vatandaşı', 'TC Vatandaşı'],
    'tc_no': ['12345678901', '98765432109'],
    'dogum_tarihi': ['15.06.2013', '24.11.2014'],
    'okul_ili': ['İstanbul', 'Ankara'],
    'okul_ilcesi': ['Fatih', 'Çankaya'],
    'okul': ['Atatürk İlkokulu', 'Cumhuriyet Ortaokulu'],
    'yaz_okulu_il': ['İstanbul', 'Ankara'],
    'yaz_okulu_ilce': ['Fatih', 'Çankaya'],
    'hadis_competition': ['Evet', 'Hayır'],
    'veli_ad_soyad': ['Mehmet Yılmaz', 'Fatma Demir'],
    'telefon': ['5551234567', '5439876543']
}

df = pd.DataFrame(data)
df.to_excel('yaz_okulu_test.xlsx', index=False)
print("yaz_okulu_test.xlsx created successfully.")
