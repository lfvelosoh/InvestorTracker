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
import time
from _constants import db_path
import sqlite3

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

# create a dataframe using the variable name
data = pd.read_html(html, thousands='.', decimal=',')[0]

fiis_data = pd.DataFrame(data)

print(fiis_data)


# create a connection to the database
conn = sqlite3.connect(db_path)

# create a cursor object
cursor = conn.cursor()

# Create table
conn.execute('''CREATE TABLE IF NOT EXISTS fiis_data_FE
                 ('Código do fundo' TEXT,
                     'Setor' TEXT,
                     'Preço Atual' REAL,
                     'Liquidez Diária' REAL,
                     'Dividend Yield' REAL,
                     'DY (3M) Acumulado' REAL,
                     'DY (6M) Acumulado' REAL,
                     'DY (12M) Acumulado' REAL,
                     'DY (3M) Média' REAL,
                     'DY (6M) Média' REAL,
                     'DY (12M) Média' REAL,
                     'DY Ano' REAL,
                     'Variação Preço' REAL,
                     'Rentab. Período' REAL,
                     'Rentab. Acumulada' REAL,
                     'Patrimônio Líq.' REAL,
                     'VPA' REAL,
                     'P/VPA' REAL,
                     'DY Patrimonial' REAL,
                     'Variação Patrimonial' REAL,
                     'Rentab. Patr. no Período' REAL,
                     'Rentab. Patr. Acumulada' REAL,
                     'Vacância Física' REAL,
                     'Vacância Financeira' REAL,
                     'Quantidade Ativos' INTEGER,
                     'Patrimônio Líq. por Ativo' REAL,
                     'Quantidade de cotistas' INTEGER,
                     'P/VPC' REAL,
                     'Data últ cot' TEXT
                 );''')

# create a table to store the fiis_data
fiis_data.to_sql('fiis_data_FE', conn, if_exists='replace', index=False)

# close the connection to the database
conn.close()

print('Dados de fiis_data salvos em db.sqlite3 na tabela fiis_data')
