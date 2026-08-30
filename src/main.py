from __future__ import annotations

import pandas as pd
import os

from etl import executar_etl
from indicadores import adicionar_indicadores
from classificacao import classificar_associados

SAIDA_PATH = "data/processed/base_consolidada.xlsx"


def main() -> pd.DataFrame:
    print("1/4 - Carregando e tratando bases brutas...")
    df = executar_etl()
    print(f"      -> {len(df)} associados consolidados.")

    print("2/4 - Calculando indicadores...")
    df = adicionar_indicadores(df)

    print("3/4 - Classificando associados...")
    df = classificar_associados(df)

    print("4/4 - Salvando base tratada em", SAIDA_PATH)
    os.makedirs(os.path.dirname(SAIDA_PATH), exist_ok=True)
    df.to_excel(SAIDA_PATH, index=False)

    print("\nResumo da classificação:")
    print(df["CLASSIFICACAO"].value_counts())
    print("\nResumo por faixa de renda:")
    print(df["FAIXA_RENDA"].value_counts())
    print("\nAssociados com data de associação futura (inconsistência de origem):",
          df["FLAG_DATA_FUTURA"].sum())

    return df


if __name__ == "__main__":
    main()
