import pandas as pd
import glob
import os
import re
import warnings
import unidecode
from _constants import monthly_path, db_path
import sqlite3

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# name of the sheet
sheet = "Proventos Recebidos"

# Criar um DataFrame vazio
earnings = pd.DataFrame()

# Criar uma lista de files
files = glob.glob(os.path.join(monthly_path, "*.xlsx"))

# Percorrer todos os files na lista
for file in files:
    if sheet in pd.ExcelFile(file).sheet_names:

        # Ler o file
        earnings_temp = pd.read_excel(file, sheet_name=sheet, dtype={
            'Produto': str,
            'Tipo de Evento': str,
            'Instituição': str,
            'Administrador': str,
            })

        # Concatenar o DataFrame temporário ao DataFrame principal
        earnings = pd.concat([earnings, earnings_temp], ignore_index = True)     

earnings.rename(columns={'Produto': 'codigo'}, inplace=True)

earnings.dropna(subset=['codigo'], inplace=True)
earnings["codigo"] = earnings["codigo"].str.replace(" ", "").str.slice(0, 6).str.replace("-", "")
earnings["Pagamento"] = pd.to_datetime(earnings["Pagamento"], dayfirst=True)
earnings.iloc[:, 4:] = earnings.iloc[:, 4:].fillna(value=0).astype('float')

def substituir_codigo(codigo):
    match = re.search(r'\d{2}$', codigo)
    if match:
        last_number = int(match.group())
        if last_number in [12, 13, 14]:
            codigo = codigo[:-2] + '11'
    return codigo

earnings['codigo'] = earnings['codigo'].apply(substituir_codigo)

earnings.columns = [ unidecode.unidecode(col) for col in earnings.columns ]
earnings.columns = [col.lower().replace(' ', '_') for col in earnings.columns]

# Criar conexão com o banco de dados
conn = sqlite3.connect(db_path)

# Criar tabela earnings
conn.execute('''CREATE TABLE IF NOT EXISTS earnings
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             codigo TEXT,
             tipo_de_evento TEXT,
             instituicao TEXT,
             administrador TEXT,
             pagamento DATE,
             quantidade FLOAT,
             valor FLOAT,
             total FLOAT);''')

# Salvar dados de earnings na tabela earnings
earnings.to_sql('earnings', conn, if_exists='replace', index=False)

# Fechar conexão com o banco de dados
conn.close()

print("Dados de earnings salvos na tabela earnings em db.sqlite3")


