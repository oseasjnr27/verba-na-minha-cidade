# TESTING.md — Guia de Testes

## Filosofia
Seguimos TDD estrito inspirado em Extreme Programming (XP).
Teste primeiro. Sempre. Sem exceção.

## O Ciclo Obrigatório

### 🔴 RED → 🟢 GREEN → 🔵 REFACTOR

1. RED   → Escreva o teste. Veja ele FALHAR
2. GREEN → Escreva o mínimo de código para PASSAR
3. BLUE  → Refatore sem quebrar os testes

## Estrutura de Testes

tests/
├── conftest.py          ← fixtures e mocks compartilhados
├── test_guardrails.py   ← testes de segurança (CRÍTICO)
├── test_utils.py        ← testes de busca de dados
├── test_llm.py          ← testes do Gemini
├── test_charts.py       ← testes dos gráficos
├── test_memory.py       ← testes de memória/contexto
└── test_agent_identity.py

## Regras de Ouro

### 1. NUNCA chame APIs reais nos testes

# ❌ ERRADO
def test_busca_municipio():
resultado = get_municipio_ibge("São Paulo")

# ✅ CERTO
def test_busca_municipio(mock_ibge):
resultado = get_municipio_ibge("São Paulo")

### 2. Nomenclatura obrigatória

# Padrão: test_[o_que_testa]_[cenario]_[resultado_esperado]
def test_busca_municipio_com_acento_retorna_cidade_correta():
def test_guardrails_com_injection_retorna_erro():
def test_charts_sem_dados_retorna_grafico_vazio():

### 3. Cada teste testa UMA coisa só

### 4. Estrutura AAA obrigatória
def test_exemplo():
# ARRANGE — prepara os dados
municipio = "Muriaé"
esperado  = "Muriaé"

# ACT — executa a ação
resultado = normalizar_municipio(municipio)

# ASSERT — verifica o resultado
assert resultado == esperado

## Regra de Ouro dos Mocks
"Mock onde é USADO, não onde é DEFINIDO"

Exemplo real do projeto:

    # utils.py faz:
    from utils_cache import get_municipios_df

    # Para mockar em test_utils.py:
    monkeypatch.setattr(
        "utils.get_municipios_df",       # ✅ onde é USADO
        mock_fn
    )

    # NÃO:
    monkeypatch.setattr(
        "utils_cache.get_municipios_df", # ❌ onde é DEFINIDO
        mock_fn
    )

Por quê:
`from X import Y` cria uma referência local em Z.
Trocar `X.Y` não afeta `Z.Y` já resolvido.
Sempre troque `Z.Y` — onde está sendo usado.

## Mocks Padrão do Projeto

MOCK_IBGE_MUNICIPIO = {
"id": "3143906",
"nome": "Muriaé",
"microrregiao": {
    "mesorregiao": {
        "UF": {"sigla": "MG"}
    }
}
}

MOCK_EMENDAS = {
"total_empenhado": 1399803.00,
"total_pago": 1049852.25,
"quantidade": 15,
"parlamentares": ["Dep. João Silva", "Sen. Maria Santos"]
}

MOCK_NARRATIVA = "Muriaé recebeu R$ 1,4 milhão em emendas parlamentares..."

## Cobertura Mínima Exigida

| Módulo            | Cobertura Mínima |
|-------------------|-----------------|
| guardrails.py     | 95%             |
| utils.py          | 85%             |
| llm.py            | 80%             |
| charts.py         | 75%             |
| memory.py         | 80%             |
| agent_identity.py | 70%             |

## Comandos de Teste

pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
pytest tests/test_utils.py -v

## Bugs → Testes

Todo bug corrigido OBRIGATORIAMENTE ganha um teste:
Bug encontrado → Cria teste que reproduz o bug
           → Vê o teste falhar (RED)
           → Corrige o bug
           → Vê o teste passar (GREEN)
           → Commita os dois juntos

## Histórico de Bugs Corrigidos

| Bug                                  | Teste criado                        | Status        |
|--------------------------------------|-------------------------------------|---------------|
| Busca "muriaé" retorna cidade errada | test_busca_municipio_com_acento     | 🔴 Pendente   |