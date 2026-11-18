import json
from pathlib import Path

import typer
from rich.console import Console

from cli_tareas import __version__
from cli_tareas.acciones import cargar_acciones, obtener_config
from cli_tareas.buscar import (
    buscar_entradas,
    construir_tabla_busqueda,
    limitar_resultados,
)
from cli_tareas.clasificar import (
    clasificar_determinista,
    construir_tabla_clasificacion,
    normalizar_categoria,
)
from cli_tareas.clasificar import (
    construir_salida_json as construir_salida_json_clasificacion,
)
from cli_tareas.contar import construir_texto, contar_entradas
from cli_tareas.describir import (
    construir_salida_json,
    construir_tabla_descripciones,
    describir_determinista,
)
from cli_tareas.excepciones import (
    ConfiguracionInvalidaError,
    ErrorAccion,
    IANoDisponibleError,
)
from cli_tareas.ficheros import (
    formatear_fecha,
    obtener_entradas,
    ordenar_entradas,
    resolver_ruta,
)
from cli_tareas.ia import configuracion_ia, pedir_clasificacion, pedir_descripcion
from cli_tareas.listar import construir_tabla
from cli_tareas.resumen import calcular_resumen, construir_tabla_resumen

app = typer.Typer(
    help="CLI para gestionar tareas asistidas por IA (DAM)",
    no_args_is_help=True,
)
consola = Console()

ERRORES_PREPARACION = (ErrorAccion, FileNotFoundError, ValueError, TypeError)


def _error_json(exc: Exception) -> str:
    return json.dumps({"error": str(exc)}, ensure_ascii=False)


def _iniciar(
    nombre: str,
    ruta: Path | None,
    simular: bool,
    mensaje_simulacion: str,
    json_salida: bool = False,
    json_en_simulacion: bool = False,
) -> tuple[dict, Path]:
    """Carga la configuración de la acción y resuelve la ruta a tratar."""
    try:
        acciones = cargar_acciones()
        config = obtener_config(nombre, acciones)
        ruta_resuelta = resolver_ruta(config, ruta)
    except ERRORES_PREPARACION as exc:
        print(_error_json(exc) if json_salida else f"Error: {exc}")
        raise typer.Exit(code=1) from exc
    if simular:
        if json_salida and json_en_simulacion:
            print(
                json.dumps(
                    {
                        "accion": nombre,
                        "simulacion": True,
                        "ruta": str(ruta_resuelta),
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(f"[simulación] {mensaje_simulacion.format(ruta=ruta_resuelta)}")
        raise typer.Exit()
    return config, ruta_resuelta


def _fallar(exc: Exception, json_salida: bool = False) -> typer.Exit:
    print(_error_json(exc) if json_salida else f"Error: {exc}")
    return typer.Exit(code=1)


def _metadatos_entradas(entradas: list[dict]) -> list[dict]:
    return [
        {
            "nombre": entrada["nombre"],
            "tipo": entrada["tipo"],
            "tamano": entrada["tamano"],
            "modificado": formatear_fecha(entrada["modificado"]),
        }
        for entrada in entradas
    ]


def _manejar_error_ia(exc: ErrorAccion, json_salida: bool) -> typer.Exit:
    if json_salida:
        print(_error_json(exc))
        return typer.Exit(code=1)
    print(f"Error: {exc}")
    consola.print(
        "[yellow]Puedes usar --sin-ia o las acciones sin IA: "
        "listar, contar, buscar, resumen[/yellow]"
    )
    return typer.Exit(code=1)


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
    config, ruta_resuelta = _iniciar(
        "listar", ruta, simular, "Se listaría el contenido de: {ruta}"
    )
    incluir_carpetas = bool(config.get("incluir_carpetas", True))
    ordenar_por = str(config.get("ordenar_por", "nombre"))
    try:
        entradas = obtener_entradas(ruta_resuelta, incluir_carpetas)
        entradas = ordenar_entradas(entradas, ordenar_por)
    except ErrorAccion as exc:
        raise _fallar(exc) from exc

    consola.print(construir_tabla(entradas, ruta_resuelta))


@app.command()
def contar(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta a analizar; por defecto, la ruta_predeterminada de acciones.json",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos)",
    ),
) -> None:
    """Cuenta los ficheros de una carpeta."""
    config, ruta_resuelta = _iniciar(
        "contar", ruta, simular, "Se contarían los ficheros de: {ruta}"
    )
    incluir_carpetas = bool(config.get("incluir_carpetas", False))
    try:
        conteo = contar_entradas(ruta_resuelta, incluir_carpetas)
    except ErrorAccion as exc:
        raise _fallar(exc) from exc

    consola.print(construir_texto(conteo, ruta_resuelta))


@app.command()
def buscar(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta donde buscar; por defecto, la ruta_predeterminada de acciones.json",
    ),
    termino: str = typer.Option(
        "",
        "--termino",
        help="Texto que debe contener el nombre del fichero",
    ),
    extension: str = typer.Option(
        "",
        "--extension",
        help="Extensión a buscar, p. ej. .txt (se admite sin punto)",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos)",
    ),
) -> None:
    """Busca ficheros por nombre o extensión."""
    filtros = []
    if termino:
        filtros.append(f"nombre con «{termino}»")
    if extension:
        filtros.append(f"extensión {extension}")
    detalle = f" ({', '.join(filtros)})" if filtros else ""
    config, ruta_resuelta = _iniciar(
        "buscar", ruta, simular, f"Se buscarían ficheros{detalle} en: {{ruta}}"
    )
    try:
        resultados = buscar_entradas(ruta_resuelta, termino, extension)
        max_resultados = config.get("max_resultados")
        total = len(resultados)
        resultados = limitar_resultados(resultados, max_resultados)
    except ErrorAccion as exc:
        raise _fallar(exc) from exc

    consola.print(construir_tabla_busqueda(resultados, ruta_resuelta))
    if max_resultados is not None and total > len(resultados):
        consola.print(
            f"[yellow]Mostrando {len(resultados)} de {total} resultados[/yellow]"
        )


@app.command()
def resumen(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta a resumir; por defecto, la ruta_predeterminada de acciones.json",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos)",
    ),
) -> None:
    """Resume una carpeta: nº de ficheros, tipos y tamaño total."""
    _, ruta_resuelta = _iniciar(
        "resumen", ruta, simular, "Se generaría el resumen de: {ruta}"
    )
    try:
        datos = calcular_resumen(ruta_resuelta)
    except ErrorAccion as exc:
        raise _fallar(exc) from exc

    consola.print(construir_tabla_resumen(datos, ruta_resuelta))


@app.command()
def describir(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta a describir; por defecto, la ruta_predeterminada de acciones.json",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos ni llamadas de red)",
    ),
    sin_ia: bool = typer.Option(
        False,
        "--sin-ia",
        help="Genera descripciones deterministas a partir de los metadatos, sin IA ni red",
    ),
    json_salida: bool = typer.Option(
        False,
        "--json",
        help="Salida en JSON (sin colores ni decoración)",
    ),
) -> None:
    """Genera descripciones en español de los ficheros de una carpeta (solo metadatos)."""
    config, ruta_resuelta = _iniciar(
        "describir",
        ruta,
        simular,
        "Se describirían los ficheros de: {ruta}",
        json_salida=json_salida,
        json_en_simulacion=True,
    )
    max_ficheros = int(config.get("max_ficheros", 10))
    try:
        entradas = obtener_entradas(ruta_resuelta, incluir_carpetas=True)
        entradas = ordenar_entradas(entradas, "nombre")[:max_ficheros]
    except ErrorAccion as exc:
        raise _fallar(exc, json_salida=json_salida) from exc

    metas = _metadatos_entradas(entradas)
    if sin_ia:
        origen = "determinista"
        filas = [
            {**meta, "descripcion": describir_determinista(meta)} for meta in metas
        ]
    else:
        origen = "ia"
        try:
            config_ia = configuracion_ia()
            filas = [
                {**meta, "descripcion": pedir_descripcion(meta, config_ia)}
                for meta in metas
            ]
        except (ConfiguracionInvalidaError, IANoDisponibleError) as exc:
            raise _manejar_error_ia(exc, json_salida) from exc

    if json_salida:
        print(construir_salida_json(filas, ruta_resuelta, origen))
    else:
        consola.print(construir_tabla_descripciones(filas, ruta_resuelta, origen))
        if origen == "ia":
            consola.print(
                "[dim]Descripciones generadas por IA: pueden contener inexactitudes.[/dim]"
            )


@app.command()
def clasificar(
    ruta: Path | None = typer.Argument(
        None,
        help="Carpeta a clasificar; por defecto, la ruta_predeterminada de acciones.json",
    ),
    simular: bool = typer.Option(
        False,
        "--simular",
        help="Ejecuta en modo simulación (sin efectos externos ni llamadas de red)",
    ),
    sin_ia: bool = typer.Option(
        False,
        "--sin-ia",
        help="Clasifica por extensión, sin IA ni red",
    ),
    json_salida: bool = typer.Option(
        False,
        "--json",
        help="Salida en JSON (sin colores ni decoración)",
    ),
) -> None:
    """Clasifica los ficheros de una carpeta por categorías (solo metadatos)."""
    config, ruta_resuelta = _iniciar(
        "clasificar",
        ruta,
        simular,
        "Se clasificarían los ficheros de: {ruta}",
        json_salida=json_salida,
        json_en_simulacion=True,
    )
    max_ficheros = int(config.get("max_ficheros", 10))
    try:
        entradas = obtener_entradas(ruta_resuelta, incluir_carpetas=False)
        entradas = ordenar_entradas(entradas, "nombre")[:max_ficheros]
    except ErrorAccion as exc:
        raise _fallar(exc, json_salida=json_salida) from exc

    metas = _metadatos_entradas(entradas)
    if sin_ia:
        origen = "determinista"
        filas = [{**meta, "categoria": clasificar_determinista(meta)} for meta in metas]
    else:
        origen = "ia"
        try:
            config_ia = configuracion_ia()
            filas = [
                {
                    **meta,
                    "categoria": normalizar_categoria(
                        pedir_clasificacion(meta, config_ia)
                    ),
                }
                for meta in metas
            ]
        except (ConfiguracionInvalidaError, IANoDisponibleError) as exc:
            raise _manejar_error_ia(exc, json_salida) from exc

    if json_salida:
        print(construir_salida_json_clasificacion(filas, ruta_resuelta, origen))
    else:
        consola.print(construir_tabla_clasificacion(filas, ruta_resuelta, origen))
        if origen == "ia":
            consola.print(
                "[dim]Clasificación generada por IA: revisa las categorías dudosas.[/dim]"
            )


if __name__ == "__main__":
    app()
