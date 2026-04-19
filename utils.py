"""
utils.py - Módulo de acesso a dados

FONTES:
- API IBGE: Validação e busca de municípios
- BigQuery: Dados de população e emendas parlamentares
"""

import pandas as pd
import requests
from unidecode import unidecode
import streamlit as st
from config import CACHE_TTL_SECONDS
from utils_cache import get_municipios_df, _bd_read_sql


# =============================================================================
# CONSTANTES
# =============================================================================
IBGE_API_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"


# =============================================================================
# API IBGE - Busca e validação de municípios
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_municipio_ibge(id_municipio: str) -> dict:
    """Busca dados do município na API do IBGE pelo ID."""
    url = f"{IBGE_API_BASE}/municipios/{id_municipio}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "id": data["id"],
            "nome": data["nome"],
            "uf": data["microrregiao"]["mesorregiao"]["UF"]["sigla"],
            "uf_nome": data["microrregiao"]["mesorregiao"]["UF"]["nome"],
            "microrregiao": data["microrregiao"]["nome"],
            "mesorregiao": data["microrregiao"]["mesorregiao"]["nome"],
            "regiao": data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
        }
    except Exception as e:
        print(f"Erro API IBGE: {e}")
        return {}


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_municipios_por_uf(sigla_uf: str) -> list:
    """Lista todos os municípios de uma UF."""
    url = f"{IBGE_API_BASE}/estados/{sigla_uf}/municipios"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [{"id": m["id"], "nome": m["nome"]} for m in data]
    except Exception as e:
        print(f"Erro API IBGE: {e}")
        return []


# =============================================================================
# SELEÇÃO DE MUNICÍPIO — lógica extraída de app.py (BUG #2)
# =============================================================================

def extrair_id_municipio(df: pd.DataFrame, nome_completo: str) -> str:
    """
    Retorna o id_municipio correspondente ao nome_completo selecionado.

    Usa rsplit para separar nome e UF pelo último " - ", garantindo que nomes
    com hífen (ex: "Luís Correia - PI") sejam tratados corretamente.
    Filtra por nome E sigla_uf para evitar colisão entre municípios homônimos.
    """
    partes = nome_completo.rsplit(" - ", 1)
    nome = partes[0]
    sigla_uf = partes[1] if len(partes) == 2 else ""

    mask = (df["nome"] == nome) & (df["sigla_uf"] == sigla_uf)
    return df[mask]["id_municipio"].iloc[0]


# =============================================================================
# BIGQUERY - Busca de municípios (para autocomplete)
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def buscar_municipio_por_nome(nome_busca: str) -> pd.DataFrame:
    """Busca municípios que contenham o texto digitado.

    Usa cache CSV local (data/municipios.csv) para evitar custo e latência
    do BigQuery a cada busca. Filtro via unidecode + regex=False no Python.
    """
    df = get_municipios_df()

    nome_busca_normalizado = unidecode(nome_busca.lower().strip())
    df = df.copy()
    df['nome_normalizado'] = df['nome'].apply(lambda x: unidecode(x.lower()))
    # BUG #7: regex=False evita que caracteres especiais do usuário sejam interpretados
    mask = df['nome_normalizado'].str.contains(nome_busca_normalizado, na=False, regex=False)

    resultado = df[mask].copy()
    # Ordena por relevância: exato (3) > prefixo (2) > contém (1)
    q = nome_busca_normalizado
    resultado['_score'] = resultado['nome_normalizado'].apply(
        lambda x: 3 if x == q else (2 if x.startswith(q) else 1)
    )
    resultado = resultado.sort_values('_score', ascending=False).head(10)
    resultado = resultado.drop(columns=['nome_normalizado', '_score'])
    resultado['nome_completo'] = resultado['nome'] + ' - ' + resultado['sigla_uf']

    return resultado


# =============================================================================
# BIGQUERY - Dados de população
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_populacao_municipio(id_municipio: str) -> dict:
    """Busca população do município no BigQuery (último ano disponível)."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        id_municipio,
        ano,
        populacao
    FROM `basedosdados.br_ibge_populacao.municipio`
    WHERE id_municipio = '{id_municipio}'
    ORDER BY ano DESC
    LIMIT 1
    """
    try:
        df = _bd_read_sql(query)
        if not df.empty:
            return {
                "populacao": int(df.iloc[0]['populacao']),
                "ano_populacao": int(df.iloc[0]['ano'])
            }
    except Exception as e:
        print(f"Erro BigQuery população: {e}")

    return {"populacao": 0, "ano_populacao": 0}


# =============================================================================
# BIGQUERY - Dados de EMENDAS PARLAMENTARES
# =============================================================================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_emendas_municipio(id_municipio: str) -> pd.DataFrame:
    """Busca todas as emendas parlamentares de um município."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        ano_emenda,
        id_emenda,
        tipo_emenda,
        id_autor_emenda,
        nome_autor_emenda,
        nome_funcao,
        nome_subfuncao,
        nome_acao,
        valor_empenhado,
        valor_pago
    FROM `basedosdados.br_cgu_emendas_parlamentares.microdados`
    WHERE id_municipio_gasto = '{id_municipio}'
    ORDER BY ano_emenda DESC, valor_empenhado DESC
    """
    try:
        df = _bd_read_sql(query)
        return df
    except Exception as e:
        print(f"Erro ao buscar emendas: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_resumo_emendas(id_municipio: str) -> dict:
    """Retorna resumo agregado das emendas de um município."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        COUNT(*) as total_emendas,
        SUM(valor_empenhado) as total_empenhado,
        SUM(valor_pago) as total_pago,
        COUNT(DISTINCT nome_autor_emenda) as total_autores,
        COUNT(DISTINCT nome_funcao) as total_areas
    FROM `basedosdados.br_cgu_emendas_parlamentares.microdados`
    WHERE id_municipio_gasto = '{id_municipio}'
    """
    try:
        df = _bd_read_sql(query)
        if not df.empty:
            return {
                "total_emendas": int(df.iloc[0]['total_emendas'] or 0),
                "total_empenhado": float(df.iloc[0]['total_empenhado'] or 0),
                "total_pago": float(df.iloc[0]['total_pago'] or 0),
                "total_autores": int(df.iloc[0]['total_autores'] or 0),
                "total_areas": int(df.iloc[0]['total_areas'] or 0)
            }
    except Exception as e:
        print(f"Erro ao buscar resumo: {e}")

    return {
        "total_emendas": 0,
        "total_empenhado": 0,
        "total_pago": 0,
        "total_autores": 0,
        "total_areas": 0
    }


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_emendas_por_ano(id_municipio: str) -> pd.DataFrame:
    """Retorna emendas agrupadas por ano."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        ano_emenda as ano,
        SUM(valor_empenhado) as valor_empenhado,
        SUM(valor_pago) as valor_pago,
        COUNT(*) as quantidade
    FROM `basedosdados.br_cgu_emendas_parlamentares.microdados`
    WHERE id_municipio_gasto = '{id_municipio}'
    GROUP BY ano_emenda
    ORDER BY ano_emenda
    """
    try:
        return _bd_read_sql(query)
    except Exception as e:
        print(f"Erro: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_emendas_por_area(id_municipio: str) -> pd.DataFrame:
    """Retorna emendas agrupadas por área (função)."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        nome_funcao as area,
        SUM(valor_empenhado) as valor_empenhado,
        SUM(valor_pago) as valor_pago,
        COUNT(*) as quantidade
    FROM `basedosdados.br_cgu_emendas_parlamentares.microdados`
    WHERE id_municipio_gasto = '{id_municipio}'
    GROUP BY nome_funcao
    ORDER BY valor_empenhado DESC
    """
    try:
        return _bd_read_sql(query)
    except Exception as e:
        print(f"Erro: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_emendas_por_autor(id_municipio: str) -> pd.DataFrame:
    """Retorna emendas agrupadas por autor (parlamentar), top 15."""
    # nosec B608 — id_municipio vem de lookup interno validado pelo guardrail,
    # nunca de input direto do usuário
    query = f"""
    SELECT
        nome_autor_emenda AS autor,
        SUM(valor_empenhado) AS valor_empenhado,
        SUM(valor_pago) AS valor_pago,
        COUNT(*) AS quantidade
    FROM `basedosdados.br_cgu_emendas_parlamentares.microdados`
    WHERE id_municipio_gasto = '{id_municipio}'
    GROUP BY nome_autor_emenda
    ORDER BY valor_empenhado DESC
    LIMIT 15
    """
    try:
        df = _bd_read_sql(query)
        return df
    except Exception as e:
        print(f"Erro ao buscar emendas por autor: {e}")
        return pd.DataFrame()


# =============================================================================
# FUNÇÃO PRINCIPAL - Dados completos do município
# =============================================================================

def get_dados_completos_municipio(id_municipio: str) -> dict:
    """Busca todos os dados básicos de um município (IBGE + população)."""
    dados_ibge = get_municipio_ibge(id_municipio)
    dados_pop = get_populacao_municipio(id_municipio)

    return {
        "codigo_ibge": id_municipio,
        "nome": dados_ibge.get("nome", ""),
        "uf": dados_ibge.get("uf", ""),
        "uf_nome": dados_ibge.get("uf_nome", ""),
        "microrregiao": dados_ibge.get("microrregiao", ""),
        "mesorregiao": dados_ibge.get("mesorregiao", ""),
        "regiao": dados_ibge.get("regiao", ""),
        "populacao": dados_pop["populacao"],
        "ano_populacao": dados_pop["ano_populacao"],
        # Campos de emendas (podem ser preenchidos separadamente)
        "resumo_emendas": get_resumo_emendas(id_municipio),
        "emendas_por_ano": get_emendas_por_ano(id_municipio),
        "emendas_por_area": get_emendas_por_area(id_municipio),
        "emendas_por_autor": get_emendas_por_autor(id_municipio)
    }


# =============================================================================
# BLOCO DE TESTE
# =============================================================================

if __name__ == "__main__":
    print("Testando utils.py\n")

    print("1. API IBGE - São Paulo...")
    dados = get_municipio_ibge("3550308")
    print(f"   {dados.get('nome')} - {dados.get('uf')}\n")

    print("2. População - São Paulo...")
    pop = get_populacao_municipio("3550308")
    print(f"   {pop['populacao']:,} hab ({pop['ano_populacao']})\n")

    print("3. Resumo de emendas - Guarapari (3202405)...")
    resumo = get_resumo_emendas("3202405")
    print(f"   Total: {resumo['total_emendas']} emendas")
    print(f"   Empenhado: R$ {resumo['total_empenhado']:,.2f}\n")

    print("4. Busca 'Muriae'...")
    r = buscar_municipio_por_nome("Muriae")
    print(f"   {r['nome_completo'].tolist()}\n")

    print("OK!")