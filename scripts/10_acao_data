import pandas as pd
import unidecode

# Importa o arquivo csv
acao = pd.read_csv('../resultados/resultado.csv', sep=';')

acao.columns = [unidecode.unidecode(col) for col in acao.columns]
acao.columns = [col.lower().replace(' ', '_') for col in acao.columns]
acao.columns = [col.lower().replace('.', '') for col in acao.columns]
acao['divyield'] = acao['divyield'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao['mrg_ebit'] = acao['mrg_ebit'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao['mrg_liq'] = acao['mrg_liq'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao['roic'] = acao['roic'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao['roe'] = acao['roe'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao['cresc_rec5a'] = acao['cresc_rec5a'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
acao.rename(columns={'papel': 'codigo'}, inplace=True)

# Importa o arquivo com os códigos dos acaos
codigos = pd.read_csv('../resultados/codigos.csv', sep=';')

# Filtra os acaos do arquivo original que estão na lista de códigos
acao_codigos = acao[acao['codigo'].isin(codigos['codigo'])]
acao_codigos.head(15)