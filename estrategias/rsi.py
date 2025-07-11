import MetaTrader5 as mt5
"""
Estrategia basada en el indicador RSI
"""

from .base import EstrategiaBase
import pandas as pd
import numpy as np
from utils.funciones import calcular_lote
from log import Logger

class EstrategiaRSI(EstrategiaBase):
    """
    Estrategia basada en el indicador RSI
    """
    
    def __init__(self, conector, interfaz=None):
        super().__init__(conector, interfaz)
        self.periodo = 14
        self.nivel_sobrecompra = 70
        self.nivel_sobreventa = 30
        self.stop_loss = 50
        self.take_profit = 100
        self.interfaz = interfaz
        self.logger = Logger()
        
    def calcular_rsi(self, datos, periodo):
        """
        Calcula el RSI
        
        Args:
            datos: DataFrame con datos históricos
            periodo: Periodo para calcular el RSI
            
        Returns:
            DataFrame con el RSI
        """
        df = datos.copy()
        
        # Calcular cambios de precio
        delta = df['close'].diff()
        
        # Separar ganancias y pérdidas
        ganancias = delta.where(delta > 0, 0)
        perdidas = -delta.where(delta < 0, 0)
        
        # Calcular promedios
        avg_ganancias = ganancias.rolling(window=periodo).mean()
        avg_perdidas = perdidas.rolling(window=periodo).mean()
        
        # Calcular RS y RSI
        rs = avg_ganancias / avg_perdidas
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def ejecutar(self):
        """
        Ejecuta la estrategia RSI
        """
        try:
            if not self.activo or not self.divisa:
                self.logger.log_warning("Estrategia no activa o sin divisa")
                return None

            # Obtener datos históricos
            try:
                datos = self.conector.obtener_datos(self.divisa, mt5.TIMEFRAME_M1, 100)
                if datos is None or len(datos) < self.periodo:
                    self.logger.log_warning(f"No hay suficientes datos para {self.divisa}")
                    return None
            except Exception as e:
                self.logger.log_error(f"Error al obtener datos para {self.divisa}: {str(e)}")
                return None

            # Calcular RSI
            try:
                rsi = self.calcular_rsi(datos, self.periodo)
                if rsi is None:
                    self.logger.log_error("Error al calcular RSI")
                    return None
            except Exception as e:
                self.logger.log_error(f"Error en el cálculo del RSI: {str(e)}")
                return None
                
            # Obtener el último valor de RSI
            ultimo_rsi = rsi.iloc[-1]
            
            # Obtener el precio actual
            precio_actual = datos['close'].iloc[-1]
            
            # Obtener información de la cuenta para calcular lote
            try:
                cuenta = self.conector.obtener_info_cuenta()
                if not cuenta:
                    self.logger.log_error("No se pudo obtener información de la cuenta")
                    return None
            except Exception as e:
                self.logger.log_error(f"Error al obtener información de la cuenta: {str(e)}")
                return None
                
            # Calcular el tamaño del lote
            try:
                balance = cuenta.balance
                risk_percent = 1  # 1% de riesgo
                stop_loss_points = self.stop_loss
                lote = calcular_lote(risk_percent, balance, stop_loss_points)
            except Exception as e:
                self.logger.log_error(f"Error al calcular lote: {str(e)}")
                return None
            
            # Verificar condiciones de entrada
            if ultimo_rsi < self.nivel_sobreventa:
                # Condiciones de compra
                try:
                    if self.conector.puede_operar(self.divisa):
                        self.conector.ordenar(self.divisa, "BUY", lote, 
                                            stop_loss=precio_actual - self.stop_loss,
                                            take_profit=precio_actual + self.take_profit)
                        self.logger.log_info(f"Orden de compra en {self.divisa} - RSI: {ultimo_rsi:.2f}")
                    else:
                        self.logger.log_warning(f"No se puede operar con {self.divisa}")
                except Exception as e:
                    self.logger.log_error(f"Error al realizar orden de compra: {str(e)}")
            elif ultimo_rsi > self.nivel_sobrecompra:
                # Condiciones de venta
                try:
                    if self.conector.puede_operar(self.divisa):
                        self.conector.ordenar(self.divisa, "SELL", lote, 
                                            stop_loss=precio_actual + self.stop_loss,
                                            take_profit=precio_actual - self.take_profit)
                        self.logger.log_info(f"Orden de venta en {self.divisa} - RSI: {ultimo_rsi:.2f}")
                    else:
                        self.logger.log_warning(f"No se puede operar con {self.divisa}")
                except Exception as e:
                    self.logger.log_error(f"Error al realizar orden de venta: {str(e)}")

            # Actualizar estadísticas
            try:
                self.actualizar_estadisticas(self.conector.calcular_ganancias(), self.conector.calcular_perdidas())
            except Exception as e:
                self.logger.log_error(f"Error al actualizar estadísticas: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(f"Error general en la estrategia RSI: {str(e)}")
            return None
        
        # Agregar RSI al DataFrame original
        datos['RSI'] = rsi
        return datos
    
    def actualizar_estadisticas(self, ganancias, perdidas):
        """
        Actualiza las estadísticas de la estrategia
        
        Args:
            ganancias: Monto total de ganancias
            perdidas: Monto total de pérdidas
        """
        try:
            if ganancias is None:
                ganancias = 0.0
            if perdidas is None:
                perdidas = 0.0
                
            self.ganancias = float(ganancias)
            self.perdidas = float(perdidas)
            
            # Evitar división por cero
            if self.perdidas == 0:
                self.ratio_ganancia = 0.0 if self.ganancias == 0 else float('inf')
            else:
                self.ratio_ganancia = self.ganancias / self.perdidas
                
            self.logger.log_info(f"Estadísticas actualizadas - Ganancias: {self.ganancias:.2f}, Pérdidas: {self.perdidas:.2f}, Ratio: {self.ratio_ganancia:.2f}")
        except Exception as e:
            self.logger.log_error(f"Error al actualizar estadísticas: {str(e)}")
            self.logger.log_error(f"Valores recibidos - Ganancias: {ganancias}, Pérdidas: {perdidas}")
            return None
        
    def generar_senales(self, datos):
        """
        Genera señales de trading basadas en el RSI
        
        Args:
            datos: DataFrame con datos históricos
            
        Returns:
            DataFrame con señales de trading
        """
        df = self.calcular_rsi(datos, self.periodo)
        
        # Generar señales
        df['senal'] = 0
        df.loc[df['RSI'] < self.nivel_sobreventa, 'senal'] = 1  # Compra
        df.loc[df['RSI'] > self.nivel_sobrecompra, 'senal'] = -1  # Venta
        
        return df
    
    def ejecutar_operacion(self, par, timeframe, precio_actual, balance):
        """
        Ejecuta una operación basada en el RSI
        
        Args:
            par: Par de divisas
            timeframe: Timeframe
            precio_actual: Precio actual
            balance: Balance de la cuenta
            
        Returns:
            bool: True si se ejecutó una operación, False si no
        """
        try:
            # Obtener datos históricos
            datos = self.conector.obtener_datos(par, timeframe, 100)
            
            if datos is None:
                return False
                
            # Generar señales
            df = self.generar_senales(datos)
            
            # Obtener el último RSI
            ultimo_rsi = df['RSI'].iloc[-1]
            
            # Calcular tamaño de lote
            lote = calcular_lote(1, balance, self.stop_loss)
            
            if ultimo_rsi < self.nivel_sobreventa:  # Señal de compra
                return self.conector.orden_compra(par, lote, self.stop_loss, self.take_profit)
            elif ultimo_rsi > self.nivel_sobrecompra:  # Señal de venta
                return self.conector.orden_venta(par, lote, self.stop_loss, self.take_profit)
                
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error en EstrategiaRSI: {str(e)}")
            return False
