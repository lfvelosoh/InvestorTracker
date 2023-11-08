import sys
sys.path.insert(0, "venv/Lib/site-packages")
import pandas as pd
from prettytable import PrettyTable

# Define o caminho da pasta resultados
caminho = './resultados/'
carteira = pd.read_csv('./resultados/carteira.csv') # Importa o arquivo carteira
preco_medio = pd.read_csv('./resultados/preco_medio.csv') # Importa o arquivo de preço médio
cotacao_atual = pd.read_csv('./resultados/cotacao_atual.csv') # Importa o arquivo de cotação atual
proventos = pd.read_csv('./resultados/proventos.csv')

# Faz o merge dos três dataframes
wallet = pd.merge(carteira, preco_medio, on='codigo')
wallet = pd.merge(wallet, cotacao_atual, on='codigo')

wallet.drop(columns=['produto', 'tipo', 'administrador', 'cnpj', 'instituicao', 'preco_de_fechamento', 'total'], inplace=True)

wallet['valor_atual'] = wallet['quantidade'] * wallet['preco_atual']
wallet['valor_total'] = wallet['quantidade'] * wallet['preco_medio_total']
wallet['lucro'] = wallet['valor_atual'] - wallet['valor_total']
wallet['lucro_percentual'] = (wallet['lucro'] / wallet['valor_total']) * 100
wallet['lucro_percentual'] = wallet['lucro_percentual'].round(2)
wallet['peso_carteira'] = (wallet['valor_atual'] / wallet['valor_atual'].sum()) * 100
wallet['peso_carteira'] = wallet['peso_carteira'].round(2)

proventos_sum = proventos.groupby('codigo')['valor_liquido'].sum().reset_index()
wallet = pd.merge(wallet, proventos_sum, on='codigo', how='left')
wallet['valor_liquido'].fillna(0, inplace=True)
wallet.rename(columns={'valor_liquido': 'proventos'}, inplace=True)
colunas = ['classe', 'valor_atual', 'valor_total']
classe = wallet[colunas]

classe = classe.groupby('classe').sum()
classe['lucro'] = classe['valor_atual'] - classe['valor_total']
classe['lucro_percentual'] = (classe['lucro'] / classe['valor_total']) * 100
classe['lucro_percentual'] = classe['lucro_percentual'].round(2)
classe['peso'] = (classe['valor_atual'] / classe['valor_atual'].sum()) * 100
classe['peso'] = classe['peso'].round(2)

table_carteira = PrettyTable()
table_carteira.field_names = ["Código", "Classe", "Quantidade", "Preco Medio",  "Preco Atual", "Valor Atual","Valor Total", "Lucro", "Lucro %", "Peso %", "Proventos"]
for index, row in wallet.iterrows():
    table_carteira.add_row([row.codigo, row.classe, round(row.quantidade, 2), round(row.preco_medio_total, 2), round(row.preco_atual, 2), round(row.valor_atual, 2), round(row.valor_total, 2), round(row.lucro, 2), round(row.lucro_percentual, 2), round(row.peso_carteira, 2), round(row.proventos, 2)])
print(table_carteira)

table_classe = PrettyTable()
table_classe.field_names = ["Classe", "Valor Atual", "Valor Total", "Lucro", "Lucro %", "Peso %"]
for index, row in classe.iterrows():
    table_classe.add_row([row.name, round(row.valor_atual, 2), round(row.valor_total, 2), round(row.lucro, 2), round(row.lucro_percentual, 2), round(row.peso, 2)])
print(table_classe)

# Exporta os dataframes em um arquivo xlsx com abas separadas
with pd.ExcelWriter('./resultados/analise.xlsx') as writer:
    wallet.to_excel(writer, sheet_name='wallet')
    classe.to_excel(writer, sheet_name='classe')
print('Arquivo analise.xlsx criado com sucesso em ./resultados/analise.xlsx')
