# CLI Tareas con IA

CLI de línea de comandos para **gestionar tareas asistidas por IA**, desarrollada como **Proyecto 2 de DAM (2º DAM)** con fines educativos. Automatiza tareas repetitivas del sistema de ficheros (listar, contar, buscar, resumir, describir y clasificar carpetas) de forma **segura, configurable y verificable**, e incorpora dos acciones asistidas por IA (`describir` y `clasificar`).

## Objetivos y funcionalidades

- Interfaz de terminal coherente, con ayuda autogenerada y salida formateada con tablas.
- **Acciones configurables sin tocar el código fuente**, mediante `acciones.json`.
- **Seguridad**: modo `--simular` para prever el efecto de una operación antes de ejecutarla, validación estricta de la configuración y límite de resultados.
- **Calidad comprobable**: 189 pruebas automatizadas superadas y lint limpio con Ruff.

Funcionalidades actuales (todas de **solo lectura** sobre el sistema de ficheros):

| Comando | Descripción |
|---|---|
| `version` / `--version` | Muestra la versión de la aplicación. |
| `listar` | Lista el contenido de una carpeta (nombre, tipo, tamaño y fecha). |
| `contar` | Cuenta los ficheros de una carpeta. |
| `buscar` | Busca ficheros por nombre o extensión. |
| `resumen` | Resume una carpeta: nº de ficheros, tipos y tamaño total. |
| `describir` | Genera descripciones en español de los ficheros usando IA (o modo determinista con `--sin-ia`). |
| `clasificar` | Clasifica los ficheros por categorías (documentos, imágenes, código, datos, comprimidos, otros) usando IA (o modo determinista con `--sin-ia`). |

## Tecnologías y dependencias

| Herramienta | Versión | Uso |
|---|---|---|
| Python | 3.12 (obligatorio) | Lenguaje del proyecto, con type hints modernos (`Path \| None`, etc.). |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.9 | Gestión de entorno virtual, dependencias y ejecución (`pyproject.toml` + `uv.lock`). |
| [Typer](https://typer.tiangolo.com/) | ≥ 0.19 | Definición de la CLI con funciones tipadas y `--help` autogenerado. |
| [Rich](https://rich.readthedocs.io/) | ≥ 14 | Tablas y mensajes con estilos en la terminal. |
| pytest (dev) | ≥ 8 | Pruebas automatizadas. |
| Ruff (dev) | ≥ 0.14 | Lint y formato (PEP 8). |

## Requisitos previos

- **Windows** con **PowerShell** (el proyecto se prueba en este entorno).
- **Python 3.12** instalado.
- **uv** instalado. En PowerShell:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

- Una carpeta de pruebas fuera del repositorio (por defecto `~/pruebas-tareas`), usada como `ruta_predeterminada` de las acciones. Puedes crearla con:

  ```powershell
  New-Item -ItemType Directory -Path "$HOME\pruebas-tareas"
  ```

## Instalación (Windows / PowerShell)

1. Clona o descarga el repositorio y sitúate en la carpeta del proyecto.
2. Crea el entorno virtual e instala las dependencias:

   ```powershell
   uv sync
   ```

3. Comprueba que la aplicación responde:

   ```powershell
   uv run python -m cli_tareas.main version
   ```

   Debe mostrar `cli-tareas 0.1.0`.

### Ejecución en Windows: `uv run tareas` vs `python -m`

El punto de entrada declarado en `pyproject.toml` es el comando `tareas`:

```powershell
uv run tareas --help
```

Sin embargo, en algunos equipos Windows el **control de aplicaciones** (App Control / antivirus) puede bloquear el script `tareas` generado por uv en el entorno virtual y fallar con un error como:

```text
error: Failed to spawn: tareas
  cause: Una directiva de Control de aplicaciones bloqueó este archivo. (os error 4551)
```

Como alternativa verificada, usa la forma equivalente mediante el módulo de Python, que siempre funciona:

```powershell
uv run python -m cli_tareas.main --help
```

Ambas formas ejecutan la misma aplicación (`cli_tareas.main:app`). Los ejemplos del resto de este documento usan la forma `python -m` para garantizar la compatibilidad.

## Comandos disponibles

La ayuda general se muestra con `--help` (también al ejecutar la CLI sin argumentos):

```powershell
uv run python -m cli_tareas.main --help
```

### `version`

```powershell
uv run python -m cli_tareas.main version
```

También se puede consultar con la opción global `--version`:

```powershell
uv run python -m cli_tareas.main --version
```

### `listar` — listar una carpeta

Muestra nombre, tipo, tamaño y fecha de modificación de cada entrada.

```powershell
# Con la ruta_predeterminada de acciones.json (~/pruebas-tareas)
uv run python -m cli_tareas.main listar

# Con una ruta concreta
uv run python -m cli_tareas.main listar C:\Users\Public
```

### `contar` — contar ficheros

```powershell
uv run python -m cli_tareas.main contar
```

### `buscar` — buscar ficheros

Opciones: `--termino` (texto que debe contener el nombre) y `--extension` (extensión, admite escribir `txt` o `.txt`).

```powershell
# Por término en el nombre
uv run python -m cli_tareas.main buscar --termino informe

# Por extensión
uv run python -m cli_tareas.main buscar --extension .txt

# Combinando ambos filtros
uv run python -m cli_tareas.main buscar --termino informe --extension txt

# En una carpeta concreta
uv run python -m cli_tareas.main buscar C:\Users\Public --extension .csv
```

Si la búsqueda devuelve más resultados que `max_resultados` (configurado en `acciones.json`), se recorta la lista y se avisa: `Mostrando X de Y resultados`.

### `resumen` — resumir una carpeta

```powershell
uv run python -m cli_tareas.main resumen
```

### `describir` — describir ficheros (capa IA)

Genera una descripción en español de cada fichero y carpeta de primer nivel,
**a partir de únicamente sus metadatos** (nombre, tipo, tamaño y fecha):
nunca se envía el contenido de los ficheros.

```powershell
# Con IA (requiere configurar las variables de entorno, ver «Capa de IA»)
uv run python -m cli_tareas.main describir

# Modo determinista, sin IA ni red (no requiere ninguna configuración)
uv run python -m cli_tareas.main describir --sin-ia

# Salida en JSON (sin colores, apta para tuberías)
uv run python -m cli_tareas.main describir --json --sin-ia
```

`max_ficheros` (en `acciones.json`, por defecto 10) limita cuántos elementos
se describen por orden.

### `clasificar` — clasificar ficheros (capa IA)

Clasifica cada fichero de primer nivel en una de estas categorías:
`documentos`, `imágenes`, `código`, `datos`, `comprimidos` u `otros`. Solo se
usan **metadatos** (nombre, tipo, tamaño y fecha); nunca se lee ni se envía el
contenido. Las carpetas se ignoran y no se mueve, renombra, elimina ni modifica
ningún archivo.

```powershell
# Con IA (requiere configurar las variables de entorno, ver «Capa de IA»)
uv run python -m cli_tareas.main clasificar

# Clasificación determinista por extensión, sin IA ni red
uv run python -m cli_tareas.main clasificar --sin-ia

# Salida en JSON (sin colores, apta para tuberías)
uv run python -m cli_tareas.main clasificar --sin-ia --json

# Simulación combinada con JSON: solo se emite JSON por stdout
uv run python -m cli_tareas.main clasificar --simular --json
```

`max_ficheros` (en `acciones.json`, por defecto 10) limita cuántos ficheros se
clasifican, tras ordenarlos por nombre. Si la IA devuelve una categoría
desconocida, se asigna `otros`; los errores de conexión, autenticación o las
respuestas malformadas siguen tratándose como errores controlados.

### Ayuda de cada comando

```powershell
uv run python -m cli_tareas.main listar --help
```

## Modo `--simular`

Todas las acciones con efectos aceptan la opción `--simular`, que **muestra lo que se haría sin ejecutar nada** (no hay efectos externos). Es una red de seguridad pensada para prever el resultado de una operación antes de ejecutarla, especialmente útil en un desarrollo asistido por IA:

```powershell
uv run python -m cli_tareas.main listar --simular
# Salida: [simulación] Se listaría el contenido de: <ruta>

uv run python -m cli_tareas.main buscar --termino informe --simular
# Salida: [simulación] Se buscarían ficheros (nombre con «informe») en: <ruta>

uv run python -m cli_tareas.main describir --simular
# Salida: [simulación] Se describirían los ficheros de: <ruta>

uv run python -m cli_tareas.main clasificar --simular
# Salida: [simulación] Se clasificarían los ficheros de: <ruta>

uv run python -m cli_tareas.main clasificar --simular --json
# Salida: {"accion": "clasificar", "simulacion": true, "ruta": "<ruta>"}
```

`describir --simular` y `clasificar --simular` no realizan ninguna llamada de
red ni exigen ninguna variable de entorno: la simulación se corta antes de la
capa de IA. En `clasificar`, la combinación `--simular --json` emite
exclusivamente JSON válido por stdout.

## Capa de IA y modo sin red

Las acciones `describir` y `clasificar` llaman a un **endpoint compatible con la API de OpenAI**
(el formato usado por los modelos locales del centro, p. ej. ollama, y por
OpenCode). La configuración va **exclusivamente por variables de entorno**,
nunca en el repo; `.env.example` documenta los nombres sin valores reales:

| Variable | Papel |
|---|---|
| `TAREAS_API_BASE` | URL base del servicio (obligatoria para usar IA). |
| `TAREAS_MODELO` | Nombre del modelo (obligatorio para usar IA). |
| `TAREAS_API_KEY` | Clave, solo si el servicio la exige (opcional). |
| `TAREAS_IA_TIMEOUT` | Segundos de espera (opcional, por defecto 30). |

Cuando el centro facilite los datos de conexión, copia `.env.example` a
`.env`, completa los valores y ejecuta:

```powershell
# Cargar las variables del .env y lanzar la CLI
uv run --env-file .env python -m cli_tareas.main describir
```

**Modo sin red**: si falta configuración, no hay conexión o el servicio
responde con error, la CLI lo explica en una línea (sin traceback, sin
secretos), recuerda las alternativas (`--sin-ia` y las acciones sin IA:
`listar`, `contar`, `buscar`, `resumen`) y termina con código de salida 1.
Con `--sin-ia` se generan descripciones o clasificaciones deterministas a
partir de los metadatos, etiquetadas como «determinista», sin IA ni red.

Las peticiones a la IA contienen **solo metadatos** (nombre, tipo, tamaño y
fecha); nunca el contenido de los ficheros. La decisión completa está en
[`docs/adr/ADR-0002.md`](docs/adr/ADR-0002.md).

## Configuración: `acciones.json`

Las acciones se definen en `acciones.json`, en la **raíz del proyecto**. Nunca se codifican (hardcodean) en el código fuente. Contenido actual:

```json
{
  "listar": {
    "activa": true,
    "descripcion": "Lista el contenido de una carpeta",
    "ruta_predeterminada": "~/pruebas-tareas",
    "incluir_carpetas": true,
    "ordenar_por": "nombre"
  },
  "contar": {
    "activa": true,
    "descripcion": "Cuenta los ficheros de una carpeta",
    "ruta_predeterminada": "~/pruebas-tareas",
    "incluir_carpetas": false
  },
  "buscar": {
    "activa": true,
    "descripcion": "Busca ficheros por nombre o extensión",
    "ruta_predeterminada": "~/pruebas-tareas",
    "max_resultados": 50
  },
  "resumen": {
    "activa": true,
    "descripcion": "Resumen de una carpeta: ficheros, tipos y tamaño total",
    "ruta_predeterminada": "~/pruebas-tareas"
  },
  "describir": {
    "activa": true,
    "descripcion": "Genera descripciones en español de los ficheros de una carpeta usando IA",
    "ruta_predeterminada": "~/pruebas-tareas",
    "max_ficheros": 10
  },
  "clasificar": {
    "activa": true,
    "descripcion": "Clasifica los ficheros de una carpeta por categorías usando IA",
    "ruta_predeterminada": "~/pruebas-tareas",
    "max_ficheros": 10
  }
}
```

### La carpeta `~/pruebas-tareas`

Las acciones usan como `ruta_predeterminada` la carpeta `~/pruebas-tareas`, que es **externa al repositorio** (se encuentra en la carpeta personal del usuario). Esta carpeta **debe existir** para poder utilizar las acciones sin indicar una ruta; si no existe, la CLI mostrará un error controlado («La carpeta no existe: …») y terminará con código de salida 1.

Puedes crearla desde PowerShell:

```powershell
New-Item -ItemType Directory -Path "$HOME\pruebas-tareas"
```

También es donde residen los **datos y fixtures mutables** de las pruebas (sección «Pruebas automatizadas»), por lo que se crea automáticamente al ejecutar `uv run pytest`.

Si no quieres usar la ruta predeterminada, siempre puedes pasar una ruta concreta al comando:

```powershell
uv run python -m cli_tareas.main listar C:\Users\Public
```

### Significado de las claves

- `activa`: interruptor para activar/desactivar la acción (`false` la desactiva de forma centralizada; la CLI lo notifica con un error controlado).
- `descripcion`: descripción breve de la acción (una frase en español).
- `ruta_predeterminada`: carpeta usada si no se indica ruta al invocar el comando (`~` se expande a la carpeta personal del usuario).
- `incluir_carpetas`: controla si se incluyen las subcarpetas de **primer nivel** de la carpeta analizada. Lo usan `listar` (por defecto `true`: las subcarpetas aparecen como filas de la tabla) y `contar` (por defecto `false`: se cuentan solo los ficheros). No afecta a `buscar` ni a `resumen`, que procesan solo el primer nivel de la carpeta: `buscar` examina ficheros y carpetas (y excluye las carpetas cuando se filtra por extensión), y `resumen` cuenta ficheros y carpetas de primer nivel.
- `ordenar_por`: criterio de ordenación de `listar` (valores válidos: `nombre`, `tamano`, `modificado`, `tipo`).
- `max_resultados`: límite de resultados de `buscar` (debe ser un entero mayor que 0).
- `max_ficheros`: límite de elementos que `describir` y `clasificar` procesan por orden (debe ser un entero mayor que 0). En `clasificar`, las carpetas no cuentan: solo se clasifican ficheros.

La configuración se **valida estrictamente** al ejecutar cualquier acción (`src/cli_tareas/acciones.py`): existencia de la acción y de su esquema, que esté activa, rechazo de claves desconocidas, tipos correctos de cada clave, valores positivos y valores permitidos para `ordenar_por`. Las claves opcionales ausentes se completan con los predeterminados declarados en `PREDETERMINADOS` (`listar`: `incluir_carpetas=true` y `ordenar_por=nombre`; `contar`: `incluir_carpetas=false`; `buscar`: sin límite de resultados; `describir` y `clasificar`: `max_ficheros=10`). Ante un error, la CLI muestra un mensaje claro y termina con código de salida 1.

## Estructura del proyecto

```text
cli-tareas/
├── acciones.json              # Configuración declarativa de las acciones
├── .env.example               # Nombres de las variables de entorno de IA (sin valores)
├── AGENTS.md                  # Reglas de desarrollo que guían al agente
├── opencode.json              # Permisos de OpenCode (edición, bash, secretos)
├── pyproject.toml             # Metadatos, dependencias y punto de entrada
├── uv.lock                    # Bloqueo reproducible de dependencias
├── docs/
│   ├── prompts.md             # Registro de prompts del desarrollo agéntico
│   └── adr/
│       ├── ADR-0001.md        # Decisiones de arquitectura
│       └── ADR-0002.md        # Capa de IA y modo sin red
├── .opencode/
│   ├── agents/
│   │   └── revisor.md         # Subagente de revisión (solo lectura)
│   ├── commands/
│   │   └── nueva-accion.md    # Comando /nueva-accion
│   └── skills/
│       └── acciones-json/
│           └── SKILL.md       # Skill para acciones configurables
├── src/cli_tareas/
│   ├── main.py                # Comandos Typer y orquestación (capa CLI)
│   ├── acciones.py            # Carga, validación y esquemas de acciones.json
│   ├── ficheros.py            # Dominio: resolver/validar/listar entradas
│   ├── ia.py                  # Capa de IA: configuración y llamada al modelo
│   ├── listar.py              # Tabla de listar (presentación)
│   ├── contar.py              # Texto de contar (presentación)
│   ├── buscar.py              # Tabla de buscar (presentación)
│   ├── resumen.py             # Tabla de resumen (presentación)
│   ├── describir.py           # Tabla/JSON de describir (presentación)
│   ├── clasificar.py          # Clasificación por extensión, tabla/JSON
│   └── excepciones.py         # Jerarquía propia de errores (ErrorAccion)
└── tests/                     # 189 pruebas automatizadas (pytest)
```

## Pruebas automatizadas (pytest)

Las pruebas cubren la lógica de acciones, la validación estricta de `acciones.json`, la resolución de rutas, cada comando, el modo `--simular`, la desactivación de acciones, los errores de configuración, la clasificación determinista, la capa de IA (con la red simulada; nunca se llama a un servicio real en las pruebas) y la allowlist Git de `opencode.json` (sintaxis V1, orden de reglas y comandos permitidos/denegados):

```powershell
uv run pytest
```

Los **datos y fixtures mutables** de las pruebas viven **exclusivamente fuera del repositorio**, en `~/pruebas-tareas` (creados y limpiados automáticamente por los fixtures de `tests/conftest.py`). El **código** de las pruebas sí está en `tests/`.

## Análisis y formato con Ruff

```powershell
uv run ruff check .      # lint (PEP 8 y más)
uv run ruff format .     # formato automático
```

## Seguridad y protección de información privada

- **Sin secretos en el repo**: nunca se guardan claves, tokens ni contraseñas en el código ni en archivos versionados. Los valores sensibles van por variables de entorno (`.env`, protegido por `.gitignore`, documentado en `.env.example` sin valores reales). La capa de IA no necesita ninguna clave con los modelos locales del centro (`TAREAS_API_KEY` solo si el servicio la exige).
- **Modo simulación**: toda acción con efectos acepta `--simular`.
- **Interruptor centralizado**: cualquier acción puede desactivarse con `activa: false`.
- **Validación de configuración** antes de actuar, con errores controlados y código de salida 1 (sin trazas brutas).
- **Git de solo lectura para los agentes**: `opencode.json` deniega Git por defecto y solo permite consultas concretas (`git status`, `git diff`, `git log`, `git show` y `git --version`). El resto de operaciones, incluidas `commit`, `push`, `reset`, `merge`, `switch`, `checkout` y las variantes con opciones globales (`-C`, `-c`, `--git-dir`), quedan bloqueadas para las herramientas del agente. Sintaxis y precedencia verificadas con OpenCode 1.18.35 (`opencode debug config` y `opencode agent list`). Es una medida de **defensa en profundidad**, no un aislamiento absoluto: rutas completas a `git.exe`, alias, envoltorios de PowerShell/CMD, pipes y otra configuración de Git pueden eludir los patrones (ver limitaciones). Los commits que ejecutes manualmente en PowerShell no se ven afectados.
- **Alcance de solo lectura**: no existen acciones de escritura o borrado.
- **Archivos de prueba mutables solo en `~/pruebas-tareas`**, nunca dentro del repo.
- **Sin modo `--auto`** ni ejecución automática no supervisada; los commits y el push solo se hacen por petición explícita del usuario.

## Integración con OpenCode

El desarrollo es **agéntico**, con [OpenCode](https://opencode.ai) guiado por `AGENTS.md`. El archivo `opencode.json` configura permisos para operar con seguridad:

| Permiso | Regla |
|---|---|
| `read` | Permitido en general; **denegado** para `.env`, `.env.*`, `.pem`, `.key`, `.p12` (protección de secretos). |
| `edit` | Con **confirmación del usuario**; denegado para los mismos tipos de archivo sensibles. |
| `bash` | Con **confirmación del usuario** para comandos generales (no se conceden permisos amplios). Git se **deniega por defecto**; solo se permiten consultas de solo lectura: `git status`, `git diff`, `git log`, `git show` y `git --version`. Se bloquean además las opciones que escriben o ejecutan filtros (`--output`, `--ext-diff`, `--textconv`) y las redirecciones de Git. |

El registro de los prompts importantes del desarrollo se documenta en [`docs/prompts.md`](docs/prompts.md). La decisión de arquitectura de la capa de IA está en [`docs/adr/ADR-0002.md`](docs/adr/ADR-0002.md).

### Subagente `revisor`

El proyecto incluye un subagente de revisión en `.opencode/agents/revisor.md`
(OpenCode 1.18.35, formato de configuración V1). Se ejecuta en **solo lectura**:
no puede editar archivos ni ejecutar `git commit`, `push`, `reset` u otras
operaciones de escritura. Revisa el código Python, `acciones.json`, las pruebas
y la documentación, comprueba el cumplimiento de `AGENTS.md` y devuelve los
hallazgos ordenados por gravedad con una solución propuesta para cada uno.

Permisos destacados:

| Permiso | Regla |
|---|---|
| `edit` | Denegado para todos los archivos (incluye crear y parchear). |
| `read` | Permitido; denegado `.env`, `.env.*`, `.pem`, `.key` y `.p12`; `.env.example` permitido. |
| `bash` | Denegado salvo `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest` y consultas de solo lectura de git (`status`, `diff`, `log`). |
| `task`, `skill`, `webfetch`, `websearch` | Denegados. |
| `external_directory` | Denegado (no accede a `~/pruebas-tareas` ni a otras rutas externas). |

Para usarlo, reinicia la sesión de OpenCode y pide al agente principal algo como:

```text
Usa el subagente revisor para revisar el proyecto completo
```

El subagente se ejecuta en una sesión hija y devuelve el informe al agente
principal. No modifica el repositorio: los fixtures de pytest siguen viviendo
en `~/pruebas-tareas` y los caches (`.pytest_cache/`, `.ruff_cache/`) están
ignorados por git.

## Skill `acciones-json` y comando `/nueva-accion`

Para **añadir, modificar, desactivar o documentar una acción** hay una skill de OpenCode en `.opencode/skills/acciones-json/SKILL.md`. Define el flujo obligatorio:

1. **Analizar** (solo lectura) `acciones.json`, `ESQUEMAS` en `acciones.py` y el ADR vigente.
2. **Diseñar y pedir aprobación**: propuesta de entrada JSON, esquema, comando Typer y pruebas previstas, esperando un «sí» explícito antes de tocar nada.
3. **Implementar** siguiendo el patrón de las acciones existentes (`_iniciar()`, `--simular`, presentación separada del dominio).
4. **Validar en este orden**: `ruff check` + `ruff format` → ejecución primero con `--simular` → `pytest` completo → `--help` actualizado.
5. **Documentar** la acción y, si introduce una decisión nueva, actualizar el ADR (con permiso).

Además, el comando personalizado **`/nueva-accion`** (`.opencode/commands/nueva-accion.md`) orquesta este proceso en dos fases:

- **Fase 1** (agente *plan*, solo lectura): analiza y presenta el diseño de la acción; no modifica nada.
- **Fase 2** (agente *Build*, solo tras aprobación explícita del usuario y cambio manual de agente): implementa, valida y prueba.

Uso:

```text
/nueva-accion <descripción de la acción que quieres crear>
```

## Decisiones de arquitectura (ADR-0001)

Las decisiones técnicas del proyecto están registradas en [`docs/adr/ADR-0001.md`](docs/adr/ADR-0001.md): elección de **Python 3.12 + uv + Typer + Rich** (con alternativas descartadas), configuración declarativa mediante `acciones.json` con validación por esquemas, arquitectura en tres capas (presentación → motor de acciones → dominio de ficheros) y el diseño del modo `--simular` como medida de seguridad.

## Limitaciones conocidas

- **Solo lectura**: las acciones actuales no escriben, mueven ni borran ficheros.
- **Windows/PowerShell**: probado en Windows; en algunos equipos el comando `uv run tareas` puede ser bloqueado por App Control (usar `python -m cli_tareas.main` como alternativa).
- `ruta_predeterminada` apunta a `~/pruebas-tareas`, fuera del repo: la carpeta debe existir en cada máquina.
- Añadir una acción nueva requiere tocar `acciones.json` **y** el bloque `ESQUEMAS` de `acciones.py` (duplicación parcial documentada en el ADR).
- `acciones.json` no admite comentarios (limitación del formato JSON).
- La allowlist Git de `opencode.json` es una medida de **defensa en profundidad**, no un aislamiento absoluto: rutas completas a `git.exe`, alias de Git, envoltorios de PowerShell/CMD y otros procesos pueden eludir los patrones de prefijo. Además, un pipe puede dividir el comando y evaluar por separado el programa de destino. Los commits manuales del usuario no están restringidos.
- La integración con IA está preparada (`describir` y `clasificar`) pero pendiente de los datos de conexión de los modelos del centro (`TAREAS_API_BASE`/`TAREAS_MODELO`); hasta entonces funcionan el modo `--sin-ia` y el resto de acciones.
