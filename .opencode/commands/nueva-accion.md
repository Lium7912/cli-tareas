---
description: Diseñar una acción nueva para acciones.json (Fase 1, solo lectura); la implementación requiere aprobación y cambio manual a Build
agent: plan
---

Voy a diseñar una acción nueva para la CLI «tareas» a partir de esta
descripción del usuario:

<descripcion>
$ARGUMENTS
</descripcion>

Si la descripción está vacía o es ambigua, pregunta al usuario los detalles
que falten (nombre, parámetros, efectos esperados) ANTES de continuar.
No asumas nada.

## Regla principal (inquebrantable)

Este comando se ejecuta en dos fases. La Fase 1 NO modifica ningún archivo
y solo termina presentando el diseño. La Fase 2 (implementación) solo puede
comenzar cuando el usuario haya aprobado el diseño de forma explícita
(un «sí» claro) Y haya cambiado manualmente al agente Build.
Hasta entonces actúa SOLO en modo lectura: no edites, no crees archivos,
no ejecutes comandos con efectos secundarios.

## FASE 1 — Analizar y diseñar (solo lectura)

### 1. Cargar la skill y analizar

1. Lee y sigue estrictamente `.opencode/skills/acciones-json/SKILL.md`.
2. Lee `AGENTS.md` y respétalo en todo momento.
3. Analiza sin modificar nada:
   - `acciones.json` (acciones existentes y su formato).
   - `src/cli_tareas/acciones.py` (bloques `ESQUEMAS`, `CLAVES_POSITIVAS` y
     `PREDETERMINADOS`).
   - `src/cli_tareas/main.py` (patrón de comandos Typer existentes y `_iniciar()`).
   - `docs/adr/ADR-0001.md` (decisiones de arquitectura vigentes).
4. Determina si la petición crea una acción nueva o modifica una existente
   (en ese caso, avisa del riesgo de romper las pruebas actuales).

### 2. Presentar el diseño

Muestra al usuario una propuesta completa que incluya:

1. **Entrada JSON**: clave nueva (inglés minúsculas, sin espacios), valor de
   `descripcion` (una frase en español, sin puntos), `activa` (por defecto
   `false` hasta confirmación) y el resto de claves específicas.
2. **Esquema**: qué añadir en `ESQUEMAS` (tipos Python), en
   `CLAVES_POSITIVAS` (si hay enteros ≥ 1) y en `PREDETERMINADOS` (si hay
   claves opcionales). No se permiten claves fuera del esquema.
3. **Comando Typer** en `main.py`: cómo usará `_iniciar()` y cómo soportará
   `--simular` con un mensaje claro del tipo «Se …ría…».
4. **Pruebas previstas**: código en `tests/`; cualquier dato o fixture
   mutable SOLO en `~/pruebas-tareas` (nunca dentro del repo).
5. **Lista exacta de archivos** que se crearían o editarían.

### 3. Terminar la Fase 1 y esperar

Tras presentar el diseño, DETENTE. No intentes implementar nada desde el
agente plan. Recuerda al usuario que la Fase 2 requiere:

1. Su aprobación explícita del diseño (o sus correcciones, en cuyo caso
   repite la Fase 1 con el diseño ajustado).
2. Cambiar manualmente al agente Build (por ejemplo, con `/build`).
3. Volver a invocar el comando o pedir la implementación indicando el
   diseño aprobado.

## FASE 2 — Implementar (solo con agente Build y aprobación previa)

Si el usuario ya aprobó el diseño y está en el agente Build, continúa aquí.
Si no es así (sigues en agente plan), devuelve el control al final de la
Fase 1 sin editar nada.

1. Edita `acciones.json`, `ESQUEMAS`/`CLAVES_POSITIVAS`/`PREDETERMINADOS`,
   el módulo de presentación y `main.py`, siguiendo el patrón de las acciones
   existentes.
2. Mantén PEP 8, type hints de Python 3.12, módulos pequeños y mensajes en
   español. Sin comentarios triviales ni secretos en el código.
3. Ejecuta en este orden:
   - `uv run ruff check .` y `uv run ruff format .`
   - `uv run tareas <accion> --simular` (SIEMPRE primero, y verificar que
     no hay efectos reales).
   - `uv run pytest` (todas las pruebas existentes deben seguir pasando;
     si alguna falla, corrígelo antes de continuar).
   - Solo si el usuario aprueba, probar sin `--simular` sobre
     `~/pruebas-tareas`.
4. Ofrece actualizar `docs/adr/ADR-0001.md` (secciones 3 y 5) si la acción
   introduce una decisión nueva, pidiendo permiso antes de editar.

## Límites que nunca se cruzan (en ambas fases)

- No uses ni propongas `--auto` ni ningún modo de ejecución no supervisada.
- No hagas `git commit`, `git push`, `git reset` ni operaciones git de
  escritura (opencode.json ya las deniega).
- No escribas claves, tokens ni rutas personales en el repo; valores
  sensibles solo por variables de entorno, documentados en `.env.example`
  sin valores reales.
- No modifiques nada fuera del repositorio, salvo datos de prueba mutables
  en `~/pruebas-tareas` (y solo con aprobación del usuario).
- Toda acción con efectos externos debe respetar `--simular`.
