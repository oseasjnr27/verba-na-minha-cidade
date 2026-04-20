# test_lgpd.py — Testa o módulo LGPD (banner de consentimento).
# Cobre: lgpd_foi_aceito, aceitar_lgpd, mostrar_banner_lgpd.

from unittest.mock import MagicMock
import pytest

from lgpd import lgpd_foi_aceito, aceitar_lgpd, mostrar_banner_lgpd


# =============================================================================
# lgpd_foi_aceito()
# =============================================================================

class TestLgpdFoiAceito:

    def test_lgpd_nao_aceito_quando_session_state_vazio(self):
        # ARRANGE
        session = {}
        # ACT + ASSERT
        assert lgpd_foi_aceito(session) is False

    def test_lgpd_foi_aceito_retorna_true_apos_aceitar(self):
        # ARRANGE
        session = {}
        aceitar_lgpd(session)
        # ACT + ASSERT
        assert lgpd_foi_aceito(session) is True

    def test_lgpd_false_explicito_retorna_false(self):
        # ARRANGE — chave existe mas valor é False
        session = {"lgpd_aceito": False}
        # ACT + ASSERT
        assert lgpd_foi_aceito(session) is False


# =============================================================================
# aceitar_lgpd()
# =============================================================================

class TestAceitarLgpd:

    def test_aceitar_lgpd_seta_chave_no_session_state(self):
        # ARRANGE
        session = {}
        # ACT
        aceitar_lgpd(session)
        # ASSERT
        assert session.get("lgpd_aceito") is True

    def test_aceitar_lgpd_idempotente(self):
        # ARRANGE — chamar duas vezes não deve causar erro
        session = {}
        aceitar_lgpd(session)
        aceitar_lgpd(session)
        # ASSERT
        assert lgpd_foi_aceito(session) is True


# =============================================================================
# mostrar_banner_lgpd()
# =============================================================================

class TestMostrarBannerLgpd:

    def test_banner_nao_exibe_se_lgpd_ja_aceito(self):
        # ARRANGE
        session = {"lgpd_aceito": True}
        st_mock = MagicMock()
        # ACT
        mostrar_banner_lgpd(st_mock, session)
        # ASSERT — nenhuma chamada de display ao st
        st_mock.info.assert_not_called()
        st_mock.warning.assert_not_called()

    def test_banner_exibe_quando_lgpd_nao_aceito(self):
        # ARRANGE
        session = {}
        st_mock = MagicMock()
        st_mock.button.return_value = False  # usuário ainda não clicou
        # ACT
        mostrar_banner_lgpd(st_mock, session)
        # ASSERT — banner deve chamar st.info com texto sobre LGPD
        st_mock.info.assert_called_once()
        chamada = st_mock.info.call_args[0][0]
        assert "LGPD" in chamada or "dados" in chamada.lower()
