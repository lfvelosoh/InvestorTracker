import os
from _constants import *

# for to rename monthly files
for file in os.listdir(monthly_path):
    if file.endswith(".xlsx"):
        for mes in month:
            if mes in file:
                new_name = file.replace("relatorio-consolidado-mensal-", "")
                new_name = new_name.replace(mes, str(month[mes]))
                os.rename(os.path.join(monthly_path, file), os.path.join(monthly_path, new_name))
                break

# for to rename yearly files
for file in os.listdir(yearly_path):
    if file.endswith(".xlsx"):
        new_name = file.replace("relatorio-consolidado-anual-", "")
        os.rename(os.path.join(yearly_path, file), os.path.join(yearly_path, new_name))

print("files renamed successfully.")