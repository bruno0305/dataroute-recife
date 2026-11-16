"""
CAMADA BRONZE — Coleta e Ingestão.   Responsável: F2 | Aprovador: F1

Regras da camada:
- Os CSVs originais do Portal Dados Abertos do Recife ficam em data/raw
  EXATAMENTE como baixados (nunca editar à mão, nunca sobrescrever).
- Nome do arquivo: <base>_<ano>.csv  (ex.: sinistros_2021.csv).
- Esta camada só LÊ e INSPECIONA (volumetria, colunas, memória). Nenhuma limpeza.

Baseline do F1: inventário + volumetria automática. O F2 complementa com o
download documentado (URLs em FONTES) e o Dicionário de Dados.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import BRONZE_DIR, PREFIXO_SINISTROS
from src.utils import ler_csv_robusto, log, memoria_mb

# Conjunto oficial: "Chamados de Sinistros (Acidentes) de Trânsito com e sem vítimas
# 2015 a 2024" — CTTU / Portal de Dados Abertos do Recife (licença ODbL).
# https://dados.recife.pe.gov.br/dataset/acidentes-de-transito-com-e-sem-vitimas
# Os arquivos em data/raw são cópias byte a byte destes recursos (baixados em 15/11/2026).
_BASE = "https://dados.recife.pe.gov.br/dataset/fdd001d5-05ba-46cd-9edf-5c5a6b58351f/resource"
FONTES: dict[str, str] = {
    "sinistros_2015.csv": f"{_BASE}/58816e1f-18bc-4335-82bf-80ff080cb0e5/download/acidentes-de-transito-2015.csv",
    "sinistros_2016.csv": f"{_BASE}/edc820d6-0f01-4fd2-b8a4-5a8c95f7e743/download/acidentes-de-transito-2016.csv",
    "sinistros_2017.csv": f"{_BASE}/d364e034-7e00-41a7-b557-0b16c21814e7/download/acidentes-de-transito-2017.csv",
    "sinistros_2018.csv": f"{_BASE}/a7b72334-9229-4e52-a6cb-8006de4942e3/download/acidentes-de-transito-2018.csv",
    "sinistros_2019.csv": f"{_BASE}/c9fe4a98-0f61-4e81-9c4b-a22f8dc6f1a2/download/acidentes-de-transito-2019.csv",
    "sinistros_2020.csv": f"{_BASE}/b2594588-2aa8-42c4-b96d-246102ecde3c/download/acidentes-de-transito-2020.csv",
    "sinistros_2021.csv": f"{_BASE}/31ee35d9-6f8e-4694-9492-efe96e902b07/download/acidentes-de-transito-2021.csv",
    "sinistros_2022.csv": f"{_BASE}/c2281788-2e8c-472c-8812-67c4f85e9272/download/acidentes-de-transito-2022.csv",
    "sinistros_2023.csv": f"{_BASE}/dbb9165a-7539-4fdd-943a-acffe12df3e0/download/acidentes-de-transito-2023.csv",
    "sinistros_2024.csv": f"{_BASE}/87ac4237-f5f9-44d2-bcf1-927aaa0a2d31/download/acidentes-de-transito-2024.csv",
}


def listar_arquivos(prefixo: str = PREFIXO_SINISTROS) -> list[Path]:
    return sorted(BRONZE_DIR.glob(f"{prefixo}*.csv"))


def inspecionar(arquivos: list[Path]) -> pd.DataFrame:
    """Gera a tabela de volumetria bruta (vai para a Seção 4 do relatório)."""
    linhas = []
    for arq in arquivos:
        df = ler_csv_robusto(arq)
        linhas.append({
            "arquivo": arq.name,
            "linhas": len(df),
            "colunas": df.shape[1],
            "memoria_mb": memoria_mb(df),
            "encoding": df.attrs.get("encoding"),
            "separador": df.attrs.get("sep"),
            "tamanho_disco_mb": round(arq.stat().st_size / 1024 ** 2, 2),
        })
    return pd.DataFrame(linhas)


def run() -> dict:
    arquivos = listar_arquivos()
    volumetria = inspecionar(arquivos) if arquivos else pd.DataFrame()
    total = int(volumetria["linhas"].sum()) if not volumetria.empty else 0
    log.info("BRONZE: %d arquivos, %d linhas brutas", len(arquivos), total)
    return {"arquivos": arquivos, "volumetria": volumetria, "linhas_brutas": total}
