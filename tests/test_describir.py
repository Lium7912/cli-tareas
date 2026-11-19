import json
from pathlib import Path
from typing import Self

import pytest
from typer.testing import CliRunner

import cli_tareas.main
from cli_tareas.excepciones import IANoDisponibleError
from cli_tareas.main import app

runner = CliRunner()


@pytest.fixture
def sin_red(monkeypatch: pytest.MonkeyPatch):
    def _prohibida(*args, **kwargs):
        raise AssertionError("No se debe realizar ninguna llamada de red")

    monkeypatch.setattr("urllib.request.urlopen", _prohibida)


@pytest.fixture
def env_ia(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TAREAS_API_BASE", "http://localhost:9/v1")
    monkeypatch.setenv("TAREAS_MODELO", "modelo-prueba")


@pytest.fixture
def sin_env_ia(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("TAREAS_API_BASE", raising=False)
    monkeypatch.delenv("TAREAS_MODELO", raising=False)
    monkeypatch.delenv("TAREAS_API_KEY", raising=False)
    monkeypatch.delenv("TAREAS_IA_TIMEOUT", raising=False)


@pytest.fixture
def ia_falsa(monkeypatch: pytest.MonkeyPatch):
    llamadas: list[dict] = []

    def _falsa(meta: dict, config: dict) -> str:
        llamadas.append(meta)
        return f"Descripción de {meta['nombre']}"

    monkeypatch.setattr(
        cli_tareas.main,
        "configuracion_ia",
        lambda: {
            "api_base": "http://localhost:9/v1",
            "modelo": "modelo-prueba",
            "api_key": "",
            "timeout": 30.0,
        },
    )
    monkeypatch.setattr(cli_tareas.main, "pedir_descripcion", _falsa)
    return llamadas


def test_describir_simular_sin_llamadas(
    carpeta_contenido: Path, sin_red, sin_env_ia
) -> None:
    resultado = runner.invoke(app, ["describir", str(carpeta_contenido), "--simular"])
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output
    assert "Se describirían los ficheros" in resultado.output


def test_describir_simular_json(carpeta_contenido: Path, sin_red, sin_env_ia) -> None:
    resultado = runner.invoke(
        app, ["describir", str(carpeta_contenido), "--simular", "--json"]
    )
    assert resultado.exit_code == 0
    assert json.loads(resultado.output) == {
        "accion": "describir",
        "simulacion": True,
        "ruta": str(carpeta_contenido),
    }


class _RespuestaFalsa:
    def __init__(self, cuerpo: bytes) -> None:
        self._cuerpo = cuerpo

    def read(self) -> bytes:
        return self._cuerpo

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> bool:
        return False


def test_describir_respuesta_no_utf8_sin_traceback(
    carpeta_contenido: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *args, **kwargs: _RespuestaFalsa(b"\xff\xfe")
    )
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "UTF-8" in resultado.output


def test_describir_api_base_invalida_sin_traceback(
    carpeta_contenido: Path,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    monkeypatch.setenv("TAREAS_API_BASE", "no-es-url")
    monkeypatch.setenv("TAREAS_MODELO", "modelo-prueba")
    monkeypatch.delenv("TAREAS_IA_TIMEOUT", raising=False)
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "URL" in resultado.output


def test_describir_tabla_ia(
    carpeta_contenido: Path, sin_env_ia, ia_falsa, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 0
    assert "Descripción de informe.txt" in resultado.output
    assert "Descripciones (ia)" in resultado.output


def test_describir_json_valido(
    carpeta_contenido: Path, sin_env_ia, ia_falsa, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir", "--json"])
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert datos["accion"] == "describir"
    assert datos["origen"] == "ia"
    nombres = [f["nombre"] for f in datos["ficheros"]]
    assert "informe.txt" in nombres
    assert "datos.csv" in nombres


def test_describir_json_error_sin_red(
    carpeta_contenido: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    def _falla(meta: dict, config: dict) -> str:
        raise IANoDisponibleError("No hay conexión con el servicio de IA")

    monkeypatch.setattr(cli_tareas.main, "pedir_descripcion", _falla)
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir", "--json"])
    assert resultado.exit_code == 1
    datos = json.loads(resultado.output)
    assert "error" in datos
    assert "No hay conexión" in datos["error"]


def test_describir_sin_config(
    carpeta_contenido: Path, sin_env_ia, sin_red, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 1
    assert "IA no configurada" in resultado.output
    assert "listar, contar, buscar, resumen" in resultado.output


def test_describir_sin_red_mensaje(
    carpeta_contenido: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    def _falla(meta: dict, config: dict) -> str:
        raise IANoDisponibleError("No hay conexión con el servicio de IA")

    monkeypatch.setattr(cli_tareas.main, "pedir_descripcion", _falla)
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 1
    assert "No hay conexión con el servicio de IA" in resultado.output
    assert "--sin-ia" in resultado.output


def test_describir_sin_ia(
    carpeta_contenido: Path, sin_red, sin_env_ia, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir", "--sin-ia"])
    assert resultado.exit_code == 0
    assert "determinista" in resultado.output
    assert "informe.txt" in resultado.output
    assert "fichero de texto" in resultado.output


def test_describir_max_ficheros(
    carpeta_contenido: Path, sin_env_ia, ia_falsa, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_contenido),
            "max_ficheros": 2,
        },
    )
    resultado = runner.invoke(app, ["describir", "--json"])
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert len(datos["ficheros"]) == 2
    assert len(ia_falsa) == 2


def test_describir_accion_desactivada(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales("describir", {"activa": False})
    resultado = runner.invoke(app, ["describir", str(carpeta_contenido)])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output


def test_describir_max_ficheros_invalido(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "describir",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_contenido),
            "max_ficheros": 0,
        },
    )
    resultado = runner.invoke(app, ["describir", str(carpeta_contenido)])
    assert resultado.exit_code == 1
    assert "mayor que 0" in resultado.output


@pytest.mark.parametrize("timeout", ["no-es-numero", "0"])
def test_describir_timeout_invalido_texto(
    carpeta_contenido: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    sin_red,
    acciones_temporales,
    timeout: str,
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", timeout)
    monkeypatch.setenv("TAREAS_API_KEY", "secreto-no-debe-aparecer")
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "TAREAS_IA_TIMEOUT" in resultado.output
    assert "secreto-no-debe-aparecer" not in resultado.output


@pytest.mark.parametrize("timeout", ["no-es-numero", "0"])
def test_describir_timeout_invalido_json(
    carpeta_contenido: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    sin_red,
    acciones_temporales,
    timeout: str,
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", timeout)
    monkeypatch.setenv("TAREAS_API_KEY", "secreto-no-debe-aparecer")
    acciones_temporales(
        "describir",
        {"activa": True, "ruta_predeterminada": str(carpeta_contenido)},
    )
    resultado = runner.invoke(app, ["describir", "--json"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "TAREAS_IA_TIMEOUT" in json.loads(resultado.output)["error"]
    assert "secreto-no-debe-aparecer" not in resultado.output
