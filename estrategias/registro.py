"""
Registro dinámico de estrategias disponibles
"""

from .base import EstrategiaBase
from .cruce_ma import CruceMedias
from .rsi import EstrategiaRSI
from log import Logger

# Diccionario de estrategias disponibles
ESTRATEGIAS_DISPONIBLES = {
    "Estrategia Base": EstrategiaBase,
    "Cruce de Medias": CruceMedias,
    "Estrategia RSI": EstrategiaRSI
}

def obtener_estrategias_disponibles():
    """
    Obtiene la lista de estrategias disponibles
    
    Returns:
        list: Lista de nombres de estrategias
    """
    return list(ESTRATEGIAS_DISPONIBLES.keys())

def crear_estrategia(nombre: str, conector, interfaz=None) -> EstrategiaBase:
    """
    Crea una instancia de la estrategia especificada
    
    Args:
        nombre: Nombre de la estrategia
        conector: Conector MT5 o SimuladorMT5
        interfaz: Referencia a la interfaz principal
        
    Returns:
        Instancia de la estrategia
    """
    try:
        if nombre not in ESTRATEGIAS_DISPONIBLES:
            raise ValueError(f"Estrategia no válida: {nombre}")
            
        estrategia = ESTRATEGIAS_DISPONIBLES[nombre](conector, interfaz)
        estrategia.iniciar()
        return estrategia
        
    except Exception as e:
        logger = Logger()
        logger.log_error(f"Error al crear estrategia {nombre}: {str(e)}")
        return None
