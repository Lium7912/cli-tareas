import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
RUTA_CONFIG = RAIZ / "opencode.json"

LECTURA = (
    "git status",
    "git status *",
    "git diff",
    "git diff *",
    "git log",
    "git log *",
    "git show",
    "git show *",
    "git --version",
)

DENEGACIONES_ESPECIFICAS = (
    "git diff *--out*",
    "git log *--out*",
    "git show *--out*",
    "git diff *--ext-d*",
    "git log *--ext-d*",
    "git show *--ext-d*",
    "git diff *--textc*",
    "git log *--textc*",
    "git show *--textc*",
    "git *>*",
)


def _config() -> dict:
    return json.loads(RUTA_CONFIG.read_text(encoding="utf-8"))


def _bash() -> dict:
    return _config()["permission"]["bash"]


def _coincide(texto: str, patron: str) -> bool:
    normalizado = texto.replace("\\", "/")
    escapado = patron.replace("\\", "/")
    escapado = "".join(
        "\\" + caracter if caracter in r".+^${}()|[]" else caracter
        for caracter in escapado
    )
    escapado = escapado.replace("*", ".*").replace("?", ".")
    if escapado.endswith(" .*"):
        escapado = escapado[:-3] + "( .*)?"
    banderas = re.IGNORECASE if sys.platform == "win32" else 0
    return re.fullmatch(escapado, normalizado, flags=banderas) is not None


def _evaluar(comando: str, bash: dict) -> str:
    for patron, accion in reversed(list(bash.items())):
        if _coincide(comando, patron):
            return accion
    return "ask"


def test_opencode_json_usa_sintaxis_v1() -> None:
    config = _config()
    permiso = config["permission"]
    assert "permissions" not in config
    assert "shell" not in permiso
    assert "subagent" not in permiso
    assert isinstance(permiso["bash"], dict)


def test_valores_de_permisos_validos() -> None:
    assert set(_bash().values()) <= {"allow", "ask", "deny"}


def test_catch_all_primero_y_git_denegado_por_defecto() -> None:
    bash = _bash()
    assert next(iter(bash)) == "*"
    assert bash["*"] == "ask"
    assert bash["git *"] == "deny"
    assert bash["git.exe *"] == "deny"


def test_comandos_git_de_lectura_permitidos() -> None:
    bash = _bash()
    for patron in LECTURA:
        assert bash[patron] == "allow"


def test_orden_de_reglas_de_la_allowlist() -> None:
    claves = list(_bash())
    indice = claves.index
    assert indice("*") == 0
    assert indice("git *") > indice("*")
    assert indice("git.exe *") > indice("git *")
    assert all(indice("git *") < indice(patron) for patron in LECTURA)
    assert all(indice("git.exe *") < indice(patron) for patron in LECTURA)
    assert all(
        indice(patron) < indice(denegacion)
        for patron in LECTURA
        for denegacion in DENEGACIONES_ESPECIFICAS
    )


@pytest.mark.parametrize(
    ("comando", "esperado"),
    [
        ("git status", "allow"),
        ("git status --short", "allow"),
        ("git diff", "allow"),
        ("git diff --check", "allow"),
        ("git diff --stat", "allow"),
        ("git log", "allow"),
        ("git log --oneline -10", "allow"),
        ("git show HEAD", "allow"),
        ("git --version", "allow"),
        ("git commit -m x", "deny"),
        ("git commit --amend", "deny"),
        ("git push", "deny"),
        ("git reset --hard", "deny"),
        ("git merge main", "deny"),
        ("git switch main", "deny"),
        ("git checkout main", "deny"),
        ("git rebase main", "deny"),
        ("git apply parche.patch", "deny"),
        ("git pull", "deny"),
        ("git branch -D rama", "deny"),
        ("git tag -d v1", "deny"),
        ("git clean -fd", "deny"),
        ("git stash", "deny"),
        ("git restore .", "deny"),
        ("git -C . status", "deny"),
        ("git -c core.pager=cat log", "deny"),
        ("git --git-dir=.git status", "deny"),
        ("git diff --output=salida.txt", "deny"),
        ("git diff --output salida.txt", "deny"),
        ("git log --ext-diff", "deny"),
        ("git show --textconv HEAD", "deny"),
        ("git diff > salida.txt", "deny"),
        ("git.exe status", "deny"),
        ("git.exe commit -m x", "deny"),
        ("uv run pytest", "ask"),
        ("Get-ChildItem", "ask"),
    ],
)
def test_precedencia_y_resultados(comando: str, esperado: str) -> None:
    assert _evaluar(comando, _bash()) == esperado
