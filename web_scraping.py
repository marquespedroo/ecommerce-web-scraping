from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium_stealth import stealth

# Configuração inicial
url = 'https://www.casasbahia.com.br/'
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializa o driver com o Selenium Stealth
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Aplicando o stealth para evitar detecção
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# Acessando o site
driver.get('https://www.casasbahia.com.br/')

time.sleep(3)  # Tempo de espera para garantir que a página carregue
driver.find_element(By.ID, 'search-form-input').click()
driver.find_element(By.ID, 'search-form-input').send_keys('iphone')
time.sleep(3)  # Espera para simular o tempo que o usuário leva para digitar
driver.find_element(By.ID, 'search-form-input').send_keys(Keys.ENTER)

time.sleep(5)  # Esperar a página de resultados carregar

soup = BeautifulSoup(driver.page_source, 'html.parser')
last_page = 23

# Estrutura para armazenar os resultados
dic_items = {'nome': [], 'link': [], 'preco': []}

for i in range(1, last_page + 1):
    url_pag = f'{url}iphone/b?page={i}'
    driver.get(url_pag)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all('div', class_=re.compile('css-1enexmx'))

    for item in items:
        # Extrair nome e link
        elem_name = item.find('h3', class_='product-card__title')
        if elem_name and elem_name.a:
            nome = elem_name.a.text.strip()
            link = elem_name.a['href']
            if not link.startswith('http'):
                link = 'https://www.casasbahia.com.br' + link
        else:
            continue
        elem_price = item.find('div', class_='product-card__installment-text')
        if elem_price:
            price_text = elem_price.text.strip()
            match = re.search(r'R\$\s*([\d.,]+)', price_text)
            if match:
                price = match.group(1).replace('.', '').replace(',', '.')
            else:
                price = 'Preço não disponível'
        else:
            price = 'Preço não disponível'

        dic_items['nome'].append(nome)
        dic_items['link'].append(link)
        dic_items['preco'].append(price)
    print(url_pag)

driver.quit()

# Cria um DataFrame com os resultados
df_items = pd.DataFrame(dic_items)
df_items.to_csv('iphoneCB.csv', encoding='utf-8', sep=';')
print(df_items)

# Converte o CSV para Excel
excel_filename = 'iphoneCB.xlsx'
df_items.to_excel(excel_filename, index=False)

print(f"Planilha '{excel_filename}' gerada com sucesso!")