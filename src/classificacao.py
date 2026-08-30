"""
classificacao.py
-----------------
Regra de classificação dos associados em 4 perfis:
Inicial, Em Desenvolvimento, Maduro, Engajado.

Metodologia
-----------
1. Calcula-se um ÍNDICE DE ENGAJAMENTO (0 a 100), combinando três sinais de
   uso normalizados por percentil dentro da própria base:
      - SALDO_MEDIO       (peso 35%)
      - PIX_MENSAL        (peso 25%)
      - COMPRAS_CARTAO    (peso 40%, maior peso por refletir uso recorrente/transacional)
   Cada variável é convertida em percentil (rank 0-100) antes de combinar,
   para que escalas diferentes (R$ x quantidade) não distorçam o índice.

2. Classificação, aplicada nesta ordem de prioridade:

   a) ENGAJADO: índice de engajamento no quartil superior (>= percentil 75)
      E diversificação de produtos (QTD_PRODUTOS >= 4)
      E relacionamento consolidado (TEMPO_RELACIONAMENTO_ANOS >= 2).
      -> Captura "alta utilização + diversificação + relacionamento
         consolidado", conforme os critérios do desafio. Tem prioridade
         sobre "Maduro" porque um cliente de alto uso deve ser destacado
         mesmo que também atenda aos critérios de maduro.

   b) MADURO: QTD_PRODUTOS >= 4 E TEMPO_RELACIONAMENTO_ANOS > 3
      E SALDO_MEDIO acima da mediana da base.

   c) INICIAL: QTD_PRODUTOS <= 1 E TEMPO_RELACIONAMENTO_ANOS < 2
      E índice de engajamento abaixo da mediana (baixa movimentação).

   d) EM DESENVOLVIMENTO: todos os demais casos (inclui o miolo da base:
      2-3 produtos, relacionamento crescente, uso moderado).

A ordem de prioridade evita ambiguidade quando um associado atende a mais
de uma regra simultaneamente.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def calcular_indice_engajamento(df: pd.DataFrame) -> pd.Series:
    pct_saldo = df["SALDO_MEDIO"].rank(pct=True) * 100
    pct_pix = df["PIX_MENSAL"].rank(pct=True) * 100
    pct_compras = df["COMPRAS_CARTAO"].rank(pct=True) * 100

    indice = 0.35 * pct_saldo + 0.25 * pct_pix + 0.40 * pct_compras
    return indice.round(1)


def classificar_associados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["INDICE_ENGAJAMENTO"] = calcular_indice_engajamento(df)

    p75_engajamento = df["INDICE_ENGAJAMENTO"].quantile(0.75)
    mediana_engajamento = df["INDICE_ENGAJAMENTO"].median()
    mediana_saldo = df["SALDO_MEDIO"].median()

    condicoes = [
        # a) Engajado
        (df["INDICE_ENGAJAMENTO"] >= p75_engajamento)
        & (df["QTD_PRODUTOS"] >= 4)
        & (df["TEMPO_RELACIONAMENTO_ANOS"] >= 2),
        # b) Maduro
        (df["QTD_PRODUTOS"] >= 4)
        & (df["TEMPO_RELACIONAMENTO_ANOS"] > 3)
        & (df["SALDO_MEDIO"] > mediana_saldo),
        # c) Inicial
        (df["QTD_PRODUTOS"] <= 1)
        & (df["TEMPO_RELACIONAMENTO_ANOS"] < 2)
        & (df["INDICE_ENGAJAMENTO"] < mediana_engajamento),
    ]
    escolhas = ["Engajado", "Maduro", "Inicial"]

    df["CLASSIFICACAO"] = np.select(condicoes, escolhas, default="Em Desenvolvimento")
    return df
