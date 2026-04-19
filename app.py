"""
app.py - Interface com dados REAIS de emendas parlamentares

Integra todos os módulos para apresentar informações de municípios
e emendas parlamentares de forma acessível e interativa.
"""

import streamlit as st
import pandas as pd

# Imports dos nossos módulos
from config import APP_NAME, APP_DESCRIPTION
from agent_identity import AGENT_IDENTITY
from utils import (
    buscar_municipio_por_nome,
    extrair_id_municipio,
    get_dados_completos_municipio,
    get_resumo_emendas,
    get_emendas_por_ano,
    get_emendas_por_area,
    get_emendas_por_autor,
    get_emendas_municipio
)
from llm import gerar_analise_municipio, responder_pergunta
from guardrails import filtrar_entrada, filtrar_saida, validar_municipio
from memory import MemoriaAgente, get_memoria_sessao
from styles import aplicar_estilos
from charts import (
    grafico_evolucao_anual,
    grafico_pizza_areas,
    grafico_barras_areas,
    grafico_barras_autores
)


# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏛️",
    layout="wide"
)

# Tema dark (BUG #4)
aplicar_estilos(st)

# Memória isolada por sessão de usuário (BUG #3)
memoria = get_memoria_sessao(st.session_state)


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.title("🏛️ " + APP_NAME)
    st.markdown(APP_DESCRIPTION)
    st.divider()

    with st.expander("Sobre o Agente"):
        st.markdown(f"**{AGENT_IDENTITY['nome']}**")
        for item in AGENT_IDENTITY['escopo']['faz']:
            st.markdown(f"- {item}")

    st.divider()
    st.markdown("**Fontes:**")
    st.markdown("- [IBGE](https://servicodados.ibge.gov.br)")
    st.markdown("- [CGU - Emendas](https://portaldatransparencia.gov.br)")
    st.markdown("- [Base dos Dados](https://basedosdados.org)")
    st.divider()
    st.caption("Projeto educacional")


# =============================================================================
# PÁGINA PRINCIPAL
# =============================================================================
st.title("🏛️ Emendas Parlamentares do seu Município")
st.markdown(
    "Descubra quanto seu município recebeu em emendas parlamentares, "
    "de quais parlamentares e para quais áreas."
)

# Input de busca
col1, col2 = st.columns([3, 1])
with col1:
    municipio_input = st.text_input(
        "Nome do Município",
        placeholder="Ex: Guarapari, São Paulo, Muriaé, Carmo...",
        key="municipio_input"
    )
with col2:
    btn_buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)


# =============================================================================
# LÓGICA DE BUSCA E CARREGAMENTO
# =============================================================================
if municipio_input and btn_buscar:
    # Validações de segurança
    entrada_ok, msg = validar_municipio(municipio_input)
    if not entrada_ok:
        st.error(msg)
        st.stop()

    seguro, msg = filtrar_entrada(municipio_input)
    if not seguro:
        st.error(msg)
        st.stop()

    # Busca municípios correspondentes
    with st.spinner("Buscando município..."):
        resultados = buscar_municipio_por_nome(municipio_input)

    if resultados.empty:
        st.warning("Município não encontrado. Tente outro nome.")
        st.stop()

    # Seleção do município
    if len(resultados) > 1:
        opcoes = resultados['nome_completo'].tolist()
        selecionado = st.selectbox("Selecione o município:", opcoes)
        id_mun = extrair_id_municipio(resultados, selecionado)
        nome_mun = resultados[resultados['id_municipio'] == id_mun]['nome'].iloc[0]
    else:
        nome_mun = resultados.iloc[0]['nome']
        id_mun = resultados.iloc[0]['id_municipio']
        selecionado = resultados.iloc[0]['nome_completo']

    st.success(f"**{selecionado}** | Código IBGE: `{id_mun}`")

    # Carrega todos os dados reais
    with st.spinner("Carregando dados do IBGE e emendas parlamentares..."):
        try:
            dados_mun = get_dados_completos_municipio(id_mun)
            resumo = get_resumo_emendas(id_mun)
            emendas_ano = get_emendas_por_ano(id_mun)
            emendas_area = get_emendas_por_area(id_mun)
            emendas_autor = get_emendas_por_autor(id_mun)

            memoria.definir_contexto_municipio(dados_mun)

        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            st.stop()


# =============================================================================
# DASHBOARD (só aparece após busca bem-sucedida)
# =============================================================================
if 'dados_mun' in locals() and 'resumo' in locals():
    st.divider()
    st.header(f"📊 {dados_mun['nome']} - {dados_mun['uf']}")
    st.caption(f"{dados_mun['mesorregiao']} | {dados_mun['regiao']}")

    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pop_fmt = f"{dados_mun['populacao']:,}".replace(",", ".")
        st.metric("População", pop_fmt, help=f"IBGE {dados_mun['ano_populacao']}")
    with col2:
        emp_fmt = f"R$ {resumo['total_empenhado']:,.0f}".replace(",", ".")
        st.metric("Total Empenhado", emp_fmt)
    with col3:
        pago_fmt = f"R$ {resumo['total_pago']:,.0f}".replace(",", ".")
        st.metric("Total Pago", pago_fmt)
    with col4:
        per_capita = resumo['total_empenhado'] / dados_mun['populacao'] if dados_mun['populacao'] > 0 else 0
        pc_fmt = f"R$ {per_capita:,.2f}".replace(",", ".")
        st.metric("Per Capita", pc_fmt)

    # KPIs secundários
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Emendas", resumo['total_emendas'])
    with col2:
        st.metric("Parlamentares", resumo['total_autores'])
    with col3:
        st.metric("Áreas", resumo['total_areas'])
    with col4:
        exec_pct = (resumo['total_pago'] / resumo['total_empenhado'] * 100) if resumo['total_empenhado'] > 0 else 0
        st.metric("Execução", f"{exec_pct:.1f}%")


    # =============================================================================
    # GRÁFICOS
    # =============================================================================
    st.divider()
    st.subheader("📈 Visualizações")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(grafico_evolucao_anual(emendas_ano), use_container_width=True, key="chart_evolucao_anual")
    with col2:
        st.plotly_chart(grafico_pizza_areas(emendas_area), use_container_width=True, key="chart_pizza_areas")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(grafico_barras_areas(emendas_area), use_container_width=True, key="chart_barras_areas")
    with col2:
        st.plotly_chart(grafico_barras_autores(emendas_autor), use_container_width=True, key="chart_barras_autores")


    # =============================================================================
    # TABELA DETALHADA + DOWNLOAD
    # =============================================================================
    st.divider()
    with st.expander("📋 Ver tabela completa de emendas"):
        df_emendas = get_emendas_municipio(id_mun)

        if not df_emendas.empty:
            st.dataframe(
                df_emendas,
                use_container_width=True,
                hide_index=True
            )

            # Download CSV
            csv = df_emendas.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"emendas_{id_mun}_{dados_mun['nome']}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhuma emenda encontrada para este município.")


    # =============================================================================
    # NARRATIVA DO LLM
    # =============================================================================
    st.divider()
    st.header("📝 Análise do Agente")

    with st.spinner("Gerando análise com IA..."):
        dados_llm = {
            "nome": dados_mun['nome'],
            "uf": dados_mun['uf'],
            "populacao": dados_mun['populacao'],
            "regiao": dados_mun['regiao'],
            "total_empenhado": resumo['total_empenhado'],
            "total_pago": resumo['total_pago'],
            "total_emendas": resumo['total_emendas'],
            "total_autores": resumo['total_autores'],
            "per_capita": per_capita,
            "execucao": exec_pct,
            "principais_areas": emendas_area.head(3)['area'].tolist() if not emendas_area.empty else [],
            "principais_autores": emendas_autor.head(3)['autor'].tolist() if not emendas_autor.empty else []
        }

        analise = gerar_analise_municipio(dados_llm)
        narrativa_filtrada = filtrar_saida(analise["narrativa"])
        resumo_filtrado = filtrar_saida(analise["resumo"])
        memoria.adicionar_interacao("assistant", narrativa_filtrada[:500])

    st.caption(resumo_filtrado)
    st.markdown(narrativa_filtrada)


    # =============================================================================
    # CHAT INTERATIVO
    # =============================================================================
    st.divider()
    st.header("💬 Pergunte ao Agente")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        pergunta = st.text_input(
            "Sua pergunta:",
            placeholder="Ex: Por que a saúde recebe mais recursos?",
            label_visibility="collapsed"
        )
    with col_btn:
        btn_enviar = st.button("Enviar", use_container_width=True)

    if pergunta and btn_enviar:
        seguro, msg = filtrar_entrada(pergunta)
        if not seguro:
            st.error(msg)
        else:
            with st.spinner("Pensando..."):
                memoria.adicionar_interacao("user", pergunta)
                resposta = responder_pergunta(pergunta, dados_llm)
                resposta_filtrada = filtrar_saida(resposta)
                memoria.adicionar_interacao("assistant", resposta_filtrada)

            st.markdown(resposta_filtrada)


    # =============================================================================
    # COMPARTILHAR
    # =============================================================================
    st.divider()
    share_text = (
        f"Descobri que {dados_mun['nome']}-{dados_mun['uf']} recebeu "
        f"R$ {resumo['total_empenhado']:,.0f} em emendas parlamentares! "
        f"Veja mais em: [link do app]"
    )
    st.text_area("Compartilhar:", share_text, height=80)


# =============================================================================
# FOOTER (sempre visível)
# =============================================================================
st.divider()
st.caption(
    "Fonte: CGU/Emendas Parlamentares via Base dos Dados | IBGE | "
    "Projeto educacional – Transparência Pública"
)