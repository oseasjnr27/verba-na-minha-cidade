# test_styles.py — Testa o design system e injeção de CSS.
# Cobre: CUSTOM_CSS (conteúdo), aplicar_estilos() (comportamento).
# Cenários: CSS não-vazio, classes esperadas presentes, st.markdown chamado corretamente.
# BUG #4 — CSS nunca era injetado no app.

from unittest.mock import MagicMock
from styles import CUSTOM_CSS, aplicar_estilos


# =============================================================================
# CUSTOM_CSS — conteúdo
# =============================================================================

class TestCustomCss:

    def test_custom_css_nao_esta_vazio(self):
        # ARRANGE + ACT + ASSERT
        assert isinstance(CUSTOM_CSS, str)
        assert len(CUSTOM_CSS.strip()) > 0

    def test_custom_css_contem_tag_style(self):
        assert "<style>" in CUSTOM_CSS

    def test_custom_css_contem_classe_kpi_card(self):
        assert ".kpi-card" in CUSTOM_CSS

    def test_custom_css_contem_classe_ai_card(self):
        assert ".ai-card" in CUSTOM_CSS


# =============================================================================
# aplicar_estilos() — comportamento
# =============================================================================

class TestAplicarEstilos:

    def test_aplicar_estilos_chama_st_markdown(self):
        # ARRANGE
        mock_st = MagicMock()
        # ACT
        aplicar_estilos(mock_st)
        # ASSERT
        mock_st.markdown.assert_called_once()

    def test_aplicar_estilos_passa_unsafe_allow_html_true(self):
        # ARRANGE
        mock_st = MagicMock()
        # ACT
        aplicar_estilos(mock_st)
        # ASSERT
        _, kwargs = mock_st.markdown.call_args
        assert kwargs.get("unsafe_allow_html") is True
