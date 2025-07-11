import random
from datetime import datetime, timedelta
import pandas as pd
from cuenta import InfoCuenta

class SimuladorMT5:
    """
    Clase para simular el comportamiento de MetaTrader 5
    """
    def __init__(self):
        """
        Inicializa el simulador
        """
        self.pares_disponibles = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
            "AUDUSD", "NZDUSD", "USDCAD", "EURGBP"
        ]
        self.historico = {}
        self.ordenes = []
        self.cuenta = {
            "balance": 10000.0,
            "equity": 10000.0,
            "profit": 0.0,
            "margin": 0.0
        }
        self.conectado = False
        
    def conectar(self):
        """
        Simula la conexión a MT5
        
        Returns:
            bool: True si la conexión es exitosa
        """
        self.conectado = True
        return True
        
    def desconectar(self):
        """
        Simula la desconexión de MT5
        
        Returns:
            bool: True si la desconexión es exitosa
        """
        try:
            if self.conectado:
                self.conectado = False
                # Limpiar datos simulados
                self.historico.clear()
                self.ordenes.clear()
                return True
            else:
                return True  # Ya estaba desconectado
        except Exception as e:
            print(f"Error al desconectar: {str(e)}")
            return False
        
    def obtener_info_cuenta(self):
        """
        Simula la obtención de información de cuenta
        
        Returns:
            InfoCuenta: Información de cuenta
        """
        try:
            if not self.conectado:
                return None
                
            return InfoCuenta(
                balance=self.cuenta["balance"],
                equity=self.cuenta["equity"],
                profit=self.cuenta["profit"],
                margin=self.cuenta["margin"]
            )
        except Exception as e:
            print(f"Error en obtener_info_cuenta: {str(e)}")
            return None
        
    def obtener_divisas_disponibles(self):
        """
        Simula la obtención de divisas disponibles
        
        Returns:
            list: Lista de divisas disponibles
        """
        return [(par, f"{par} - Par de divisas") for par in self.pares_disponibles]
        
    def obtener_datos_historicos(self, par, timeframe, start, end):
        """
        Simula la obtención de datos históricos
        
        Args:
            par: Par de divisas
            timeframe: Periodo de tiempo
            start: Fecha de inicio
            end: Fecha de fin
        
        Returns:
            pd.DataFrame: Datos históricos
        """
        # Crear datos simulados
        data = {
            'time': pd.date_range(start, end, freq='1min'),
            'open': [random.uniform(1.0, 2.0) for _ in range(len(data['time']))],
            'high': [random.uniform(1.0, 2.0) for _ in range(len(data['time']))],
            'low': [random.uniform(1.0, 2.0) for _ in range(len(data['time']))],
            'close': [random.uniform(1.0, 2.0) for _ in range(len(data['time']))],
            'tick_volume': [random.randint(100, 1000) for _ in range(len(data['time']))]
        }
        return pd.DataFrame(data)
        
    def abrir_orden(self, par, tipo, volumen, precio, stop_loss=None, take_profit=None):
        """
        Simula la apertura de una orden
        
        Args:
            par: Par de divisas
            tipo: Tipo de orden (OP_BUY, OP_SELL)
            volumen: Volumen de la orden
            precio: Precio de entrada
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
        
        Returns:
            dict: Detalles de la orden
        """
        orden = {
            'ticket': len(self.ordenes) + 1,
            'par': par,
            'tipo': tipo,
            'volumen': volumen,
            'precio': precio,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'tiempo': datetime.now(),
            'estado': 'abierta'
        }
        self.ordenes.append(orden)
        return orden
        
    def cerrar_orden(self, ticket):
        """
        Simula el cierre de una orden
        
        Args:
            ticket: Número de ticket de la orden
        
        Returns:
            dict: Resultado del cierre
        """
        for orden in self.ordenes:
            if orden['ticket'] == ticket:
                orden['estado'] = 'cerrada'
                orden['tiempo_cierre'] = datetime.now()
                return orden
        return None
        
    def obtener_orden(self, ticket):
        """
        Simula la obtención de detalles de una orden
        
        Args:
            ticket: Número de ticket de la orden
        
        Returns:
            dict: Detalles de la orden
        """
        for orden in self.ordenes:
            if orden['ticket'] == ticket:
                return orden
        return None
