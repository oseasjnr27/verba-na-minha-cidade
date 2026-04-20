# test_sentry.py — Testa inicialização do Sentry.
# Garante: DSN obrigatório para init, send_default_pii=False, app não quebra sem DSN.

from unittest.mock import patch

from sentry_setup import inicializar_sentry


class TestInicializarSentry:

    def test_sentry_inicializa_com_dsn_valido(self):
        # ARRANGE
        dsn = "https://abc123@sentry.io/123"
        with patch("sentry_setup.sentry_sdk") as mock_sdk:
            # ACT
            inicializar_sentry(dsn)
            # ASSERT
            mock_sdk.init.assert_called_once()

    def test_sentry_nao_inicializa_sem_dsn(self):
        # ARRANGE — mocka _ler_dsn para garantir ausência de DSN no ambiente de teste
        with patch("sentry_setup.sentry_sdk") as mock_sdk, \
             patch("sentry_setup._ler_dsn", return_value=None):
            # ACT
            inicializar_sentry(None)
            # ASSERT
            mock_sdk.init.assert_not_called()

    def test_sentry_nao_envia_pii(self):
        # ARRANGE — LGPD: send_default_pii deve ser False
        dsn = "https://abc123@sentry.io/123"
        with patch("sentry_setup.sentry_sdk") as mock_sdk:
            # ACT
            inicializar_sentry(dsn)
            # ASSERT
            _, kwargs = mock_sdk.init.call_args
            assert kwargs.get("send_default_pii") is False

    def test_sentry_nao_quebra_app_se_dsn_ausente(self):
        # ARRANGE — DSN vazio ou None não deve lançar exceção
        for dsn in [None, "", "   "]:
            with patch("sentry_setup.sentry_sdk"), \
                 patch("sentry_setup._ler_dsn", return_value=None):
                # ACT + ASSERT — não deve lançar exceção
                inicializar_sentry(dsn)
