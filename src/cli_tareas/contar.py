from pathlib import Path

from cli_tareas.ficheros import obtener_entradas


def contar_entradas(ruta: Path, incluir_carpetas: bool) -> dict[str, int]:
    entradas = obtener_entradas(ruta, incluir_carpetas)
    ficheros = sum(1 for entrada in entradas if entrada["tipo"] == "fichero")
    carpetas = sum(1 for entrada in entradas if entrada["tipo"] == "carpeta")
    return {"ficheros": ficheros, "carpetas": carpetas}


def construir_texto(conteo: dict[str, int], ruta: Path) -> str:
    texto = f"Conteo de {ruta}\n"
    texto += f"Ficheros: {conteo['ficheros']}"
    if conteo["carpetas"]:
        texto += f"\nCarpetas: {conteo['carpetas']}"
    return texto
