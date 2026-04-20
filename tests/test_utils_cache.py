# test_utils_cache.py — Testa o sistema de cache CSV para municípios.
# Usa tmp_path do pytest para isolamento: nenhum arquivo CSV real é criado.
# Cobre: get_municipios_df(), refresh_municipios_cache(), _get_credentials().

import logging
import sys
from unittest.mock import MagicMock

import pandas as pd

import utils_cache


def _df_municipios_fake():
    return pd.DataFrame({
        "id_municipio": ["3143906", "3143807"],
        "nome":         ["Muriaé",  "Murici"],
        "sigla_uf":     ["MG",      "AL"],
        "nome_uf":      ["Minas Gerais", "Alagoas"],
    })


# =============================================================================
# get_municipios_df()
# =============================================================================

class TestGetMunicipiosDf:

    def test_cache_carrega_csv_se_arquivo_existe(self, tmp_path, monkeypatch):
        # ARRANGE — CSV já existe no disco (simulado via tmp_path)
        csv_path = tmp_path / "municipios.csv"
        _df_municipios_fake().to_csv(csv_path, index=False)
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))

        bd_mock_chamado = []
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: bd_mock_chamado.append(1) or _df_municipios_fake()
        )
        # ACT
        df = utils_cache.get_municipios_df()
        # ASSERT — leu do CSV, não chamou BigQuery
        assert not df.empty
        assert len(bd_mock_chamado) == 0

    def test_cache_baixa_bigquery_e_salva_csv_se_arquivo_nao_existe(self, tmp_path, monkeypatch):
        # ARRANGE — CSV não existe ainda
        csv_path = tmp_path / "municipios.csv"
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: _df_municipios_fake()
        )
        # ACT
        df = utils_cache.get_municipios_df()
        # ASSERT — retornou dados e criou o CSV
        assert not df.empty
        assert csv_path.exists()

    def test_cache_csv_criado_contem_colunas_esperadas(self, tmp_path, monkeypatch):
        # ARRANGE
        csv_path = tmp_path / "municipios.csv"
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: _df_municipios_fake()
        )
        # ACT
        utils_cache.get_municipios_df()
        df_salvo = pd.read_csv(csv_path)
        # ASSERT
        for col in ["id_municipio", "nome", "sigla_uf", "nome_uf"]:
            assert col in df_salvo.columns

    def test_cache_segunda_chamada_nao_chama_bigquery(self, tmp_path, monkeypatch):
        # ARRANGE — primeira chamada baixa e salva; segunda deve usar CSV
        csv_path = tmp_path / "municipios.csv"
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))

        chamadas_bq = []
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: chamadas_bq.append(1) or _df_municipios_fake()
        )
        # ACT
        utils_cache.get_municipios_df()  # 1ª — baixa BigQuery, salva CSV
        utils_cache.get_municipios_df()  # 2ª — usa CSV
        # ASSERT — BigQuery chamado apenas uma vez
        assert len(chamadas_bq) == 1


# =============================================================================
# refresh_municipios_cache()
# =============================================================================

class TestRefreshMunicipiosCache:

    def test_refresh_sobrescreve_cache_existente(self, tmp_path, monkeypatch):
        # ARRANGE — CSV antigo já existe
        csv_path = tmp_path / "municipios.csv"
        _df_municipios_fake().to_csv(csv_path, index=False)
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))

        df_novo = pd.DataFrame({
            "id_municipio": ["9999999"],
            "nome":         ["Cidade Nova"],
            "sigla_uf":     ["ZZ"],
            "nome_uf":      ["Estado Novo"],
        })
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: df_novo
        )
        # ACT
        utils_cache.refresh_municipios_cache()
        df_recarregado = pd.read_csv(csv_path)
        # ASSERT — CSV substituído com dados novos
        assert df_recarregado.iloc[0]["nome"] == "Cidade Nova"

    def test_refresh_chama_bigquery_mesmo_com_csv_existente(self, tmp_path, monkeypatch):
        # ARRANGE
        csv_path = tmp_path / "municipios.csv"
        _df_municipios_fake().to_csv(csv_path, index=False)
        monkeypatch.setattr("utils_cache.CACHE_FILE", str(csv_path))

        chamadas_bq = []
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: chamadas_bq.append(1) or _df_municipios_fake()
        )
        # ACT
        utils_cache.refresh_municipios_cache()
        # ASSERT — forçou BigQuery independente do CSV existir
        assert len(chamadas_bq) == 1


# =============================================================================
# _get_credentials() — logging estruturado
# =============================================================================

def _secrets_raising(exc):
    """Cria mock de st.secrets que levanta exc ao ser subscrito."""
    mock = MagicMock()
    mock.__getitem__ = MagicMock(side_effect=exc)
    return mock


class TestGetCredentialsLogging:

    def test_get_credentials_loga_debug_quando_sem_secrets(
        self, monkeypatch, caplog
    ):
        # ARRANGE — KeyError: secrets não configurados (modo local esperado)
        monkeypatch.setattr(
            sys.modules["streamlit"], "secrets",
            _secrets_raising(KeyError("gcp"))
        )
        monkeypatch.setattr("utils_cache._credentials", lambda: None)

        # ACT
        with caplog.at_level(logging.DEBUG, logger="utils_cache"):
            utils_cache._get_credentials()

        # ASSERT — debug logado, sem warnings
        debug_msgs = [r.message for r in caplog.records if r.levelno == logging.DEBUG]
        assert any("modo local" in m for m in debug_msgs)
        assert not any(r.levelno >= logging.WARNING for r in caplog.records)

    def test_get_credentials_loga_warning_quando_excecao_inesperada(
        self, monkeypatch, caplog
    ):
        # ARRANGE — RuntimeError: exceção não esperada
        monkeypatch.setattr(
            sys.modules["streamlit"], "secrets",
            _secrets_raising(RuntimeError("falha inesperada"))
        )
        monkeypatch.setattr("utils_cache._credentials", lambda: None)

        # ACT
        with caplog.at_level(logging.WARNING, logger="utils_cache"):
            utils_cache._get_credentials()

        # ASSERT — warning com tipo da exceção
        warning_msgs = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert len(warning_msgs) >= 1
        assert any("RuntimeError" in m for m in warning_msgs)

    def test_get_credentials_nao_loga_dados_sensiveis(
        self, monkeypatch, caplog
    ):
        # ARRANGE — exceção com conteúdo sensível na mensagem
        mensagem_sensivel = "private_key=abc123secret"
        monkeypatch.setattr(
            sys.modules["streamlit"], "secrets",
            _secrets_raising(RuntimeError(mensagem_sensivel))
        )
        monkeypatch.setattr("utils_cache._credentials", lambda: None)

        # ACT
        with caplog.at_level(logging.DEBUG, logger="utils_cache"):
            utils_cache._get_credentials()

        # ASSERT — nenhum record vaza o dado sensível
        for record in caplog.records:
            assert "abc123secret" not in record.message
            assert mensagem_sensivel not in record.message
            assert "private_key" not in record.message
