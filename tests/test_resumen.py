from pathlib import Path

from typer.testing import CliRunner

from cli_tareas.main import app
from cli_tareas.resumen import calcular_resumen

runner = CliRunner()


def test_calcular_resumen(carpeta_contenido: Path) -> None:
    datos = calcular_resumen(carpeta_contenido)
    assert datos["ficheros"] == 3
    assert datos["carpetas"] == 1
    assert datos["tamano_total"] == 301
    assert datos["tipos"] == {".csv": 1, ".md": 1, ".txt": 1}


def test_resumen_cli(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(app, ["resumen", str(carpeta_contenido)])
    assert resultado.exit_code == 0
    assert "Ficheros" in resultado.output
    assert "301" in resultado.output
    assert ".txt" in resultado.output


def test_resumen_simular() -> None:
    resultado = runner.invoke(app, ["resumen", "--simular"])
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output


def test_resumen_ruta_inexistente() -> None:
    resultado = runner.invoke(app, ["resumen", "~/pruebas-tareas/no-existe-xyz"])
    assert resultado.exit_code == 1
    assert "no existe" in resultado.output


def test_resumen_es_fichero_no_carpeta(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(app, ["resumen", str(carpeta_contenido / "nota.md")])
    assert resultado.exit_code == 1
    assert "no es una carpeta" in resultado.output


def test_resumen_accion_desactivada(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales("resumen", {"activa": False})
    resultado = runner.invoke(app, ["resumen", str(carpeta_contenido)])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output
