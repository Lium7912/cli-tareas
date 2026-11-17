---
name: acciones-json
description: Crear, validar y documentar nuevas acciones de la CLI tareas configuradas en acciones.json, sin romper las existentes. Usar cuando el usuario pida añadir, modificar, desactivar o documentar una acción.
---

# Skill: acciones-json

Guía para trabajar con el sistema de acciones de la CLI «tareas»
(Proyecto 2 de DAM). Las acciones se definen en `acciones.json` (raíz del
repo) y se validan en `src/cli_tareas/acciones.py`. Nada se hardcodea.

## Reglas inquebrantables (antes de cualquier paso)

1. **Aprobación explícita**: presentar el diseño (JSON + esquema + comando +
   pruebas) y esperar el «sí» del usuario ANTES de crear o modificar cualquier
   archivo. Nunca editar por iniciativa propia.
2. **Sin secretos**: nunca escribir claves, tokens ni rutas personales en el
   código ni en el repo. Valores sensibles solo por variables de entorno
   (`.env` protegido por `.gitignore`; documentar en `.env.example` sin
   valores reales).
3. **Sin `--auto`**: no usar ni proponer ningún modo de ejecución automática
   no supervisada.
4. **Sin commits**: no hacer `git commit`, `push`, `reset` ni similares.
   `opencode.json` ya los deniega; no intentar rodearlo.
5. **Archivos mutables de prueba solo en `~/pruebas-tareas`**: nunca dentro
   del repo. El código de pruebas sí va en `tests/`.

## Flujo de trabajo

### 1. Analizar (solo lectura)
- Leer `acciones.json` y `src/cli_tareas/acciones.py` (bloque `ESQUEMAS`).
- Leer `docs/adr/ADR-0001.md` para respetar la arquitectura y no contradecir
  decisiones ya aceptadas.
- Identificar si la petición modifica una acción existente (riesgo de romper
  las 53 pruebas actuales) o crea una nueva.

### 2. Diseñar y pedir aprobación
Presentar al usuario un plan con:
- Entrada JSON propuesta (claves `activa`, `descripcion`, `ruta_predeterminada`
  y las específicas; `activa` debe ser booleano).
- Esquema a añadir en `ESQUEMAS` (tipos Python) y, si hay enteros con mínimo 1,
  añadirlos a `CLAVES_POSITIVAS`.
- Comando Typer en `main.py` que use `_iniciar()` y soporte `--simular` con un
  mensaje «Se …ría…» claro, siguiendo el patrón de las acciones existentes.
- Pruebas previstas (código en `tests/`, datos en `~/pruebas-tareas`).
Esperar aprobación explícita. Si el usuario duda, no editar nada.

### 3. Implementar (tras aprobación)
- Editar `acciones.json` (la clave de acción nueva en inglés minúsculas, sin
  espacios; `activa: true` solo si el usuario lo confirma).
- Añadir el esquema en `ESQUEMAS` y las claves positivas correspondientes.
- Crear el módulo de presentación en `src/cli_tareas/` (solo construcción de
  tablas/textos; E.S. de ficheros en `ficheros.py`) y el comando en `main.py`
  pasando por `_iniciar()`.
- Mantener PEP 8, type hints de Python 3.12, módulos pequeños y mensajes en
  español. Sin comentarios triviales.

### 4. Validar y probar (en este orden)
1. `uv run ruff check .` y `uv run ruff format .`
2. Preparar datos de prueba SOLO en `~/pruebas-tareas` (crearlos si faltan,
   previa aprobación del usuario).
3. Ejecutar SIEMPRE primero en simulación:
   `uv run tareas <accion> --simular` — verificar el mensaje y que no hay
   efectos. Solo si el usuario aprueba, ejecutar sin `--simular` sobre
   `~/pruebas-tareas`.
4. `uv run pytest` — todas las pruebas existentes deben seguir pasando.
5. Comprobar `uv run tareas --help` muestra el comando nuevo.
6. Actualizar `docs/adr/ADR-0001.md` (secciones 3 y 5) si la acción introduce
   una decisión nueva, y proponer el cambio al usuario.

### 5. Documentar la acción
- `descripcion` en `acciones.json`: una frase clara en español, sin puntos.
- Si la acción tiene parámetros, documentar su significado en la ayuda del
  comando Typer (aparece en `--help`), no en comentarios del código.

## Criterios de no romper lo existente
- No renombrar ni reordenar claves de acciones existentes en `acciones.json`.
- No cambiar la firma de `cargar_acciones()`, `obtener_config()` ni
  `validar_config()`; solo extender `ESQUEMAS` / `CLAVES_POSITIVAS`.
- Toda acción debe poder desactivarse con `activa: false` sin errores.
- Si alguna prueba falla tras el cambio, corregir ANTES de continuar y volver
  a ejecutar la suite completa.
