"""
styles.py - Design System Dark para a aplicação VerbaCidade
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

/* Reset Geral */
.stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, hsl(222, 47%, 6%) 0%, hsl(217, 33%, 12%) 100%);
    color: white;
}

/* Esconder elementos nativos */
#MainMenu, footer, header {visibility: hidden;}

/* Cards de Indicadores (KPIs) */
.kpi-card {
    background: hsl(222, 47%, 9%);
    border: 1px solid hsl(217, 33%, 18%);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.2s ease;
    margin-bottom: 15px;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: hsl(217, 91%, 60%);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.kpi-title {
    font-size: 11px;
    font-weight: 500;
    color: hsl(215, 20%, 60%);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    margin-top: 5px;
}

/* Variantes de cores */
.primary { color: hsl(217, 91%, 60%); }
.success { color: hsl(160, 84%, 39%); }
.warning { color: hsl(38, 92%, 50%); }
.ai { color: hsl(258, 90%, 66%); }

/* Hero Section */
.hero { text-align: center; padding: 40px 20px; }
.hero-title { font-size: 42px; font-weight: 800; color: white; margin-bottom: 10px; }
.hero-subtitle { font-size: 16px; color: hsl(215, 20%, 60%); max-width: 600px; margin: 0 auto; }

/* AI Analysis Card */
.ai-card {
    background: linear-gradient(135deg, hsl(258, 50%, 12%) 0%, hsl(222, 47%, 9%) 100%);
    border: 1px solid hsl(258, 50%, 25%);
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
}

.ai-content { color: hsl(215, 20%, 80%); line-height: 1.6; font-size: 14px; }

/* Progress Bar */
.progress-container { background: hsl(217, 33%, 15%); border-radius: 4px; height: 8px; margin-top: 8px; }
.progress-bar { height: 100%; background: hsl(160, 84%, 39%); border-radius: 4px; }

/* Footer */
.footer { text-align: center; padding: 40px; color: #555; font-size: 12px; border-top: 1px solid #1e293b; }
</style>
"""


def aplicar_estilos(st_module) -> None:
    """Injeta o tema dark no app. Aceita o módulo st como parâmetro para testabilidade."""
    st_module.markdown(CUSTOM_CSS, unsafe_allow_html=True)