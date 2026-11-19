# Registro de prompts — CLI Tareas con IA (DAM)

## 1. Introducción

Este documento registra los **prompts importantes** utilizados durante el
desarrollo agéntico del proyecto `tareas` con **OpenCode 1.18.35**, con fines
educativos (2º DAM).

Finalidad:

- Trazabilidad: saber qué se pidió al agente, cuándo y con qué modelo.
- Aprendizaje: revisar cómo la redacción del prompt influye en el resultado.
- Verificación: dejar constancia de la aprobación del usuario en cada paso.

Reglas para registrar prompts:

- El texto del prompt se copia **literalmente**, entre comillas o en bloque de
  código. No se parafrasea.
- Solo se registra información **verificable** (archivos existentes, resultados
  comprobables con comandos, fechas de commits). Si un dato no se puede
  verificar, se indica **«pendiente de documentar»**; nunca se inventa.
- No se incluyen **claves, tokens, contraseñas ni información privada**.
- Cada entrada usa la plantilla de la sección 5 y se añade al final del
  registro, con el apartado al que pertenece.

## 2. Configuración inicial: creación de `AGENTS.md`

### Entrada 2.1 — Creación de `AGENTS.md`

- **Fecha:** pendiente de documentar
  (referencia verificable: commit `4527156` con fecha 2026-11-17).
- **Objetivo:** definir las reglas de desarrollo del proyecto (stack,
  comandos, arquitectura, pruebas, límites de seguridad y estilo) en un
  archivo `AGENTS.md` que guíe al agente.
- **Texto del prompt:** pendiente de documentar (el prompt que originó el
  archivo no está registrado en el repositorio).
- **Modelo utilizado:** pendiente de documentar.
- **Archivos afectados:** `AGENTS.md` (verificado: existe en la raíz del repo
  y está versionado en el commit `4527156`).
- **Resultado obtenido:** verificado por el contenido actual de `AGENTS.md`,
  que incluye las secciones: stack técnico (Python 3.12, uv, OpenCode 1.18.35),
  comandos (`uv sync`, `uv run tareas`, `uv run pytest`, ruff), arquitectura
  (acciones configurables en `acciones.json`, modo `--simular`), pruebas
  (fixtures mutables solo en `~/pruebas-tareas`), reglas de seguridad
  (no secretos en el repo, no commits por iniciativa propia, no modificar
  archivos personales) y estilo (PEP 8 con ruff, textos en español).
- **Aprobación realizada por el usuario:** pendiente de documentar.

## 3. Configuración de OpenCode: creación de `opencode.json`

### Entrada 3.1 — Creación de `opencode.json` y sus permisos

- **Fecha:** pendiente de documentar
  (referencia verificable: el archivo está versionado en el commit `2e6061c`
  con fecha 2026-11-17).
- **Objetivo:** configurar los permisos de OpenCode para que las operaciones
  de edición y ejecución de comandos requieran autorización del usuario, y
  para denegar operaciones de git peligrosas y la lectura/edición de archivos
  con secretos.
- **Texto del prompt:** pendiente de documentar.
- **Modelo utilizado:** pendiente de documentar.
- **Archivos afectados:** `opencode.json` (verificado: existe en la raíz del
  repo, versionado en el commit `2e6061c`).
- **Resultado obtenido:** verificado por el contenido actual de
  `opencode.json`, con el esquema de permisos siguiente:

  | Permiso | Regla |
  |---|---|
  | `read` | `*` permitido; **denegado** para `.env`, `.env.*`, `.pem`, `.key`, `.p12`; `.env.example` permitido |
  | `edit` | `*` con **confirmación (ask)**; **denegado** para `.env`, `.env.*`, `.pem`, `.key`, `.p12`; `.env.example` con confirmación |
  | `bash` | `*` con **confirmación (ask)**; **denegado**: `git commit`, `git push`, `git reset`, `git restore`, `git checkout`, `git stash`, `git rebase`, `git clean` (y sus variantes con argumentos) |

  **Nota de actualización (2026-11-19):** la fila `bash` anterior refleja la
  configuración inicial de la entrada 3.1. La allowlist vigente, con
  `git *`/`git.exe *` denegados por defecto y las consultas de solo lectura
  permitidas, se documenta en las entradas 5.7, 5.8 y 5.10, en `README.md` y
  en `docs/trazabilidad.md`.

- **Aprobación realizada por el usuario:** pendiente de documentar.

## 4. Pruebas de seguridad: autorización de comandos

### Entrada 4.1 — Comprobación de que OpenCode solicita autorización

- **Fecha:** pendiente de documentar.
- **Objetivo:** comprobar que OpenCode respeta la configuración de permisos de
  `opencode.json` y **solicita autorización al usuario** antes de editar
  archivos o ejecutar comandos, y que deniega directamente los comandos
  prohibidos.
- **Texto del prompt:** pendiente de documentar.
- **Modelo utilizado:** pendiente de documentar.
- **Archivos afectados:** ninguno esperado (las pruebas de permisos no deben
  modificar archivos; los archivos con secretos como `.env` deben quedar
  inaccesibles tanto para lectura como para edición, según la configuración).
- **Resultado obtenido:** pendiente de documentar (quedaría por registrar qué
  pruebas se realizaron, por ejemplo: intento de edición de un archivo,
  intento de ejecución de un comando con permisos `ask`, e intento de un
  comando denegado como `git commit`, y el comportamiento observado en cada
  caso).
- **Aprobación realizada por el usuario:** pendiente de documentar.

## 5. Registro de futuros prompts

Para cada nueva tarea, añadir una entrada con esta plantilla, en el apartado
que corresponda (o en un apartado nuevo si la tarea no encaja en los
anteriores):

```markdown
### Entrada X.Y — <título breve de la tarea>

- **Fecha:** AAAA-MM-DD
- **Objetivo:** <qué se pretendía conseguir con el prompt>
- **Texto del prompt:**
  > <transcripción literal del prompt, sin parafrasear>
- **Modelo utilizado:** <modelo y versión del agente, si se conoce>
- **Archivos afectados:** <lista de archivos creados/modificados/leídos>
- **Resultado obtenido:** <qué ocurrió, con verificación cuando sea posible
  (salida de comandos, tests, commits)>
- **Aprobación realizada por el usuario:** <cómo y cuándo se aprobó
  (confirmación de permiso, revisión del diff, respuesta a una pregunta, …)>
```

Recordatorios al añadir entradas:

- Solo información verificable; usar «pendiente de documentar» si falta un
  dato.
- No incluir claves, tokens ni información privada.
- Mantener el documento en español y seguir el estilo PEP 8 / ruff del
  proyecto donde aplique.

---

### Entrada 5.1 — Creación de este documento (`docs/prompts.md`)

- **Fecha:** 2026-11-17
- **Objetivo:** crear `docs/prompts.md` para documentar los prompts
  importantes del desarrollo agéntico, con apartados de introducción,
  configuración inicial, configuración de OpenCode, pruebas de seguridad y
  plantilla para futuros prompts.
- **Texto del prompt:**
  > «Estoy desarrollando el Proyecto 2 de DAM: una herramienta CLI llamada
  > `tareas`, utilizando Python 3.12, uv y OpenCode 1.18.35. Quiero crear el
  > archivo `docs/prompts.md` para documentar los prompts importantes
  > utilizados durante el desarrollo agéntico. Incluye estos apartados:
  > 1. Introducción: finalidad del documento y cómo registrar los prompts.
  > 2. Configuración inicial: creación de AGENTS.md.
  > 3. Configuración de OpenCode: creación de opencode.json y sus permisos.
  > 4. Pruebas de seguridad: comprobación de que OpenCode solicita
  > autorización para ejecutar comandos.
  > 5. Registro de futuros prompts: plantilla reutilizable para nuevas tareas.
  > Para cada prompt documenta: Fecha. Objetivo. Texto del prompt. Modelo
  > utilizado. Archivos afectados. Resultado obtenido. Aprobación realizada
  > por el usuario. Utiliza únicamente información que puedas verificar.
  > No inventes fechas, prompts literales ni resultados. Si falta información,
  > indica que está pendiente de documentar. No incluyas claves, contraseñas
  > ni información privada. Mantén toda la documentación en español. Primero
  > muéstrame el contenido completo propuesto para `docs/prompts.md`. No crees
  > ni modifiques archivos todavía. Espera mi aprobación.»
- **Modelo utilizado:** GLM (`glm-5.3-flash-free`) mediante OpenCode 1.18.35.
- **Archivos afectados:** `docs/prompts.md` (creación propuesta; pendiente de
  aprobación del usuario en el momento de registrar esta entrada).
- **Resultado obtenido:** propuesta de contenido mostrada al usuario en la
  conversación; creación del archivo pendiente de aprobación.
- **Aprobación realizada por el usuario:** pendiente (esta entrada se
  actualizará cuando el usuario apruebe la creación del archivo).

### Entrada 5.2 — Revisión de este documento (`docs/prompts.md`)

- **Fecha:** 2026-11-17
- **Objetivo:** revisar `docs/prompts.md`, ya creado y versionado en el
  commit `2e6061c`, corregir datos desactualizados y registrar esta
  intervención en el propio documento.
- **Texto del prompt:**
  > «Quiero continuar con el Proyecto 2 de DAM, una CLI llamada `tareas`,
  > desarrollada con Python 3.12, uv y OpenCode 1.18.35.
  > Necesito crear el archivo `docs/prompts.md` para documentar el
  > desarrollo agéntico.
  > Incluye:
  > 1. Introducción y finalidad del registro.
  > 2. Creación de AGENTS.md y las normas de seguridad.
  > 3. Creación de opencode.json y configuración de permisos.
  > 4. Comprobación de que OpenCode solicita aprobación para ejecutar comandos.
  > 5. Plantilla para registrar futuros prompts.
  > Para cada intervención importante, documenta:
  > - Fecha, cuando sea conocida.
  > - Objetivo.
  > - Prompt utilizado, literalmente cuando esté disponible.
  > - Modelo utilizado.
  > - Archivos afectados.
  > - Resultado.
  > - Aprobación del usuario.
  > Utiliza únicamente información verificable. No inventes prompts, fechas
  > ni resultados. Si falta información, indícalo.
  > No incluyas claves, contraseñas ni información privada.
  > Primero muéstrame el contenido completo propuesto de docs/prompts.md.
  > No crees ni modifiques archivos todavía. Espera mi aprobación.»
- **Modelo utilizado:** GLM (`glm-5.3-flash-free`) mediante OpenCode 1.18.35.
- **Archivos afectados:** `docs/prompts.md` (solo edición documental;
  actualización de la entrada 3.1 y adición de esta entrada 5.2).
- **Resultado obtenido:** verificado el estado del repositorio (3 commits:
  `691d334`, `4527156`, `2e6061c`); corregida en la entrada 3.1 la
  referencia al versionado de `opencode.json`, que ya está en el commit
  `2e6061c`; añadida esta entrada 5.2.
- **Aprobación realizada por el usuario:** tras revisar el contenido
  propuesto en la conversación, el usuario eligió la opción «Actualizar»
  entre las opciones ofrecidas (aplicar las dos correcciones mínimas).

### Entrada 5.3 — Capa de IA y acción `describir` (ADR-0002)

- **Fecha:** 2026-11-18
- **Objetivo:** implementar la primera acción con IA (`describir`) sobre el
  motor de acciones existente, con la integración configurable por variables
  de entorno, sin secretos en el repositorio, con modo sin red y alternativa
  determinista, y con la documentación y el ADR-0002 actualizados.
- **Texto del prompt (aprobación definitiva):**
  > «Sí, apruebo definitivamente el plan actualizado para implementar la
  > acción `describir`.
  >
  > Puedes comenzar la implementación en modo Build, respetando todas las
  > condiciones acordadas.
  >
  > Como todavía no dispongo de las credenciales ni de los datos de conexión
  > de los modelos del centro, deja la integración preparada para
  > configurarse posteriormente mediante variables de entorno. No inventes
  > credenciales ni fijes un proveedor externo como obligatorio.
  >
  > Comprueba que `--simular` no realiza ninguna llamada HTTP y que funciona
  > sin conexión.
  >
  > Al terminar:
  > 1. Ejecuta Ruff y comprueba el formato.
  > 2. Ejecuta las 63 pruebas previstas.
  > 3. Verifica `describir --simular`, `describir --sin-ia`,
  >    `describir --json` y `--help`.
  > 4. Muéstrame los archivos creados y modificados.
  > 5. Muéstrame el resultado de `git status --short` y `git diff --check`.
  >
  > No hagas commits, push ni utilices `--auto`.
  >
  > Detente después de las verificaciones y espera mi autorización antes de
  > cualquier cambio adicional.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode.
- **Archivos afectados:** creados `src/cli_tareas/ia.py`,
  `src/cli_tareas/describir.py`, `tests/test_describir.py`, `.env.example`
  y `docs/adr/ADR-0002.md`; modificados `src/cli_tareas/main.py`,
  `src/cli_tareas/acciones.py`, `src/cli_tareas/excepciones.py`,
  `acciones.json`, `README.md` y este documento.
- **Resultado obtenido:** `uv run ruff check .` y `ruff format --check .` sin
  errores; `uv run python -m pytest -q` con **63 pruebas superadas** (53
  anteriores + 10 nuevas); verificados `describir --simular` (código 0, sin
  red ni variables de entorno), `--sin-ia` (código 0), `--json --sin-ia`
  (JSON válido) y `--json` sin configuración (error JSON controlado, código
  1); `--help` general y de `describir` muestran la acción y sus opciones.
  La capa de IA envía únicamente metadatos (nunca el contenido de ficheros).
- **Aprobación realizada por el usuario:** aprobación explícita del plan
  actualizado en la conversación (texto citado arriba).

### Entrada 5.4 — Segunda acción con IA: `clasificar`

- **Fecha:** 2026-11-18
- **Objetivo:** implementar la segunda acción con IA (`clasificar`), que
  propone categorías (documentos, imágenes, código, datos, comprimidos y
  otros) a partir exclusivamente de metadatos, reutilizando `ia.py` y la
  arquitectura de `describir`, con `--simular`, `--sin-ia`, `--json`, ruta
  opcional y límite configurable.
- **Texto del prompt (aprobación definitiva):**
  > «Apruebo el diseño de la segunda acción con IA `clasificar`, con las
  > siguientes decisiones definitivas:
  >
  > 1. Carpetas: ignorarlas. Clasificar exclusivamente archivos.
  > 2. Respuestas de IA con categorías desconocidas: asignar `otros`, siempre
  >    que la respuesta sea válida. Los errores de conexión, autenticación o
  >    respuestas malformadas deben seguir tratándose como errores
  >    controlados.
  > 3. `--simular` combinado con `--json`: devolver exclusivamente JSON válido
  >    por stdout, sin llamadas a la API ni modificaciones de archivos.
  > 4. Límite predeterminado: `max_ficheros: 10`, configurable mediante
  >    acciones.json.
  >
  > Autorizo pasar a la Fase 2 (Build) para implementar exclusivamente la
  > acción `clasificar` según el diseño aprobado.
  >
  > Condiciones obligatorias:
  >
  > - Mantener intacto el comportamiento de listar, contar, buscar y resumen.
  > - Conservar la compatibilidad de describir, incluyendo su firma pública y
  >   sus mensajes.
  > - Reutilizar la infraestructura de IA existente sin duplicar lógica
  >   innecesariamente.
  > - No utilizar credenciales reales ni realizar llamadas a la API durante
  >   las pruebas.
  > - Ejecutar Ruff, todas las pruebas con pytest y las simulaciones
  >   necesarias.
  > - Las 63 pruebas existentes deben continuar pasando.
  > - Mostrar los resultados de las pruebas y `git diff --check`.
  > - Mostrar `git status --short` y un resumen de todos los archivos
  >   modificados.
  > - No realizar commits, push, reset ni utilizar `--auto`.
  >
  > Si alguna prueba falla, corrige el problema y vuelve a ejecutar la suite
  > completa.
  >
  > Al terminar, detente y espera mi autorización antes de cualquier cambio
  > adicional.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode.
- **Archivos afectados:** creados `src/cli_tareas/clasificar.py` y
  `tests/test_clasificar.py`; modificados `acciones.json`,
  `src/cli_tareas/acciones.py`, `src/cli_tareas/ia.py`,
  `src/cli_tareas/main.py`, `tests/conftest.py`, `README.md`,
  `docs/adr/ADR-0002.md` y este documento.
- **Resultado obtenido:** `uv run ruff check .` y
  `uv run ruff format --check .` sin errores; `uv run python -m pytest -q`
  con **92 pruebas superadas** (63 anteriores + 29 nuevas, incluidas las
  parametrizadas); verificados `clasificar --simular`,
  `clasificar --simular --json` (solo JSON válido),
  `clasificar --sin-ia --json`, `clasificar --sin-ia`, `clasificar --help`
  y `describir --sin-ia --json`; ninguna llamada real a la API.
- **Aprobación realizada por el usuario:** aprobación explícita del diseño
  y autorización de la Fase 2 en la conversación (texto citado arriba).

### Entrada 5.5 — Subagente `revisor` (solo lectura)

- **Fecha:** 2026-11-18
- **Objetivo:** implementar el subagente `revisor` exigido en la sesión 2 del
  Proyecto 2, compatible con OpenCode 1.18.35 y con permisos de solo lectura,
  para revisar código Python, `acciones.json`, pruebas y documentación,
  comprobar el cumplimiento de `AGENTS.md` y presentar los hallazgos por
  gravedad con soluciones propuestas.
- **Texto del prompt:**
  > «Sí, apruebo el diseño final del subagente `revisor`.
  >
  > Autorizo su implementación en modo Build, exclusivamente con los siguientes
  > cambios:
  >
  > 1. Crear `.opencode/agents/revisor.md`.
  > 2. Actualizar `README.md` para documentar el subagente.
  > 3. Actualizar `docs/prompts.md` con la entrada 5.5.
  >
  > Condiciones obligatorias:
  >
  > - Compatible con OpenCode 1.18.35.
  > - Configurar el subagente para revisión de solo lectura, sin permisos de
  >   edición.
  > - Permitir únicamente los comandos de verificación necesarios, como Ruff y
  >   pytest, con los datos de prueba en `~/pruebas-tareas`.
  > - No ejecutar operaciones de Git que modifiquen el repositorio.
  > - No acceder a credenciales, tokens ni archivos .env.
  > - No modificar código Python, acciones.json ni pruebas.
  > - No crear el comando `/revisar`.
  > - No realizar commits, push, reset ni utilizar --auto.
  >
  > Al finalizar, ejecuta las verificaciones previstas y muestra:
  >
  > 1. Resultado de `opencode agent list`.
  > 2. Resultado de Ruff.
  > 3. Número total de pruebas superadas con pytest.
  > 4. Resultado de `git diff --check`.
  > 5. Resultado de `git status --short`.
  > 6. Configuración definitiva de permisos del subagente.
  >
  > No realices cambios adicionales sin mi autorización.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode 1.18.35.
- **Archivos afectados:** creado `.opencode/agents/revisor.md`; modificados
  `README.md` y `docs/prompts.md`. Sin cambios en código Python,
  `acciones.json`, `tests/` ni `opencode.json`.
- **Resultado obtenido:** `cmd /c "opencode agent list"` detecta
  `revisor (subagent)`; los permisos efectivos incluyen `edit: deny`, la
  allowlist de `bash` (Ruff, pytest y consultas git de solo lectura) y la
  denegación de lectura de `.env*`/`.pem`/`.key`/`.p12`. `uv run ruff check .`
  pasa sin errores; `uv run ruff format --check .` informa de 29 archivos ya
  formateados; `uv run pytest -q` supera **92 pruebas**.
- **Aprobación realizada por el usuario:** aprobación explícita del diseño
  final en la conversación (texto citado arriba), con las decisiones de
  permitir pytest, no crear `/revisar` y actualizar `README.md` y
  `docs/prompts.md`.

### Entrada 5.6 — Revisión R-04 y R-05: fixtures y documentación

- **Fecha:** 2026-11-18
- **Objetivo:** cerrar los hallazgos pendientes del subagente revisor tras el
  commit `7f887ce`: R-04 (fixtures mutables de pytest fuera de
  `~/pruebas-tareas`) y R-05 (documentación desactualizada sobre las seis
  acciones y las 138 pruebas actuales), sin modificar `src/`,
  `acciones.json` ni el comportamiento de las acciones existentes.
- **Texto del prompt:**
  > «El plan R-04 y R-05 queda aprobado definitivamente.
  >
  > Ejecuta únicamente las modificaciones descritas, incluyendo el refactor de
  > `test_listar_ruta_predeterminada` y la entrada 5.6 completa de
  > `docs/prompts.md`.
  >
  > Mantén las 138 pruebas existentes, ejecuta todas las verificaciones
  > previstas y comprueba que los fixtures mutables se crean exclusivamente
  > dentro de `~/pruebas-tareas`.
  >
  > No modifiques `src/` ni `acciones.json`. No realices commits, push, reset
  > ni utilices `--auto`.
  >
  > Al finalizar, muestra los resultados de Ruff, pytest,
  > `git diff --check` y `git status --short`. Espera mi autorización antes de
  > cualquier cambio adicional.»
- **Decisiones aprobadas:**
  1. Añadir el fixture `carpeta_temporal` en `tests/conftest.py`, con base en
     `~/pruebas-tareas/_pytest/tmp`, y sustituir los usos de `tmp_path` en
     `acciones_inactivas` y en `tests/test_acciones.py`.
  2. Refactorizar `test_listar_ruta_predeterminada` para usar
     `acciones_temporales`, conservando sus comprobaciones originales
     (`exit_code == 0` y `"pruebas-tareas"` en la salida).
  3. Actualizar `README.md` y `docs/adr/ADR-0001.md` para reflejar las seis
     acciones (`listar`, `contar`, `buscar`, `resumen`, `describir` y
     `clasificar`) y las 138 pruebas.
  4. Conservar el historial de `docs/prompts.md` y añadir esta entrada 5.6 con
     el objetivo, el prompt, las decisiones, los archivos y los resultados.
- **Archivos afectados:** modificados `tests/conftest.py`,
  `tests/test_acciones.py`, `tests/test_listar.py`, `README.md`,
  `docs/adr/ADR-0001.md` y `docs/prompts.md`. Sin cambios en `src/`,
  `acciones.json`, `opencode.json` ni en el resto de pruebas.
- **Resultado obtenido:** `uv run ruff check .` sin errores;
  `uv run ruff format .` reformateó un único archivo y
  `uv run ruff format --check .` informa de 30 archivos ya formateados;
  `uv run pytest -q` supera **138 pruebas**; `git diff --check` sin errores;
  `git status --short` muestra únicamente los seis archivos modificados
  anteriores. Todas las escrituras de fixtures derivan de
  `Path.home() / "pruebas-tareas"`; no quedan usos de `tmp_path`, `tempfile`,
  `TemporaryDirectory`, `mkdtemp` ni `gettempdir` en `tests/`.
- **Aprobación realizada por el usuario:** aprobación definitiva del plan
  R-04 y R-05 en la conversación (texto citado arriba), con la decisión de
  incluir el refactor de `test_listar_ruta_predeterminada` y la entrada 5.6.

### Entrada 5.7 — Revisión R-07 y R-08: allowlist Git y validación estricta

- **Fecha:** 2026-11-18
- **Objetivo:** cerrar los hallazgos R-07 (permisos de operaciones Git
  peligrosas) y R-08 (claves desconocidas y predeterminados contradictorios)
  sin cambiar el comportamiento de las seis acciones existentes.
- **Texto del prompt:**
  > «Apruebo el diseño R-08 y el enfoque de allowlist para R-07,
  > condicionado a verificar la sintaxis y precedencia en OpenCode 1.18.35,
  > comprobar comandos permitidos y bloqueados, documentar las limitaciones,
  > mantener los permisos mínimos del subagente revisor e implementar R-08
  > conservando los predeterminados y el comportamiento de las seis acciones.»
- **Decisiones aprobadas:**
  1. Sustituir la blocklist Git por una allowlist en `opencode.json`: Git
     denegado por defecto y solo `git status`, `git diff`, `git log`,
     `git show` y `git --version` permitidos.
  2. Bloquear opciones de escritura o ejecución (`--output`, `--ext-diff`,
     `--textconv`) y redirecciones de Git; el resto de bash sigue en `ask`.
  3. Validación estricta en `acciones.py`: rechazo de acciones sin esquema y
     de claves desconocidas, validación de `ordenar_por` y predeterminados
     centralizados en `PREDETERMINADOS`.
  4. Actualizar `main.py` para consumir la configuración ya validada y
     fusionada, sin valores por defecto ocultos.
  5. Añadir pruebas de seguridad de `opencode.json` y de validación de
     acciones; actualizar README, ADR-0001, esta bitácora y la skill.
- **Verificación de compatibilidad:** se revisó el código fuente de
  OpenCode `v1.18.35`: `permission`/`bash` (V1), evaluación con `findLast`
  (gana la última regla), `propertyOrder: "original"` al cargar la
  configuración y comodines donde `*` también cubre el comando sin
  argumentos. `opencode debug config` confirmó el orden resuelto.
- **Archivos afectados:** modificados `opencode.json`,
  `src/cli_tareas/acciones.py`, `src/cli_tareas/main.py`,
  `tests/test_acciones.py`, `README.md`, `docs/adr/ADR-0001.md`,
  `docs/prompts.md`, `.opencode/skills/acciones-json/SKILL.md` y
  `.opencode/commands/nueva-accion.md`; creado
  `tests/test_permisos_opencode.py`. Sin cambios en `acciones.json` ni en
  los permisos propios del subagente `revisor`.
- **Resultado obtenido:** `uv run ruff check .` sin errores;
  `uv run ruff format --check .` sin cambios pendientes;
  `uv run pytest -q` supera **185 pruebas**; `git diff --check` sin errores;
  `git status --short` muestra únicamente los archivos previstos.
- **Limitación documentada:** la allowlist es defensa en profundidad, no
  aislamiento absoluto; rutas completas a `git.exe`, alias, envoltorios de
  PowerShell/CMD y otros procesos pueden eludir los patrones. Los commits
  manuales del usuario en PowerShell no están restringidos.
- **Aprobación realizada por el usuario:** aprobación explícita del diseño
  definitivo de la allowlist y de R-08 en la conversación (texto citado
  arriba).

### Entrada 5.8 — Implementación y verificación final de R-07 y R-08

- **Fecha:** 2026-11-19
- **Objetivo:** implementar y verificar la allowlist Git de solo lectura
  (R-07) y la validación estricta de `acciones.json` (R-08), confirmando la
  sintaxis y la precedencia en OpenCode 1.18.35, conservando los permisos
  mínimos del subagente `revisor`, los predeterminados y el comportamiento
  de las seis acciones.
- **Texto del prompt (aprobación definitiva):**
  > «Apruebo el diseño R-08 y el enfoque de allowlist para R-07,
  > condicionado a las siguientes comprobaciones:
  >
  > 1. Verifica que la sintaxis de permisos y la precedencia de las reglas
  >    allow/deny funcionan correctamente en OpenCode 1.18.35.
  > 2. Comprueba que los comandos Git de solo lectura autorizados funcionan y
  >    que commit, push, reset, merge, switch y las variantes con opciones
  >    globales quedan bloqueados.
  > 3. No presentes la allowlist como una protección absoluta si siguen
  >    existiendo vías alternativas mediante git.exe, PowerShell, CMD o alias.
  >    Documenta claramente esa limitación.
  > 4. Mantén los permisos mínimos necesarios para el subagente revisor y no
  >    amplíes permisos de ejecución generales.
  > 5. Implementa R-08 conservando exactamente los valores predeterminados y
  >    el comportamiento de las seis acciones existentes.
  > 6. Ejecuta Ruff, pytest completo y las nuevas pruebas de seguridad y
  >    validación.
  > 7. Actualiza README.md, ADR-0001.md, docs/prompts.md y la documentación
  >    de acciones-json según el plan.
  > 8. No realices commits, push, reset ni utilices --auto.
  >
  > Puedes pasar a Build e implementar R-07 y R-08, pero si no puedes
  > verificar la precedencia de permisos o detectas una incompatibilidad,
  > detente y solicita mi aprobación antes de aplicar una alternativa.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode 1.18.35.
- **Comprobaciones de compatibilidad:** `opencode --version` devuelve
  `1.18.35`; `opencode debug config` carga `opencode.json` y conserva el orden
  de las reglas; `opencode agent list` muestra las reglas globales y las del
  subagente `revisor` en el orden resuelto; `opencode debug agent revisor`
  confirma `edit: deny`, `bash: "*": deny` y la allowlist mínima de Ruff,
  pytest y consultas Git. La documentación oficial de OpenCode confirma que
  gana la última regla coincidente y que un patrón terminado en ` *` cubre
  también el comando sin argumentos.
- **Comandos Git de solo lectura comprobados:** `git status --short`,
  `git diff --check`, `git log --oneline -5`, `git show --stat --oneline -1`
  y `git --version` se ejecutaron correctamente. No se ejecutaron `commit`,
  `push`, `reset`, `merge`, `switch` ni otras operaciones destructivas: su
  bloqueo se verifica con `tests/test_permisos_opencode.py` y la precedencia
  resuelta, sin efectos sobre el repositorio.
- **Archivos afectados:** modificados `opencode.json`,
  `src/cli_tareas/acciones.py`, `src/cli_tareas/main.py`,
  `tests/test_acciones.py`, `README.md`, `docs/adr/ADR-0001.md`,
  `docs/prompts.md`, `.opencode/skills/acciones-json/SKILL.md` y
  `.opencode/commands/nueva-accion.md`; creado
  `tests/test_permisos_opencode.py`. Sin cambios en `acciones.json` ni en los
  permisos del subagente `revisor`; tampoco se conceden permisos generales de
  bash.
- **Resultado obtenido:** `uv run ruff check .` sin errores;
  `uv run ruff format --check .` sin cambios pendientes; `uv run pytest -q`
  supera **189 pruebas** (185 anteriores + 4 casos nuevos de operaciones
  destructivas y `git.exe`); `uv run pytest tests/test_permisos_opencode.py
  tests/test_acciones.py -q` supera **67 pruebas** de seguridad y validación;
  las seis acciones responden a `--simular` y `--help` muestra los seis
  comandos; `git diff --check` sin errores y `git status --short` muestra
  únicamente los archivos previstos. La allowlist se documenta como defensa
  en profundidad, no como aislamiento absoluto: rutas completas a `git.exe`,
  alias, PowerShell/CMD, pipes y otra configuración de Git pueden eludir los
  patrones.
- **Aprobación realizada por el usuario:** aprobación explícita en la
  conversación (texto citado arriba), tras presentar el diseño definitivo de
  la allowlist y de R-08.

---

### Entrada 5.9 — Corrección de hallazgos de la auditoría (H-01 a H-04)

- **Fecha:** 2026-11-19
- **Objetivo:** aplicar los cuatro hallazgos aprobados de la auditoría final:
  bloquear `git diff --no-index` en los permisos de OpenCode (H-01), convertir
  en errores controlados las respuestas no UTF-8 y las URLs inválidas de la
  capa de IA (H-02), evitar que llaves en `--termino`/`--extension` rompan el
  mensaje de `--simular` (H-03) y tratar `TAREAS_IA_TIMEOUT` vacío como el
  valor predeterminado de 30 s (H-04).
- **Texto del prompt:** transcripción resumida (el texto literal completo no
  se conserva en el contexto de esta sesión):
  > «Revisa el proyecto completo en solo lectura y devuelve un informe con
  > hallazgos ordenados por gravedad.»
  >
  > «Apruebo implementar H-01 a H-04 con estas condiciones: mantener las seis
  > acciones y las interfaces públicas, añadir pruebas por cada corrección,
  > compatibilidad con OpenCode 1.18.35, sin dependencias nuevas, sin commits
  > ni `--auto`, y no modificar `acciones.json`.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode 1.18.35.
- **Archivos afectados:** modificados `opencode.json`,
  `src/cli_tareas/ia.py`, `src/cli_tareas/main.py`, `tests/test_ia.py`,
  `tests/test_buscar.py`, `tests/test_describir.py`,
  `tests/test_permisos_opencode.py`, `.env.example`, `README.md`,
  `docs/adr/ADR-0001.md`, `docs/prompts.md` y
  `.opencode/skills/acciones-json/SKILL.md`. Sin cambios en `acciones.json`.
- **Resultado obtenido:** `uv run ruff check .` sin errores;
  `uv run ruff format --check .` sin cambios pendientes; `uv run pytest -q`
  supera **204 pruebas** (189 anteriores + 15 nuevas); `opencode debug config`
  resuelve `"git diff *--no-i*": "deny"`; las seis acciones responden a
  `--simular`; `buscar --simular --termino '{foo}'`, `'{}'` y `'{0}'` ya no
  falla; `git diff --check` sigue permitido. Limitación documentada: una
  sesión de OpenCode ya abierta mantiene las reglas cargadas al inicio, por lo
  que la denegación de `git diff --no-index` se aplica al reiniciar la sesión.
- **Aprobación realizada por el usuario:** aprobación explícita de H-01 a H-04
  y de sus condiciones en la conversación, antes de editar archivos.

### Entrada 5.10 — Seguridad, trazabilidad y documentación (H-06 a H-08)

- **Fecha:** 2026-11-19
- **Objetivo:** ampliar las pruebas de seguridad de `opencode.json` con
  variantes de `git diff --no-index`, comandos compuestos, tuberías y
  redirecciones (H-06); crear la matriz de trazabilidad R-01 a R-08,
  identificando las definiciones inferidas (H-07); y corregir la documentación
  de permisos, recuentos y limitaciones (H-08). Sin modificar `src/`,
  `acciones.json` ni el comportamiento de las seis acciones.
- **Texto del prompt (aprobación definitiva):**
  > «Apruebo el plan y el mapa provisional de R-01 a R-08. Implementa
  > únicamente los cambios descritos, identifica claramente los requisitos
  > inferidos y ejecuta todas las verificaciones previstas. No realices
  > commits, push, reset ni utilices --auto. Detente al terminar y muéstrame
  > los resultados y el estado de Git.»
- **Modelo utilizado:** `deepseek-v4.1-flash-free` mediante OpenCode 1.18.35.
- **Archivos afectados:** modificado `tests/test_permisos_opencode.py`; creado
  `docs/trazabilidad.md`; modificados `README.md`,
  `docs/adr/ADR-0001.md` y `docs/prompts.md`. Sin cambios en `opencode.json`,
  `src/`, `acciones.json` ni `tests/conftest.py`.
- **Resultado obtenido:** `uv run pytest tests/test_permisos_opencode.py -q`
  supera **85 pruebas**; `uv run pytest -q` supera **244 pruebas**;
  `uv run ruff check .` sin errores; `uv run ruff format --check .` informa de
  31 archivos ya formateados; `cmd /c "opencode --version"` devuelve
  `1.18.35`; `cmd /c "opencode debug config"` confirma `git diff *--no-i*`
  como `deny` y el orden de la allowlist. Las seis acciones responden a
  `--simular`. `opencode.json`, `src/` y `acciones.json` no se modificaron.
- **Limitaciones documentadas:** R-01, R-02, R-03 y R-06 son definiciones
  inferidas al no conservarse el informe original del subagente `revisor`; la
  allowlist Git es defensa en profundidad y no aislamiento absoluto. Las
  tuberías se evalúan por segmentos y el destino puede quedar en `ask`.
- **Aprobación realizada por el usuario:** aprobación explícita del plan y del
  mapa provisional en la conversación (texto citado arriba).
