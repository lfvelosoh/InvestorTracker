# InvestorTacker

## Descrição

Este projeto tem como objetivo simplificar o processo de acompanhamento de investimentos em ações, fundos e outros ativos financeiros. Ele recebe arquivos em formato Excel gerados pelo portal da B3 (Bolsa de Valores do Brasil) e realiza a importação e tratamento dos dados contidos nesses arquivos. Ao final do processo, o projeto consulta informações atualizadas sobre o valor da cotação das ações por meio da biblioteca yFinance e gera um relatório consolidado da sua carteira de investimentos, proporcionando uma visão abrangente das posições atuais e do desempenho dos ativos.

## Instalação

1. Clone o repositório: `git clone https://github.com/lfvelosoh/InvestorTracker`
2. Entre no diretório do projeto: `cd InvestorTracker`
3. Instale as dependências: `pip install -r requirements.txt`

## Uso

1. Execute o arquivo `menu.bat` disponível na pasta raiz.
2. Através da opção `Criar Pastas`, realize a criação dos diretórios necessários para a execução do código.
3. Insira nos diretórios criados `./relatorios_mensais` e `./relatorios_anuais` os relatórios mensais e anuais que podem ser extraídos na [Área do Investidor B3](https://www.investidor.b3.com.br/login).
4. Selecione a opção `Renomear Arquivos` para organizar os arquivos incluídos por data.
5. Selecione a opção `Consolidar Carteira` para gerar o relatório final e o consolidado na tela.
* Todos os arquivos gerados serão salvos no caminho `./resultados`.

## Recursos Futuros

- [ ] Leitura e tratamento de relatórios anuais para facilitar o preenchimento da da declaração de IR
- [ ] Scrap com dados de Ações e FIIs para analise através de parametros pré-definidos pelo investidor
- [ ] Scrap com atualização semanal de proventos recebidos
- [ ] Envio de e-mails com resumo de informações da carteira

## Links

- [yFinance](https://github.com/ranaroussi/yfinance)
