"""
styles.py - Design System Dark para a aplicação VerbaCidade
Tokens: bg=#0a0a0b, accent=#00d4aa, surface=#111113
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* ── Tokens ── */
:root {
    --bg:      #0a0a0b;
    --surface: #111113;
    --border:  rgba(255,255,255,0.08);
    --accent:  #00d4aa;
    --text:    #e0e0e0;
    --muted:   #6b7280;
}

/* ── Reset Geral ── */
.stApp {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Hero ── */
.hero { text-align: center; padding: 48px 20px 32px; }
.hero-title {
    font-size: 40px; font-weight: 800; color: #fff; margin-bottom: 8px;
    letter-spacing: -0.5px;
}
.hero-subtitle { font-size: 15px; color: var(--muted); max-width: 560px; margin: 0 auto; }
.hero-accent { color: var(--accent); }

/* ── KPI Cards ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 12px;
}
.kpi-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent), 0 8px 24px rgba(0,212,170,0.08);
}
.kpi-title {
    font-size: 11px; font-weight: 500; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.6px;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px; font-weight: 700; color: var(--accent);
    margin-top: 6px;
}
.kpi-delta { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ── AI / Analysis Card ── */
.ai-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
}
.ai-card::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 12px;
    padding: 1px;
    background: linear-gradient(135deg, var(--accent), transparent 60%);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
}
.ai-label {
    font-size: 11px; font-weight: 600; color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;
}
.ai-content { color: var(--text); line-height: 1.7; font-size: 14px; }

/* ── Vera Chat Section ── */
.vera-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-top: 24px;
}
.vera-header {
    font-size: 13px; font-weight: 600; color: var(--accent);
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}

/* ── Charts ── */
.chart-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

/* ── Progress Bar ── */
.progress-container {
    background: rgba(255,255,255,0.06);
    border-radius: 4px; height: 6px; margin-top: 8px;
}
.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #00a88a);
    border-radius: 4px;
}

/* ── Footer ── */
.footer {
    text-align: center; padding: 40px 20px;
    color: var(--muted); font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 48px;
}

/* ── Streamlit overrides ── */
[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
}
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}
</style>
"""


def aplicar_estilos(st_module) -> None:
    """Injeta o tema dark no app. Aceita o módulo st como parâmetro para testabilidade."""
    st_module.markdown(CUSTOM_CSS, unsafe_allow_html=True)
