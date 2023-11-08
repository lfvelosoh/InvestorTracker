@echo off
:MENU
CLS
echo.
echo 1 - Criar Pastas
echo 2 - Renomear Arquivos
echo 3 - Consolidar Carteira
echo S - Sair
echo.
set /P M=Escolha uma opcao e pressione Enter: 
IF %M%==1 GOTO ARQUIVO1
IF %M%==2 GOTO ARQUIVO2
IF %M%==3 GOTO ARQUIVO3
IF /I "%M%"=="S" GOTO SAIR
echo Opcao invalida
pause
GOTO MENU

:ARQUIVO1
python ./scripts/1_criar_pasta.py
pause
GOTO MENU

:ARQUIVO2
python ./scripts/2_renomear_arquivos.py
pause
GOTO MENU

:ARQUIVO3
python ./scripts/3_carteira.py
python ./scripts/4_proventos.py
python ./scripts/5_movimentacoes.py
python ./scripts/6_cotacoes.py
python ./scripts/7_analise.py
pause
GOTO MENU

:SAIR
exit