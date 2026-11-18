import pytest
from typer.testing import CliRunner

import cli_tareas.main
from cli_tareas import __version__
from cli_tareas.main import app

runner = CliRunner()


def test_version_muestra_numero() -> None:
    resultado = runner.invoke(app, ["version"])
    assert resultado.exit_code == 0
    assert __version__ in resultado.output
    assert "cli-tareas" in resultado.output


def test_opcion_version_muestra_numero() -> None:
    resultado = runner.invoke(app, ["--version"])
    assert resultado.exit_code == 0
    assert resultado.output.strip() == f"cli-tareas {__version__}"


def test_opcion_version_no_ejecuta_acciones(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _prohibida(*args, **kwargs):
        raise AssertionError("No se debe ejecutar ninguna acción ni llamada de red")

    monkeypatch.setattr(cli_tareas.main, "cargar_acciones", _prohibida)
    monkeypatch.setattr("urllib.request.urlopen", _prohibida)

    resultado = runner.invoke(app, ["--version"])

    assert resultado.exit_code == 0
    assert f"cli-tareas {__version__}" in resultado.output


def test_opcion_version_funciona_sin_entorno_ia(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TAREAS_API_BASE", raising=False)
    monkeypatch.delenv("TAREAS_MODELO", raising=False)
    monkeypatch.delenv("TAREAS_API_KEY", raising=False)

    resultado = runner.invoke(app, ["--version"])

    assert resultado.exit_code == 0
    assert f"cli-tareas {__version__}" in resultado.output


def test_ayuda_incluye_opcion_version() -> None:
    resultado = runner.invoke(app, ["--help"])
    assert resultado.exit_code == 0
    assert "--version" in resultado.output
