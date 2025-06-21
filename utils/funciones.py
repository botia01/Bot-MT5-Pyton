"""
Funciones utilitarias para el bot de trading
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import MetaTrader5 as mt5
import winsound

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

def convertir_timeframe(timeframe_str):
    """
    Convierte string de timeframe a constante de MT5
    
    Args:
        timeframe_str: String del timeframe (ej: "M1", "H4")
        
    Returns:
        int: Constante de MT5 correspondiente
    """
    timeframes = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1
    }
    return timeframes.get(timeframe_str)

def calcular_lote(risk_percent, balance, stop_loss_points):
    """
    Calcula el tamaño de lote basado en el riesgo
    
    Args:
        risk_percent: Porcentaje de riesgo (0-100)
        balance: Balance de la cuenta
        stop_loss_points: Puntos del stop loss
        
    Returns:
        float: Tamaño de lote
    """
    try:
        risk_amount = (risk_percent / 100) * balance
        return risk_amount / (stop_loss_points * 10000)
    except Exception as e:
        logger.error(f"Error al calcular lote: {str(e)}")
        return 0.01  # Lote mínimo por defecto

def mostrar_alerta(mensaje, tipo='info'):
    """
    Muestra una alerta al usuario
    
    Args:
        mensaje: Mensaje a mostrar
        tipo: Tipo de alerta (info, warning, error)
    """
    try:
        import tkinter.messagebox as messagebox
        if tipo == 'info':
            messagebox.showinfo("Información", mensaje)
        elif tipo == 'warning':
            messagebox.showwarning("Advertencia", mensaje)
        elif tipo == 'error':
            messagebox.showerror("Error", mensaje)
            
        # Sonido de alerta
        winsound.Beep(1000, 500)  # Frecuencia 1000Hz, duración 500ms
    except Exception as e:
        logger.error(f"Error al mostrar alerta: {str(e)}")

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
