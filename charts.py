"""
charts.py - Gráficos com tema escuro
"""

import plotly.graph_objects as go
import pandas as pd

# Cores do tema
COLORS = {
    'primary': '#3b82f6',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'purple': '#8b5cf6',
    'background': 'rgba(0,0,0,0)',
    'card': '#0f172a',
    'grid': '#1e3a5f',
    'text': '#94a3b8',
    'text_light': '#e2e8f0'
}

AREA_COLORS = [
    '#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ef4444',
    '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
    '#84cc16', '#a855f7'
]


def apply_dark_theme(fig):
    """Aplica tema escuro consistente a todos os gráficos."""
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'], family='Inter'),
        title_font=dict(color=COLORS['text_light'], size=14),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], size=11)
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            gridcolor=COLORS['grid'],
            linecolor=COLORS['grid'],
            tickfont=dict(color=COLORS['text'])
        ),
        yaxis=dict(
            gridcolor=COLORS['grid'],
            linecolor=COLORS['grid'],
            tickfont=dict(color=COLORS['text'])
        )
    )
    return fig


def grafico_evolucao_anual(df: pd.DataFrame) -> go.Figure:
    """Gráfico de linha: evolução temporal."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados disponíveis", showarrow=False,
                           font=dict(size=14, color=COLORS['text']))
        return apply_dark_theme(fig)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['ano'],
        y=df['valor_empenhado'],
        name='Empenhado',
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['primary']),
        hovertemplate='%{x}<br>Empenhado: R$ %{y:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df['ano'],
        y=df['valor_pago'],
        name='Pago',
        mode='lines+markers',
        line=dict(color=COLORS['success'], width=3),
        marker=dict(size=8, color=COLORS['success']),
        hovertemplate='%{x}<br>Pago: R$ %{y:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Evolução das Emendas por Ano',
        xaxis_title='Ano',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )
    return apply_dark_theme(fig)


def grafico_barras_areas_clusterizado(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras clusterizadas: Empenhado vs Pago por Área."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados disponíveis", showarrow=False,
                           font=dict(size=14, color=COLORS['text']))
        return apply_dark_theme(fig)

    df_top = df.head(8).copy()
    df_top = df_top.sort_values('valor_empenhado', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_top['area'],
        x=df_top['valor_empenhado'],
        name='Empenhado',
        orientation='h',
        marker_color=COLORS['primary'],
        text=df_top['valor_empenhado'].apply(lambda x: f'R$ {x/1e6:.1f}M'),
        textposition='outside',
        textfont=dict(size=10, color=COLORS['text']),
        hovertemplate='%{y}<br>Empenhado: R$ %{x:,.0f}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        y=df_top['area'],
        x=df_top['valor_pago'],
        name='Pago',
        orientation='h',
        marker_color=COLORS['success'],
        text=df_top['valor_pago'].apply(lambda x: f'R$ {x/1e6:.1f}M'),
        textposition='outside',
        textfont=dict(size=10, color=COLORS['text']),
        hovertemplate='%{y}<br>Pago: R$ %{x:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Distribuição por Área (Empenhado vs Pago)',
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        height=400
    )
    return apply_dark_theme(fig)


def grafico_barras_areas(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras horizontais: Top áreas."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados disponíveis", showarrow=False,
                           font=dict(size=14, color=COLORS['text']))
        return apply_dark_theme(fig)

    df_top = df.head(10).copy()
    df_top = df_top.sort_values('valor_empenhado', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_top['area'],
        x=df_top['valor_empenhado'],
        name='Empenhado',
        orientation='h',
        marker_color=COLORS['primary'],
        text=df_top['valor_empenhado'].apply(lambda x: f'R$ {x/1e6:.1f}M'),
        textposition='outside',
        textfont=dict(size=9, color=COLORS['text'])
    ))
    fig.add_trace(go.Bar(
        y=df_top['area'],
        x=df_top['valor_pago'],
        name='Pago',
        orientation='h',
        marker_color=COLORS['success'],
        text=df_top['valor_pago'].apply(lambda x: f'R$ {x/1e6:.1f}M'),
        textposition='outside',
        textfont=dict(size=9, color=COLORS['text'])
    ))
    fig.update_layout(
        title='Emendas por Área (Top 10)',
        barmode='group',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        height=400
    )
    return apply_dark_theme(fig)


def grafico_barras_autores(df: pd.DataFrame) -> go.Figure:
    """Gráfico de barras horizontais: Top parlamentares."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados disponíveis", showarrow=False,
                           font=dict(size=14, color=COLORS['text']))
        return apply_dark_theme(fig)

    # Remove "Sem informação"
    df_filtrado = df[~df['autor'].str.contains('Sem inform', case=False, na=False)].head(10)
    if df_filtrado.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados de autores", showarrow=False,
                           font=dict(size=14, color=COLORS['text']))
        return apply_dark_theme(fig)

    df_filtrado = df_filtrado.sort_values('valor_empenhado', ascending=True)
    fig = go.Figure(go.Bar(
        y=df_filtrado['autor'],
        x=df_filtrado['valor_empenhado'],
        orientation='h',
        marker_color=COLORS['purple'],
        text=df_filtrado['valor_empenhado'].apply(lambda x: f'R$ {x/1e6:.1f}M'),
        textposition='outside',
        textfont=dict(size=9, color=COLORS['text']),
        hovertemplate='%{y}<br>Valor: R$ %{x:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='Top Parlamentares por Valor Empenhado',
        height=400
    )
    return apply_dark_theme(fig)


# Mantém função antiga para compatibilidade, mas redireciona
def grafico_pizza_areas(df: pd.DataFrame) -> go.Figure:
    """Substitui pizza por barras clusterizadas."""
    return grafico_barras_areas_clusterizado(df)