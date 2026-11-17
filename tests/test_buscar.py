from pathlib import Path

from typer.testing import CliRunner

from cli_tareas.buscar import buscar_entradas, limitar_resultados
from cli_tareas.main import app

runner = CliRunner()


def test_buscar_por_termino(carpeta_contenido: Path) -> None:
    nombres = [
        e["nombre"] for e in buscar_entradas(carpeta_contenido, termino="informe")
    ]
    assert nombres == ["informe.txt"]


def test_buscar_insensible_a_mayusculas(carpeta_contenido: Path) -> None:
    nombres = [
        e["nombre"] for e in buscar_entradas(carpeta_contenido, termino="INFORME")
    ]
    assert nombres == ["informe.txt"]


def test_buscar_por_extension(carpeta_contenido: Path) -> None:
    nombres = [
        e["nombre"] for e in buscar_entradas(carpeta_contenido, extension=".csv")
    ]
    assert nombres == ["datos.csv"]


def test_buscar_extension_sin_punto(carpeta_contenido: Path) -> None:
    nombres = [e["nombre"] for e in buscar_entradas(carpeta_contenido, extension="txt")]
    assert nombres == ["informe.txt"]


def test_buscar_termino_y_extension(carpeta_contenido: Path) -> None:
    nombres = [
        e["nombre"]
        for e in buscar_entradas(carpeta_contenido, termino="informe", extension=".txt")
    ]
    assert nombres == ["informe.txt"]


def test_buscar_termino_y_extension_no_coinciden(carpeta_contenido: Path) -> None:
    assert buscar_entradas(carpeta_contenido, termino="informe", extension=".csv") == []


def test_buscar_sin_filtros(carpeta_contenido: Path) -> None:
    entradas = buscar_entradas(carpeta_contenido)
    assert len(entradas) == 4


def test_buscar_sin_resultados(carpeta_contenido: Path) -> None:
    assert buscar_entradas(carpeta_contenido, termino="inexistente") == []


def test_limitar_resultados() -> None:
    entradas = [{"nombre": str(i)} for i in range(5)]
    assert len(limitar_resultados(entradas, 2)) == 2
    assert len(limitar_resultados(entradas, None)) == 5
    assert len(limitar_resultados(entradas, 10)) == 5


def test_buscar_cli(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(
        app, ["buscar", str(carpeta_contenido), "--termino", "informe"]
    )
    assert resultado.exit_code == 0
    assert "informe.txt" in resultado.output
    assert "datos.csv" not in resultado.output


def test_buscar_cli_extension(carpeta_contenido: Path) -> None:
    resultado = runner.invoke(
        app, ["buscar", str(carpeta_contenido), "--extension", ".md"]
    )
    assert resultado.exit_code == 0
    assert "nota.md" in resultado.output


def test_buscar_max_resultados(carpeta_contenido: Path, acciones_temporales) -> None:
    acciones_temporales(
        "buscar",
        {
            "activa": True,
            "ruta_predeterminada": str(carpeta_contenido),
            "max_resultados": 2,
        },
    )
    resultado = runner.invoke(app, ["buscar"])
    assert resultado.exit_code == 0
    assert "Mostrando 2 de 4" in resultado.output


def test_buscar_simular() -> None:
    resultado = runner.invoke(app, ["buscar", "--simular"])
    assert resultado.exit_code == 0
    assert "simulación" in resultado.output


def test_buscar_accion_desactivada(
    carpeta_contenido: Path, acciones_temporales
) -> None:
    acciones_temporales("buscar", {"activa": False})
    resultado = runner.invoke(app, ["buscar", str(carpeta_contenido)])
    assert resultado.exit_code == 1
    assert "desactivada" in resultado.output


def test_buscar_ruta_inexistente() -> None:
    resultado = runner.invoke(app, ["buscar", "~/pruebas-tareas/no-existe-xyz"])
    assert resultado.exit_code == 1
    assert "no existe" in resultado.output
