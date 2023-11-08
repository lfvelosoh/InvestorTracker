import sys
sys.path.insert(0, ".venv/Lib/site-packages")
import pandas as pd
import glob
import os
import re
import warnings
import unidecode

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

#path dos arquivos xlsx
pasta = "./relatorios_mensais/"
aba = "Proventos Recebidos"

# Criar um DataFrame vazio
proventos = pd.DataFrame()

# Criar uma lista de arquivos
arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))

# Percorrer todos os arquivos na lista
for arquivo in arquivos:
    if aba in pd.ExcelFile(arquivo).sheet_names:

        # Ler o arquivo
        proventos_temp = pd.read_excel(arquivo, sheet_name=aba, dtype={
            'Produto': str,
            'Tipo de Evento': str,
            'Instituição': str,
            'Administrador': str,
            })

        # Concatenar o DataFrame temporário ao DataFrame principal
        proventos = pd.concat([proventos, proventos_temp], ignore_index = True)     

proventos.rename(columns={'Produto': 'codigo'}, inplace=True)

proventos.dropna(subset=['codigo'], inplace=True)
proventos["codigo"] = proventos["codigo"].str.replace(" ", "").str.slice(0, 6).str.replace("-", "")
proventos["Pagamento"] = pd.to_datetime(proventos["Pagamento"], dayfirst=True)
proventos.iloc[:, 4:] = proventos.iloc[:, 4:].fillna(value=0).astype('float')

def substituir_codigo(codigo):
    match = re.search(r'\d{2}$', codigo)
    if match:
        ultimo_numero = int(match.group())
        if ultimo_numero in [12, 13, 14]:
            codigo = codigo[:-2] + '11'
    return codigo

proventos['codigo'] = proventos['codigo'].apply(substituir_codigo)

proventos.columns = [ unidecode.unidecode(col) for col in proventos.columns ]

proventos.columns = [col.lower().replace(' ', '_') for col in proventos.columns]

proventos.to_csv('./resultados/proventos.csv', index=False)

print("Proventos salvos em ./resultados/proventos.csv")
