"""
config.py - Configurações centralizadas do projeto

💡 LÓGICA: 
- Centralizar configs evita "magic strings" espalhadas pelo código
- Se precisar mudar algo, muda em UM lugar só
- Facilita alternar entre ambientes (dev/prod)
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do .env para o ambiente
load_dotenv()

# === Google Cloud / BigQuery ===
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "US")

# === Gemini ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# === Configurações do App ===
APP_NAME = "Verba na Minha Cidade"
APP_DESCRIPTION = "Descubra quanto seu município recebeu em emendas parlamentares"

# === Cache ===
CACHE_TTL_SECONDS = 86400  # 24 horas

# === Validação (fail fast) ===
def validate_config():
    """Falhar cedo: se falta config, melhor descobrir ao iniciar o app."""
    missing = []
    if not GCP_PROJECT_ID:
        missing.append("GCP_PROJECT_ID")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")

    if missing:
        raise EnvironmentError(
            f"Variáveis de ambiente faltando: {', '.join(missing)}\n"
            f"Configure no arquivo .env"
        )

# Executa validação ao importar
if __name__ != "__main__":  # pragma: no cover
    validate_config()