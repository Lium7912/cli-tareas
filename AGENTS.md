# AGENTS.md — CLI Tareas con IA (DAM)

Proyecto de línea de comandos para gestionar tareas asistidas por IA.
Desarrollado en el contexto de DAM (2º DAM), con fines educativos.

## Stack técnico

- **Python 3.12** (obligatorio; no usar otras versiones)
- **uv** para gestión de dependencias, entornos virtuales y ejecución de scripts
- **OpenCode 1.18.35** como agente de desarrollo (este archivo es su guía)

## Comandos

```powershell
uv sync                  # crear/actualizar .venv e instalar dependencias
uv add <paquete>         # añadir dependencia (registrarla en pyproject.toml)
uv run tareas            # ejecutar la aplicación
uv run pytest            # ejecutar pruebas
uv run ruff check .      # lint
uv run ruff format .     # formato
```

- El punto de entrada es `src/cli_tareas/main.py`; el comando de terminal es
  `tareas` (configurado en `pyproject.toml` con uv).

## Arquitectura y funcionalidad

- La CLI funciona con **acciones configurables** definidas en `acciones.json`:
  cualquier acción nueva o modificada debe leerse de ese archivo, no codificarse
  (hardcodear) en el código fuente.
- Existe un modo `--simular` que ejecuta las acciones en modo simulación
  (sin efectos reales). Toda acción con efectos externos debe respetar
  `--simular`.
- Mantener la estructura simple y modular (módulos pequeños, funciones puras
  cuando sea posible, tipado con type hints de Python 3.12).

## Pruebas

- El **código** de pruebas automatizadas puede estar dentro del repositorio
  (p. ej. en `tests/`).
- Los **archivos de prueba que puedan modificarse** (datos, fixtures mutables,
  archivos de entrada/salida) deben estar **exclusivamente** en
  `~/pruebas-tareas` (fuera del repositorio). No crearlos dentro del proyecto.
- Al añadir funcionalidad, añadir o actualizar pruebas y ejecutarlas con
  `uv run pytest`.
- No subir nunca contenido de `~/pruebas-tareas` al repositorio.

## Reglas de seguridad y límites

- **Nunca guardar claves, tokens ni secretos** en el código ni en archivos del
  repo. Usar variables de entorno (`.env`, protegido por `.gitignore`) y
  documentar el valor esperado en `.env.example` sin valores reales.
- **No usar `--auto`** (ni ningún modo de ejecución automática no supervisada).
- **No hacer commits** por iniciativa propia; solo cuando el usuario lo pida
  explícitamente.
- **No modificar archivos personales** (nada fuera de este repositorio, salvo
  los archivos de prueba modificables en `~/pruebas-tareas` según la sección
  anterior).

## Estilo

- Seguir PEP 8 (verificado con ruff).
- Comentarios y mensajes de usuario en español, en línea con el proyecto.
- No añadir comentarios triviales; el código debe autoexplicarse.
