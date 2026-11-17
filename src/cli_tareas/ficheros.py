from datetime import datetime
from pathlib import Path

from cli_tareas.excepciones import ConfiguracionInvalidaError, RutaInvalidaError


def resolver_ruta(config: dict, ruta: Path | None) -> Path:
    if ruta is not None:
        return ruta.expanduser()
    predeterminada = config.get("ruta_predeterminada", "")
    if not predeterminada:
        raise ConfiguracionInvalidaError(
            "No hay ruta indicada ni ruta_predeterminada en acciones.json"
        )
    return Path(predeterminada).expanduser()


def validar_carpeta(ruta: Path) -> None:
    if not ruta.exists():
        raise RutaInvalidaError(f"La carpeta no existe: {ruta}")
    if not ruta.is_dir():
        raise RutaInvalidaError(f"La ruta no es una carpeta: {ruta}")


def obtener_entradas(ruta: Path, incluir_carpetas: bool) -> list[dict]:
    validar_carpeta(ruta)
    entradas: list[dict] = []
    try:
        for entrada in ruta.iterdir():
            es_carpeta = entrada.is_dir()
            if es_carpeta and not incluir_carpetas:
                continue
            info = entrada.stat()
            entradas.append(
                {
                    "nombre": entrada.name,
                    "tipo": "carpeta" if es_carpeta else "fichero",
                    "tamano": info.st_size,
                    "modificado": datetime.fromtimestamp(info.st_mtime),
                }
            )
    except PermissionError as exc:
        raise RutaInvalidaError(f"Sin permisos para leer la carpeta: {ruta}") from exc
    return entradas


def ordenar_entradas(entradas: list[dict], clave: str = "nombre") -> list[dict]:
    claves_validas = {"nombre", "tamano", "modificado", "tipo"}
    if clave not in claves_validas:
        raise ConfiguracionInvalidaError(f"Clave de ordenación no válida: {clave}")
    return sorted(
        entradas, key=lambda e: str(e[clave]).lower() if clave == "nombre" else e[clave]
    )


def formatear_fecha(momento: datetime) -> str:
    return momento.strftime("%Y-%m-%d %H:%M")


def formatear_tamano(tamano: int) -> str:
    return f"{tamano:,}".replace(",", ".")
