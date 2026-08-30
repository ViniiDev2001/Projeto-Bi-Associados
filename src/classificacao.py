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
