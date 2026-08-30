"""
main.py
-------
Orquestra o pipeline completo:
  1. Carrega e trata as bases brutas (etl.py)
  2. Consolida pela CHAVE
  3. Calcula indicadores (indicadores.py)
  4. Classifica os associados (classificacao.py)
  5. Salva a base final tratada em data/processed/

Uso:
    python src/main.py
"""

from __future__ import annotations

import os
import pandas as pd

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
