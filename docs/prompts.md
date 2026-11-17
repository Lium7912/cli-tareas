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
  (referencia verificable: el archivo existe en la raíz del repo pero **aún
  no está versionado en git**).
- **Objetivo:** configurar los permisos de OpenCode para que las operaciones
  de edición y ejecución de comandos requieran autorización del usuario, y
  para denegar operaciones de git peligrosas y la lectura/edición de archivos
  con secretos.
- **Texto del prompt:** pendiente de documentar.
- **Modelo utilizado:** pendiente de documentar.
- **Archivos afectados:** `opencode.json` (verificado: existe en la raíz del
  repo, sin commit todavía).
- **Resultado obtenido:** verificado por el contenido actual de
  `opencode.json`, con el esquema de permisos siguiente:

  | Permiso | Regla |
  |---|---|
  | `read` | `*` permitido; **denegado** para `.env`, `.env.*`, `.pem`, `.key`, `.p12`; `.env.example` permitido |
  | `edit` | `*` con **confirmación (ask)**; **denegado** para `.env`, `.env.*`, `.pem`, `.key`, `.p12`; `.env.example` con confirmación |
  | `bash` | `*` con **confirmación (ask)**; **denegado**: `git commit`, `git push`, `git reset`, `git restore`, `git checkout`, `git stash`, `git rebase`, `git clean` (y sus variantes con argumentos) |

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
