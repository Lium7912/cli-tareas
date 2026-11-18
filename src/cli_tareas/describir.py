import json
from pathlib import Path

from rich.table import Table

from cli_tareas.ficheros import formatear_tamano


def describir_determinista(meta: dict) -> str:
    nombre = str(meta["nombre"])
    fecha = str(meta["modificado"])
    if meta["tipo"] == "carpeta":
        return f"«{nombre}»: carpeta, modificada el {fecha}"
    extension = Path(nombre).suffix.lower().lstrip(".") or "sin extensión"
    clases = {
        "txt": "un fichero de texto",
        "md": "un documento Markdown",
        "pdf": "un documento PDF",
        "csv": "un fichero de datos CSV",
        "jpg": "una imagen JPEG",
        "jpeg": "una imagen JPEG",
        "png": "una imagen PNG",
    }
    clase = clases.get(extension, f"un fichero {extension}")
    return f"«{nombre}»: {clase} de {formatear_tamano(int(meta['tamano']))} B, modificado el {fecha}"


def construir_tabla_descripciones(filas: list[dict], ruta: Path, origen: str) -> Table:
    tabla = Table(title=f"Descripciones ({origen}) de {ruta}")
    tabla.add_column("Fichero")
    tabla.add_column("Descripción")
    for fila in filas:
        tabla.add_row(fila["nombre"], fila["descripcion"])
    return tabla


def construir_salida_json(filas: list[dict], ruta: Path, origen: str) -> str:
    datos = {
        "accion": "describir",
        "ruta": str(ruta),
        "origen": origen,
        "ficheros": filas,
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)
