import MetaTrader5 as mt5
"""
Estrategia de Cruce de Medias Móviles
"""

from .base import EstrategiaBase
import pandas as pd
import numpy as np
from utils.funciones import calcular_lote

class CruceMedias(EstrategiaBase):
    """
    Estrategia basada en el cruce de medias móviles
    """
    
    def __init__(self, conector, interfaz=None):
        super().__init__(conector, interfaz)
        self.periodo_corta = 9
        self.periodo_larga = 21
        self.stop_loss = 50
        self.take_profit = 100
        self.interfaz = interfaz
        
    def calcular_indicadores(self, datos):
        """
        Calcula las medias móviles
        
        Args:
            datos: DataFrame con datos históricos
            
        Returns:
            DataFrame con las medias móviles
        """
        df = datos.copy()
        df['MA_corta'] = df['close'].rolling(window=self.periodo_corta).mean()
        df['MA_larga'] = df['close'].rolling(window=self.periodo_larga).mean()
        return df
    
    def generar_senales(self, datos):
        """
        Genera señales de trading basadas en el cruce de medias
        
        Args:
            datos: DataFrame con datos históricos
            
        Returns:
            DataFrame con señales de trading
        """
        df = self.calcular_indicadores(datos)
        
        # Generar señales
        df['senal'] = 0
        df.loc[df['MA_corta'] > df['MA_larga'], 'senal'] = 1
        df.loc[df['MA_corta'] < df['MA_larga'], 'senal'] = -1
        
        return df

    def ejecutar(self):
        """
        Ejecuta la estrategia de cruce de medias
        """
        try:
            if not self.activo or not self.divisa:
                return

            # Obtener datos históricos
            try:
                # Verificar disponibilidad del símbolo
                if not self.conector.puede_operar(self.divisa):
                    self.logger.log_warning(f"El símbolo {self.divisa} no está disponible para operar")
                    return

                # Intentar con diferentes timeframes
                timeframes = [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M15]
                for timeframe in timeframes:
                    try:
                        self.logger.log_info(f"Intentando obtener datos para {self.divisa} con timeframe {timeframe}")
                        datos = self.conector.obtener_datos(self.divisa, timeframe, 100)
                        if datos is not None and len(datos) >= self.periodo_larga:
                            self.logger.log_info(f"Datos obtenidos exitosamente para {self.divisa} con timeframe {timeframe}")
                            break
                    except Exception as e:
                        self.logger.log_warning(f"Error con timeframe {timeframe}: {str(e)}")
                        continue
                
                if datos is None or len(datos) < self.periodo_larga:
                    self.logger.log_warning(f"No se pudieron obtener datos suficientes para {self.divisa}")
                    return
            except Exception as e:
                self.logger.log_error(f"Error al obtener datos: {str(e)}")
                return

            # Generar señales
            df = self.generar_senales(datos)
            
            # Obtener la última señal
            ultima_senal = df['senal'].iloc[-1]
            
            # Obtener el precio actual
            precio_actual = datos['close'].iloc[-1]
            
            # Obtener información de la cuenta para calcular lote
            cuenta = self.conector.obtener_info_cuenta()
            if not cuenta:
                self.logger.log_error("No se pudo obtener información de la cuenta")
                return
                
            # Calcular el tamaño del lote
            balance = cuenta.balance
            risk_percent = 1  # 1% de riesgo
            stop_loss_points = self.stop_loss
            
            try:
                lote = calcular_lote(risk_percent, balance, stop_loss_points)
            except Exception as e:
                self.logger.log_error(f"Error al calcular lote: {str(e)}")
                return
            
            # Verificar condiciones de entrada
            if ultima_senal == 1:  # Señal de compra
                if self.conector.puede_operar(self.divisa):
                    self.conector.ordenar(self.divisa, "BUY", lote, 
                                        stop_loss=precio_actual - self.stop_loss,
                                        take_profit=precio_actual + self.take_profit)
                    self.logger.log_info(f"Orden de compra en {self.divisa} - Señal: {ultima_senal}")
            elif ultima_senal == -1:  # Señal de venta
                if self.conector.puede_operar(self.divisa):
                    self.conector.ordenar(self.divisa, "SELL", lote, 
                                        stop_loss=precio_actual + self.stop_loss,
                                        take_profit=precio_actual - self.take_profit)
                    self.logger.log_info(f"Orden de venta en {self.divisa} - Señal: {ultima_senal}")

            # Actualizar estadísticas
            self.actualizar_estadisticas(self.conector.calcular_ganancias(), self.conector.calcular_perdidas())
            
        except Exception as e:
            self.logger.log_error(f"Error en la estrategia CruceMedias: {str(e)}")
    
    def ejecutar(self):
        """
        Método principal que ejecuta la lógica de la estrategia
        """
        try:
            if not self.activo:
                return
                
            # Obtener datos históricos
            datos = self.conector.obtener_datos(self.divisa, 'M1', 100)
            
            if datos is None:
                return
                
            # Generar señales
            df = self.generar_senales(datos)
            
            # Obtener la última señal
            ultima_senal = df['senal'].iloc[-1]
            
            # Obtener balance actual
            balance = self.conector.obtener_balance()
            
            if balance is None:
                return
                
            # Calcular tamaño de lote
            lote = calcular_lote(1, balance, self.stop_loss)
            
            if ultima_senal == 1:  # Señal de compra
                resultado = self.conector.orden_compra(self.divisa, lote, self.stop_loss, self.take_profit)
                if resultado:
                    self.ganancias += self.take_profit
                    self.actualizar_estadisticas(self.ganancias, self.perdidas)
            elif ultima_senal == -1:  # Señal de venta
                resultado = self.conector.orden_venta(self.divisa, lote, self.stop_loss, self.take_profit)
                if resultado:
                    self.ganancias += self.take_profit
                    self.actualizar_estadisticas(self.ganancias, self.perdidas)
            
        except Exception as e:
            self.logger.log_error(f"Error en CruceMedias ejecutar: {str(e)}")
