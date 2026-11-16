"""Utilitários compartilhados por todas as camadas (mantidos pelo F1)."""
from __future__ import annotations

import csv
import logging
import re
import unicodedata
from pathlib import Path

import pandas as pd

from src.config import ENCODINGS_ENTRADA, ENCODING_SAIDA, SEP_SAIDA

log = logging.getLogger("dataroute")


def configurar_log(nivel: int = logging.INFO) -> None:
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )


def ler_csv_robusto(caminho: Path, **kwargs) -> pd.DataFrame:
    """
    Lê CSVs de portais governamentais tratando os ruídos mais comuns:
    - encoding variável (UTF-8 x Latin-1)  -> Veracidade dos 5 Vs
    - separador variável (';' ou ',')
    Todas as colunas entram como texto; a tipagem é feita na Silver (F3).
    """
    ultimo_erro: Exception | None = None
    for enc in ENCODINGS_ENTRADA:
        try:
            with open(caminho, encoding=enc) as f:
                amostra = f.read(4096)
            try:
                sep = csv.Sniffer().sniff(amostra, delimiters=";,|\t").delimiter
            except csv.Error:
                sep = ";" if amostra.count(";") > amostra.count(",") else ","
            df = pd.read_csv(caminho, sep=sep, encoding=enc, dtype=str,
                             low_memory=False, **kwargs)
            df.attrs["encoding"] = enc
            df.attrs["sep"] = sep
            log.info("Lido %s (%s, sep='%s'): %d linhas x %d colunas",
                     caminho.name, enc, sep, len(df), df.shape[1])
            return df
        except UnicodeDecodeError as e:
            ultimo_erro = e
    raise ValueError(f"Não foi possível ler {caminho.name}: {ultimo_erro}")


def salvar_csv(df: pd.DataFrame, caminho: Path) -> Path:
    """Escrita padronizada: UTF-8, separador ',', sem índice."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, sep=SEP_SAIDA, encoding=ENCODING_SAIDA, index=False)
    log.info("Salvo %s: %d linhas", caminho.name, len(df))
    return caminho


def snake_case(texto: str) -> str:
    """'Natureza Acidente' -> 'natureza_acidente'; remove acentos."""
    texto = remover_acentos(str(texto)).strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Padroniza categorias (bairros, clima...): sem acento, MAIÚSCULO, espaços únicos."""
    return (serie.astype("string")
                 .str.strip()
                 .map(lambda s: remover_acentos(s) if isinstance(s, str) else s)
                 .str.upper()
                 .str.replace(r"\s+", " ", regex=True))


def memoria_mb(df: pd.DataFrame) -> float:
    return round(df.memory_usage(deep=True).sum() / 1024 ** 2, 2)
