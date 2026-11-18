import json
import os
import urllib.error
import urllib.request

from cli_tareas.excepciones import ConfiguracionInvalidaError, IANoDisponibleError

TIMEOUT_DEFECTO = 30.0


def configuracion_ia() -> dict:
    base = os.environ.get("TAREAS_API_BASE", "")
    modelo = os.environ.get("TAREAS_MODELO", "")
    if not base or not modelo:
        raise IANoDisponibleError(
            "IA no configurada: define TAREAS_API_BASE y TAREAS_MODELO "
            "en el entorno (ver .env.example)"
        )
    try:
        timeout = float(os.environ.get("TAREAS_IA_TIMEOUT", TIMEOUT_DEFECTO))
    except ValueError as exc:
        raise ConfiguracionInvalidaError(
            "La variable TAREAS_IA_TIMEOUT debe ser un número"
        ) from exc
    return {
        "api_base": base.rstrip("/"),
        "modelo": modelo,
        "api_key": os.environ.get("TAREAS_API_KEY", ""),
        "timeout": timeout,
    }


def construir_prompt(meta: dict) -> str:
    return (
        "Genera una descripción en español, de una sola frase y sin puntos "
        "finales, para este elemento a partir de únicamente sus metadatos: "
        f"nombre={meta['nombre']}, tipo={meta['tipo']}, "
        f"tamaño={meta['tamano']} bytes, modificado={meta['modificado']}."
    )


def pedir_descripcion(meta: dict, config: dict) -> str:
    cuerpo = json.dumps(
        {
            "model": config["modelo"],
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente que describe ficheros para una CLI. "
                        "Responde únicamente con la descripción pedida, en "
                        "español, de una frase y sin puntos finales."
                    ),
                },
                {"role": "user", "content": construir_prompt(meta)},
            ],
        }
    ).encode("utf-8")
    cabeceras = {"Content-Type": "application/json"}
    if config["api_key"]:
        cabeceras["Authorization"] = f"Bearer {config['api_key']}"
    peticion = urllib.request.Request(
        f"{config['api_base']}/chat/completions",
        data=cuerpo,
        headers=cabeceras,
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=config["timeout"]) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise IANoDisponibleError(
                f"Error de autenticación con el servicio de IA (código {exc.code})"
            ) from exc
        raise IANoDisponibleError(
            f"El servicio de IA respondió con el código {exc.code}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise IANoDisponibleError(
            f"No hay conexión con el servicio de IA ({exc.reason if hasattr(exc, 'reason') else exc})"
        ) from exc
    except json.JSONDecodeError as exc:
        raise IANoDisponibleError(
            "La respuesta del servicio de IA no es JSON válido"
        ) from exc
    try:
        texto = str(datos["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise IANoDisponibleError(
            "La respuesta del servicio de IA no tiene el formato esperado"
        ) from exc
    if not texto:
        raise IANoDisponibleError("El servicio de IA devolvió una descripción vacía")
    return texto
