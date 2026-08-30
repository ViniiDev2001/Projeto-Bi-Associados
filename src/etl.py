from __future__ import annotations

import unicodedata
import pandas as pd

RAW_PATH = "data/raw/teste_bi_base_crua.xlsx"

# Mapeamento de variações de cidade -> nome canônico
CIDADE_CANONICA = {
    "pato branco": "Pato Branco",
    "p. branco": "Pato Branco",
    "cascavel": "Cascavel",
    "chapeco": "Chapecó",
    "toledo": "Toledo",
    "maringa": "Maringá",
}


def _strip_accents_lower(texto: str) -> str:
    texto = str(texto).strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return texto


def carregar_bases(caminho: str = RAW_PATH) -> dict[str, pd.DataFrame]:
    """Carrega as 3 abas da planilha bruta."""
    xls = pd.ExcelFile(caminho)
    return {
        "associados": pd.read_excel(xls, "Associados"),
        "produtos": pd.read_excel(xls, "Produtos"),
        "movimentacao": pd.read_excel(xls, "Movimentacao"),
    }


def tratar_associados(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Duplicados exatos e duplicados de CHAVE
    dup_exatos = df.duplicated().sum()
    if dup_exatos:
        df = df.drop_duplicates()
    dup_chave = df.duplicated(subset=["CHAVE"]).sum()
    if dup_chave:
        df = df.drop_duplicates(subset=["CHAVE"], keep="first")

    # Padronização de texto
    df["NOME"] = df["NOME"].astype(str).str.strip().str.title()
    df["CIDADE_CHAVE_NORMALIZADA"] = df["CIDADE"].apply(_strip_accents_lower)
    df["CIDADE"] = df["CIDADE_CHAVE_NORMALIZADA"].map(CIDADE_CANONICA).fillna(
        df["CIDADE"].astype(str).str.strip().str.title()
    )
    df = df.drop(columns=["CIDADE_CHAVE_NORMALIZADA"])

    # Renda nula -> mediana por agência
    mediana_por_agencia = df.groupby("AGENCIA")["RENDA_MENSAL"].transform("median")
    df["RENDA_MENSAL"] = df["RENDA_MENSAL"].fillna(mediana_por_agencia)
    # fallback: se ainda restar nulo (agência inteira nula), usa mediana geral
    df["RENDA_MENSAL"] = df["RENDA_MENSAL"].fillna(df["RENDA_MENSAL"].median())

    # Inconsistência: data de associação no futuro
    hoje = pd.Timestamp.today().normalize()
    df["FLAG_DATA_FUTURA"] = df["DATA_ASSOCIACAO"] > hoje

    return df


def tratar_produtos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["CHAVE"], keep="first")

    colunas_produto = ["CONTA_CORRENTE", "CARTAO", "CREDITO", "INVESTIMENTO", "CONSORCIO", "SEGURO"]
    for col in colunas_produto:
        df[col] = df[col].astype(str).str.strip().str.upper()
        df[col] = df[col].where(df[col].isin(["S", "N"]), "N")  # valor inesperado -> N

    return df


def tratar_movimentacao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["CHAVE"], keep="first")

    colunas_numericas = ["SALDO_MEDIO", "PIX_MENSAL", "COMPRAS_CARTAO"]
    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())
        # não permitir valores negativos (inconsistência de origem)
        df[col] = df[col].clip(lower=0)

    return df


def consolidar(bases_tratadas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une as três bases pela CHAVE (left join a partir de Associados)."""
    df = bases_tratadas["associados"].merge(
        bases_tratadas["produtos"], on="CHAVE", how="left"
    ).merge(
        bases_tratadas["movimentacao"], on="CHAVE", how="left"
    )
    return df


def executar_etl(caminho_bruto: str = RAW_PATH) -> pd.DataFrame:
    brutas = carregar_bases(caminho_bruto)
    tratadas = {
        "associados": tratar_associados(brutas["associados"]),
        "produtos": tratar_produtos(brutas["produtos"]),
        "movimentacao": tratar_movimentacao(brutas["movimentacao"]),
    }
    return consolidar(tratadas)
