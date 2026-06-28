import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://basvuru.tugva.org/ihtisas-akademi')
    time.sleep(10) # give it time in case of cloudflare
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    inputs = soup.find_all('input')
    selects = soup.find_all('select')
    print('--- INPUTS ---')
    for i in inputs:
        print(f"Type: {i.get('type')}, Name: {i.get('name')}, ID: {i.get('id')}")
    print('--- SELECTS ---')
    for s in selects:
        print(f"Name: {s.get('name')}, ID: {s.get('id')}")
    
    # Let's save the page source for extra safety
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    driver.quit()
except Exception as e:
    print(e)
