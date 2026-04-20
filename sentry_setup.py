"""
sentry_setup.py — Inicialização opcional do Sentry.

App não quebra se DSN ausente.
send_default_pii=False: nenhum dado pessoal enviado (LGPD).
"""

import logging
import os

import sentry_sdk

logger = logging.getLogger(__name__)


def _ler_dsn() -> str | None:
    """Tenta st.secrets primeiro; cai no .env se local."""
    try:
        import streamlit as st
        val = st.secrets.get("SENTRY_DSN", "")
        if isinstance(val, str) and val.strip():
            return val.strip()
    except Exception as e:
        logger.debug("st.secrets indisponível para SENTRY_DSN: %s", type(e).__name__)
    return os.getenv("SENTRY_DSN", "").strip() or None


def inicializar_sentry(dsn: str | None = None) -> None:
    """Inicializa o Sentry se DSN válido estiver disponível."""
    if dsn is None:
        dsn = _ler_dsn()

    if not dsn or not dsn.strip():
        logger.debug("Sentry não inicializado — DSN ausente")
        return

    sentry_sdk.init(
        dsn=dsn,
        send_default_pii=False,
        traces_sample_rate=0.1,
    )
    logger.debug("Sentry inicializado")
