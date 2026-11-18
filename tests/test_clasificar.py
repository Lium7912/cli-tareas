import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import cli_tareas.main
from cli_tareas.clasificar import clasificar_determinista, normalizar_categoria
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
def ia_clasificacion_falsa(monkeypatch: pytest.MonkeyPatch):
    llamadas: list[dict] = []
    categorias = {
        ".pdf": "documentos",
        ".jpg": "imágenes",
        ".py": "código",
        ".csv": "datos",
        ".zip": "comprimidos",
    }

    def _falsa(meta: dict, config: dict) -> str:
        llamadas.append(meta)
        return categorias.get(Path(meta["nombre"]).suffix.lower(), "otros")

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
    monkeypatch.setattr(cli_tareas.main, "pedir_clasificacion", _falsa)
    return llamadas


@pytest.mark.parametrize(
    ("nombre", "esperada"),
    [
        ("informe.PDF", "documentos"),
        ("foto.jpg", "imágenes"),
        ("script.py", "código"),
        ("datos.csv", "datos"),
        ("paquete.zip", "comprimidos"),
        ("raro.xyz", "otros"),
        ("sin_extension", "otros"),
    ],
)
def test_clasificar_determinista_extensiones(nombre: str, esperada: str) -> None:
    assert clasificar_determinista({"nombre": nombre, "tipo": "fichero"}) == esperada


def test_clasificar_determinista_carpeta_otros() -> None:
    assert (
        clasificar_determinista({"nombre": "subcarpeta", "tipo": "carpeta"}) == "otros"
    )


@pytest.mark.parametrize(
    ("texto", "esperada"),
    [
        ("imágenes", "imágenes"),
        ("IMAGENES", "imágenes"),
        ("código", "código"),
        ("La categoría es: datos.", "datos"),
        ("no-categoria", "otros"),
        ("", "otros"),
    ],
)
def test_normalizar_categoria_ia(texto: str, esperada: str) -> None:
    assert normalizar_categoria(texto) == esperada


def test_clasificar_sin_ia(
    carpeta_clasificar: Path, sin_red, sin_env_ia, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--sin-ia"])
    assert resultado.exit_code == 0
    assert "determinista" in resultado.output
    assert "informe.pdf" in resultado.output
    assert "documentos" in resultado.output
    assert "imágenes" in resultado.output
    assert "comprimidos" in resultado.output


def test_clasificar_ia_mock(
    carpeta_clasificar: Path, sin_env_ia, ia_clasificacion_falsa, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar"])
    assert resultado.exit_code == 0
    assert "Clasificación (ia)" in resultado.output
    assert "Descripción" not in resultado.output
    assert len(ia_clasificacion_falsa) == 6
    claves = {"nombre", "tipo", "tamano", "modificado"}
    assert all(set(meta) == claves for meta in ia_clasificacion_falsa)
    assert "contenido-centinela" not in json.dumps(ia_clasificacion_falsa)


def test_clasificar_simular_sin_llamadas(
    carpeta_clasificar: Path, sin_red, sin_env_ia
) -> None:
    resultado = runner.invoke(app, ["clasificar", str(carpeta_clasificar), "--simular"])
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output
    assert "Se clasificarían los ficheros" in resultado.output


def test_clasificar_simular_json(carpeta_clasificar: Path, sin_red, sin_env_ia) -> None:
    resultado = runner.invoke(
        app, ["clasificar", str(carpeta_clasificar), "--simular", "--json"]
    )
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert datos["accion"] == "clasificar"
    assert datos["simulacion"] is True
    assert datos["ruta"] == str(carpeta_clasificar)


def test_clasificar_json_valido(
    carpeta_clasificar: Path, sin_red, sin_env_ia, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--json", "--sin-ia"])
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert datos["accion"] == "clasificar"
    assert datos["origen"] == "determinista"
    categorias = {f["nombre"]: f["categoria"] for f in datos["ficheros"]}
    assert categorias["informe.pdf"] == "documentos"
    assert categorias["foto.jpg"] == "imágenes"
    assert categorias["script.py"] == "código"
    assert categorias["datos.csv"] == "datos"
    assert categorias["paquete.zip"] == "comprimidos"
    assert categorias["raro.xyz"] == "otros"


def test_clasificar_ignora_carpetas(
    carpeta_clasificar: Path, sin_red, sin_env_ia, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--json", "--sin-ia"])
    assert resultado.exit_code == 0
    nombres = [f["nombre"] for f in json.loads(resultado.output)["ficheros"]]
    assert "subcarpeta" not in nombres
    assert "nota.txt" not in nombres


def test_clasificar_json_error_ruta(
    carpeta_clasificar: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    inexistente = carpeta_clasificar / "no-existe"
    resultado = runner.invoke(app, ["clasificar", str(inexistente), "--json"])
    assert resultado.exit_code == 1
    datos = json.loads(resultado.output)
    assert "error" in datos
    assert "no existe" in datos["error"]


def test_clasificar_ruta_inexistente(
    carpeta_clasificar: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    inexistente = carpeta_clasificar / "no-existe"
    resultado = runner.invoke(app, ["clasificar", str(inexistente)])
    assert resultado.exit_code == 1
    assert "La carpeta no existe" in resultado.output


def test_clasificar_json_error_ia(
    carpeta_clasificar: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    def _falla(meta: dict, config: dict) -> str:
        raise IANoDisponibleError("No hay conexión con el servicio de IA")

    monkeypatch.setattr(cli_tareas.main, "pedir_clasificacion", _falla)
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--json"])
    assert resultado.exit_code == 1
    datos = json.loads(resultado.output)
    assert "error" in datos
    assert "No hay conexión" in datos["error"]


def test_clasificar_sin_config(
    carpeta_clasificar: Path, sin_env_ia, sin_red, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar"])
    assert resultado.exit_code == 1
    assert "IA no configurada" in resultado.output
    assert "listar, contar, buscar, resumen" in resultado.output


def test_clasificar_accion_desactivada(
    carpeta_clasificar: Path, acciones_temporales
) -> None:
    acciones_temporales("clasificar", {"activa": False})
    resultado = runner.invoke(app, ["clasificar", str(carpeta_clasificar)])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output


def test_clasificar_max_ficheros(
    carpeta_clasificar: Path, sin_env_ia, ia_clasificacion_falsa, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_clasificar),
            "max_ficheros": 2,
        },
    )
    resultado = runner.invoke(app, ["clasificar", "--json"])
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert len(datos["ficheros"]) == 2
    assert len(ia_clasificacion_falsa) == 2


def test_clasificar_max_ficheros_invalido(
    carpeta_clasificar: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "clasificar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_clasificar),
            "max_ficheros": 0,
        },
    )
    resultado = runner.invoke(app, ["clasificar", str(carpeta_clasificar)])
    assert resultado.exit_code == 1
    assert "mayor que 0" in resultado.output


@pytest.mark.parametrize("timeout", ["no-es-numero", "0"])
def test_clasificar_timeout_invalido_texto(
    carpeta_clasificar: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    sin_red,
    acciones_temporales,
    timeout: str,
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", timeout)
    monkeypatch.setenv("TAREAS_API_KEY", "secreto-no-debe-aparecer")
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "TAREAS_IA_TIMEOUT" in resultado.output
    assert "secreto-no-debe-aparecer" not in resultado.output


@pytest.mark.parametrize("timeout", ["no-es-numero", "0"])
def test_clasificar_timeout_invalido_json(
    carpeta_clasificar: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    sin_red,
    acciones_temporales,
    timeout: str,
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", timeout)
    monkeypatch.setenv("TAREAS_API_KEY", "secreto-no-debe-aparecer")
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--json"])
    assert resultado.exit_code == 1
    assert "Traceback" not in resultado.output
    assert "TAREAS_IA_TIMEOUT" in json.loads(resultado.output)["error"]
    assert "secreto-no-debe-aparecer" not in resultado.output


def test_clasificar_ia_categoria_invalida(
    carpeta_clasificar: Path,
    env_ia,
    monkeypatch: pytest.MonkeyPatch,
    acciones_temporales,
) -> None:
    monkeypatch.setattr(
        cli_tareas.main, "pedir_clasificacion", lambda meta, config: "no-categoria"
    )
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--json"])
    assert resultado.exit_code == 0
    datos = json.loads(resultado.output)
    assert datos["origen"] == "ia"
    assert all(f["categoria"] == "otros" for f in datos["ficheros"])


def test_clasificar_no_lee_contenido(
    carpeta_clasificar: Path,
    monkeypatch: pytest.MonkeyPatch,
    sin_red,
    sin_env_ia,
    acciones_temporales,
) -> None:
    def _prohibido(*args, **kwargs):
        raise AssertionError("No se debe leer el contenido de los ficheros")

    monkeypatch.setattr(Path, "read_text", _prohibido)
    monkeypatch.setattr(Path, "read_bytes", _prohibido)
    acciones_temporales(
        "clasificar",
        {"activa": True, "ruta_predeterminada": str(carpeta_clasificar)},
    )
    resultado = runner.invoke(app, ["clasificar", "--sin-ia"])
    assert resultado.exit_code == 0
    assert "informe.pdf" in resultado.output
