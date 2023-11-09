import yfinance as yf
import pandas as pd
import sqlite3
from _constants import db_path


conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT codigo FROM tickers")
df = pd.DataFrame(c.fetchall(), columns=['codigo'])

conn.close()
tickers = df['codigo'].map(lambda x: x + '.SA') # adiciona a extensão .SA para realizar a pesquisa no Yahoo Finance

# função para pegar os preços atuais
def get_current_prices(tickers):
    data = yf.download(tickers, period='1d', group_by='ticker')
    prices = pd.DataFrame()
    for ticker in tickers:
        prices[ticker] = data[ticker]['Close']
    prices.columns = prices.columns.str.replace('.SA', '') # remove .SA from column names
    return prices.to_dict()

tickers = tickers.tolist()# transforma a coluna de códigos em uma lista
prices = get_current_prices(tickers) # pega os preços atuais

# transforma o dicionário aninhado em um dicionário desaninhado
prices = {chave_externa: valor_float for chave_externa, dicionario_interno in prices.items() for valor_float in dicionario_interno.values()}
prices = pd.DataFrame.from_dict(prices, orient='index', columns=['preco_atual']) # transforma o dicionário em um dataframe
prices = prices.reset_index()# reseta o index
prices.rename(columns={'index': 'codigo'}, inplace=True) #renomeia a coluna index para Codigo
prices['preco_atual'] = prices['preco_atual'].round(2) #arredonda os valores para duas casas decimais


# # salva o dataframe em um arquivo csv
# prices.to_csv('./resultados/cotacao_atual.csv', index=False)


conn = sqlite3.connect(db_path)
c = conn.cursor()

# cria a tabela cotacoes se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS prices
             (codigo text, preco_atual real, data text)''')

# Salva os dados de negotiations na tabela negotiations
prices.to_sql('prices', conn, if_exists='replace', index=False)

conn.commit()
conn.close()


print('Cotação atual salva com sucesso em ./resultados/cotacao_atual.csv')