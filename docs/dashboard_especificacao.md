# Especificação do Dashboard Power BI

Fonte de dados: `data/processed/base_consolidada.xlsx` (uma linha por
associado, já tratada e com indicadores/classificação calculados).

> Nota: este arquivo especifica o que construir em cada página; a
> montagem visual precisa ser feita no Power BI Desktop, que roda em
> ambiente gráfico Windows/Mac.

## Página 1 — Visão Geral

Cartões (Cards):
- **Total de Associados** = `COUNTROWS(base_consolidada)`
- **Renda Média** = `AVERAGE(base_consolidada[RENDA_MENSAL])`
- **Saldo Médio** = `AVERAGE(base_consolidada[SALDO_MEDIO])`
- **Produtos por Associado** = `AVERAGE(base_consolidada[QTD_PRODUTOS])`

## Página 2 — Relacionamento

- **Associados por Agência**: gráfico de barras, eixo `AGENCIA`, valor = contagem de `CHAVE`.
- **Associados por Cidade**: gráfico de barras ou mapa, eixo `CIDADE`.
- **Faixa de Renda**: gráfico de pizza/rosca ou barras, campo `FAIXA_RENDA`.
- **Tempo de Relacionamento**: histograma de `TEMPO_RELACIONAMENTO_ANOS`
  (agrupar em faixas: <1 ano, 1-2, 2-3, 3-5, 5+).

## Página 3 — Classificação

- Gráfico de pizza/rosca ou barras com `CLASSIFICACAO` (contagem e %).
- Cards com quantidade e % de cada categoria (Inicial, Em Desenvolvimento,
  Maduro, Engajado) — usar medida de % com `DIVIDE(COUNTROWS(...), [Total Associados])`.

## Página 4 — Oportunidades

Segmentações/tabelas para os três cenários pedidos no desafio:

- **Alta renda e poucos produtos**: filtro `FAIXA_RENDA IN {"R$ 8.001 a R$ 15.000", "Acima de R$ 15.000"}` e `QTD_PRODUTOS <= 1`.
- **Baixa utilização dos serviços**: `INDICE_ENGAJAMENTO` abaixo do percentil 25.
- **Potencial de crescimento**: `CLASSIFICACAO = "Em Desenvolvimento"` com `INDICE_ENGAJAMENTO` acima da mediana (já engajados, mas ainda com poucos produtos — bons candidatos a oferta de novos produtos).

Sugestão de medida DAX para o percentil 25 do índice de engajamento:

```
P25_Engajamento =
PERCENTILE.INC(base_consolidada[INDICE_ENGAJAMENTO], 0.25)
```
