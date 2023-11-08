import sys
sys.path.insert(0, ".venv/Lib/site-packages")
import pandas as pd
from unidecode import unidecode
import glob
import os
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

#path dos arquivos xlsx
pasta = "./relatorios_mensais/"
aba = "Negociações"

# Criar um DataFrame vazio
negociacoes = pd.DataFrame()

# Criar uma lista de arquivos
arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))

# Percorrer todos os arquivos na lista
for arquivo in arquivos:
    if aba in pd.ExcelFile(arquivo).sheet_names:

        # Ler o arquivo
        negociacoes_temp = pd.read_excel(arquivo, sheet_name=aba)

        # Concatenar o DataFrame temporário ao DataFrame principal
        negociacoes = pd.concat([negociacoes, negociacoes_temp], ignore_index = True)    

# remove accents from column names
negociacoes.columns = [unidecode(col) for col in negociacoes.columns]

#coverte as colunas para o tipo data
negociacoes["Data"] = pd.to_datetime(negociacoes["Periodo (Inicial)"], format='%d/%m/%Y')

#remove as colunas que não serão utilizadas
negociacoes.drop(["Periodo (Final)", "Periodo (Inicial)", "Quantidade (Liquida)"], axis=1, inplace=True)

#renomeia as colunas
negociacoes = negociacoes.rename(columns={'Codigo de Negociacao': 'Codigo'})

#realiza limpeza na coluna 'Codigo'
negociacoes['UltimoC'] = negociacoes['Codigo'].str.endswith('F')
negociacoes.loc[negociacoes['UltimoC'], 'Codigo'] = negociacoes.loc[negociacoes['UltimoC'], 'Codigo'].str[:-1]
negociacoes.drop(columns=['UltimoC'], inplace=True)

#cria dataframes para compras e vendas
compras = negociacoes[['Codigo', 'Instituicao', 'Quantidade (Compra)', 'Preco Medio (Compra)', 'Data']].rename(columns={'Quantidade (Compra)': 'Quantidade', 'Preco Medio (Compra)': 'Preco_Medio', 'Data': 'Data', 'Instituicao': 'Instituicao', 'Codigo': 'Codigo',}).assign(Negociacao='Compra')
vendas = negociacoes[['Codigo', 'Instituicao', 'Quantidade (Venda)', 'Preco Medio (Venda)', 'Data']].rename(columns={'Quantidade (Venda)': 'Quantidade', 'Preco Medio (Venda)': 'Preco_Medio', 'Data': 'Data', 'Instituicao': 'Instituicao', 'Codigo': 'Codigo',}).assign(Negociacao='Venda')

#concatena os dataframes de compras e vendas
negociacoes = pd.concat([compras, vendas], ignore_index=True)

# check if "NUBR33" and "FBOK34" exist in "Codigo" column and replace them
negociacoes['Codigo'] = negociacoes['Codigo'].replace({'NUBR33': 'ROXO34', 'FBOK34': 'M1TA34'})

# drop rows with 0 values in the 'Quantidade' column
negociacoes = negociacoes[negociacoes['Quantidade'] != 0]

#reorganiza as colunas
negociacoes = negociacoes[['Codigo', 'Data', 'Negociacao','Instituicao', 'Quantidade', 'Preco_Medio']]

#calcula o total da negociação e arredonda
negociacoes['Total'] = (negociacoes['Quantidade'] * negociacoes['Preco_Medio']).round(2)

#ordena as negociações por data
negociacoes = negociacoes.sort_values(by='Data', ascending=True)

#calcula o preço médio total de cada código
preco_medio = negociacoes.groupby('Codigo').apply(lambda x: sum(x['Total']) / sum(x['Quantidade'])).reset_index(name='Preco_Medio_Total').round(2)

preco_medio.columns = [unidecode(col).lower().replace(' ', '_') for col in preco_medio.columns]

negociacoes.columns = [unidecode(col).lower().replace(' ', '_') for col in negociacoes.columns]

#salva os resultados em csv
preco_medio.to_csv('./resultados/preco_medio.csv', index=False)
negociacoes.to_csv('./resultados/negociacoes.csv', index=False)

print('Preço médio total salvo em ./resultados/preco_medio.csv')
print('Negociações salvas em ./resultados/negociacoes.csv')