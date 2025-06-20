from .base import IndicadorBase
import pandas as pd
import numpy as np

class RSI(IndicadorBase):
    """
    Indicador RSI (Relative Strength Index)
    """
    def __init__(self, periodo=14):
        super().__init__("RSI", periodo)

    def calcular(self, datos):
        """
        Calcula el RSI basado en los datos históricos
        
        Args:
            datos: DataFrame con los datos históricos
            
        Returns:
            DataFrame con los valores del RSI
        """
        # Calcular las ganancias y pérdidas
        delta = datos['close'].diff()
        ganancias = delta.where(delta > 0, 0)
        perdidas = -delta.where(delta < 0, 0)

        # Calcular el promedio de ganancias y pérdidas
        avg_ganancias = ganancias.rolling(window=self.periodo).mean()
        avg_perdidas = perdidas.rolling(window=self.periodo).mean()

        # Calcular el RSI
        rs = avg_ganancias / avg_perdidas
        rsi = 100 - (100 / (1 + rs))

        # Guardar los valores
        self.valores = rsi.tolist()
        self.ultimo_valor = rsi.iloc[-1] if len(rsi) > 0 else None

        return rsi

    def actualizar(self, nuevo_precio, datos_anteriores):
        """
        Actualiza el RSI con un nuevo precio
        
        Args:
            nuevo_precio: Nuevo precio para actualizar el indicador
            datos_anteriores: DataFrame con los datos históricos anteriores
        """
        # Agregar el nuevo precio a los datos
        datos = datos_anteriores.copy()
        datos = datos.append({'close': nuevo_precio}, ignore_index=True)

        # Calcular el RSI actualizado
        rsi = self.calcular(datos)
        return rsi.iloc[-1]
