from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from databases import Database
from selenium import webdriver
from datetime import datetime
import pandas as pd
import json
import time
from sqlite3 import IntegrityError

#definitions
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.fundsexplorer.com.br/ranking'

driver.get(url)
time.sleep(3)  # espera 5 segundos

# Localiza o elemento span que contém o checkbox
span_buton = driver.find_element(By.XPATH, '//*[@id="colunas-ranking__select-button"]')
# Clica no checkbox
span_buton.click()

# Localiza o elemento span que contém o checkbox
span_checkbox = driver.find_element(By.XPATH, '//*[@id="colunas-ranking__select"]/li[1]/label/span')
# Clica no checkbox
span_checkbox.click()
time.sleep(2)

# Acha elemento que possui informações sobre as previsões
elementId = '//*[@id="upTo--default-fiis-table"]/div/table'
element = driver.find_element("xpath", elementId)

html = element.get_attribute('outerHTML')
nome_variavel = url.split('/')[-1].split('.')[0]
# create a dataframe using the variable name
globals()[nome_variavel] = pd.read_html(html, thousands='.', decimal=',')[0]
globals()[nome_variavel].to_csv(f'./resultados/{nome_variavel}.csv', sep=';', encoding='utf-8-sig', index=False)