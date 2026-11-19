from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli_tareas.acciones import cargar_acciones, obtener_config
from cli_tareas.excepciones import (
    AccionDesactivadaError,
    AccionNoDefinidaError,
    ConfiguracionInvalidaError,
)
from cli_tareas.ficheros import ordenar_entradas, resolver_ruta
from cli_tareas.main import app

runner = CliRunner()


def test_cargar_acciones_valido() -> None:
    acciones = cargar_acciones()
    for nombre in ("listar", "contar", "buscar", "resumen"):
        assert isinstance(acciones[nombre], dict)


def test_cargar_acciones_json_invalido(carpeta_temporal: Path) -> None:
    ruta = carpeta_temporal / "acciones.json"
    ruta.write_text("{ no válido", encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_acciones(ruta)


def test_cargar_acciones_inexistente(carpeta_temporal: Path) -> None:
    with pytest.raises(FileNotFoundError):
        cargar_acciones(carpeta_temporal / "no-existe.json")


def test_cargar_acciones_no_objeto(carpeta_temporal: Path) -> None:
    ruta = carpeta_temporal / "acciones.json"
    ruta.write_text("[]", encoding="utf-8")
    with pytest.raises(TypeError):
        cargar_acciones(ruta)


def test_config_accion_no_definida() -> None:
    with pytest.raises(AccionNoDefinidaError):
        obtener_config("contar", {})


def test_config_accion_desactivada() -> None:
    with pytest.raises(AccionDesactivadaError):
        obtener_config("contar", {"contar": {"activa": False}})


def test_config_accion_no_objeto() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        obtener_config("contar", {"contar": "texto"})


def test_config_activa_no_bool() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        obtener_config("contar", {"contar": {"activa": "sí"}})


def test_config_tipo_invalido() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        obtener_config("contar", {"contar": {"activa": True, "incluir_carpetas": "sí"}})


def test_config_max_resultados_invalido() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        obtener_config("buscar", {"buscar": {"activa": True, "max_resultados": 0}})


def test_config_valida_devuelve_dict() -> None:
    config = obtener_config("contar", {"contar": {"activa": True}})
    assert config["activa"] is True


def test_config_clave_desconocida() -> None:
    with pytest.raises(ConfiguracionInvalidaError, match="desconocida"):
        obtener_config("contar", {"contar": {"activa": True, "clave_extra": 1}})


def test_config_accion_sin_esquema() -> None:
    with pytest.raises(ConfiguracionInvalidaError, match="esquema"):
        obtener_config("inexistente", {"inexistente": {"activa": True}})


def test_config_ordenar_por_invalido() -> None:
    with pytest.raises(ConfiguracionInvalidaError, match="ordenar_por"):
        obtener_config("listar", {"listar": {"activa": True, "ordenar_por": "peso"}})


@pytest.mark.parametrize(
    ("nombre", "esperados"),
    [
        ("listar", {"incluir_carpetas": True, "ordenar_por": "nombre"}),
        ("contar", {"incluir_carpetas": False}),
        ("buscar", {"max_resultados": None}),
        ("describir", {"max_ficheros": 10}),
        ("clasificar", {"max_ficheros": 10}),
    ],
)
def test_config_aplica_predeterminados(nombre: str, esperados: dict) -> None:
    config = obtener_config(nombre, {nombre: {"activa": True}})
    for clave, valor in esperados.items():
        assert config[clave] == valor


def test_config_valores_explicitos_prevalecen() -> None:
    config = obtener_config(
        "listar",
        {
            "listar": {
                "activa": True,
                "incluir_carpetas": False,
                "ordenar_por": "tamano",
            }
        },
    )
    assert config["incluir_carpetas"] is False
    assert config["ordenar_por"] == "tamano"


def test_cli_config_clave_desconocida(
    carpeta_temporal: Path, acciones_temporales
) -> None:
    acciones_temporales(
        "contar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_temporal),
            "clave_extra": 1,
        },
    )
    resultado = runner.invoke(app, ["contar"])
    assert resultado.exit_code == 1
    assert "desconocida" in resultado.output.lower()


def test_resolver_ruta_predeterminada(carpeta_temporal: Path) -> None:
    config = {"ruta_predeterminada": str(carpeta_temporal)}
    assert resolver_ruta(config, None) == carpeta_temporal


def test_resolver_ruta_indicada(carpeta_temporal: Path) -> None:
    config = {"ruta_predeterminada": "~/pruebas-tareas"}
    assert resolver_ruta(config, carpeta_temporal) == carpeta_temporal


def test_resolver_ruta_sin_predeterminada() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        resolver_ruta({}, None)


def test_ordenar_entradas_por_tamano() -> None:
    entradas = [
        {"nombre": "a", "tipo": "fichero", "tamano": 100, "modificado": None},
        {"nombre": "b", "tipo": "fichero", "tamano": 10, "modificado": None},
    ]
    ordenadas = ordenar_entradas(entradas, "tamano")
    assert ordenadas[0]["nombre"] == "b"


def test_ordenar_entradas_clave_invalida() -> None:
    with pytest.raises(ConfiguracionInvalidaError):
        ordenar_entradas([], "no-existe")
