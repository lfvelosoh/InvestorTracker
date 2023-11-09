from unidecode import unidecode
import os
import warnings
from _constants import monthly_path, db_path
import sqlite3
import pandas as pd
import glob

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

sheet = "Negociações"

# Criar um DataFrame vazio
negotiations = pd.DataFrame()

# Criar uma lista de files
files = glob.glob(os.path.join(monthly_path, "*.xlsx"))

# Percorrer todos os files na lista
for file in files:
    if sheet in pd.ExcelFile(file).sheet_names:

        # Ler o file
        negotiations_temp = pd.read_excel(file, sheet_name=sheet)

        # Concatenar o DataFrame temporário ao DataFrame principal
        negotiations = pd.concat([negotiations, negotiations_temp], ignore_index = True)    

# remove accents from column names
negotiations.columns = [unidecode(col) for col in negotiations.columns]

#coverte as colunas para o tipo data
negotiations["Data"] = pd.to_datetime(negotiations["Periodo (Inicial)"], format='%d/%m/%Y')

#remove as colunas que não serão utilizadas
negotiations.drop(["Periodo (Final)", "Periodo (Inicial)", "Quantidade (Liquida)"], axis=1, inplace=True)

#renomeia as colunas
negotiations = negotiations.rename(columns={'Codigo de Negociacao': 'Codigo'})

#realiza limpeza na coluna 'Codigo'
negotiations['UltimoC'] = negotiations['Codigo'].str.endswith('F')
negotiations.loc[negotiations['UltimoC'], 'Codigo'] = negotiations.loc[negotiations['UltimoC'], 'Codigo'].str[:-1]
negotiations.drop(columns=['UltimoC'], inplace=True)

#cria dataframes para purchases e sales
purchases = negotiations[['Codigo', 'Instituicao', 'Quantidade (Compra)', 'Preco Medio (Compra)', 'Data']].rename(columns={'Quantidade (Compra)': 'Quantidade', 'Preco Medio (Compra)': 'avg_price', 'Data': 'Data', 'Instituicao': 'Instituicao', 'Codigo': 'Codigo',}).assign(Negociacao='Compra')
sales = negotiations[['Codigo', 'Instituicao', 'Quantidade (Venda)', 'Preco Medio (Venda)', 'Data']].rename(columns={'Quantidade (Venda)': 'Quantidade', 'Preco Medio (Venda)': 'avg_price', 'Data': 'Data', 'Instituicao': 'Instituicao', 'Codigo': 'Codigo',}).assign(Negociacao='Venda')

#concatena os dataframes de purchases e sales
negotiations = pd.concat([purchases, sales], ignore_index=True)

# checa se há algum código que não está na carteira
negotiations['Codigo'] = negotiations['Codigo'].replace({'NUBR33': 'ROXO34', 'FBOK34': 'M1TA34'})

# apaga as negociações que não estão na carteira
negotiations = negotiations[negotiations['Quantidade'] != 0]

#reorganiza as colunas
negotiations = negotiations[['Codigo', 'Data', 'Negociacao','Instituicao', 'Quantidade', 'avg_price']]

#calcula o total da negociação e arredonda
negotiations['Total'] = (negotiations['Quantidade'] * negotiations['avg_price']).round(2)

#ordena as negociações por data
negotiations = negotiations.sort_values(by='Data', ascending=True)

#calcula o preço médio total de cada código
avg_price = negotiations.groupby('Codigo').apply(lambda x: sum(x['Total']) / sum(x['Quantidade'])).reset_index(name='avg_price_Total').round(2)

avg_price.columns = [unidecode(col).lower().replace(' ', '_') for col in avg_price.columns]

negotiations.columns = [unidecode(col).lower().replace(' ', '_') for col in negotiations.columns]


# Cria uma conexão com o banco de dados
conn = sqlite3.connect(db_path)

# Cria a tabela negotiations
conn.execute('''CREATE TABLE IF NOT EXISTS negotiations
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             codigo TEXT NOT NULL,
             data DATE NOT NULL,
             negociacao TEXT NOT NULL,
             instituicao TEXT NOT NULL,
             quantidade INTEGER NOT NULL,
             avg_price REAL NOT NULL,
             total REAL NOT NULL);''')

# Salva os dados de negotiations na tabela negotiations
negotiations.to_sql('negotiations', conn, if_exists='replace', index=False)

# Fecha a conexão com o banco de dados
conn.close()

print('Dados de negotiations salvos em db.sqlite3 na tabela negotiations')

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
wallet = wallet[['codigo', 'instituicao', 'quantidade']].copy()

# merge wallet and avg_price
wallet = pd.merge(wallet, avg_price, on='codigo', how='left')


# Connect to database
conn = sqlite3.connect(db_path)

# Create table
conn.execute('''CREATE TABLE IF NOT EXISTS tickers
             (codigo TEXT PRIMARY KEY,
             produto TEXT NOT NULL,
             classe TEXT NOT NULL,
             administrador TEXT NOT NULL,
             cnpj TEXT NOT NULL);''')

# Salva os dados de negotiations na tabela negotiations
tickers.to_sql('tickers', conn, if_exists='replace', index=False)
print('Dados de tickers salvos com sucesso na tabela tickers do database.db')

# Create table
conn.execute('''CREATE TABLE IF NOT EXISTS wallet
             (codigo TEXT NOT NULL,
             instituicao TEXT NOT NULL,
             quantidade INTEGER NOT NULL,
             avg_price_total REAL NOT NULL
             );''')

# Salva os dados de negotiations na tabela negotiations
wallet.to_sql('wallet', conn, if_exists='replace', index=False)
print('Dados de wallet salvos com sucesso na tabela wallet do sb.sqlite3')

conn.close()

