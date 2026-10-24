# 📊 DataScope — Internet Access Analytics

### 🚀 Demonstração online

👉 [Acessar o DataScope — Dashboard Interativo](https://datascope-lucolivbr.streamlit.app/)

Dashboard interativo para explorar a evolução do uso da internet no Brasil, Argentina e Chile, utilizando dados públicos do Banco Mundial.

![Dashboard DataScope](assets/dashboard.png)

O projeto combina coleta de dados via API, tratamento com Python e Pandas, armazenamento em SQLite, consultas SQL e visualização interativa com Streamlit.

## Funcionalidades

- Coleta de dados reais da API do Banco Mundial.
- Análise histórica do percentual da população que utiliza a internet.
- Comparação entre Brasil, Argentina e Chile.
- Filtros interativos por país e ano.
- Ranking e indicadores calculados a partir dos dados.
- Insights descritivos automáticos.
- Exportação dos dados filtrados em CSV.

## Tecnologias

- **Python** — processamento e integração.
- **Pandas** — manipulação dos dados.
- **SQLite / SQL** — armazenamento e consultas.
- **Streamlit** — dashboard interativo.
- **Matplotlib** — geração do gráfico estático.
- **Requests** — integração com a API.

## Como executar

Recomendado: Python 3.12.

Clone o repositório e, na pasta do projeto, instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Para atualizar os dados a partir da API e criar o banco SQLite:

```bash
python main.py
python analise_sql.py
```

Inicie o dashboard:

```bash
python -m streamlit run app.py
```

A aplicação será aberta localmente no navegador.

## Fonte dos dados

**Banco Mundial — World Development Indicators**

Indicador: `IT.NET.USER.ZS` — indivíduos que utilizam a internet (% da população).

Período coletado: 2000 a 2024, conforme disponibilidade dos dados.

API: https://api.worldbank.org/v2/

## Exemplo de resultado

Na comparação de 2024:

| País | População que utiliza a internet |
|---|---:|
| Chile | 95,59% |
| Argentina | 89,67% |
| Brasil | 84,46% |

O Chile apresentou o maior percentual entre os três países, ficando 11,13 pontos percentuais acima do Brasil.

Esses resultados são descritivos e não demonstram relações de causa e efeito.

## Objetivo

Projeto de portfólio desenvolvido para praticar conceitos de ciência de dados, integração com APIs, análise exploratória, SQL e desenvolvimento de dashboards interativos.

## Próximas melhorias

- Ampliar a cobertura de indicadores.
- Testar a coleta da API com respostas simuladas.
- Acrescentar indicadores com a mesma validação e cobertura de testes.
## Qualidade dos dados e testes

O dashboard lê o snapshot CSV versionado. O conteúdo do arquivo integra a chave do cache: atualizar o CSV invalida os dados em cache. O banco SQLite é uma saída da análise, não uma fonte oculta que pode divergir do CSV.

`pipeline.py` valida colunas, país, ano inteiro, percentuais finitos entre 0 e 100 e unicidade por país/ano. Dados inválidos são rejeitados com a linha indicada. A consulta usa parâmetros SQL e encontra o último ano comum aos países selecionados, sem presumir sempre três países.

```bash
python -m unittest discover -s tests -v
python analise_sql.py
```

Os nove testes usam somente a biblioteca padrão, sem rede: snapshot real, seleção variável, anos sem correspondência, duplicação, dados inválidos e preservação da base anterior quando a validação falha. O CI repete os testes e executa a análise SQL. Não testa visualmente o Streamlit nem a disponibilidade da API externa.

`analise_sql.py` funciona de qualquer diretório, resolvendo os caminhos a partir do projeto. A coleta em `main.py` ainda deve ser executada na raiz. Depois da coleta, rode a análise para validar a base. O período 2000–2024 é o recorte do snapshot, não uma promessa de dados em tempo real.
