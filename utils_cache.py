"""
utils_cache.py - Cache CSV local para dados estáticos de municípios.

DECISÃO DE ARQUITETURA:
    Municípios brasileiros são 5.570 registros que raramente mudam.
    Cache local elimina custo e latência do BigQuery a cada busca.
    BigQuery continua sendo usado para emendas e população (dados dinâmicos).

    Para atualizar: chamar refresh_municipios_cache() manualmente.
"""

import pandas as pd
from pandas_gbq import read_gbq
from basedosdados.download.download import _credentials

from config import GCP_PROJECT_ID, GCP_LOCATION


def _get_credentials():
    """Retorna credenciais adequadas ao ambiente.

    Streamlit Cloud: Service Account via st.secrets.
    Local: OAuth via basedosdados (_credentials).
    """
    try:
        import streamlit as st
        from google.oauth2 import service_account
        sa_info = dict(st.secrets["gcp"]["service_account"])
        if isinstance(sa_info.get("type"), str):
            return service_account.Credentials.from_service_account_info(
                sa_info,
                scopes=["https://www.googleapis.com/auth/bigquery"],
            )
    except Exception:
        pass
    return _credentials()

CACHE_FILE = "data/municipios.csv"

_QUERY_MUNICIPIOS = """
SELECT
    id_municipio,
    nome,
    sigla_uf,
    nome_uf
FROM `basedosdados.br_bd_diretorios_brasil.municipio`
ORDER BY nome
"""


def _bd_read_sql(query: str) -> pd.DataFrame:
    """Wrapper sobre pandas_gbq.read_gbq com location explícita.

    basedosdados 2.0.x não passa location para pandas_gbq, que por sua vez
    deixa o campo vazio na requisição REST. O BigQuery rejeita location=""
    com 'Cannot parse as CloudRegion'. Passando location=GCP_LOCATION
    explicitamente contornamos o bug da lib.
    """
    return read_gbq(
        query,
        project_id=GCP_PROJECT_ID,
        location=GCP_LOCATION,
        credentials=_get_credentials(),
    )


def _baixar_do_bigquery() -> pd.DataFrame:
    """Baixa todos os municípios do BigQuery e retorna DataFrame."""
    return _bd_read_sql(_QUERY_MUNICIPIOS)


def get_municipios_df() -> pd.DataFrame:
    """
    Retorna DataFrame com todos os municípios brasileiros.

    Carrega do CSV local se existir; caso contrário baixa do BigQuery,
    salva em CACHE_FILE e retorna. Na segunda chamada usa o CSV (<1s).
    """
    try:
        return pd.read_csv(CACHE_FILE, dtype=str)
    except FileNotFoundError:
        df = _baixar_do_bigquery()
        df.to_csv(CACHE_FILE, index=False)
        return df


def refresh_municipios_cache() -> pd.DataFrame:
    """
    Força re-download do BigQuery e sobrescreve o CSV local.
    Usar quando os dados de municípios precisarem ser atualizados.
    """
    df = _baixar_do_bigquery()
    df.to_csv(CACHE_FILE, index=False)
    return df
