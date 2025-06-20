import pandas as pd
import numpy as np

class IndicadorBase:
    """
    Clase base para todos los indicadores técnicos
    """
    def __init__(self, nombre, periodo=14):
        """
        Inicializa el indicador
        
        Args:
            nombre: Nombre del indicador
            periodo: Período de cálculo del indicador
        """
        self.nombre = nombre
        self.periodo = periodo
        self.valores = []
        self.ultimo_valor = None

    def calcular(self, datos):
        """
        Método abstracto que debe ser implementado por cada indicador
        
        Args:
            datos: DataFrame con los datos históricos
            
        Returns:
            DataFrame con los valores calculados del indicador
        """
        raise NotImplementedError("Este método debe ser implementado por la clase hija")

    def actualizar(self, nuevo_precio):
        """
        Actualiza el indicador con un nuevo precio
        
        Args:
            nuevo_precio: Nuevo precio para actualizar el indicador
        """
        raise NotImplementedError("Este método debe ser implementado por la clase hija")

    def obtener_ultimo_valor(self):
        """
        Obtiene el último valor calculado del indicador
        
        Returns:
            El último valor calculado
        """
        return self.ultimo_valor

    def obtener_valores(self):
        """
        Obtiene todos los valores calculados del indicador
        
        Returns:
            Lista de todos los valores calculados
        """
        return self.valores
