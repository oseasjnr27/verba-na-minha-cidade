# test_utils_apis.py — Testa funções de acesso a APIs externas em utils.py.
# Cobre: get_municipio_ibge(), get_municipios_por_uf(),
#        get_populacao_municipio(), get_resumo_emendas(),
#        get_emendas_municipio(), get_emendas_por_ano(),
#        get_emendas_por_area(), get_emendas_por_autor(),
#        get_dados_completos_municipio().
# Todas as APIs externas são mockadas — nenhuma chamada real ocorre.

import pandas as pd
from unittest.mock import MagicMock

from utils import (
    get_municipio_ibge,
    get_municipios_por_uf,
    get_populacao_municipio,
    get_resumo_emendas,
    get_emendas_municipio,
    get_emendas_por_ano,
    get_emendas_por_area,
    get_emendas_por_autor,
    get_dados_completos_municipio,
)

ID_MUN = "3143906"

_IBGE_RESPONSE = {
    "id": "3143906",
    "nome": "Muriaé",
    "microrregiao": {
        "nome": "Muriaé",
        "mesorregiao": {
            "nome": "Zona da Mata",
            "UF": {
                "sigla": "MG",
                "nome": "Minas Gerais",
                "regiao": {"nome": "Sudeste"},
            },
        },
    },
}


def _mock_requests_ok(json_data):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = json_data
    return resp


def _mock_requests_error():
    resp = MagicMock()
    resp.raise_for_status.side_effect = Exception("HTTP 500")
    return resp


def _df_populacao():
    return pd.DataFrame({"id_municipio": [ID_MUN], "ano": [2022], "populacao": [115423]})


def _df_resumo():
    return pd.DataFrame({
        "total_emendas": [42],
        "total_empenhado": [1_399_803.0],
        "total_pago": [1_049_852.0],
        "total_autores": [5],
        "total_areas": [3],
    })


def _df_emendas():
    return pd.DataFrame({
        "ano_emenda": [2023, 2022],
        "valor_empenhado": [500000.0, 899803.0],
        "valor_pago": [400000.0, 649852.0],
    })


def _df_por_ano():
    return pd.DataFrame({
        "ano": [2022, 2023],
        "valor_empenhado": [899803.0, 500000.0],
        "valor_pago": [649852.0, 400000.0],
        "quantidade": [25, 17],
    })


def _df_por_area():
    return pd.DataFrame({
        "area": ["Saúde", "Educação"],
        "valor_empenhado": [800000.0, 599803.0],
        "valor_pago": [600000.0, 449852.0],
        "quantidade": [20, 22],
    })


def _df_por_autor():
    return pd.DataFrame({
        "autor": ["Dep. João Silva", "Sen. Maria Santos"],
        "valor_empenhado": [900000.0, 499803.0],
        "valor_pago": [700000.0, 349852.0],
        "quantidade": [30, 12],
    })


# =============================================================================
# get_municipio_ibge
# =============================================================================

class TestGetMunicipioIbge:

    def test_retorna_dict_com_campos_corretos(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils.requests.get", lambda url, timeout: _mock_requests_ok(_IBGE_RESPONSE))
        # ACT
        resultado = get_municipio_ibge(ID_MUN)
        # ASSERT
        assert resultado["nome"] == "Muriaé"
        assert resultado["uf"] == "MG"
        assert resultado["uf_nome"] == "Minas Gerais"
        assert resultado["regiao"] == "Sudeste"

    def test_quando_api_falha_retorna_dict_vazio(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils.requests.get", lambda url, timeout: _mock_requests_error())
        # ACT
        resultado = get_municipio_ibge("id-invalido")
        # ASSERT
        assert resultado == {}


# =============================================================================
# get_municipios_por_uf
# =============================================================================

class TestGetMunicipiosPorUf:

    def test_retorna_lista_de_municipios(self, monkeypatch):
        # ARRANGE
        ibge_data = [{"id": "3143906", "nome": "Muriaé"}, {"id": "3143807", "nome": "Murici"}]
        monkeypatch.setattr("utils.requests.get", lambda url, timeout: _mock_requests_ok(ibge_data))
        # ACT
        resultado = get_municipios_por_uf("MG")
        # ASSERT
        assert len(resultado) == 2
        assert resultado[0]["nome"] == "Muriaé"

    def test_quando_api_falha_retorna_lista_vazia(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils.requests.get", lambda url, timeout: _mock_requests_error())
        # ACT
        resultado = get_municipios_por_uf("XX")
        # ASSERT
        assert resultado == []


# =============================================================================
# get_populacao_municipio
# =============================================================================

class TestGetPopulacaoMunicipio:

    def test_retorna_populacao_e_ano(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_populacao())
        # ACT
        resultado = get_populacao_municipio(ID_MUN)
        # ASSERT
        assert resultado["populacao"] == 115423
        assert resultado["ano_populacao"] == 2022

    def test_quando_bigquery_retorna_vazio_retorna_zeros(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: pd.DataFrame())
        # ACT
        resultado = get_populacao_municipio(ID_MUN)
        # ASSERT
        assert resultado["populacao"] == 0
        assert resultado["ano_populacao"] == 0

    def test_quando_bigquery_lanca_excecao_retorna_zeros(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_populacao_municipio(ID_MUN)
        # ASSERT
        assert resultado == {"populacao": 0, "ano_populacao": 0}


# =============================================================================
# get_resumo_emendas
# =============================================================================

class TestGetResumoEmendas:

    def test_retorna_resumo_com_totais(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_resumo())
        # ACT
        resultado = get_resumo_emendas(ID_MUN)
        # ASSERT
        assert resultado["total_emendas"] == 42
        assert resultado["total_empenhado"] == 1_399_803.0
        assert resultado["total_autores"] == 5

    def test_quando_bigquery_retorna_vazio_retorna_zeros(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: pd.DataFrame())
        # ACT
        resultado = get_resumo_emendas(ID_MUN)
        # ASSERT
        assert resultado["total_emendas"] == 0
        assert resultado["total_empenhado"] == 0

    def test_quando_bigquery_lanca_excecao_retorna_zeros(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_resumo_emendas(ID_MUN)
        # ASSERT
        assert resultado["total_emendas"] == 0


# =============================================================================
# get_emendas_municipio
# =============================================================================

class TestGetEmendasMunicipio:

    def test_retorna_dataframe_com_emendas(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_emendas())
        # ACT
        resultado = get_emendas_municipio(ID_MUN)
        # ASSERT
        assert not resultado.empty
        assert "valor_empenhado" in resultado.columns

    def test_quando_bigquery_lanca_excecao_retorna_dataframe_vazio(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_emendas_municipio(ID_MUN)
        # ASSERT
        assert resultado.empty


# =============================================================================
# get_emendas_por_ano
# =============================================================================

class TestGetEmendasPorAno:

    def test_retorna_dataframe_agrupado_por_ano(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_por_ano())
        # ACT
        resultado = get_emendas_por_ano(ID_MUN)
        # ASSERT
        assert not resultado.empty
        assert "ano" in resultado.columns

    def test_quando_bigquery_lanca_excecao_retorna_dataframe_vazio(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_emendas_por_ano(ID_MUN)
        # ASSERT
        assert resultado.empty


# =============================================================================
# get_emendas_por_area
# =============================================================================

class TestGetEmendasPorArea:

    def test_retorna_dataframe_agrupado_por_area(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_por_area())
        # ACT
        resultado = get_emendas_por_area(ID_MUN)
        # ASSERT
        assert not resultado.empty
        assert "area" in resultado.columns

    def test_quando_bigquery_lanca_excecao_retorna_dataframe_vazio(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_emendas_por_area(ID_MUN)
        # ASSERT
        assert resultado.empty


# =============================================================================
# get_emendas_por_autor
# =============================================================================

class TestGetEmendasPorAutor:

    def test_retorna_dataframe_agrupado_por_autor(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: _df_por_autor())
        # ACT
        resultado = get_emendas_por_autor(ID_MUN)
        # ASSERT
        assert not resultado.empty
        assert "autor" in resultado.columns

    def test_quando_bigquery_lanca_excecao_retorna_dataframe_vazio(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils._bd_read_sql", lambda q: (_ for _ in ()).throw(Exception("BQ error")))
        # ACT
        resultado = get_emendas_por_autor(ID_MUN)
        # ASSERT
        assert resultado.empty


# =============================================================================
# get_dados_completos_municipio
# =============================================================================

class TestGetDadosCompletosMunicipio:

    def test_retorna_dict_com_todos_os_campos(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils.get_municipio_ibge", lambda id: {"nome": "Muriaé", "uf": "MG", "uf_nome": "Minas Gerais", "microrregiao": "Muriaé", "mesorregiao": "Zona da Mata", "regiao": "Sudeste"})
        monkeypatch.setattr("utils.get_populacao_municipio", lambda id: {"populacao": 115423, "ano_populacao": 2022})
        monkeypatch.setattr("utils.get_resumo_emendas", lambda id: {"total_emendas": 42, "total_empenhado": 1_399_803.0, "total_pago": 1_049_852.0, "total_autores": 5, "total_areas": 3})
        monkeypatch.setattr("utils.get_emendas_por_ano", lambda id: _df_por_ano())
        monkeypatch.setattr("utils.get_emendas_por_area", lambda id: _df_por_area())
        monkeypatch.setattr("utils.get_emendas_por_autor", lambda id: _df_por_autor())
        # ACT
        resultado = get_dados_completos_municipio(ID_MUN)
        # ASSERT
        assert resultado["nome"] == "Muriaé"
        assert resultado["uf"] == "MG"
        assert resultado["populacao"] == 115423
        assert resultado["resumo_emendas"]["total_emendas"] == 42
        assert not resultado["emendas_por_ano"].empty
