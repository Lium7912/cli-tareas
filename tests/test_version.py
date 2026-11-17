from typer.testing import CliRunner

from cli_tareas import __version__
from cli_tareas.main import app

runner = CliRunner()


def test_version_muestra_numero() -> None:
    resultado = runner.invoke(app, ["version"])
    assert resultado.exit_code == 0
    assert __version__ in resultado.output
    assert "cli-tareas" in resultado.output
