# test_memory.py — Testa o sistema de memória/contexto de sessão.
# Cobre: __init__, adicionar_interacao, definir_contexto_municipio,
#        get_historico_formatado, get_resumo_sessao, limpar,
#        get_memoria_sessao (BUG #3 — isolamento entre sessões).
# Cobertura mínima exigida: 80%

import pytest
from memory import MemoriaAgente, get_memoria_sessao


# =============================================================================
# __init__
# =============================================================================

class TestMemoriaAgenteInit:

    def test_init_historico_comeca_vazio(self):
        # ARRANGE + ACT
        memoria = MemoriaAgente()
        # ASSERT
        assert memoria.historico == []

    def test_init_contexto_municipio_comeca_none(self):
        # ARRANGE + ACT
        memoria = MemoriaAgente()
        # ASSERT
        assert memoria.contexto_municipio is None

    def test_init_sessao_inicio_e_datetime(self):
        # ARRANGE + ACT
        from datetime import datetime
        memoria = MemoriaAgente()
        # ASSERT
        assert isinstance(memoria.sessao_inicio, datetime)


# =============================================================================
# adicionar_interacao()
# =============================================================================

class TestAdicionarInteracao:

    def test_adicionar_interacao_user_aparece_no_historico(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        memoria.adicionar_interacao("user", "Quero dados de Muriaé")
        # ASSERT
        assert len(memoria.historico) == 1
        assert memoria.historico[0]["role"] == "user"
        assert memoria.historico[0]["content"] == "Quero dados de Muriaé"

    def test_adicionar_interacao_assistant_aparece_no_historico(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        memoria.adicionar_interacao("assistant", "Muriaé recebeu R$ 1,4 milhão.")
        # ASSERT
        assert memoria.historico[0]["role"] == "assistant"

    def test_adicionar_interacao_entrada_tem_timestamp(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        memoria.adicionar_interacao("user", "teste")
        # ASSERT
        assert "timestamp" in memoria.historico[0]
        assert isinstance(memoria.historico[0]["timestamp"], str)

    def test_adicionar_interacao_com_10_entradas_mantem_todas(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        for i in range(10):
            memoria.adicionar_interacao("user", f"mensagem {i}")
        # ASSERT
        assert len(memoria.historico) == 10

    def test_adicionar_interacao_com_11_entradas_trunca_para_10(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        for i in range(11):
            memoria.adicionar_interacao("user", f"mensagem {i}")
        # ASSERT
        assert len(memoria.historico) == 10

    def test_adicionar_interacao_truncamento_preserva_mais_recentes(self):
        # ARRANGE
        memoria = MemoriaAgente()
        for i in range(11):
            memoria.adicionar_interacao("user", f"mensagem {i}")
        # ACT + ASSERT — a primeira mensagem (índice 0) foi descartada
        assert memoria.historico[0]["content"] == "mensagem 1"
        assert memoria.historico[-1]["content"] == "mensagem 10"


# =============================================================================
# definir_contexto_municipio()
# =============================================================================

class TestDefinirContextoMunicipio:

    def test_definir_contexto_seta_dados_do_municipio(self):
        # ARRANGE
        memoria = MemoriaAgente()
        dados = {"nome": "Muriaé", "uf": "MG"}
        # ACT
        memoria.definir_contexto_municipio(dados)
        # ASSERT
        assert memoria.contexto_municipio == dados

    def test_definir_contexto_sobrescreve_contexto_anterior(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.definir_contexto_municipio({"nome": "Muriaé", "uf": "MG"})
        # ACT
        memoria.definir_contexto_municipio({"nome": "São Paulo", "uf": "SP"})
        # ASSERT
        assert memoria.contexto_municipio["nome"] == "São Paulo"


# =============================================================================
# get_historico_formatado()
# =============================================================================

class TestGetHistoricoFormatado:

    def test_get_historico_formatado_vazio_retorna_mensagem_padrao(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT
        assert resultado == "Nenhuma interação anterior."

    def test_get_historico_formatado_role_user_exibe_como_usuario(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.adicionar_interacao("user", "Olá")
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT
        assert "Usuário:" in resultado

    def test_get_historico_formatado_role_assistant_exibe_como_agente(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.adicionar_interacao("assistant", "Olá, posso ajudar.")
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT
        assert "Agente:" in resultado

    def test_get_historico_formatado_com_6_entradas_exibe_so_ultimas_5(self):
        # ARRANGE
        memoria = MemoriaAgente()
        for i in range(6):
            memoria.adicionar_interacao("user", f"mensagem {i}")
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT — "mensagem 0" foi excluída, "mensagem 1" é a mais antiga exibida
        assert "mensagem 0" not in resultado
        assert "mensagem 1" in resultado
        assert "mensagem 5" in resultado

    def test_get_historico_formatado_conteudo_longo_e_truncado(self):
        # ARRANGE
        memoria = MemoriaAgente()
        conteudo_longo = "x" * 250
        memoria.adicionar_interacao("user", conteudo_longo)
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT
        assert "..." in resultado
        assert "x" * 201 not in resultado  # não exibe além de 200 chars + "..."

    def test_get_historico_formatado_conteudo_curto_exibe_completo(self):
        # ARRANGE
        memoria = MemoriaAgente()
        conteudo = "Quero dados de Muriaé"
        memoria.adicionar_interacao("user", conteudo)
        # ACT
        resultado = memoria.get_historico_formatado()
        # ASSERT
        assert conteudo in resultado
        assert "..." not in resultado


# =============================================================================
# get_resumo_sessao()
# =============================================================================

class TestGetResumoSessao:

    def test_get_resumo_sessao_sem_contexto_municipio_e_none(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        resumo = memoria.get_resumo_sessao()
        # ASSERT
        assert resumo["municipio_analisado"] is None

    def test_get_resumo_sessao_com_contexto_retorna_nome_municipio(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.definir_contexto_municipio({"nome": "Muriaé", "uf": "MG"})
        # ACT
        resumo = memoria.get_resumo_sessao()
        # ASSERT
        assert resumo["municipio_analisado"] == "Muriaé"

    def test_get_resumo_sessao_total_interacoes_e_correto(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.adicionar_interacao("user", "pergunta 1")
        memoria.adicionar_interacao("assistant", "resposta 1")
        # ACT
        resumo = memoria.get_resumo_sessao()
        # ASSERT
        assert resumo["total_interacoes"] == 2

    def test_get_resumo_sessao_duracao_e_inteiro_nao_negativo(self):
        # ARRANGE
        memoria = MemoriaAgente()
        # ACT
        resumo = memoria.get_resumo_sessao()
        # ASSERT
        assert isinstance(resumo["duracao_sessao_segundos"], int)
        assert resumo["duracao_sessao_segundos"] >= 0

    def test_get_resumo_sessao_duracao_sessao_longa_retorna_total_correto(self):
        # ARRANGE — BUG #5: sessão de 24h30s; .seconds retorna 30, total_seconds() retorna 86430
        from unittest.mock import patch
        from datetime import datetime, timedelta
        memoria = MemoriaAgente()
        inicio_falso = datetime(2026, 1, 1, 0, 0, 0)
        agora_falso  = inicio_falso + timedelta(days=1, seconds=30)
        memoria.sessao_inicio = inicio_falso
        # ACT
        with patch("memory.datetime") as mock_dt:
            mock_dt.now.return_value = agora_falso
            resumo = memoria.get_resumo_sessao()
        # ASSERT — .seconds retornaria 30 (BUG); total_seconds() retorna 86430 (correto)
        assert resumo["duracao_sessao_segundos"] == 86430


# =============================================================================
# limpar()
# =============================================================================

class TestLimpar:

    def test_limpar_zera_historico(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.adicionar_interacao("user", "mensagem")
        # ACT
        memoria.limpar()
        # ASSERT
        assert memoria.historico == []

    def test_limpar_zera_contexto_municipio(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.definir_contexto_municipio({"nome": "Muriaé"})
        # ACT
        memoria.limpar()
        # ASSERT
        assert memoria.contexto_municipio is None

    def test_limpar_permite_uso_normal_em_seguida(self):
        # ARRANGE
        memoria = MemoriaAgente()
        memoria.adicionar_interacao("user", "antes")
        memoria.limpar()
        # ACT
        memoria.adicionar_interacao("user", "depois")
        # ASSERT
        assert len(memoria.historico) == 1
        assert memoria.historico[0]["content"] == "depois"

    def test_limpar_reseta_sessao_inicio(self):
        # ARRANGE — BUG #11: limpar() deve reiniciar o contador de duração
        from datetime import datetime, timedelta
        memoria = MemoriaAgente()
        memoria.sessao_inicio = datetime.now() - timedelta(seconds=3600)
        # ACT
        memoria.limpar()
        # ASSERT — após limpar, a duração deve ser próxima de zero (< 5s)
        resumo = memoria.get_resumo_sessao()
        assert resumo["duracao_sessao_segundos"] < 5


# =============================================================================
# get_memoria_sessao()  — BUG #3
# =============================================================================

class TestGetMemoriaSessao:
    """BUG #3 — memória compartilhada entre sessões de usuários."""

    def test_get_memoria_sessao_cria_instancia_na_primeira_chamada(self):
        # ARRANGE
        session = {}
        # ACT
        memoria = get_memoria_sessao(session)
        # ASSERT
        assert isinstance(memoria, MemoriaAgente)
        assert "memoria" in session

    def test_get_memoria_sessao_reutiliza_instancia_na_mesma_sessao(self):
        # ARRANGE
        session = {}
        primeira = get_memoria_sessao(session)
        # ACT
        segunda = get_memoria_sessao(session)
        # ASSERT — mesmo objeto, não uma cópia nova
        assert primeira is segunda

    def test_get_memoria_sessao_sessoes_diferentes_tem_instancias_isoladas(self):
        # ARRANGE — BUG #3: sem correção, ambas apontariam para o mesmo singleton
        session_a = {}
        session_b = {}
        # ACT
        memoria_a = get_memoria_sessao(session_a)
        memoria_b = get_memoria_sessao(session_b)
        # ASSERT
        assert memoria_a is not memoria_b

    def test_get_memoria_sessao_historico_nao_vaza_entre_sessoes(self):
        # ARRANGE
        session_a = {}
        session_b = {}
        memoria_a = get_memoria_sessao(session_a)
        memoria_b = get_memoria_sessao(session_b)
        # ACT — usuário A interage
        memoria_a.adicionar_interacao("user", "São Paulo")
        # ASSERT — sessão B permanece limpa
        assert len(memoria_b.historico) == 0

    def test_get_memoria_sessao_contexto_nao_vaza_entre_sessoes(self):
        # ARRANGE
        session_a = {}
        session_b = {}
        memoria_a = get_memoria_sessao(session_a)
        memoria_b = get_memoria_sessao(session_b)
        # ACT — usuário A define contexto
        memoria_a.definir_contexto_municipio({"nome": "São Paulo", "uf": "SP"})
        # ASSERT — sessão B não vê o contexto de A
        assert memoria_b.contexto_municipio is None
