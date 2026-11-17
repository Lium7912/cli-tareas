from pathlib import Path

import pytest

from cli_tareas.listar import (
    AccionDesactivadaError,
    cargar_acciones,
    obtener_config_listar,
    ordenar_entradas,
    resolver_ruta,
)


def test_cargar_acciones_valido() -> None:
    acciones = cargar_acciones()
    assert "listar" in acciones
    assert isinstance(acciones["listar"], dict)


def test_cargar_acciones_json_invalido(tmp_path: Path) -> None:
    ruta = tmp_path / "acciones.json"
    ruta.write_text("{ no válido", encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_acciones(ruta)


def test_cargar_acciones_inexistente(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        cargar_acciones(tmp_path / "no-existe.json")


def test_config_listar_desactivada(tmp_path: Path) -> None:
    with pytest.raises(AccionDesactivadaError):
        obtener_config_listar({"listar": {"activa": False}})


def test_config_listar_sin_clave() -> None:
    with pytest.raises(ValueError):
        obtener_config_listar({})


def test_resolver_ruta_predeterminada(tmp_path: Path) -> None:
    config = {"ruta_predeterminada": str(tmp_path)}
    assert resolver_ruta(config, None) == tmp_path


def test_resolver_ruta_indicada(tmp_path: Path) -> None:
    config = {"ruta_predeterminada": "~/pruebas-tareas"}
    assert resolver_ruta(config, tmp_path) == tmp_path


def test_ordenar_entradas_por_tamano() -> None:
    entradas = [
        {"nombre": "a", "tipo": "fichero", "tamano": 100, "modificado": None},
        {"nombre": "b", "tipo": "fichero", "tamano": 10, "modificado": None},
    ]
    ordenadas = ordenar_entradas(entradas, "tamano")
    assert ordenadas[0]["nombre"] == "b"


def test_ordenar_entradas_clave_invalida() -> None:
    with pytest.raises(ValueError):
        ordenar_entradas([], "no-existe")
