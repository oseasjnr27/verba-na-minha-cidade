# test_app_structure.py — Verifica propriedades estruturais de app.py via AST.
# Não executa o app nem depende de mocks externos.
# Captura regressões onde widgets Streamlit ficam sem key= (BUG #14).

import ast
import pathlib


APP_PATH = pathlib.Path(__file__).parent.parent / "app.py"


def _get_plotly_chart_calls(source: str) -> list[ast.Call]:
    """Retorna todos os nós AST de chamadas a st.plotly_chart."""
    tree = ast.parse(source)
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "plotly_chart"
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            calls.append(node)
    return calls


class TestPlotlyChartKeys:

    def setup_method(self):
        self.source = APP_PATH.read_text(encoding="utf-8")
        self.calls = _get_plotly_chart_calls(self.source)

    def test_existe_ao_menos_um_grafico_plotly(self):
        assert len(self.calls) >= 1, "Nenhum st.plotly_chart encontrado em app.py"

    def test_todo_plotly_chart_tem_parametro_key(self):
        sem_key = []
        for call in self.calls:
            keywords = {kw.arg for kw in call.keywords}
            if "key" not in keywords:
                sem_key.append(ast.get_source_segment(self.source, call))
        assert sem_key == [], (
            f"st.plotly_chart sem key= encontrado(s):\n" + "\n".join(str(s) for s in sem_key)
        )

    def test_chaves_dos_graficos_sao_unicas(self):
        keys = []
        for call in self.calls:
            for kw in call.keywords:
                if kw.arg == "key" and isinstance(kw.value, ast.Constant):
                    keys.append(kw.value.value)
        assert len(keys) == len(set(keys)), (
            f"Keys duplicadas em st.plotly_chart: {[k for k in keys if keys.count(k) > 1]}"
        )
