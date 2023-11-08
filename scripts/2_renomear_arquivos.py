import os

#dicionário para converter nome do mês para número
meses = {
    "janeiro": "01",
    "fevereiro": "02",
    "marco": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12"
}

#path dos arquivos xlsx
pasta_mensal = "./relatorios_mensais/"
pasta_anual = "./relatorios_anuais/"

#for para renomear arquivos mensais
for arquivo in os.listdir(pasta_mensal):
    if arquivo.endswith(".xlsx"):
        for mes in meses:
            if mes in arquivo:
                novo_nome = arquivo.replace("relatorio-consolidado-mensal-", "")
                novo_nome = novo_nome.replace(mes, str(meses[mes]))
                os.rename(os.path.join(pasta_mensal, arquivo), os.path.join(pasta_mensal, novo_nome))
                break

#for para renomear arquivos anuais
for arquivo in os.listdir(pasta_anual):
    if arquivo.endswith(".xlsx"):
        novo_nome = arquivo.replace("relatorio-consolidado-anual-", "")
        os.rename(os.path.join(pasta_anual, arquivo), os.path.join(pasta_anual, novo_nome))

print("Arquivos Renomeados com sucesso!")