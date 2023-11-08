import os

pastas = ["relatorios_mensais", "relatorios_anuais", "resultados"] #define nome das pastas a serem criadas

#se pastas não existirem, criar
for pasta in pastas:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

print("Pasta(s) criada(s) com sucesso!")
print("Insira os relatórios na pasta 'relatorios_mensais' e 'relatorios_anuais' antes de renomear.")