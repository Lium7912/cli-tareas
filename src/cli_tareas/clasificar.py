import json
import unicodedata
from pathlib import Path

from rich.table import Table

CATEGORIAS = ("documentos", "imágenes", "código", "datos", "comprimidos", "otros")

EXTENSIONES = {
    "documentos": {
        "pdf",
        "doc",
        "docx",
        "odt",
        "rtf",
        "txt",
        "md",
        "markdown",
        "tex",
        "ppt",
        "pptx",
        "epub",
    },
    "imágenes": {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "svg",
        "webp",
        "tif",
        "tiff",
        "ico",
        "heic",
    },
    "código": {
        "py",
        "pyi",
        "js",
        "jsx",
        "ts",
        "tsx",
        "java",
        "c",
        "h",
        "cpp",
        "hpp",
        "cc",
        "cs",
        "go",
        "rs",
        "rb",
        "php",
        "pl",
        "lua",
        "r",
        "swift",
        "kt",
        "kts",
        "scala",
        "sh",
        "bash",
        "zsh",
        "ps1",
        "bat",
        "cmd",
        "html",
        "htm",
        "css",
        "scss",
        "sass",
        "less",
        "vue",
        "svelte",
        "sql",
        "ipynb",
    },
    "datos": {
        "csv",
        "tsv",
        "json",
        "jsonl",
        "xml",
        "yaml",
        "yml",
        "toml",
        "ini",
        "cfg",
        "conf",
        "parquet",
        "avro",
        "xls",
        "xlsx",
        "ods",
        "db",
        "sqlite",
        "sqlite3",
        "mdb",
    },
    "comprimidos": {
        "zip",
        "rar",
        "7z",
        "tar",
        "gz",
        "tgz",
        "bz2",
        "xz",
        "zst",
        "iso",
    },
}

MAPA_EXTENSIONES = {
    extension: categoria
    for categoria, extensiones in EXTENSIONES.items()
    for extension in extensiones
}

EQUIVALENCIAS = {
    "documento": "documentos",
    "documentos": "documentos",
    "imagen": "imágenes",
    "imagenes": "imágenes",
    "codigo": "código",
    "codigos": "código",
    "dato": "datos",
    "datos": "datos",
    "comprimido": "comprimidos",
    "comprimidos": "comprimidos",
    "otro": "otros",
    "otros": "otros",
}


def _sin_acentos(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(
        caracter for caracter in normalizado if not unicodedata.combining(caracter)
    )


def clasificar_determinista(meta: dict) -> str:
    if meta.get("tipo") == "carpeta":
        return "otros"
    extension = Path(str(meta["nombre"])).suffix.lower().lstrip(".")
    return MAPA_EXTENSIONES.get(extension, "otros")


def normalizar_categoria(texto: str) -> str:
    palabras = _sin_acentos(str(texto).strip().lower()).replace("_", " ").split()
    for palabra in palabras:
        limpia = "".join(caracter for caracter in palabra if caracter.isalpha())
        categoria = EQUIVALENCIAS.get(limpia)
        if categoria is not None:
            return categoria
    return "otros"


def construir_tabla_clasificacion(filas: list[dict], ruta: Path, origen: str) -> Table:
    tabla = Table(title=f"Clasificación ({origen}) de {ruta}")
    tabla.add_column("Fichero")
    tabla.add_column("Categoría")
    for fila in filas:
        tabla.add_row(fila["nombre"], fila["categoria"])
    return tabla


def construir_salida_json(filas: list[dict], ruta: Path, origen: str) -> str:
    datos = {
        "accion": "clasificar",
        "ruta": str(ruta),
        "origen": origen,
        "ficheros": filas,
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)
