# test_rate_limit.py — Testa rate limiting por sessão (sem dependência externa).
# Cobre: incrementar_busca, limite_busca_atingido, get_buscas_restantes,
#        incrementar_chat, limite_chat_atingido.

from rate_limit import (
    LIMITE_BUSCAS,
    LIMITE_CHAT,
    incrementar_busca,
    limite_busca_atingido,
    get_buscas_restantes,
    incrementar_chat,
    limite_chat_atingido,
)


# =============================================================================
# Buscas
# =============================================================================

class TestLimiteBusca:

    def test_limite_busca_nao_atingido_inicialmente(self):
        session = {}
        assert limite_busca_atingido(session) is False

    def test_incrementar_busca_aumenta_contador(self):
        session = {}
        incrementar_busca(session)
        assert session["buscas"] == 1

    def test_limite_busca_atingido_apos_limite_buscas(self):
        session = {}
        for _ in range(LIMITE_BUSCAS):
            incrementar_busca(session)
        assert limite_busca_atingido(session) is True

    def test_limite_busca_nao_atingido_antes_do_limite(self):
        session = {}
        for _ in range(LIMITE_BUSCAS - 1):
            incrementar_busca(session)
        assert limite_busca_atingido(session) is False

    def test_get_buscas_restantes_inicia_com_limite_total(self):
        session = {}
        assert get_buscas_restantes(session) == LIMITE_BUSCAS

    def test_get_buscas_restantes_decrementa_com_uso(self):
        session = {}
        incrementar_busca(session)
        incrementar_busca(session)
        incrementar_busca(session)
        assert get_buscas_restantes(session) == LIMITE_BUSCAS - 3

    def test_get_buscas_restantes_nao_vai_abaixo_de_zero(self):
        session = {}
        for _ in range(LIMITE_BUSCAS + 5):
            incrementar_busca(session)
        assert get_buscas_restantes(session) == 0


# =============================================================================
# Chat
# =============================================================================

class TestLimiteChat:

    def test_limite_chat_nao_atingido_inicialmente(self):
        session = {}
        assert limite_chat_atingido(session) is False

    def test_incrementar_chat_aumenta_contador(self):
        session = {}
        incrementar_chat(session)
        assert session["mensagens_chat"] == 1

    def test_limite_chat_atingido_apos_limite_chat(self):
        session = {}
        for _ in range(LIMITE_CHAT):
            incrementar_chat(session)
        assert limite_chat_atingido(session) is True

    def test_limite_chat_nao_atingido_antes_do_limite(self):
        session = {}
        for _ in range(LIMITE_CHAT - 1):
            incrementar_chat(session)
        assert limite_chat_atingido(session) is False

    def test_buscas_e_chat_sao_contadores_independentes(self):
        session = {}
        for _ in range(LIMITE_BUSCAS):
            incrementar_busca(session)
        # limite de busca atingido, mas chat ainda livre
        assert limite_busca_atingido(session) is True
        assert limite_chat_atingido(session) is False
