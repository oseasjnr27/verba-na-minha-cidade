"""
rate_limit.py — Controle de uso por sessão via session_state.

Sem dependência externa — puro Python/Streamlit.
Limites por sessão de usuário; resetam ao fechar/reabrir o navegador.
"""

LIMITE_BUSCAS = 10
LIMITE_CHAT = 20


def incrementar_busca(session: dict) -> None:
    session["buscas"] = session.get("buscas", 0) + 1


def limite_busca_atingido(session: dict) -> bool:
    return session.get("buscas", 0) >= LIMITE_BUSCAS


def get_buscas_restantes(session: dict) -> int:
    return max(0, LIMITE_BUSCAS - session.get("buscas", 0))


def incrementar_chat(session: dict) -> None:
    session["mensagens_chat"] = session.get("mensagens_chat", 0) + 1


def limite_chat_atingido(session: dict) -> bool:
    return session.get("mensagens_chat", 0) >= LIMITE_CHAT
