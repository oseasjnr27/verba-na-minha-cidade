"""
conftest.py — Fixtures e mocks compartilhados por toda a suíte de testes.
Carregado pelo pytest ANTES de qualquer módulo do projeto.
Nunca chame APIs reais aqui.
"""

import os
import sys
from unittest.mock import MagicMock
import pytest
import pandas as pd

# ---------------------------------------------------------------------------
# Env vars de teste — devem vir antes de qualquer import do projeto,
# pois config.py chama validate_config() no momento do import.
# setdefault preserva chaves reais do .env quando já estiverem definidas.
# ---------------------------------------------------------------------------

os.environ.setdefault("GEMINI_API_KEY", "test-api-key")
os.environ.setdefault("GCP_PROJECT_ID", "test-project-id")

# ---------------------------------------------------------------------------
# Mock do Streamlit — deve vir ANTES de qualquer import do projeto,
# pois os decoradores @st.cache_data são aplicados no momento do import.
# ---------------------------------------------------------------------------

_st_mock = MagicMock()
_st_mock.cache_data = lambda ttl=None, **kw: (lambda f: f)  # passthrough
sys.modules["streamlit"] = _st_mock


# ---------------------------------------------------------------------------
# Mocks: IBGE
# ---------------------------------------------------------------------------

MOCK_IBGE_MUNICIPIO = {
    "id": "3143906",
    "nome": "Muriaé",
    "microrregiao": {
        "mesorregiao": {
            "UF": {"sigla": "MG"}
        }
    }
}


@pytest.fixture
def mock_ibge_municipio():
    return MOCK_IBGE_MUNICIPIO


# ---------------------------------------------------------------------------
# Mocks: BigQuery / Emendas
# ---------------------------------------------------------------------------

MOCK_EMENDAS = {
    "total_empenhado": 1_399_803.00,
    "total_pago": 1_049_852.25,
    "quantidade": 15,
    "parlamentares": ["Dep. João Silva", "Sen. Maria Santos"]
}


@pytest.fixture
def mock_emendas():
    return MOCK_EMENDAS


# ---------------------------------------------------------------------------
# Mocks: Google Gemini
# ---------------------------------------------------------------------------

MOCK_NARRATIVA = "Muriaé recebeu R$ 1,4 milhão em emendas parlamentares..."


@pytest.fixture
def mock_narrativa():
    return MOCK_NARRATIVA


# ---------------------------------------------------------------------------
# Proteção global: CACHE_FILE nunca aponta para o arquivo real durante testes.
# BUG #16: utils.bd e utils_cache.bd são o mesmo objeto — mockar um afeta o outro.
# Sem esta proteção, um mock de bd.read_sql pode escrever no CSV de produção.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def proteger_cache_real(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "utils_cache.CACHE_FILE",
        str(tmp_path / "municipios_test.csv")
    )


# ---------------------------------------------------------------------------
# Fixture: DataFrame de municípios (simula retorno do BigQuery)
# ---------------------------------------------------------------------------

def _df_municipios():
    return pd.DataFrame({
        "id_municipio": ["3143906", "3143807", "3304300"],
        "nome":         ["Muriaé",  "Murici",  "Nova Iguaçu"],
        "sigla_uf":     ["MG",      "AL",      "RJ"],
        "nome_uf":      ["Minas Gerais", "Alagoas", "Rio de Janeiro"],
    })


@pytest.fixture
def df_municipios():
    return _df_municipios()
