from collections import Counter
from pathlib import Path

from rich.table import Table

from cli_tareas.ficheros import formatear_tamano, obtener_entradas


def calcular_resumen(ruta: Path) -> dict:
    entradas = obtener_entradas(ruta, incluir_carpetas=True)
    ficheros = [entrada for entrada in entradas if entrada["tipo"] == "fichero"]
    tipos = Counter(
        Path(entrada["nombre"]).suffix.lower() or "(sin extensión)"
        for entrada in ficheros
    )
    return {
        "ficheros": len(ficheros),
        "carpetas": len(entradas) - len(ficheros),
        "tipos": dict(sorted(tipos.items())),
        "tamano_total": sum(entrada["tamano"] for entrada in ficheros),
    }


def construir_tabla_resumen(datos: dict, ruta: Path) -> Table:
    tabla = Table(title=f"Resumen de {ruta}")
    tabla.add_column("Concepto")
    tabla.add_column("Valor", justify="right")
    tabla.add_row("Ficheros", str(datos["ficheros"]))
    tabla.add_row("Carpetas", str(datos["carpetas"]))
    for tipo, cantidad in datos["tipos"].items():
        tabla.add_row(f"Tipo {tipo}", str(cantidad))
    tabla.add_row("Tamaño total (B)", formatear_tamano(datos["tamano_total"]))
    return tabla
