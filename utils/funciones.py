"""
Funciones utilitarias para el bot de trading
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger('BotMT5')

def validar_par_divisa(par):
    """
    Valida si un par de divisas es válido
    
    Args:
        par: Par de divisas a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    pares_validos = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "NZDUSD", "USDCAD", "EURGBP",
        "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY"
    ]
    
    return par in pares_validos

def calcular_retornos(precios):
    """
    Calcula los retornos porcentuales de una serie de precios
    
    Args:
        precios: Serie de precios
        
    Returns:
        pd.Series: Serie de retornos
    """
    try:
        return precios.pct_change()
    except Exception as e:
        logger.error(f"Error al calcular retornos: {str(e)}")
        return None

def calcular_sharpe_ratio(retornos, rf=0.02):
    """
    Calcula el ratio de Sharpe
    
    Args:
        retornos: Serie de retornos
        rf: Tasa libre de riesgo anual
        
    Returns:
        float: Ratio de Sharpe
    """
    try:
        return (retornos.mean() - rf) / retornos.std()
    except Exception as e:
        logger.error(f"Error al calcular Sharpe ratio: {str(e)}")
        return None

def calcular_drawdown(precios):
    """
    Calcula el drawdown máximo
    
    Args:
        precios: Serie de precios
        
    Returns:
        float: Drawdown máximo
    """
    try:
        maximos = precios.cummax()
        drawdowns = (precios - maximos) / maximos
        return drawdowns.min()
    except Exception as e:
        logger.error(f"Error al calcular drawdown: {str(e)}")
        return None

def validar_timeframe(timeframe):
    """
    Valida si un timeframe es válido
    
    Args:
        timeframe: Timeframe a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    timeframes_validos = [
        "M1", "M5", "M15", "M30",
        "H1", "H4", "D1", "W1", "MN1"
    ]
    
    return timeframe in timeframes_validos

def formatear_fecha(fecha):
    """
    Formatea una fecha a string
    
    Args:
        fecha: Objeto datetime
        
    Returns:
        str: Fecha formateada
    """
    try:
        return fecha.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error al formatear fecha: {str(e)}")
        return None

def validar_volumen(volumen):
    """
    Valida si un volumen es válido
    
    Args:
        volumen: Volumen a validar
        
    Returns:
        bool: True si es válido, False si no
    """
    try:
        volumen = float(volumen)
        return volumen > 0 and volumen <= 100
    except (ValueError, TypeError):
        return False

def calcular_pips(precio1, precio2, par):
    """
    Calcula el número de pips entre dos precios
    
    Args:
        precio1: Precio inicial
        precio2: Precio final
        par: Par de divisas
        
    Returns:
        float: Número de pips
    """
    try:
        # Para JPY, los pips son en la segunda decimal
        if par[-3:] == "JPY":
            return abs((precio1 - precio2) * 100)
        # Para otros pares, los pips son en la cuarta decimal
        return abs((precio1 - precio2) * 10000)
    except Exception as e:
        logger.error(f"Error al calcular pips: {str(e)}")
        return None
