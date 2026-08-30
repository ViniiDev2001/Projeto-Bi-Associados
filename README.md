# Desafio Técnico - Assistente de BI

**Repositório:** https://github.com/ViniiDev2001/Projeto-Bi-Associados

## Objetivo do Projeto

Solução de Business Intelligence que consolida três bases de dados de
associados (cadastro, produtos contratados e movimentação financeira),
trata problemas de qualidade de dados, calcula indicadores de
relacionamento e classifica cada associado em um perfil de
relacionamento, servindo de base para um dashboard executivo em Power BI.

## Tecnologias Utilizadas

- **Python 3** (pandas, numpy, openpyxl) - tratamento, consolidação,
 cálculo de indicadores e classificação.
- **Excel** - formato de origem e de saída da base tratada.
- **Power BI** - camada de visualização (ver seção "Dashboard").
- **Git/GitHub** - versionamento do código.

## Estrutura do Projeto

```
projeto_bi/
├── data/
│ ├── raw/ # base bruta original (não editar)
│ │ └── teste_bi_base_crua.xlsx
│ └── processed/ # saída do pipeline
│ └── base_consolidada.xlsx
├── src/
│ ├── etl.py # carga + tratamento + consolidação
│ ├── indicadores.py # cálculo dos indicadores
│ ├── classificacao.py # regra de classificação
│ └── main.py # orquestração do pipeline
├── docs/
│ └── dashboard_especificacao.md
├── requirements.txt
└── README.md
```

## Passo a Passo para Execução

```bash
# 0. Clonar o repositório
git clone https://github.com/ViniiDev2001/Projeto-Bi-Associados.git
cd Projeto-Bi-Associados

# 1. Criar e ativar um ambiente virtual (opcional, recomendado)
python3 -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar o pipeline (a partir da raiz do projeto)
cd src
python main.py
```

O script gera `data/processed/base_consolidada.xlsx`, que é a base de
entrada para o Power BI.

## Tratamento e Qualidade dos Dados

| Problema encontrado | Tratamento aplicado |
|---|---|
| Cidade com 3 grafias diferentes (`Pato Branco`, `P. Branco`, `PATO BRANCO`) | Normalização para um nome canônico único |
| 12 registros de `RENDA_MENSAL` nulos | Preenchidos com a **mediana da própria agência** |
| 37 registros com `DATA_ASSOCIACAO` no futuro | Mantidos na base (não se inventa dado), mas sinalizados em `FLAG_DATA_FUTURA`; usados com teto na data atual apenas no cálculo do indicador de tempo de relacionamento |
| Valores fora do padrão S/N em Produtos | Qualquer valor diferente de "S" é tratado como "N" |
| Duplicados (exatos ou de CHAVE) | Removidos, mantendo a primeira ocorrência |

## Indicadores Criados

- **QTD_PRODUTOS**: total de produtos com valor "S" por associado.
- **TEMPO_RELACIONAMENTO_ANOS**: `(data atual - data de associação) / 365.25`.
- **FAIXA_RENDA**: Até R$3.000 / R$3.001-8.000 / R$8.001-15.000 / Acima de R$15.000.
- **INDICE_ENGAJAMENTO** (0-100): combinação ponderada dos percentis de
 `SALDO_MEDIO` (35%), `PIX_MENSAL` (25%) e `COMPRAS_CARTAO` (40%). Usar
 percentil (e não o valor bruto) evita que a diferença de escala entre
 R$ e quantidade distorça o índice.

## Regras de Classificação

Aplicadas nesta ordem de prioridade (a primeira regra que casar decide a
classificação):

1. **Engajado** - Índice de engajamento no quartil superior (top 25% da
 base) **e** 4+ produtos **e** 2+ anos de relacionamento. Representa
 alta utilização + diversificação + relacionamento consolidado.
2. **Maduro** - 4+ produtos **e** mais de 3 anos de relacionamento **e**
 saldo médio acima da mediana da base.
3. **Inicial** - até 1 produto **e** menos de 2 anos de relacionamento
 **e** índice de engajamento abaixo da mediana.
4. **Em Desenvolvimento** - todos os demais casos (2-3 produtos,
 relacionamento em crescimento, uso moderado).

A prioridade evita ambiguidade quando um associado se encaixaria em mais
de uma regra ao mesmo tempo (ex.: um "Engajado" que também teria muitos
produtos e tempo de casa suficiente para ser "Maduro").

Resultado na base fornecida:

| Classificação | Qtd. Associados |
|---|---|
| Em Desenvolvimento | 859 |
| Engajado | 63 |
| Maduro | 57 |
| Inicial | 21 |

## Dashboard Power BI

A base `base_consolidada.xlsx` já contém todas as colunas necessárias
para montar as 4 páginas pedidas (Visão Geral, Relacionamento,
Classificação, Oportunidades). Ver `docs/dashboard_especificacao.md`
para o detalhamento de cada página, visual sugerido e fórmulas DAX de
apoio.

## Sobre os Dados

Todos os dados utilizados são fictícios, gerados exclusivamente para
fins de avaliação técnica.
