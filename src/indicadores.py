"""
indicadores.py
--------------
Cálculo dos indicadores de relacionamento a partir da base consolidada.
"""

from __future__ import annotations

import pandas as pd

COLUNAS_PRODUTO = ["CONTA_CORRENTE", "CARTAO", "CREDITO", "INVESTIMENTO", "CONSORCIO", "SEGURO"]


def calcular_qtd_produtos(df: pd.DataFrame) -> pd.Series:
    """Total de produtos ativos ('S') por associado."""
    return (df[COLUNAS_PRODUTO] == "S").sum(axis=1)


def calcular_tempo_relacionamento_anos(df: pd.DataFrame) -> pd.Series:
    """
    Tempo de relacionamento em anos = Data Atual - Data Associação.
    Datas de associação futuras (inconsistência de origem, ver FLAG_DATA_FUTURA)
    são tratadas com teto na data de hoje para não gerar tempo negativo.
    """
    hoje = pd.Timestamp.today().normalize()
    data_associacao_ajustada = df["DATA_ASSOCIACAO"].clip(upper=hoje)
    dias = (hoje - data_associacao_ajustada).dt.days
    return (dias / 365.25).round(2)


def calcular_faixa_renda(df: pd.DataFrame) -> pd.Series:
    bins = [-float("inf"), 3000, 8000, 15000, float("inf")]
    labels = [
        "Até R$ 3.000",
        "R$ 3.001 a R$ 8.000",
        "R$ 8.001 a R$ 15.000",
        "Acima de R$ 15.000",
    ]
    return pd.cut(df["RENDA_MENSAL"], bins=bins, labels=labels)


def adicionar_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["QTD_PRODUTOS"] = calcular_qtd_produtos(df)
    df["TEMPO_RELACIONAMENTO_ANOS"] = calcular_tempo_relacionamento_anos(df)
    df["FAIXA_RENDA"] = calcular_faixa_renda(df)
    return df
