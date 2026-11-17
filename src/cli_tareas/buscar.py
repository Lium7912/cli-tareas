from pathlib import Path

from rich.table import Table

from cli_tareas.ficheros import formatear_fecha, formatear_tamano, obtener_entradas


def normalizar_extension(extension: str) -> str:
    if extension and not extension.startswith("."):
        return "." + extension
    return extension


def buscar_entradas(
    ruta: Path,
    termino: str = "",
    extension: str = "",
) -> list[dict]:
    entradas = obtener_entradas(ruta, incluir_carpetas=True)
    termino = termino.lower()
    extension = normalizar_extension(extension).lower()
    resultados: list[dict] = []
    for entrada in entradas:
        if termino and termino not in entrada["nombre"].lower():
            continue
        if extension:
            if entrada["tipo"] == "carpeta":
                continue
            if Path(entrada["nombre"]).suffix.lower() != extension:
                continue
        resultados.append(entrada)
    return resultados


def limitar_resultados(entradas: list[dict], max_resultados: int | None) -> list[dict]:
    if max_resultados is None or max_resultados <= 0:
        return entradas
    return entradas[:max_resultados]


def construir_tabla_busqueda(entradas: list[dict], ruta: Path) -> Table:
    tabla = Table(title=f"Resultados de la búsqueda en {ruta}")
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
