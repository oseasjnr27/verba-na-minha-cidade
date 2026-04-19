---

## Arquivo adicional: `ARCHITECTURE.md`

```markdown
# Arquitetura Tecnica

## Diagrama de Componentes

┌─────────────────────────────────────────────────────────────────┐ │ FRONTEND │ │ (Streamlit) │ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │ │ │ Input │ │ KPIs │ │ Charts │ │ Chat │ │ │ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │ └───────┼────────────┼────────────┼────────────┼──────────────────┘ │ │ │ │ ▼ ▼ ▼ ▼ ┌─────────────────────────────────────────────────────────────────┐ │ ORQUESTRADOR │ │ (app.py) │ └───────┬────────────┬────────────┬────────────┬──────────────────┘ │ │ │ │ ▼ ▼ ▼ ▼ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │ guardrails│ │ utils │ │ charts │ │ llm │ │ .py │ │ .py │ │ .py │ │ .py │ └───────────┘ └─────┬─────┘ └───────────┘ └─────┬─────┘ │ │ ┌───────────┼───────────┐ │ ▼ ▼ ▼ ▼ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │ BigQuery │ │ API IBGE │ │ Plotly │ │ Gemini │ │ (Google) │ │ │ │ │ │ (Google) │ └───────────┘ └───────────┘ └───────────┘ └───────────┘


## Fluxo de Seguranca

Entrada Usuario │ ▼ ┌─────────────┐ ┌─────────────┐ │ VALIDACAO │ NAO │ REJEITA │ │ Tamanho? │────>│ Entrada │ │ Caracteres?│ └─────────────┘ └──────┬──────┘ │ SIM ▼ ┌─────────────┐ ┌─────────────┐ │ FILTRO │ SIM │ BLOQUEIA │ │ Injecao? │────>│ Ataque │ └──────┬──────┘ └─────────────┘ │ NAO ▼ ┌─────────────┐ │ PROCESSAMENTO│ │ Normal │ └──────┬──────┘ │ ▼ ┌─────────────┐ ┌─────────────┐ │ FILTRO │ SIM │ MASCARA │ │ Saida │────>│ Dados │ │ Sensivel? │ │ Sensiveis │ └──────┬──────┘ └──────┬──────┘ │ NAO │ ▼ ▼ ┌─────────────────────────────────┐ │ RESPOSTA SEGURA │ └─────────────────────────────────┘
Esses documentos cobrem:

✅ Visao geral para nao-tecnicos
✅ Arquitetura para devs
✅ Documentacao de cada modulo
✅ Fontes de dados
✅ Calculos e formulas
✅ Como executar
✅ Glossario