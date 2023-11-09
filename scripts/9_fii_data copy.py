import pandas as pd
import unidecode

# Importa o arquivo csv
fii = pd.read_csv('./resultados/ranking.csv', sep=';')

fii.columns = [unidecode.unidecode(col) for col in fii.columns]
fii.columns = [col.lower().replace(' ', '_') for col in fii.columns]
# fii['segmento'] = fii['segmento'].astype('category')
# fii['ffo_yield'] = fii['ffo_yield'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
# fii['dividend_yield'] = fii['dividend_yield'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
# fii['cap_rate'] = fii['cap_rate'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
# fii['vacancia_media'] = fii['vacancia_media'].str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype('float') / 100
# fii.rename(columns={'papel': 'codigo'}, inplace=True)

# Importa o arquivo com os códigos dos FIIs
codigos = pd.read_csv('./resultados/codigos.csv', sep=';')

# Filtra os FIIs do arquivo original que estão na lista de códigos
fii_codigos = fii[fii['fundos'].isin(codigos['codigo'])]
fii_codigos.head(15)


