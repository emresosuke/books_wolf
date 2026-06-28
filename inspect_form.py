import requests
from bs4 import BeautifulSoup

url = 'https://basvuru.tugva.org/kitap-kurdu/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all inputs
    inputs = soup.find_all('input')
    selects = soup.find_all('select')
    textareas = soup.find_all('textarea')
    
    print("--- INPUTS ---")
    for i in inputs:
        print(f"Type: {i.get('type')}, Name: {i.get('name')}, ID: {i.get('id')}, Placeholder: {i.get('placeholder')}")
        
    print("\n--- SELECTS ---")
    for s in selects:
        print(f"Name: {s.get('name')}, ID: {s.get('id')}")
        if s.get('id') == 'city' or s.get('name') == 'city': # Example check
             print("Found city select")

    print("\n--- TEXTAREAS ---")
    for t in textareas:
        print(f"Name: {t.get('name')}, ID: {t.get('id')}")

except Exception as e:
    print(f"Error: {e}")
