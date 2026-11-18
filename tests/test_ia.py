import pytest

from cli_tareas.excepciones import ConfiguracionInvalidaError, IANoDisponibleError
from cli_tareas.ia import TIMEOUT_DEFECTO, configuracion_ia


@pytest.fixture
def env_ia(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAREAS_API_BASE", "http://localhost:9/v1/")
    monkeypatch.setenv("TAREAS_MODELO", "modelo-prueba")
    monkeypatch.delenv("TAREAS_API_KEY", raising=False)
    monkeypatch.delenv("TAREAS_IA_TIMEOUT", raising=False)


def test_configuracion_ia_por_defecto(env_ia) -> None:
    assert configuracion_ia() == {
        "api_base": "http://localhost:9/v1",
        "modelo": "modelo-prueba",
        "api_key": "",
        "timeout": TIMEOUT_DEFECTO,
    }


def test_configuracion_ia_timeout_valido(
    env_ia, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", "5")
    assert configuracion_ia()["timeout"] == 5.0


@pytest.mark.parametrize("valor", ["abc", "", "0", "-1", "nan", "inf"])
def test_configuracion_ia_timeout_invalido(
    env_ia, monkeypatch: pytest.MonkeyPatch, valor: str
) -> None:
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", valor)
    with pytest.raises(ConfiguracionInvalidaError, match="mayor que 0"):
        configuracion_ia()


def test_configuracion_ia_sin_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAREAS_API_BASE", raising=False)
    monkeypatch.delenv("TAREAS_MODELO", raising=False)
    with pytest.raises(IANoDisponibleError, match="IA no configurada"):
        configuracion_ia()
