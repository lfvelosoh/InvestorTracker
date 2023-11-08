import sys
sys.path.insert(0, ".venv/Lib/site-packages")
import pandas as pd
from unidecode import unidecode
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

#path dos arquivos xlsx
pasta = "relatorios_mensais"

#pega somente o ultimo arquivo para calculo da carteira
arquivos = os.listdir(pasta)# lista todos os arquivos na pasta
arquivos_xlsx = [arquivo for arquivo in arquivos if arquivo.endswith('.xlsx')]# filtra apenas os arquivos com extensão xlsx
arquivos_xlsx.sort(reverse=True)# ordena os arquivos em ordem alfabética inversa
ultimo_arquivo = arquivos_xlsx[0]# seleciona o primeiro arquivo da lista resultante

#path do arquivo
arquivo = pd.read_excel(f'{pasta}/{ultimo_arquivo}', sheet_name=None, dtype={
    'CNPJ do Fundo': str, 
    'CNPJ da Empresa': str,
    'Produto': str,
    'Instituicao': str,
    'Preco de Fechamento': float,
    'Administrador': str,
})

# cria um dataframe com o nome de cada sheet
df_sheet_names = pd.DataFrame({'NOME_ATUAL': arquivo.keys()})

# remove acentos e espaços do nome das sheets
df_sheet_names['NOME_FINAL'] = df_sheet_names['NOME_ATUAL'].apply(lambda x: unidecode(x))
df_sheet_names['NOME_FINAL'] = df_sheet_names['NOME_FINAL'].str.replace('Posicao - ', '')
df_sheet_names['NOME_FINAL'] = df_sheet_names['NOME_FINAL'].str.replace(' ', '_')

# ccria um dicionário com os dataframes de cada sheet
dfs = {}
for sheet_name in arquivo.keys():
    if sheet_name in ['Posição - Ações', 'Posição - BDR', 'Posição - ETF', 'Posição - Fundos']:
        df = arquivo[sheet_name].dropna().copy()
        new_key = df_sheet_names.loc[df_sheet_names['NOME_ATUAL'] == sheet_name, 'NOME_FINAL'].iloc[0]
        df.loc[:, 'Classe'] = new_key
        dfs[new_key] = df

carteira = pd.concat(dfs.values(), ignore_index=True)

# remove os espaços e acentos das colunas
carteira.columns = [unidecode(col) for col in carteira.columns]
carteira.columns = [col.lower().replace(' ', '_') for col in carteira.columns]

# unifica as colunas de cnpj e administrador
carteira.loc[:, 'cnpj'] = carteira['cnpj_do_fundo'].fillna(carteira['cnpj_da_empresa'])
carteira['administrador'] = carteira['administrador'].fillna(carteira['escriturador'])

# renomeia as colunas
carteira = carteira.rename(columns={'codigo_de_negociacao': 'codigo'})
carteira['classe'] = carteira['classe'].str.replace('Fundos', 'FII')
carteira = carteira.drop(['cnpj_da_empresa', 'cnpj_do_fundo', 'conta', 'codigo_isin_/_distribuicao', 'quantidade_disponivel', 'quantidade_indisponivel', 'motivo', 'escriturador', 'valor_atualizado'], axis=1)

# trata os valores nulos
carteira['cnpj'] = carteira['cnpj'].fillna("-")
carteira['administrador'] = carteira['administrador'].fillna("-")

# set column types
categorical_columns = ['codigo', 'classe', 'instituicao']
float_columns = ['preco_de_fechamento']

carteira[categorical_columns] = carteira[categorical_columns].astype('category')
carteira[float_columns] = carteira[float_columns].astype('float')
carteira['quantidade'] = carteira['quantidade'].astype('int')

# limpa a coluna produto
carteira['produto'] = carteira['produto'].str.split('-').str[1]
carteira['produto'] = carteira['produto'].str.strip()

#cria carteira_agregada somando as quantidades
carteira_agg = carteira.groupby(['codigo'],observed=True)['quantidade'].sum()

#faz o merge da carteira com a carteira_agregada
carteira = pd.merge(carteira, carteira_agg, on='codigo', how='left')
carteira.drop(['quantidade_x'], axis=1, inplace=True)
carteira.drop_duplicates(inplace=True)
carteira = carteira.rename(columns={'quantidade_y': 'quantidade'})

# reordena as colunas
carteira = carteira[['codigo', 'produto', 'classe', 'tipo', 'administrador', 'cnpj', 'instituicao', 'quantidade', 'preco_de_fechamento']]

#calcula o total
carteira['total'] = carteira['quantidade'] * carteira['preco_de_fechamento']
carteira['total'] = carteira['total'].round(2)
carteira = carteira.reset_index(drop=True)

#cria coluna com o cnpj formatado
carteira['cnpj'] = carteira['cnpj'].apply(lambda x: '{}.{}.{}/{}-{}'.format(x[:2], x[2:5], x[5:8], x[8:12], x[12:]) if x != '-' else '-')

codigos = carteira[['codigo']].copy()

#salva o arquivo
carteira.to_csv('./resultados/carteira.csv', index=False)
codigos.to_csv('./resultados/codigos.csv', index=False)

print('Carteira salvo com sucesso em ./resultados/carteira.csv')
print('codigos salvo com sucesso em ./resultados/codigos.csv')