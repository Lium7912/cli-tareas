# Trazabilidad de hallazgos R-01 a R-08

- **Fecha:** 2026-11-19
- **Commit base:** `8bbadd2` («Corrige permisos Git y errores de la capa IA»).
- **Estado:** cambios de H-06, H-07 y H-08 en el árbol de trabajo, sin commit.
- **Alcance:** relacionar los hallazgos R-01 a R-08 con archivos modificados,
  pruebas y evidencia disponible, distinguiendo lo verificado de lo inferido
  o parcial.

## Leyenda

| Estado | Significado |
|---|---|
| **Verificado** | Existe evidencia comprobable en el repositorio y las pruebas pasan. |
| **Parcial** | Hay evidencia de la corrección, pero alguna comprobación no puede ejecutarse en este entorno. |
| **Inferido** | La definición no está documentada; se reconstruye desde el commit y sus pruebas. |
| **No verificable** | El permiso o el entorno impiden comprobarlo; se indica cómo hacerlo. |
| **Pendiente** | Falta evidencia o una comprobación acordada. |

## Advertencia sobre R-01 a R-08

El repositorio documenta expresamente R-04, R-05, R-07 y R-08. No se ha
localizado el informe original del subagente `revisor` que asignó los IDs
R-01, R-02, R-03 y R-06. Esas cuatro filas se reconstruyen a partir de los
commits `7277ad3` y `7f887ce` y de sus pruebas, y se marcan como **Inferido**.
No se presenta su redacción como texto original.

## Matriz de trazabilidad

| ID | Hallazgo | Archivos | Pruebas | Evidencia | Estado | Notas |
|---|---|---|---|---|---|---|
| **R-01** | Timeout de IA con valores no finitos, cero o negativos (`nan`, `inf`, `0`, `-1`) no se rechazaba correctamente | `src/cli_tareas/ia.py` | `tests/test_ia.py`, `tests/test_describir.py`, `tests/test_clasificar.py` | Commit `7277ad3`; validación `math.isfinite` y `timeout > 0`; casos parametrizados de timeout inválido | **Inferido / verificado por pruebas** | Definición reconstruida; el commit y los tests confirman la corrección |
| **R-02** | Los errores de configuración de IA podían escapar como traza bruta en `describir` y `clasificar` | `src/cli_tareas/main.py` | `tests/test_describir.py`, `tests/test_clasificar.py` | Commit `7277ad3`; `_manejar_error_ia` acepta `ErrorAccion` y se captura `ConfiguracionInvalidaError`; pruebas de texto y JSON | **Inferido / verificado por pruebas** | Definición reconstruida |
| **R-03** | `describir --simular --json` devolvía texto en lugar de JSON | `src/cli_tareas/main.py` | `tests/test_describir.py` | Commit `7277ad3`; `json_en_simulacion=True`; `test_describir_simular_json` | **Inferido / verificado por pruebas** | Definición reconstruida |
| **R-04** | Fixtures mutables de pytest fuera de `~/pruebas-tareas` | `tests/conftest.py`, `tests/test_acciones.py`, `tests/test_listar.py` | `tests/test_acciones.py`, `tests/test_listar.py` | Commit `346e540`; fixture `carpeta_temporal` basado en `~/pruebas-tareas/_pytest/tmp`; retirada de `tmp_path`/`tempfile` | **Verificado** | El subagente `revisor` tiene `external_directory: deny`; la ejecución real la confirma pytest |
| **R-05** | Documentación desactualizada sobre las seis acciones y el recuento de pruebas | `README.md`, `docs/adr/ADR-0001.md`, `docs/prompts.md` | Suite completa | Commit `346e540`; seis acciones y 138 pruebas documentadas entonces | **Verificado en su commit / actualizado en H-08** | Las cifras vigentes son 244 pruebas; se actualizan en README y ADR |
| **R-06** | Respuestas inválidas de IA (`content: null`, formatos inesperados o vacíos) podían tratarse como texto válido | `src/cli_tareas/ia.py` | `tests/test_ia.py` | Commit `7f887ce`; rechazo de `contenido is None`; pruebas de respuesta válida, formato inesperado, vacía y errores HTTP | **Inferido / verificado por pruebas** | Definición reconstruida a partir del mensaje y el diff del commit |
| **R-07** | Permisos Git peligrosos sin allowlist de solo lectura | `opencode.json`, `tests/test_permisos_opencode.py`, `README.md`, `docs/adr/ADR-0001.md`, `docs/prompts.md` | `tests/test_permisos_opencode.py` | Commits `1d8ca09` y `8bbadd2`; allowlist y denegación de `git diff --no-i*`; H-06 amplía compuestos, tuberías y redirecciones | **Parcial** | Defensa en profundidad, no aislamiento absoluto; rutas completas, alias, envoltorios y sesión ya abierta limitan la garantía |
| **R-08** | Claves desconocidas y predeterminados contradictorios en `acciones.json` | `src/cli_tareas/acciones.py`, `src/cli_tareas/main.py` | `tests/test_acciones.py` | Commit `1d8ca09`; `ESQUEMAS`, `VALORES_VALIDOS` y `PREDETERMINADOS`; rechazo de claves desconocidas y valores de `ordenar_por` | **Verificado** | Conserva los predeterminados y el comportamiento de las seis acciones |

## Evidencia detallada

### R-01 — Validación del timeout

- **Commit:** `7277ad3` («Corrige validacion de IA y salida JSON en simulacion»).
- **Cambio:** `configuracion_ia()` rechaza valores no finitos, cero y negativos,
  además de los valores no numéricos.
- **Pruebas:** `test_configuracion_ia_timeout_invalido` cubre `abc`, vacío,
  `0`, `-1`, `nan` e `inf`; las pruebas de `describir` y `clasificar` verifican
  el mensaje controlado en texto y JSON.
- **Límite de la evidencia:** no se conserva el informe original que asignó el
  ID R-01; la relación se infiere del diff y de las pruebas.

### R-02 — Errores de configuración controlados

- **Commit:** `7277ad3`.
- **Cambio:** `_manejar_error_ia` recibe `ErrorAccion` y las llamadas de
  `describir`/`clasificar` capturan `ConfiguracionInvalidaError` junto con
  `IANoDisponibleError`.
- **Pruebas:** los escenarios de timeout inválido comprueban que no aparece
  `Traceback` y que el código de salida es 1, tanto en texto como en JSON.

### R-03 — JSON en simulación de `describir`

- **Commit:** `7277ad3`.
- **Cambio:** la simulación de `describir` usa `json_en_simulacion=True`.
- **Prueba:** `test_describir_simular_json` exige un objeto JSON con
  `accion`, `simulacion` y `ruta`.

### R-04 — Fixtures mutables fuera del repositorio

- **Commit:** `346e540` («Corrige ubicacion de fixtures y actualiza
  documentacion»).
- **Cambio:** `carpeta_temporal` crea y limpia directorios bajo
  `~/pruebas-tareas/_pytest/tmp`; se sustituyen los usos de `tmp_path` en
  `tests/test_acciones.py` y `tests/conftest.py`.
- **Verificación:** no quedan usos de `tmp_path`, `tempfile`,
  `TemporaryDirectory`, `mkdtemp` ni `gettempdir` en `tests/`.
- **Límite:** el subagente `revisor` no puede acceder a `~/pruebas-tareas`
  (`external_directory: deny`), por lo que esa comprobación es **no
  verificable** para él; la suite completa sí la ejecuta.

### R-05 — Documentación de las seis acciones

- **Commit:** `346e540`.
- **Cambio:** README y ADR-0001 reflejan `listar`, `contar`, `buscar`,
  `resumen`, `describir` y `clasificar`, y el recuento de 138 pruebas de
  entonces.
- **Estado actual:** H-08 actualiza los recuentos a 244 pruebas y corrige la
  tabla de permisos y las limitaciones.

### R-06 — Respuestas inválidas de IA

- **Commit:** `7f887ce` («Corrige respuestas invalidas de IA y añade opcion
  --version»).
- **Cambio:** se rechaza `content: null` y se mantienen errores controlados
  para JSON inválido, formato inesperado, contenido vacío y errores HTTP.
- **Pruebas:** `tests/test_ia.py` cubre respuestas válidas, `content` nulo,
  formatos inesperados, contenido vacío, errores HTTP/conexión y no exposición
  de la API key.
- **Límite:** la asignación del ID R-06 es inferida; el commit también añade
  `--version`, que no forma parte de esta fila.

### R-07 — Allowlist Git

- **Commits:** `1d8ca09` (allowlist inicial) y `8bbadd2` (denegación de
  `git diff --no-i*`).
- **Configuración:** `git *` y `git.exe *` denegados por defecto; permitidos
  `git status`, `git diff`, `git log`, `git show` y `git --version`; denegadas
  las opciones de escritura/filtros (`--out*`, `--ext-d*`, `--textc*`,
  `--no-i*`) y `git *>*`.
- **Pruebas:** `tests/test_permisos_opencode.py` verifica sintaxis V1, orden de
  reglas, comandos permitidos y denegados; H-06 añade variantes de
  `--no-index`, opciones globales, comandos compuestos, tuberías y
  redirecciones.
- **Limitaciones:** rutas completas a `git.exe`, alias, funciones, `cmd /c`,
  `powershell -Command`, `Start-Process`, configuración de Git y una sesión de
  OpenCode ya abierta pueden eludir o conservar reglas anteriores. Es defensa
  en profundidad, no aislamiento absoluto.

### R-08 — Validación estricta de `acciones.json`

- **Commit:** `1d8ca09`.
- **Cambio:** `obtener_config` rechaza acciones sin esquema y claves
  desconocidas; `PREDETERMINADOS` centraliza los valores ausentes;
  `VALORES_VALIDOS` valida `ordenar_por`; `main.py` consume la configuración
  ya validada.
- **Pruebas:** `tests/test_acciones.py` cubre clave desconocida, acción sin
  esquema, `ordenar_por` inválido, predeterminados y precedencia de valores
  explícitos.

## Verificación de H-06, H-07 y H-08

| Comprobación | Resultado |
|---|---|
| `uv run pytest tests/test_permisos_opencode.py -q` | **85 passed** |
| `uv run pytest -q` | **244 passed** |
| `uv run ruff check .` | Sin errores |
| `uv run ruff format --check .` | 31 archivos ya formateados |
| `cmd /c "opencode --version"` | `1.18.35` |
| `cmd /c "opencode debug config"` | Carga `opencode.json`; `git diff *--no-i*` aparece como `deny` |
| `git diff --check` | Pendiente de la comprobación final |
| `git status --short` | Pendiente de la comprobación final |

Las comprobaciones marcadas como pendientes se actualizan al cerrar H-08,
después de editar la documentación y sin realizar ningún commit.

## Conclusión

- R-04, R-05, R-07 y R-08 tienen evidencia documentada en el repositorio.
- R-01, R-02, R-03 y R-06 tienen evidencia en commits y pruebas, pero su
  definición es inferida.
- R-07 es la única fila con garantía parcial por limitaciones del filtro
  textual y del entorno de OpenCode.
- No se ha inventado ningún prompt, resultado, fecha ni evidencia.
