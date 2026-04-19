# test_utils.py — Testa busca e processamento de dados.
# Cobre: buscar_municipio_por_nome(), extrair_id_municipio().
# Cenários: busca com acento (BUG #1), município duplicado (BUG #2),
#           regex no input (BUG #7), cache CSV em vez de BigQuery direto (BUG #6).
# Cobertura mínima exigida: 85%
#
# NOTA: mocks em "utils.get_municipios_df" — nome local em utils.py após
# "from utils_cache import get_municipios_df". Patching do módulo-origem
# (utils_cache) não afeta a referência já resolvida.

import pandas as pd

from utils import buscar_municipio_por_nome, extrair_id_municipio


def _df_municipios():
    return pd.DataFrame({
        "id_municipio": ["3143906", "3143807", "3304300"],
        "nome":         ["Muriaé",  "Murici",  "Nova Iguaçu"],
        "sigla_uf":     ["MG",      "AL",      "RJ"],
        "nome_uf":      ["Minas Gerais", "Alagoas", "Rio de Janeiro"],
    })


class TestBuscaMunicipioComAcento:
    """BUG #1 — busca com acentos retorna cidade errada."""

    def test_busca_municipio_com_acento_retorna_cidade_correta(self, monkeypatch):
        # ARRANGE
        municipio_digitado = "muriaé"
        esperado = "Muriaé"
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT
        resultado = buscar_municipio_por_nome(municipio_digitado)
        # ASSERT
        assert not resultado.empty, "Deve encontrar Muriaé ao digitar 'muriaé'"
        assert resultado.iloc[0]["nome"] == esperado

    def test_busca_municipio_sem_acento_retorna_cidade_correta(self, monkeypatch):
        # ARRANGE
        municipio_digitado = "muriae"
        esperado = "Muriaé"
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT
        resultado = buscar_municipio_por_nome(municipio_digitado)
        # ASSERT
        assert not resultado.empty, "Deve encontrar Muriaé ao digitar sem acento"
        assert resultado.iloc[0]["nome"] == esperado

    def test_busca_municipio_maiusculo_retorna_cidade_correta(self, monkeypatch):
        # ARRANGE
        municipio_digitado = "MURIAÉ"
        esperado = "Muriaé"
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT
        resultado = buscar_municipio_por_nome(municipio_digitado)
        # ASSERT
        assert not resultado.empty, "Deve encontrar Muriaé em caixa alta"
        assert resultado.iloc[0]["nome"] == esperado

    def test_busca_municipio_inexistente_retorna_dataframe_vazio(self, monkeypatch):
        # ARRANGE
        municipio_digitado = "xyzabc123"
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT
        resultado = buscar_municipio_por_nome(municipio_digitado)
        # ASSERT
        assert resultado.empty, "Município inexistente deve retornar DataFrame vazio"


def _df_municipios_duplicados():
    """DataFrame com dois municípios de mesmo nome em estados diferentes."""
    return pd.DataFrame({
        "id_municipio": ["3550308", "3143000", "2927408"],
        "nome":         ["Santa Cruz", "Santa Cruz", "Salvador"],
        "sigla_uf":     ["SP",         "MG",         "BA"],
        "nome_completo": ["Santa Cruz - SP", "Santa Cruz - MG", "Salvador - BA"],
    })


class TestExtrairIdMunicipio:
    """BUG #2 — município duplicado seleciona ID errado."""

    def test_extrair_id_municipio_unico_retorna_id_correto(self):
        # ARRANGE
        df = _df_municipios_duplicados()
        # ACT
        resultado = extrair_id_municipio(df, "Salvador - BA")
        # ASSERT
        assert resultado == "2927408"

    def test_extrair_id_municipio_duplicado_retorna_id_do_estado_correto_mg(self):
        # ARRANGE — BUG #2: sem a correção, retornaria sempre "3550308" (SP, o primeiro)
        df = _df_municipios_duplicados()
        # ACT
        resultado = extrair_id_municipio(df, "Santa Cruz - MG")
        # ASSERT
        assert resultado == "3143000", "Deve retornar o ID de MG, não de SP"

    def test_extrair_id_municipio_duplicado_retorna_id_do_estado_correto_sp(self):
        # ARRANGE
        df = _df_municipios_duplicados()
        # ACT
        resultado = extrair_id_municipio(df, "Santa Cruz - SP")
        # ASSERT
        assert resultado == "3550308"

    def test_extrair_id_municipio_nome_com_traco_retorna_id_correto(self):
        # ARRANGE — nome que contém " - " no próprio nome (edge case do split)
        df = pd.DataFrame({
            "id_municipio": ["1234567"],
            "nome":         ["Luís Correia"],
            "sigla_uf":     ["PI"],
            "nome_completo": ["Luís Correia - PI"],
        })
        # ACT
        resultado = extrair_id_municipio(df, "Luís Correia - PI")
        # ASSERT
        assert resultado == "1234567"


class TestBuscaMunicipioInputRegex:
    """BUG #7 — str.contains interpreta input do usuário como regex."""

    def test_busca_com_colchetes_nao_levanta_re_error(self, monkeypatch):
        # ARRANGE — BUG #7: "[sp]ao" é regex inválido; deve buscar literalmente
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT + ASSERT — não deve levantar re.error
        resultado = buscar_municipio_por_nome("[sp]ao")
        assert isinstance(resultado, pd.DataFrame)

    def test_busca_com_ponto_de_interrogacao_nao_e_interpretado_como_regex(self, monkeypatch):
        # ARRANGE — BUG #7: "?" em regex significa "zero ou um do anterior"
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT + ASSERT — não deve levantar e deve retornar DataFrame vazio
        resultado = buscar_municipio_por_nome("cidade?sp")
        assert isinstance(resultado, pd.DataFrame)
        assert resultado.empty

    def test_busca_com_asterisco_nao_levanta_erro(self, monkeypatch):
        # ARRANGE — BUG #7: "*" em regex é quantificador inválido sem precedente
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT + ASSERT
        resultado = buscar_municipio_por_nome("*teste*")
        assert isinstance(resultado, pd.DataFrame)


class TestBuscaMunicipioUsaCacheCSV:
    """BUG #6 (revisado) — buscar_municipio_por_nome usa cache CSV, não BigQuery direto.

    Regression #1: WHERE parametrizado quebrou basedosdados.read_sql().
    Solução: cache CSV local em data/municipios.csv via utils_cache.
    """

    def test_busca_municipio_usa_get_municipios_df_nao_bigquery(self, monkeypatch):
        # ARRANGE — rastreia se get_municipios_df é chamada em vez de bd.read_sql
        chamadas_cache = []

        def mock_get_municipios_df():
            chamadas_cache.append(1)
            return _df_municipios()

        monkeypatch.setattr("utils.get_municipios_df", mock_get_municipios_df)
        bd_chamado = []
        monkeypatch.setattr(
            "utils_cache._bd_read_sql",
            lambda *a, **kw: bd_chamado.append(1) or _df_municipios()
        )
        # ACT
        buscar_municipio_por_nome("Muriaé")
        # ASSERT — usou cache, não chamou BigQuery diretamente
        assert len(chamadas_cache) == 1
        assert len(bd_chamado) == 0

    def test_busca_municipio_retorna_nome_completo_formatado(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("utils.get_municipios_df", lambda: _df_municipios())
        # ACT
        resultado = buscar_municipio_por_nome("Muriaé")
        # ASSERT — coluna nome_completo no formato "Nome - UF"
        assert "nome_completo" in resultado.columns
        assert resultado.iloc[0]["nome_completo"] == "Muriaé - MG"
