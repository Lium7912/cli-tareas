import json
from pathlib import Path

from cli_tareas.excepciones import (
    AccionDesactivadaError,
    AccionNoDefinidaError,
    ConfiguracionInvalidaError,
)

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ACCIONES = RAIZ_PROYECTO / "acciones.json"

ESQUEMAS: dict[str, dict[str, type]] = {
    "listar": {
        "activa": bool,
        "descripcion": str,
        "ruta_predeterminada": str,
        "incluir_carpetas": bool,
        "ordenar_por": str,
    },
    "contar": {
        "activa": bool,
        "descripcion": str,
        "ruta_predeterminada": str,
        "incluir_carpetas": bool,
    },
    "buscar": {
        "activa": bool,
        "descripcion": str,
        "ruta_predeterminada": str,
        "max_resultados": int,
    },
    "resumen": {
        "activa": bool,
        "descripcion": str,
        "ruta_predeterminada": str,
    },
}

CLAVES_POSITIVAS = {"max_resultados"}


def cargar_acciones(ruta: Path | None = None) -> dict:
    ruta = ruta if ruta is not None else RUTA_ACCIONES
    try:
        with ruta.open(encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No existe el archivo de acciones: {ruta}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"acciones.json no es un JSON válido: {exc}") from exc
    if not isinstance(datos, dict):
        raise TypeError("acciones.json debe contener un objeto JSON")
    return datos


def obtener_config(nombre: str, acciones: dict) -> dict:
    config = acciones.get(nombre)
    if config is None:
        raise AccionNoDefinidaError(f"acciones.json no define la acción «{nombre}»")
    if not isinstance(config, dict):
        raise ConfiguracionInvalidaError(
            f"La configuración de «{nombre}» debe ser un objeto JSON"
        )
    if not isinstance(config.get("activa"), bool):
        raise ConfiguracionInvalidaError(
            f"La clave «activa» de «{nombre}» debe ser un booleano"
        )
    if not config["activa"]:
        raise AccionDesactivadaError(f"La acción «{nombre}» está desactivada")
    validar_config(nombre, config)
    return config


def validar_config(nombre: str, config: dict) -> None:
    esquema = ESQUEMAS.get(nombre, {})
    for clave, tipo in esquema.items():
        if clave not in config:
            continue
        valor = config[clave]
        if tipo is int and isinstance(valor, bool):
            raise ConfiguracionInvalidaError(
                f"La clave «{clave}» de «{nombre}» debe ser un entero"
            )
        if not isinstance(valor, tipo):
            raise ConfiguracionInvalidaError(
                f"La clave «{clave}» de «{nombre}» debe ser de tipo {tipo.__name__}"
            )
    for clave in CLAVES_POSITIVAS:
        valor = config.get(clave)
        if isinstance(valor, int) and not isinstance(valor, bool) and valor <= 0:
            raise ConfiguracionInvalidaError(
                f"La clave «{clave}» de «{nombre}» debe ser mayor que 0"
            )
