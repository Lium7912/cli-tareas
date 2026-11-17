from pathlib import Path

from typer.testing import CliRunner

from cli_tareas.contar import contar_entradas
from cli_tareas.main import app

runner = CliRunner()


def test_contar_entradas_sin_carpetas(carpeta_contenido: Path) -> None:
    conteo = contar_entradas(carpeta_contenido, False)
    assert conteo == {"ficheros": 3, "carpetas": 0}


def test_contar_entradas_con_carpetas(carpeta_contenido: Path) -> None:
    conteo = contar_entradas(carpeta_contenido, True)
    assert conteo == {"ficheros": 3, "carpetas": 1}


def test_contar_cli(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(app, ["contar", str(carpeta_contenido)])
    assert resultado.exit_code == 0
    assert "Ficheros: 3" in resultado.output


def test_contar_cli_incluye_carpetas(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "contar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_contenido),
            "incluir_carpetas": True,
        },
    )
    resultado = runner.invoke(app, ["contar"])
    assert resultado.exit_code == 0
    assert "Ficheros: 3" in resultado.output
    assert "Carpetas: 1" in resultado.output


def test_contar_simular() -> None:
    resultado = runner.invoke(app, ["contar", "--simular"])
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output


def test_contar_ruta_inexistente() -> None:
    resultado = runner.invoke(app, ["contar", "~/pruebas-tareas/no-existe-xyz"])
    assert resultado.exit_code == 1
    assert "no existe" in resultado.output


def test_contar_es_fichero_no_carpeta(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(app, ["contar", str(carpeta_contenido / "informe.txt")])
    assert resultado.exit_code == 1
    assert "no es una carpeta" in resultado.output


def test_contar_accion_desactivada(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales("contar", {"activa": False})
    resultado = runner.invoke(app, ["contar", str(carpeta_contenido)])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output


def test_contar_config_invalida(carpeta_contenido: Path, acciones_temporales) -> None:
    acciones_temporales(
        "contar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_contenido),
            "incluir_carpetas": "sí",
        },
    )
    resultado = runner.invoke(app, ["contar"])
    assert resultado.exit_code == 1
    assert "Error" in resultado.output
