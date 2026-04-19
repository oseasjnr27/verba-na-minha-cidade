"""
memory.py - Sistema de memória do agente

CONCEITO (SPAR - Reflecting):
Garante que o agente não comece do zero a cada interação.
Implementa:
- Memória de curto prazo (sessão atual)
- Estrutura para memória de longo prazo (futuro)
"""

from typing import Dict, List, Optional
from datetime import datetime


class MemoriaAgente:
    """
    Gerencia a memória do agente durante a sessão.
    
    CONCEITO:
        - Curto prazo: histórico da conversa atual
        - Contexto: dados do município sendo analisado
    """
    
    def __init__(self):
        self.historico: List[Dict] = []
        self.contexto_municipio: Optional[Dict] = None
        self.sessao_inicio: datetime = datetime.now()
    
    def adicionar_interacao(self, role: str, content: str):
        """
        Adiciona uma interação ao histórico.
        
        CONCEITO (Janela de Contexto):
            Mantemos as últimas N interações para não
            estourar o limite de tokens do modelo.
        """
        self.historico.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantém apenas as últimas 10 interações (gestão de contexto)
        if len(self.historico) > 10:
            self.historico = self.historico[-10:]
    
    def definir_contexto_municipio(self, dados: Dict):
        """
        Define o município atual sendo analisado.
        
        CONCEITO:
            O contexto do município é mantido durante toda
            a sessão para perguntas de follow-up.
        """
        self.contexto_municipio = dados
    
    def get_historico_formatado(self) -> str:
        """
        Retorna histórico formatado para incluir no prompt.
        
        CONCEITO (Engenharia de Contexto):
            Formata o histórico de forma eficiente para
            maximizar informação com mínimo de tokens.
        """
        if not self.historico:
            return "Nenhuma interação anterior."
        
        linhas = []
        # Últimas 5 apenas para evitar consumo excessivo de tokens
        for item in self.historico[-5:]:
            role = "Usuário" if item["role"] == "user" else "Agente"
            # Limita o conteúdo exibido para evitar prompts gigantes
            conteudo_curto = item['content'][:200] + "..." if len(item['content']) > 200 else item['content']
            linhas.append(f"{role}: {conteudo_curto}")
        
        return "\n".join(linhas)
    
    def get_resumo_sessao(self) -> Dict:
        """
        Retorna resumo da sessão para analytics.
        
        CONCEITO (Observabilidade):
            Rastrear métricas ajuda a identificar padrões
            e melhorar o agente.
        """
        return {
            "total_interacoes": len(self.historico),
            "municipio_analisado": self.contexto_municipio.get("nome") if self.contexto_municipio else None,
            "duracao_sessao_segundos": int((datetime.now() - self.sessao_inicio).total_seconds())
        }
    
    def limpar(self):
        """Limpa a memória da sessão."""
        self.historico = []
        self.contexto_municipio = None
        self.sessao_inicio = datetime.now()


def get_memoria_sessao(session: dict) -> "MemoriaAgente":
    """
    Retorna MemoriaAgente isolada por sessão (BUG #3).

    Aceita qualquer dict como session — compatível com st.session_state
    e com dicts simples em testes. Garante que cada sessão de usuário
    tenha sua própria instância, eliminando o vazamento entre sessões.
    """
    if "memoria" not in session:
        session["memoria"] = MemoriaAgente()
    return session["memoria"]


# Mantido por compatibilidade com imports existentes — remover futuramente.
# Em produção use get_memoria_sessao(st.session_state) via app.py.
memoria = MemoriaAgente()


if __name__ == "__main__":  # pragma: no cover
    print("=== Testando Sistema de Memória ===\n")
    
    # Simula interações
    memoria.adicionar_interacao("user", "Quero ver dados de Sao Paulo")
    memoria.adicionar_interacao("assistant", "Sao Paulo recebeu R$ 150 milhões...")
    memoria.adicionar_interacao("user", "E comparado com Campinas?")
    
    print("Histórico formatado:")
    print(memoria.get_historico_formatado())
    print("\nResumo da sessão:")
    print(memoria.get_resumo_sessao())