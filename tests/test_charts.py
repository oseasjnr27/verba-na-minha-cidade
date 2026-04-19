# test_charts.py — Testa geração de gráficos Plotly.
# Cobre: apply_dark_theme(), grafico_evolucao_anual(),
#        grafico_barras_areas(), grafico_barras_areas_clusterizado(),
#        grafico_barras_autores(), grafico_pizza_areas().
# Cenários: df vazio (annotation), df com dados (traces), casos especiais.
# Cobertura mínima exigida: 75%

import pandas as pd
import plotly.graph_objects as go

from charts import (
    apply_dark_theme,
    grafico_evolucao_anual,
    grafico_barras_areas,
    grafico_barras_areas_clusterizado,
    grafico_barras_autores,
    grafico_pizza_areas,
)


# ---------------------------------------------------------------------------
# DataFrames auxiliares
# ---------------------------------------------------------------------------

def _df_evolucao():
    return pd.DataFrame({
        "ano":             [2020, 2021, 2022],
        "valor_empenhado": [100_000, 200_000, 300_000],
        "valor_pago":      [80_000,  150_000, 250_000],
        "quantidade":      [5, 8, 12],
    })


def _df_areas():
    return pd.DataFrame({
        "area":            ["Saúde", "Educação", "Infraestrutura"],
        "valor_empenhado": [500_000, 300_000, 200_000],
        "valor_pago":      [400_000, 250_000, 150_000],
        "quantidade":      [10, 8, 5],
    })


def _df_autores():
    return pd.DataFrame({
        "autor":           ["Dep. João Silva", "Sen. Maria Santos", "Dep. Carlos Lima"],
        "valor_empenhado": [700_000, 500_000, 200_000],
        "valor_pago":      [600_000, 400_000, 150_000],
        "quantidade":      [15, 10, 5],
    })


def _df_autores_sem_informacao():
    return pd.DataFrame({
        "autor":           ["Sem informação", "Sem informacao"],
        "valor_empenhado": [100_000, 50_000],
        "valor_pago":      [80_000,  40_000],
        "quantidade":      [3, 2],
    })


# =============================================================================
# apply_dark_theme()
# =============================================================================

class TestApplyDarkTheme:

    def test_apply_dark_theme_retorna_o_proprio_figure(self):
        # ARRANGE
        fig = go.Figure()
        # ACT
        resultado = apply_dark_theme(fig)
        # ASSERT
        assert resultado is fig

    def test_apply_dark_theme_retorna_go_figure(self):
        fig = go.Figure()
        resultado = apply_dark_theme(fig)
        assert isinstance(resultado, go.Figure)


# =============================================================================
# grafico_evolucao_anual()
# =============================================================================

class TestGraficoEvolucaoAnual:

    def test_grafico_evolucao_df_vazio_retorna_figure(self):
        # ARRANGE
        df = pd.DataFrame()
        # ACT
        fig = grafico_evolucao_anual(df)
        # ASSERT
        assert isinstance(fig, go.Figure)

    def test_grafico_evolucao_df_vazio_tem_annotation_sem_dados(self):
        # ARRANGE + ACT
        fig = grafico_evolucao_anual(pd.DataFrame())
        # ASSERT
        textos = [a.text for a in fig.layout.annotations]
        assert any("Sem dados" in t for t in textos)

    def test_grafico_evolucao_df_valido_retorna_figure(self):
        fig = grafico_evolucao_anual(_df_evolucao())
        assert isinstance(fig, go.Figure)

    def test_grafico_evolucao_df_valido_tem_dois_traces(self):
        # Empenhado + Pago
        fig = grafico_evolucao_anual(_df_evolucao())
        assert len(fig.data) == 2

    def test_grafico_evolucao_df_valido_tem_titulo(self):
        fig = grafico_evolucao_anual(_df_evolucao())
        assert fig.layout.title.text is not None
        assert len(fig.layout.title.text) > 0


# =============================================================================
# grafico_barras_areas()
# =============================================================================

class TestGraficoBarrasAreas:

    def test_grafico_barras_areas_df_vazio_retorna_figure(self):
        fig = grafico_barras_areas(pd.DataFrame())
        assert isinstance(fig, go.Figure)

    def test_grafico_barras_areas_df_vazio_tem_annotation_sem_dados(self):
        fig = grafico_barras_areas(pd.DataFrame())
        textos = [a.text for a in fig.layout.annotations]
        assert any("Sem dados" in t for t in textos)

    def test_grafico_barras_areas_df_valido_retorna_figure(self):
        fig = grafico_barras_areas(_df_areas())
        assert isinstance(fig, go.Figure)

    def test_grafico_barras_areas_df_valido_tem_traces(self):
        fig = grafico_barras_areas(_df_areas())
        assert len(fig.data) > 0


# =============================================================================
# grafico_barras_areas_clusterizado()
# =============================================================================

class TestGraficoBarrasAreasClusterizado:

    def test_grafico_clusterizado_df_vazio_retorna_figure(self):
        fig = grafico_barras_areas_clusterizado(pd.DataFrame())
        assert isinstance(fig, go.Figure)

    def test_grafico_clusterizado_df_vazio_tem_annotation(self):
        fig = grafico_barras_areas_clusterizado(pd.DataFrame())
        textos = [a.text for a in fig.layout.annotations]
        assert any("Sem dados" in t for t in textos)

    def test_grafico_clusterizado_df_valido_tem_dois_traces(self):
        # Empenhado + Pago
        fig = grafico_barras_areas_clusterizado(_df_areas())
        assert len(fig.data) == 2


# =============================================================================
# grafico_barras_autores()
# =============================================================================

class TestGraficoBarrasAutores:

    def test_grafico_autores_df_vazio_retorna_figure(self):
        fig = grafico_barras_autores(pd.DataFrame())
        assert isinstance(fig, go.Figure)

    def test_grafico_autores_df_vazio_tem_annotation(self):
        fig = grafico_barras_autores(pd.DataFrame())
        textos = [a.text for a in fig.layout.annotations]
        assert any("Sem dados" in t for t in textos)

    def test_grafico_autores_df_valido_retorna_figure(self):
        fig = grafico_barras_autores(_df_autores())
        assert isinstance(fig, go.Figure)

    def test_grafico_autores_df_valido_tem_trace(self):
        fig = grafico_barras_autores(_df_autores())
        assert len(fig.data) > 0

    def test_grafico_autores_todos_sem_informacao_retorna_figure_vazio(self):
        # Caso especial: todos os autores são "Sem informação"
        fig = grafico_barras_autores(_df_autores_sem_informacao())
        assert isinstance(fig, go.Figure)
        textos = [a.text for a in fig.layout.annotations]
        assert any("Sem dados" in t for t in textos)


# =============================================================================
# grafico_pizza_areas() — delega para clusterizado
# =============================================================================

class TestGraficoPizzaAreas:

    def test_grafico_pizza_retorna_figure(self):
        fig = grafico_pizza_areas(_df_areas())
        assert isinstance(fig, go.Figure)

    def test_grafico_pizza_df_vazio_retorna_figure(self):
        fig = grafico_pizza_areas(pd.DataFrame())
        assert isinstance(fig, go.Figure)

    def test_grafico_pizza_com_dados_tem_traces(self):
        # Redireciona para clusterizado, que tem 2 traces
        fig = grafico_pizza_areas(_df_areas())
        assert len(fig.data) == 2
