# test_llm.py — Testa integração com o Google Gemini.
# Cobre: get_cliente(), gerar_narrativa_municipio(),
#        gerar_resumo_simples(), responder_pergunta().
# Cenários: resposta válida, falha na API (exceção), dados mínimos.
# Cobertura mínima exigida: 80%
# REGRA: nunca chama a API real — sempre mockamos get_cliente().

import pytest
from unittest.mock import MagicMock, patch

import llm
from llm import gerar_narrativa_municipio, gerar_resumo_simples, responder_pergunta, gerar_analise_municipio


def _mock_cliente(texto_resposta: str = "resposta mock do gemini"):
    """Cria mock do cliente Gemini que retorna texto_resposta."""
    cliente = MagicMock()
    cliente.models.generate_content.return_value.text = texto_resposta
    return cliente


def _mock_cliente_com_erro(excecao: Exception):
    """Cria mock do cliente que lança exceção ao gerar conteúdo."""
    cliente = MagicMock()
    cliente.models.generate_content.side_effect = excecao
    return cliente


def _dados_municipio():
    return {
        "nome": "Muriaé",
        "uf": "MG",
        "populacao": 109726,
        "regiao": "Sudeste",
        "total_empenhado": 1_399_803.00,
        "total_pago": 1_049_852.25,
        "total_emendas": 15,
        "total_autores": 3,
        "per_capita": 12.76,
        "principais_areas": ["Saúde", "Educação"],
        "principais_autores": ["Dep. João Silva", "Sen. Maria Santos"],
    }


# =============================================================================
# get_cliente()
# =============================================================================

class TestGetCliente:

    @pytest.fixture(autouse=True)
    def limpar_cache_cliente(self):
        # BUG #12: lru_cache persiste entre testes — limpa antes de cada um
        llm.get_cliente.cache_clear()
        yield
        llm.get_cliente.cache_clear()

    def test_get_cliente_retorna_objeto_nao_nulo(self, monkeypatch):
        # ARRANGE
        mock_client_class = MagicMock()
        monkeypatch.setattr("llm.genai.Client", mock_client_class)
        # ACT
        cliente = llm.get_cliente()
        # ASSERT
        assert cliente is not None

    def test_get_cliente_inicializa_com_api_key(self, monkeypatch):
        # ARRANGE
        mock_client_class = MagicMock()
        monkeypatch.setattr("llm.genai.Client", mock_client_class)
        # ACT
        llm.get_cliente()
        # ASSERT — chamado com api_key
        mock_client_class.assert_called_once()
        _, kwargs = mock_client_class.call_args
        assert "api_key" in kwargs

    def test_get_cliente_reutiliza_instancia_em_chamadas_consecutivas(self, monkeypatch):
        # ARRANGE — BUG #12: cada chamada criava novo genai.Client sem reutilização
        mock_client_class = MagicMock()
        monkeypatch.setattr("llm.genai.Client", mock_client_class)
        # ACT
        cliente1 = llm.get_cliente()
        cliente2 = llm.get_cliente()
        # ASSERT — mesma instância; Client instanciado apenas uma vez
        assert cliente1 is cliente2
        assert mock_client_class.call_count == 1


# =============================================================================
# gerar_narrativa_municipio()
# =============================================================================

class TestGerarNarrativaMunicipio:

    def test_gerar_narrativa_retorna_string(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente("Narrativa gerada."))
        # ACT
        resultado = gerar_narrativa_municipio(_dados_municipio())
        # ASSERT
        assert isinstance(resultado, str)

    def test_gerar_narrativa_retorna_texto_do_modelo(self, monkeypatch):
        # ARRANGE
        texto_esperado = "Muriaé recebeu R$ 1,4 milhão em emendas parlamentares."
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente(texto_esperado))
        # ACT
        resultado = gerar_narrativa_municipio(_dados_municipio())
        # ASSERT
        assert resultado == texto_esperado

    def test_gerar_narrativa_quando_api_falha_retorna_mensagem_de_erro(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr(
            "llm.get_cliente",
            lambda: _mock_cliente_com_erro(Exception("API indisponível"))
        )
        # ACT
        resultado = gerar_narrativa_municipio(_dados_municipio())
        # ASSERT
        assert "Erro" in resultado
        assert isinstance(resultado, str)

    def test_gerar_narrativa_com_dados_minimos_nao_lanca_excecao(self, monkeypatch):
        # ARRANGE — dados sem campos opcionais
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente("ok"))
        dados_minimos = {"nome": "Muriaé", "uf": "MG"}
        # ACT + ASSERT — não deve explodir com KeyError
        resultado = gerar_narrativa_municipio(dados_minimos)
        assert isinstance(resultado, str)


# =============================================================================
# gerar_resumo_simples()
# =============================================================================

class TestGerarResumoSimples:

    def test_gerar_resumo_retorna_string(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente("Resumo curto."))
        # ACT
        resultado = gerar_resumo_simples("Texto longo para resumir.")
        # ASSERT
        assert isinstance(resultado, str)

    def test_gerar_resumo_retorna_texto_do_modelo(self, monkeypatch):
        # ARRANGE
        esperado = "Muriaé recebeu verbas."
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente(esperado))
        # ACT
        resultado = gerar_resumo_simples("qualquer texto")
        # ASSERT
        assert resultado == esperado

    def test_gerar_resumo_quando_api_falha_retorna_mensagem_de_erro(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr(
            "llm.get_cliente",
            lambda: _mock_cliente_com_erro(Exception("timeout"))
        )
        # ACT
        resultado = gerar_resumo_simples("texto")
        # ASSERT
        assert "Erro" in resultado


# =============================================================================
# responder_pergunta()
# =============================================================================

class TestResponderPergunta:

    def test_responder_pergunta_retorna_string(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente("Resposta direta."))
        # ACT
        resultado = responder_pergunta("Quanto Muriaé recebeu?", {"nome": "Muriaé"})
        # ASSERT
        assert isinstance(resultado, str)

    def test_responder_pergunta_retorna_texto_do_modelo(self, monkeypatch):
        # ARRANGE
        esperado = "Muriaé recebeu R$ 1,4 milhão."
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente(esperado))
        # ACT
        resultado = responder_pergunta("Quanto recebeu?", {})
        # ASSERT
        assert resultado == esperado

    def test_responder_pergunta_quando_api_falha_retorna_mensagem_de_erro(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr(
            "llm.get_cliente",
            lambda: _mock_cliente_com_erro(Exception("quota excedida"))
        )
        # ACT
        resultado = responder_pergunta("pergunta qualquer", {})
        # ASSERT
        assert "Erro" in resultado


# =============================================================================
# gerar_analise_municipio()  — BUG #13
# =============================================================================

class TestGerarAnaliseMunicipio:
    """BUG #13 — gerar_resumo_simples deve ser chamada no fluxo de análise."""

    def test_gerar_analise_chama_gerar_resumo_simples(self, monkeypatch):
        # ARRANGE — BUG #13: verifica que gerar_resumo_simples É invocada
        narrativa_mock = "Muriaé recebeu R$ 1,4 milhão em emendas parlamentares."
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente(narrativa_mock))

        with patch("llm.gerar_resumo_simples", return_value="Resumo mock.") as mock_resumo:
            # ACT
            gerar_analise_municipio(_dados_municipio())
            # ASSERT — gerar_resumo_simples foi chamada com a narrativa gerada
            mock_resumo.assert_called_once_with(narrativa_mock)

    def test_gerar_analise_retorna_narrativa_e_resumo(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr("llm.get_cliente", lambda: _mock_cliente("Narrativa completa."))

        with patch("llm.gerar_resumo_simples", return_value="Resumo curto."):
            # ACT
            resultado = gerar_analise_municipio(_dados_municipio())
            # ASSERT
            assert "narrativa" in resultado
            assert "resumo" in resultado
            assert resultado["narrativa"] == "Narrativa completa."
            assert resultado["resumo"] == "Resumo curto."

    def test_gerar_analise_quando_api_falha_retorna_dicionario_com_erro(self, monkeypatch):
        # ARRANGE
        monkeypatch.setattr(
            "llm.get_cliente",
            lambda: _mock_cliente_com_erro(Exception("API indisponível"))
        )
        # ACT
        resultado = gerar_analise_municipio(_dados_municipio())
        # ASSERT
        assert "narrativa" in resultado
        assert "Erro" in resultado["narrativa"]
