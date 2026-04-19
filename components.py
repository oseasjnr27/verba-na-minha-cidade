import streamlit as st

def render_header():
    st.markdown('<div style="padding: 15px 0; font-weight: 800; font-size: 20px;">🏛️ Verba na Minha Cidade</div>', unsafe_allow_html=True)

def render_hero():
    st.markdown("""
        <div class="hero">
            <h1 class="hero-title">🏛️ Emendas Parlamentares</h1>
            <p class="hero-subtitle">Transparência real: descubra os recursos destinados ao seu município através de dados oficiais e análise inteligente.</p>
        </div>
    """, unsafe_allow_html=True)

def render_kpi_card(title, value, subtitle="", variant="primary", icon=""):
    return f"""
        <div class="kpi-card">
            <div class="kpi-title">{icon} {title}</div>
            <div class="kpi-value {variant}">{value}</div>
            <div style="font-size: 10px; color: #4a5568; margin-top: 4px;">{subtitle}</div>
        </div>
    """

def render_ai_analysis(content):
    return f"""
        <div class="ai-card">
            <div style="color: hsl(258, 90%, 66%); font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                ✨ ANALISTA DE TRANSPARÊNCIA IA
            </div>
            <div class="ai-content">{content}</div>
        </div>
    """

def render_progress_bar(pct, label):
    return f"""
        <div class="kpi-card">
            <div class="kpi-title">{label}</div>
            <div class="kpi-value success">{pct:.1f}%</div>
            <div class="progress-container"><div class="progress-bar" style="width: {pct}%"></div></div>
        </div>
    """

def render_footer():
    st.markdown("""
        <div class="footer">
            Fontes: CGU, IBGE e Portal da Transparência | Projeto Educacional de Transparência Pública
        </div>
    """, unsafe_allow_html=True)