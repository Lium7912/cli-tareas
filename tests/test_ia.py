import json
import urllib.error
from typing import Self

import pytest

import cli_tareas.ia
from cli_tareas.excepciones import ConfiguracionInvalidaError, IANoDisponibleError
from cli_tareas.ia import (
    TIMEOUT_DEFECTO,
    configuracion_ia,
    construir_prompt_clasificacion,
    pedir_clasificacion,
    pedir_descripcion,
)

META = {
    "nombre": "informe.txt",
    "tipo": "fichero",
    "tamano": 100,
    "modificado": "2024-01-01 10:00",
}


class RespuestaFalsa:
    def __init__(self, cuerpo: bytes) -> None:
        self._cuerpo = cuerpo

    def read(self) -> bytes:
        return self._cuerpo

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> bool:
        return False


def _cuerpo_respuesta(texto: str) -> bytes:
    return json.dumps({"choices": [{"message": {"content": texto}}]}).encode("utf-8")


@pytest.fixture
def env_ia(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAREAS_API_BASE", "http://localhost:9/v1/")
    monkeypatch.setenv("TAREAS_MODELO", "modelo-prueba")
    monkeypatch.delenv("TAREAS_API_KEY", raising=False)
    monkeypatch.delenv("TAREAS_IA_TIMEOUT", raising=False)


@pytest.fixture
def config_ia() -> dict:
    return {
        "api_base": "http://localhost:9/v1",
        "modelo": "modelo-prueba",
        "api_key": "",
        "timeout": 2.5,
    }


@pytest.fixture
def urlopen_ok(monkeypatch: pytest.MonkeyPatch):
    llamadas: list[dict] = []

    def _montar(cuerpo: bytes) -> list[dict]:
        def _urlopen(peticion, timeout=None):
            llamadas.append({"peticion": peticion, "timeout": timeout})
            return RespuestaFalsa(cuerpo)

        monkeypatch.setattr(cli_tareas.ia.urllib.request, "urlopen", _urlopen)
        return llamadas

    return _montar


@pytest.fixture
def urlopen_error(monkeypatch: pytest.MonkeyPatch):
    def _montar(error: BaseException) -> None:
        def _urlopen(peticion, timeout=None):
            raise error

        monkeypatch.setattr(cli_tareas.ia.urllib.request, "urlopen", _urlopen)

    return _montar


def test_configuracion_ia_por_defecto(env_ia) -> None:
    assert configuracion_ia() == {
        "api_base": "http://localhost:9/v1",
        "modelo": "modelo-prueba",
        "api_key": "",
        "timeout": TIMEOUT_DEFECTO,
    }


def test_configuracion_ia_timeout_valido(
    env_ia, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", "5")
    assert configuracion_ia()["timeout"] == 5.0


@pytest.mark.parametrize("valor", ["abc", "0", "-1", "nan", "inf"])
def test_configuracion_ia_timeout_invalido(
    env_ia, monkeypatch: pytest.MonkeyPatch, valor: str
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", valor)
    with pytest.raises(ConfiguracionInvalidaError, match="mayor que 0"):
        configuracion_ia()


@pytest.mark.parametrize("valor", ["", "   ", "\t"])
def test_configuracion_ia_timeout_vacio_usa_defecto(
    env_ia, monkeypatch: pytest.MonkeyPatch, valor: str
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", valor)
    assert configuracion_ia()["timeout"] == TIMEOUT_DEFECTO


def test_configuracion_ia_sin_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAREAS_API_BASE", raising=False)
    monkeypatch.delenv("TAREAS_MODELO", raising=False)
    with pytest.raises(IANoDisponibleError, match="IA no configurada"):
        configuracion_ia()


def test_pedir_descripcion_respuesta_valida(urlopen_ok, config_ia) -> None:
    llamadas = urlopen_ok(_cuerpo_respuesta("  descripción breve  "))

    assert pedir_descripcion(META, config_ia) == "descripción breve"
    assert len(llamadas) == 1
    assert llamadas[0]["timeout"] == 2.5

    peticion = llamadas[0]["peticion"]
    assert peticion.full_url == "http://localhost:9/v1/chat/completions"
    assert peticion.get_method() == "POST"
    assert peticion.get_header("Content-type") == "application/json"
    assert peticion.get_header("Authorization") is None

    cuerpo = json.loads(peticion.data.decode("utf-8"))
    assert cuerpo["model"] == "modelo-prueba"
    assert cuerpo["temperature"] == 0.2
    assert [mensaje["role"] for mensaje in cuerpo["messages"]] == ["system", "user"]
    assert "informe.txt" in cuerpo["messages"][1]["content"]


def test_pedir_descripcion_incluye_api_key(urlopen_ok, config_ia) -> None:
    llamadas = urlopen_ok(_cuerpo_respuesta("texto"))
    config = {**config_ia, "api_key": "clave-prueba"}

    pedir_descripcion(META, config)

    peticion = llamadas[0]["peticion"]
    assert peticion.get_header("Authorization") == "Bearer clave-prueba"
    assert "clave-prueba" not in peticion.full_url


def test_pedir_clasificacion_respuesta_valida(urlopen_ok, config_ia) -> None:
    llamadas = urlopen_ok(_cuerpo_respuesta("documentos"))

    assert pedir_clasificacion(META, config_ia) == "documentos"

    cuerpo = json.loads(llamadas[0]["peticion"].data.decode("utf-8"))
    prompt = cuerpo["messages"][1]["content"]
    assert "«informe.txt»" in prompt
    assert "documentos, imágenes, código" in prompt


def test_construir_prompt_clasificacion_trunca_nombre() -> None:
    prompt = construir_prompt_clasificacion({**META, "nombre": "a" * 300})

    assert "a" * 200 in prompt
    assert "a" * 201 not in prompt


@pytest.mark.parametrize(
    ("codigo", "mensaje"),
    [
        (401, "autenticación"),
        (403, "autenticación"),
        (500, "código 500"),
    ],
)
def test_error_http(urlopen_error, config_ia, codigo: int, mensaje: str) -> None:
    urlopen_error(
        urllib.error.HTTPError(
            "http://localhost:9/v1/chat/completions",
            codigo,
            "error",
            {},
            None,
        )
    )

    with pytest.raises(IANoDisponibleError, match=mensaje):
        pedir_descripcion(META, config_ia)


@pytest.mark.parametrize(
    "error",
    [
        urllib.error.URLError("sin ruta al servidor"),
        TimeoutError("tiempo agotado"),
    ],
)
def test_error_conexion(urlopen_error, config_ia, error: BaseException) -> None:
    urlopen_error(error)

    with pytest.raises(IANoDisponibleError, match="No hay conexión"):
        pedir_descripcion(META, config_ia)


def test_respuesta_json_invalida(urlopen_ok, config_ia) -> None:
    urlopen_ok(b"esto no es json")

    with pytest.raises(IANoDisponibleError, match="no es JSON válido"):
        pedir_descripcion(META, config_ia)


def test_respuesta_no_utf8(urlopen_ok, config_ia) -> None:
    urlopen_ok(b"\xff\xfe")

    with pytest.raises(IANoDisponibleError, match="UTF-8"):
        pedir_descripcion(META, config_ia)


def test_url_invalida(config_ia) -> None:
    config = {**config_ia, "api_base": "no-es-url", "api_key": "clave-secreta"}

    with pytest.raises(ConfiguracionInvalidaError, match="URL") as excinfo:
        pedir_descripcion(META, config)

    assert "clave-secreta" not in str(excinfo.value)


@pytest.mark.parametrize(
    "cuerpo",
    [
        b"{}",
        b"[]",
        b'"texto"',
        b"null",
        b'{"choices": []}',
        b'{"choices": [{}]}',
        b'{"choices": [{"message": {}}]}',
        b'{"choices": [{"message": {"content": null}}]}',
    ],
)
def test_respuesta_formato_inesperado(urlopen_ok, config_ia, cuerpo: bytes) -> None:
    urlopen_ok(cuerpo)

    with pytest.raises(IANoDisponibleError, match="formato esperado"):
        pedir_descripcion(META, config_ia)


@pytest.mark.parametrize("contenido", ["", "   ", "\n\t"])
def test_descripcion_vacia(urlopen_ok, config_ia, contenido: str) -> None:
    urlopen_ok(_cuerpo_respuesta(contenido))

    with pytest.raises(IANoDisponibleError, match="descripción vacía"):
        pedir_descripcion(META, config_ia)


def test_categoria_vacia(urlopen_ok, config_ia) -> None:
    urlopen_ok(_cuerpo_respuesta("  "))

    with pytest.raises(IANoDisponibleError, match="categoría vacía"):
        pedir_clasificacion(META, config_ia)


def test_error_http_no_expone_api_key(urlopen_error, config_ia) -> None:
    config = {**config_ia, "api_key": "clave-secreta-no-debe-salir"}
    urlopen_error(
        urllib.error.HTTPError(
            "http://localhost:9/v1/chat/completions",
            401,
            "Unauthorized",
            {},
            None,
        )
    )

    with pytest.raises(IANoDisponibleError) as excinfo:
        pedir_descripcion(META, config)

    assert "clave-secreta-no-debe-salir" not in str(excinfo.value)
    assert "clave-secreta-no-debe-salir" not in repr(excinfo.value)


def test_respuesta_con_acentos(urlopen_ok, config_ia) -> None:
    urlopen_ok(_cuerpo_respuesta("Clasificación de documentos"))

    assert pedir_descripcion(META, config_ia) == "Clasificación de documentos"
