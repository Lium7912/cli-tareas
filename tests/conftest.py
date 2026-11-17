import json
import shutil
from pathlib import Path

import pytest

BASE_FIXTURE = Path.home() / "pruebas-tareas" / "_pytest"


@pytest.fixture(scope="session")
def carpeta_pruebas() -> Path:
    BASE_FIXTURE.mkdir(parents=True, exist_ok=True)
    ruta = BASE_FIXTURE / "listar"
    ruta.mkdir(exist_ok=True)
    (ruta / "a.txt").write_text("contenido a", encoding="utf-8")
    (ruta / "b_largo.txt").write_text("x" * 500, encoding="utf-8")
    (ruta / "subcarpeta").mkdir(exist_ok=True)
    yield ruta
    for entrada in ruta.iterdir():
        if entrada.is_dir():
            shutil.rmtree(entrada)
        else:
            entrada.unlink()


@pytest.fixture(scope="session")
def carpeta_contenido() -> Path:
    BASE_FIXTURE.mkdir(parents=True, exist_ok=True)
    ruta = BASE_FIXTURE / "contenido"
    ruta.mkdir(exist_ok=True)
    (ruta / "informe.txt").write_text("a" * 100, encoding="utf-8")
    (ruta / "datos.csv").write_text("b" * 200, encoding="utf-8")
    (ruta / "nota.md").write_text("c", encoding="utf-8")
    subcarpeta = ruta / "subcarpeta"
    subcarpeta.mkdir(exist_ok=True)
    (subcarpeta / "informe2.txt").write_text("d" * 50, encoding="utf-8")
    yield ruta
    for entrada in ruta.iterdir():
        if entrada.is_dir():
            shutil.rmtree(entrada)
        else:
            entrada.unlink()


@pytest.fixture
def acciones_temporales(monkeypatch: pytest.MonkeyPatch):
    rutas: list[Path] = []

    def _crear(nombre: str, config: dict) -> Path:
        ruta = BASE_FIXTURE / "_acciones" / f"{nombre}.json"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps({nombre: config}), encoding="utf-8")
        import cli_tareas.acciones

        monkeypatch.setattr(cli_tareas.acciones, "RUTA_ACCIONES", ruta)
        rutas.append(ruta)
        return ruta

    yield _crear
    for ruta in rutas:
        ruta.unlink(missing_ok=True)


@pytest.fixture
def acciones_inactivas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ruta = tmp_path / "acciones.json"
    ruta.write_text(
        json.dumps({"listar": {"activa": False, "ruta_predeterminada": str(tmp_path)}}),
        encoding="utf-8",
    )
    import cli_tareas.acciones

    monkeypatch.setattr(cli_tareas.acciones, "RUTA_ACCIONES", ruta)
    return ruta
