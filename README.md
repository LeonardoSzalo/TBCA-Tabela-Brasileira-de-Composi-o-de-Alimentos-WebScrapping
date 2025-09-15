# Web Scraper da Tabela Brasileira de Composição de Alimentos (TBCA)

![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)

Este projeto consiste em um web scraper desenvolvido em Python para extrair de forma automatizada todos os dados de composição nutricional de alimentos da Tabela Brasileira de Composição de Alimentos (TBCA).

## Utilidade do Projeto

A Tabela Brasileira de Composição de Alimentos (TBCA) é uma fonte de dados pública e de alta qualidade, porém o site oficial permite apenas a consulta manual, item por item. Não há uma opção para download em massa ou uma API pública para consumo dos dados.

Este scraper resolve esse problema ao automatizar a coleta, gerando um único arquivo **JSON** estruturado. O dataset gerado pode ser utilizado para:

* **Análise de Dados:** Realizar estudos e análises nutricionais em grande escala.
* **Desenvolvimento de Aplicações:** Servir como banco de dados para aplicativos de nutrição, saúde e fitness.
* **Pesquisa Científica:** Facilitar o acesso a dados para pesquisadores da área de alimentos e saúde.
* **Projetos de Machine Learning:** Treinar modelos para prever componentes nutricionais ou classificar alimentos.

## Estrutura do JSON de Saída

O script gera o arquivo `tbca_dados_completos.json`, que é uma lista de objetos, onde cada objeto representa um alimento com a seguinte estrutura:

```json
[
  {
    "codigo": "A001",
    "classe": "Cereais e derivados",
    "descricao": "Arroz, integral, cozido",
    "composicao_100g": [
      {
        "componente": "Umidade",
        "unidade": "%",
        "valor": "70.1"
      },
      {
        "componente": "Energia",
        "unidade": "kcal",
        "valor": "124"
      }
    ],
    "medidas_caseiras": [
      {
        "descricao_medida": "Colher de sopa cheia",
        "tamanho_medida": null,
        "gramas_equivalentes": 25.0,
        "composicao": {
          "Umidade": { "valor": "17.5", "unidade": "%" },
          "Energia": { "valor": "31", "unidade": "kcal" }
        }
      }
    ]
  }
]
```

## Clone o repositório

```
git clone [https://github.com/SeuUsuario/NomeDoRepositorio.git](https://github.com/SeuUsuario/NomeDoRepositorio.git)
cd NomeDoRepositorio
```
## Instale as dependências
```
pip install -r requirements.txt
```

## Execute o script
```
python webscrapping.py
```
