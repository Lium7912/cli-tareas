class ErrorAccion(Exception):
    """Error base de las acciones de la CLI."""


class AccionNoDefinidaError(ErrorAccion):
    """La acción no aparece en acciones.json."""


class AccionDesactivadaError(ErrorAccion):
    """La acción existe pero está desactivada en acciones.json."""


class ConfiguracionInvalidaError(ErrorAccion):
    """La configuración de la acción no es válida (tipo o valor incorrectos)."""


class RutaInvalidaError(ErrorAccion):
    """La ruta indicada no existe, no es una carpeta o no es accesible."""


class IANoDisponibleError(ErrorAccion):
    """El servicio de IA no está configurado o no es accesible."""
