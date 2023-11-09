from unidecode import unidecode
import os
import warnings
from _constants import monthly_path, db_path
import sqlite3
import pandas as pd
import sqlite3


warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# use last monthly file
files = os.listdir(monthly_path)# list all files in monthly_path
files_xlsx = [file for file in files if file.endswith('.xlsx')]# filter only xlsx files
files_xlsx.sort(reverse=True)# order files by name
last_file = files_xlsx[0]# select last file

# path and read last monthly file
file = pd.read_excel(f'{monthly_path}/{last_file}', sheet_name=None, dtype={
    'CNPJ do Fundo': str, 
    'CNPJ da Empresa': str,
    'Produto': str,
    'Instituicao': str,
    'Preco de Fechamento': float,
    'Administrador': str,
})

# cria um dataframe com o nome de cada sheet
df_sheet_names = pd.DataFrame({'CURRENT_NAME': file.keys()})

# remove spaces and accents from sheet names
df_sheet_names['FINAL_NAME'] = df_sheet_names['CURRENT_NAME'].apply(lambda x: unidecode(x))
df_sheet_names['FINAL_NAME'] = df_sheet_names['FINAL_NAME'].str.replace('Posicao - ', '')
df_sheet_names['FINAL_NAME'] = df_sheet_names['FINAL_NAME'].str.replace(' ', '_')

# create a dict with all sheets
dfs = {}

# loop through all sheets
for sheet_name in file.keys():
    if sheet_name in ['Posição - Ações', 'Posição - BDR', 'Posição - ETF', 'Posição - Fundos']:
        df = file[sheet_name].dropna().copy()
        new_key = df_sheet_names.loc[df_sheet_names['CURRENT_NAME'] == sheet_name, 'FINAL_NAME'].iloc[0]
        df.loc[:, 'Classe'] = new_key
        dfs[new_key] = df

# concat all dataframes
wallet = pd.concat(dfs.values(), ignore_index=True)

# remove spaces and accents from column names
wallet.columns = [unidecode(col) for col in wallet.columns]
wallet.columns = [col.lower().replace(' ', '_') for col in wallet.columns]

# union cnpj_do_fundo and cnpj_da_empresa in cnpj and administrador and escriturador in administrador
wallet.loc[:, 'cnpj'] = wallet['cnpj_do_fundo'].fillna(wallet['cnpj_da_empresa'])
wallet['administrador'] = wallet['administrador'].fillna(wallet['escriturador'])

wallet = wallet.rename(columns={'codigo_de_negociacao': 'codigo'})# rename columns 
wallet['classe'] = wallet['classe'].str.replace('Fundos', 'FII') # replace 'Fundos' with 'FII' in classe column
#drop columns
wallet = wallet.drop(['cnpj_da_empresa', 'cnpj_do_fundo', 'conta', 'codigo_isin_/_distribuicao', 'quantidade_disponivel', 'quantidade_indisponivel', 'motivo', 'escriturador', 'valor_atualizado'], axis=1)

# trate missing values
wallet['cnpj'] = wallet['cnpj'].fillna("-")
wallet['administrador'] = wallet['administrador'].fillna("-")

# set column types
categorical_columns = ['codigo', 'classe', 'instituicao']
float_columns = ['preco_de_fechamento']
wallet[categorical_columns] = wallet[categorical_columns].astype('category')
wallet[float_columns] = wallet[float_columns].astype('float')
wallet['quantidade'] = wallet['quantidade'].astype('int')

# clean produto column
wallet['produto'] = wallet['produto'].str.split('-').str[1]
wallet['produto'] = wallet['produto'].str.strip()

#create wallet_agg
wallet_agg = wallet.groupby(['codigo'],observed=True)['quantidade'].sum()

#merge wallet with wallet_agg
wallet = pd.merge(wallet, wallet_agg, on='codigo', how='left')
wallet.drop(['quantidade_x'], axis=1, inplace=True)
wallet.drop_duplicates(inplace=True)
wallet = wallet.rename(columns={'quantidade_y': 'quantidade'})

# reorder columns
wallet = wallet[['codigo', 'produto', 'classe', 'tipo', 'administrador', 'cnpj', 'instituicao', 'quantidade', 'preco_de_fechamento']]

#format cnpj column
wallet['cnpj'] = wallet['cnpj'].apply(lambda x: '{}.{}.{}/{}-{}'.format(x[:2], x[2:5], x[5:8], x[8:12], x[12:]) if x != '-' else '-')

# create new dataframe with selected columns
tickers = wallet[['codigo', 'produto', 'classe', 'administrador', 'cnpj']].copy()
wallet = wallet[['codigo', 'instituicao', 'quantidade', 'preco_de_fechamento']].copy()

# Connect to database
conn = sqlite3.connect(db_path)

# Create table
conn.execute('''CREATE TABLE IF NOT EXISTS tickers
             (codigo TEXT PRIMARY KEY,
             produto TEXT NOT NULL,
             classe TEXT NOT NULL,
             administrador TEXT NOT NULL,
             cnpj TEXT NOT NULL);''')

# Insert data into table
for index, row in tickers.iterrows():
    conn.execute(f"INSERT OR IGNORE INTO tickers (codigo, produto, classe, administrador, cnpj) VALUES ('{row['codigo']}', '{row['produto']}', '{row['classe']}', '{row['administrador']}', '{row['cnpj']}')")

# Commit changes and close connection
conn.commit()
print('Dados de tickers salvos com sucesso na tabela tickers do database.db')

# Connect to database
conn = sqlite3.connect(db_path)

# Create table
conn.execute('''CREATE TABLE IF NOT EXISTS wallet
             (codigo TEXT NOT NULL,
             instituicao TEXT NOT NULL,
             quantidade INTEGER NOT NULL,
             preco_de_fechamento REAL NOT NULL
             );''')

# Insert data into table
for index, row in wallet.iterrows():
    conn.execute(f"INSERT OR IGNORE INTO wallet (codigo, instituicao, quantidade, preco_de_fechamento) VALUES ('{row['codigo']}', '{row['instituicao']}', {row['quantidade']}, {row['preco_de_fechamento']})")

# Commit changes and close connection
conn.commit()
conn.close()

print('Dados de wallet salvos com sucesso na tabela wallet do sb.sqlite3')
