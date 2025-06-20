from .base import IndicadorBase
import pandas as pd

class SMA(IndicadorBase):
    """
    Indicador SMA (Simple Moving Average)
    """
    def __init__(self, periodo=14):
        super().__init__("SMA", periodo)

    def calcular(self, datos):
        """
        Calcula la SMA basada en los datos históricos
        
        Args:
            datos: DataFrame con los datos históricos
            
        Returns:
            DataFrame con los valores de la SMA
        """
        # Calcular la SMA
        sma = datos['close'].rolling(window=self.periodo).mean()

        # Guardar los valores
        self.valores = sma.tolist()
        self.ultimo_valor = sma.iloc[-1] if len(sma) > 0 else None

        return sma

    def actualizar(self, nuevo_precio, datos_anteriores):
        """
        Actualiza la SMA con un nuevo precio
        
        Args:
            nuevo_precio: Nuevo precio para actualizar el indicador
            datos_anteriores: DataFrame con los datos históricos anteriores
        """
        # Agregar el nuevo precio a los datos
        datos = datos_anteriores.copy()
        datos = datos.append({'close': nuevo_precio}, ignore_index=True)

        # Calcular la SMA actualizada
        sma = self.calcular(datos)
        return sma.iloc[-1]
