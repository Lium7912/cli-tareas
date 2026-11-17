from pathlib import Path

from rich.table import Table

from cli_tareas.ficheros import formatear_fecha, formatear_tamano


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
