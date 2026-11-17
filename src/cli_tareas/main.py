from pathlib import Path

import typer
from rich.console import Console

from cli_tareas import __version__
from cli_tareas.listar import (
    AccionDesactivadaError,
    cargar_acciones,
    construir_tabla,
    obtener_config_listar,
    obtener_entradas,
    ordenar_entradas,
    resolver_ruta,
)

app = typer.Typer(
    help="CLI para gestionar tareas asistidas por IA (DAM)",
    no_args_is_help=True,
)
consola = Console()


@app.command()
def version() -> None:
    """Muestra la versión de la aplicación."""
    print(f"cli-tareas {__version__}")


@app.command(name="listar")
def listar(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta a listar; por defecto, la ruta_predeterminada de acciones.json",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos)",
    ),
) -> None:
    """Lista el contenido de una carpeta (nombre, tipo, tamaño y fecha)."""
    try:
        acciones = cargar_acciones()
        config = obtener_config_listar(acciones)
    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        AccionDesactivadaError,
    ) as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1) from exc

    ruta_resuelta = resolver_ruta(config, ruta)
    incluir_carpetas = bool(config.get("incluir_carpetas", True))
    ordenar_por = str(config.get("ordenar_por", "nombre"))

    if simular:
        print(f"[simulación] Se listaría el contenido de: {ruta_resuelta}")
        return

    try:
        entradas = obtener_entradas(ruta_resuelta, incluir_carpetas)
        entradas = ordenar_entradas(entradas, ordenar_por)
    except (FileNotFoundError, NotADirectoryError, PermissionError, ValueError) as exc:
        print(f"Error: {exc}")
        raise typer.Exit(code=1) from exc

    consola.print(construir_tabla(entradas, ruta_resuelta))


if __name__ == "__main__":
    app()
