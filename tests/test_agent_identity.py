# test_agent_identity.py — Testa a identidade e limites do agente.
# Cobre: estrutura de AGENT_IDENTITY, get_system_prompt().
# Cenários: campos obrigatórios, escopo, tom, system prompt completo.
# Cobertura mínima exigida: 70%

import pytest
from agent_identity import AGENT_IDENTITY, get_system_prompt


# =============================================================================
# Estrutura de AGENT_IDENTITY
# =============================================================================

class TestAgentIdentityEstrutura:

    def test_agent_identity_tem_campo_nome(self):
        assert "nome" in AGENT_IDENTITY
        assert isinstance(AGENT_IDENTITY["nome"], str)
        assert len(AGENT_IDENTITY["nome"]) > 0

    def test_agent_identity_tem_campo_papel(self):
        assert "papel" in AGENT_IDENTITY
        assert isinstance(AGENT_IDENTITY["papel"], str)

    def test_agent_identity_tem_campo_proposito(self):
        assert "proposito" in AGENT_IDENTITY
        assert isinstance(AGENT_IDENTITY["proposito"], str)

    def test_agent_identity_tem_campo_escopo(self):
        assert "escopo" in AGENT_IDENTITY
        assert "faz" in AGENT_IDENTITY["escopo"]
        assert "nao_faz" in AGENT_IDENTITY["escopo"]

    def test_agent_identity_escopo_faz_nao_esta_vazio(self):
        assert len(AGENT_IDENTITY["escopo"]["faz"]) > 0

    def test_agent_identity_escopo_nao_faz_nao_esta_vazio(self):
        assert len(AGENT_IDENTITY["escopo"]["nao_faz"]) > 0

    def test_agent_identity_tem_campo_tom_de_voz(self):
        assert "tom_de_voz" in AGENT_IDENTITY
        assert isinstance(AGENT_IDENTITY["tom_de_voz"], str)

    def test_agent_identity_tem_campo_limitacoes(self):
        assert "limitacoes" in AGENT_IDENTITY
        assert isinstance(AGENT_IDENTITY["limitacoes"], str)


# =============================================================================
# Conteúdo esperado da identidade
# =============================================================================

class TestAgentIdentityConteudo:

    def test_agent_identity_nome_contem_transparencia(self):
        # O agente deve ter foco em transparência pública
        assert "Transparência" in AGENT_IDENTITY["nome"] or \
               "transparencia" in AGENT_IDENTITY["nome"].lower()

    def test_agent_identity_escopo_nao_faz_menciona_opiniao_politica(self):
        nao_faz = " ".join(AGENT_IDENTITY["escopo"]["nao_faz"]).lower()
        assert "política" in nao_faz or "politica" in nao_faz or "partidária" in nao_faz

    def test_agent_identity_escopo_faz_menciona_emendas(self):
        faz = " ".join(AGENT_IDENTITY["escopo"]["faz"]).lower()
        assert "emenda" in faz


# =============================================================================
# get_system_prompt()
# =============================================================================

class TestGetSystemPrompt:

    def test_get_system_prompt_retorna_string(self):
        # ARRANGE + ACT
        resultado = get_system_prompt()
        # ASSERT
        assert isinstance(resultado, str)

    def test_get_system_prompt_nao_esta_vazio(self):
        resultado = get_system_prompt()
        assert len(resultado.strip()) > 0

    def test_get_system_prompt_contem_secao_o_que_nao_faz(self):
        resultado = get_system_prompt()
        assert "NÃO FAZ" in resultado or "não faz" in resultado.lower()

    def test_get_system_prompt_contem_secao_proposito(self):
        resultado = get_system_prompt()
        assert "PROPOSITO" in resultado.upper()

    def test_get_system_prompt_contem_secao_tom_de_voz(self):
        resultado = get_system_prompt()
        assert "TOM" in resultado.upper()

    def test_get_system_prompt_contem_itens_do_escopo_faz(self):
        resultado = get_system_prompt()
        for item in AGENT_IDENTITY["escopo"]["faz"]:
            assert item in resultado

    def test_get_system_prompt_contem_itens_do_escopo_nao_faz(self):
        resultado = get_system_prompt()
        for item in AGENT_IDENTITY["escopo"]["nao_faz"]:
            assert item in resultado
