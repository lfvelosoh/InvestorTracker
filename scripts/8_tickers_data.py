#imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

#definitions
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
local = '/html/body/div[1]/div[2]/table'

urls = ['https://www.fundamentus.com.br/resultado.php','https://www.fundamentus.com.br/fii_resultado.php']


for url in urls:
    driver.get(url)
    elemento = driver.find_element("xpath", local)
    html = elemento.get_attribute('outerHTML')
    nome_variavel = url.split('/')[-1].split('.')[0]
    # create a dataframe using the variable name
    globals()[nome_variavel] = pd.read_html(html, thousands='.', decimal=',')[0]
    globals()[nome_variavel].to_csv(f'./resultados/{nome_variavel}.csv', sep=';', encoding='utf-8-sig', index=False)