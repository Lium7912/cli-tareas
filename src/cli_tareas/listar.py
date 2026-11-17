import json
from datetime import datetime
from pathlib import Path

from rich.table import Table

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_ACCIONES = RAIZ_PROYECTO / "acciones.json"


class AccionDesactivadaError(Exception):
    pass


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


def obtener_config_listar(acciones: dict) -> dict:
    config = acciones.get("listar")
    if config is None:
        raise ValueError("acciones.json no define la acción «listar»")
    if not isinstance(config, dict):
        raise TypeError("La configuración de «listar» debe ser un objeto JSON")
    if not config.get("activa", False):
        raise AccionDesactivadaError("La acción «listar» está desactivada")
    return config


def resolver_ruta(config: dict, ruta: Path | None) -> Path:
    if ruta is not None:
        return ruta.expanduser()
    predeterminada = config.get("ruta_predeterminada", "")
    if not predeterminada:
        raise ValueError("No hay ruta indicada ni ruta_predeterminada en acciones.json")
    return Path(predeterminada).expanduser()


def obtener_entradas(ruta: Path, incluir_carpetas: bool) -> list[dict]:
    if not ruta.exists():
        raise FileNotFoundError(f"La carpeta no existe: {ruta}")
    if not ruta.is_dir():
        raise NotADirectoryError(f"La ruta no es una carpeta: {ruta}")

    entradas: list[dict] = []
    try:
        for entrada in ruta.iterdir():
            es_carpeta = entrada.is_dir()
            info = entrada.stat()
            if es_carpeta and not incluir_carpetas:
                continue
            entradas.append(
                {
                    "nombre": entrada.name,
                    "tipo": "carpeta" if es_carpeta else "fichero",
                    "tamano": info.st_size,
                    "modificado": datetime.fromtimestamp(info.st_mtime),
                }
            )
    except PermissionError as exc:
        raise PermissionError(f"Sin permisos para leer la carpeta: {ruta}") from exc
    return entradas


def ordenar_entradas(entradas: list[dict], clave: str = "nombre") -> list[dict]:
    claves_validas = {"nombre", "tamano", "modificado", "tipo"}
    if clave not in claves_validas:
        raise ValueError(f"Clave de ordenación no válida: {clave}")
    return sorted(
        entradas, key=lambda e: str(e[clave]).lower() if clave == "nombre" else e[clave]
    )


def formatear_fecha(momento: datetime) -> str:
    return momento.strftime("%Y-%m-%d %H:%M")


def formatear_tamano(tamano: int) -> str:
    return f"{tamano:,}".replace(",", ".")


def construir_tabla(entradas: list[dict], ruta: Path) -> Table:
    tabla = Table(title=f"Contenido de {ruta}")
    tabla.add_column("Nombre", style="cyan", no_wrap=True)
    tabla.add_column("Tipo")
    tabla.add_column("Tamaño (B)", justify="right")
    tabla.add_column("Modificado")
    for entrada in entradas:
        tabla.add_row(
            entrada["nombre"],
            entrada["tipo"],
            formatear_tamano(entrada["tamano"]),
            formatear_fecha(entrada["modificado"]),
        )
    return tabla
