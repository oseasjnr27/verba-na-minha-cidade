"""
lgpd.py — Consentimento LGPD via banner não-bloqueante.

Banner aparece na primeira visita; aceite persiste na sessão via session_state.
Não coleta nem transmite dados — apenas registra o consentimento localmente.
"""

_TEXTO_BANNER = (
    "🔒 **LGPD** — Este app exibe dados públicos de emendas parlamentares "
    "(CGU/Base dos Dados) e dados demográficos do IBGE. Nenhum dado pessoal "
    "seu é coletado ou armazenado. Ao continuar, você concorda com o uso "
    "dessas informações para fins de transparência pública."
)


def lgpd_foi_aceito(session_state: dict) -> bool:
    return bool(session_state.get("lgpd_aceito", False))


def aceitar_lgpd(session_state: dict) -> None:
    session_state["lgpd_aceito"] = True


def mostrar_banner_lgpd(st, session_state: dict) -> None:
    if lgpd_foi_aceito(session_state):
        return

    st.info(_TEXTO_BANNER)
    if st.button("Entendi e concordo", key="lgpd_aceitar"):
        aceitar_lgpd(session_state)
        st.rerun()
