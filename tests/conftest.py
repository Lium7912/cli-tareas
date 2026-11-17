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


@pytest.fixture
def acciones_inactivas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    ruta = tmp_path / "acciones.json"
    ruta.write_text(
        json.dumps({"listar": {"activa": False, "ruta_predeterminada": str(tmp_path)}}),
        encoding="utf-8",
    )
    import cli_tareas.listar

    monkeypatch.setattr(cli_tareas.listar, "RUTA_ACCIONES", ruta)
    return ruta
