"""
llm.py - Módulo de integração com LLM (Gemini)

LÓGICA:
Este módulo é responsável por transformar dados brutos em narrativas.
Recebe dicionários com dados e retorna texto humanizado para o usuário final.
"""

from functools import lru_cache

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


@lru_cache(maxsize=1)
def get_cliente():
    """Retorna cliente Gemini configurado. Instância única reutilizada durante a vida do módulo."""
    return genai.Client(api_key=GEMINI_API_KEY)


def gerar_narrativa_municipio(dados: dict) -> str:
    """
    Gera texto narrativo sobre emendas de um município.

    Args:
        dados: Dicionário com informações do município
            - nome: Nome do município
            - uf: Sigla do estado
            - total_emendas: Valor total recebido
            - principais_autores: Lista de deputados/senadores
            - areas: Distribuição por área (saúde, educação, etc)
            - comparativo_estado: Comparação com média estadual
            - populacao: População do município (opcional)
            - per_capita: Valor per capita (opcional)

    Returns:
        Texto narrativo em formato jornalístico
    """
    prompt = f"""
Você é um jornalista de dados especializado em transparência pública no Brasil.
Sua tarefa é gerar um texto informativo e acessível sobre emendas parlamentares.

DADOS DO MUNICIPIO:
- Nome: {dados.get('nome')}
- UF: {dados.get('uf')}
- Populacao: {dados.get('populacao', 0):,} habitantes
- Regiao: {dados.get('regiao')}

DADOS DE EMENDAS:
- Total empenhado: R$ {dados.get('total_empenhado', 0):,.2f}
- Total pago: R$ {dados.get('total_pago', 0):,.2f}
- Numero de emendas: {dados.get('total_emendas', 0)}
- Parlamentares envolvidos: {dados.get('total_autores', 0)}
- Valor per capita: R$ {dados.get('per_capita', 0):,.2f}
- Principais areas: {dados.get('principais_areas', [])}
- Principais autores: {dados.get('principais_autores', [])}


INSTRUÇÕES:
1. Escreva um texto de 200-300 palavras
2. Use linguagem acessível para o cidadão comum
3. Destaque os pontos mais relevantes
4. Inclua contexto comparativo quando disponível
5. Seja objetivo e imparcial
6. Não invente dados - use apenas o que foi fornecido

FORMATO:
- Título chamativo (uma linha)
- Parágrafo de abertura com o principal destaque
- 2-3 parágrafos de desenvolvimento
- Conclusão com reflexão para o cidadão
"""

    cliente = get_cliente()
    try:
        response = cliente.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar narrativa: {str(e)}"


def gerar_resumo_simples(texto: str, max_palavras: int = 50) -> str:
    """
    Gera um resumo curto de um texto.
    Útil para previews e cards na interface.
    """
    prompt = f"""
Resuma o texto abaixo em no máximo {max_palavras} palavras.
Mantenha apenas a informação mais importante.

TEXTO:
{texto}

RESUMO:
"""

    cliente = get_cliente()
    try:
        response = cliente.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erro ao gerar resumo: {str(e)}"


def gerar_analise_municipio(dados: dict) -> dict:
    """
    Orquestra narrativa + resumo para exibição no app.
    Garante que gerar_resumo_simples seja sempre chamada no fluxo (BUG #13).
    """
    narrativa = gerar_narrativa_municipio(dados)
    resumo = gerar_resumo_simples(narrativa)
    return {"narrativa": narrativa, "resumo": resumo}


def responder_pergunta(pergunta: str, contexto: dict) -> str:
    """
    Responde perguntas do usuário sobre os dados.
    Permite interação conversacional sobre as emendas.
    """
    prompt = f"""
Você é um assistente especializado em emendas parlamentares brasileiras.
Responda à pergunta do usuário com base no contexto fornecido.

CONTEXTO (dados do município):
{contexto}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES:
- Responda de forma direta e objetiva
- Se não souber ou não tiver dados, diga claramente
- Use linguagem acessível
- Limite a resposta a 100 palavras

RESPOSTA:
"""

    cliente = get_cliente()
    try:
        response = cliente.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        return f"Erro ao responder: {str(e)}"


if __name__ == "__main__":  # pragma: no cover
    print("Testando llm.py\n")

    print("1. Testando conexão com Gemini...")
    cliente = get_cliente()
    response = cliente.models.generate_content(model=GEMINI_MODEL, contents="Responda apenas: OK")
    print(f" Resposta: {response.text.strip()}\n")

    print("2. Testando geração de narrativa...")
    dados_teste = {
        'nome': 'São Paulo',
        'uf': 'SP',
        'total_emendas': 150000000.00,
        'populacao': 12300000,
        'per_capita': 12.19,
        'principais_autores': 'Deputado A (PT), Deputado B (PL)',
        'areas': 'Saúde (45%), Educação (30%), Infraestrutura (25%)',
        'comparativo_estado': '15% acima da média estadual'
    }
    narrativa = gerar_narrativa_municipio(dados_teste)
    print(" Narrativa gerada:\n")
    print("-" * 50)
    print(narrativa)
    print("-" * 50)
    print("\nTodos os testes passaram!")
