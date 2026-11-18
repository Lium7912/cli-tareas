from pathlib import Path

import pytest
from typer.testing import CliRunner

import cli_tareas.acciones
from cli_tareas.main import app

runner = CliRunner()


def _invocar_listar_con_acciones(
    monkeypatch: pytest.MonkeyPatch, ruta_acciones: Path, args: list[str]
):
    monkeypatch.setattr(cli_tareas.acciones, "RUTA_ACCIONES", ruta_acciones)
    return runner.invoke(app, ["listar", *args])


def test_listar_muestra_contenido(
    carpeta_pruebas: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resultado = _invocar_listar_con_acciones(
        monkeypatch,
        cli_tareas.acciones.RUTA_ACCIONES,
        [str(carpeta_pruebas)],
    )
    assert resultado.exit_code == 0
    assert "a.txt" in resultado.output
    assert "b_largo.txt" in resultado.output
    assert "subcarpeta" in resultado.output
    assert "fichero" in resultado.output
    assert "carpeta" in resultado.output


def test_listar_ruta_predeterminada(
    monkeypatch: pytest.MonkeyPatch, acciones_temporales
) -> None:
    config = {
        "activa": True,
        "ruta_predeterminada": "~/pruebas-tareas",
        "incluir_carpetas": True,
        "ordenar_por": "nombre",
    }
    acciones_temporales("listar", config)
    resultado = _invocar_listar_con_acciones(
        monkeypatch, cli_tareas.acciones.RUTA_ACCIONES, []
    )
    assert resultado.exit_code == 0
    assert "pruebas-tareas" in resultado.output


def test_listar_ruta_inexistente(monkeypatch: pytest.MonkeyPatch) -> None:
    resultado = _invocar_listar_con_acciones(
        monkeypatch,
        cli_tareas.acciones.RUTA_ACCIONES,
        ["~/pruebas-tareas/no-existe-xyz"],
    )
    assert resultado.exit_code == 1
    assert "no existe" in resultado.output


def test_listar_es_fichero_no_carpeta(
    carpeta_pruebas: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resultado = _invocar_listar_con_acciones(
        monkeypatch,
        cli_tareas.acciones.RUTA_ACCIONES,
        [str(carpeta_pruebas / "a.txt")],
    )
    assert resultado.exit_code == 1
    assert "no es una carpeta" in resultado.output


def test_listar_accion_inactiva(acciones_inactivas: Path) -> None:
    resultado = runner.invoke(app, ["listar"])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output


def test_listar_simular(monkeypatch: pytest.MonkeyPatch) -> None:
    resultado = _invocar_listar_con_acciones(
        monkeypatch, cli_tareas.acciones.RUTA_ACCIONES, ["--simular"]
    )
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output
