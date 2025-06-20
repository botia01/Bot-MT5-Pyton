import MetaTrader5 as mt5
import pandas as pd

class ConectorMT5:
    """
    Clase que maneja la conexión con MetaTrader 5 y obtiene datos de trading
    """
    def __init__(self, par_divisas="EURUSD", periodo_tiempo=mt5.TIMEFRAME_M1):
        """
        Inicializa el conector con el par de divisas y el periodo de tiempo
        
        Args:
            par_divisas: El par de divisas a monitorear (ej: "EURUSD")
            periodo_tiempo: El periodo de tiempo para los datos (ej: mt5.TIMEFRAME_M1 para 1 minuto)
        """
        self.par_divisas = par_divisas
        self.periodo_tiempo = periodo_tiempo
        self.conectado = False

    def conectar(self):
        """
        Establece la conexión con MetaTrader 5
        
        Returns:
            True si la conexión se estableció correctamente, False si hubo un error
        """
        try:
            if not mt5.initialize():
                raise ConnectionError(f"Error al conectar con MT5: {mt5.last_error()}")
            self.conectado = True
            return True
        except Exception as e:
            self.conectado = False
            raise e

    def desconectar(self):
        """
        Cierra la conexión con MetaTrader 5
        """
        mt5.shutdown()
        self.conectado = False

    def obtener_info_cuenta(self):
        """
        Obtiene información de la cuenta de trading
        
        Returns:
            Información de la cuenta
            
        Raises:
            ValueError: Si no se puede obtener la información
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        info = mt5.account_info()
        if info is None:
            raise ValueError("No se pudo obtener información de la cuenta")
        return info

    def obtener_divisas_disponibles(self):
        """
        Obtiene la lista de divisas y otros instrumentos disponibles en MetaTrader 5
        
        Returns:
            Lista de tuplas (nombre, nombre_completo) de los instrumentos disponibles
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        instrumentos = []
        try:
            # Obtener todos los símbolos disponibles
            symbols = mt5.symbols_get()
            if symbols is not None:
                for symbol in symbols:
                    # Obtener el tipo de instrumento
                    tipo = ""
                    if symbol.name[-3:] in ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]:
                        tipo = "Divisa"
                    elif "XAU" in symbol.name or "XAG" in symbol.name:
                        tipo = "Metales"
                    elif "INDEX" in symbol.name:
                        tipo = "Índices"
                    elif "STOCK" in symbol.name:
                        tipo = "Acciones"
                    else:
                        tipo = "Otro"
                    
                    # Agregar el instrumento con su tipo
                    instrumentos.append((
                        symbol.name,
                        f"{symbol.description} ({tipo})",
                        tipo
                    ))
        except Exception as e:
            raise ValueError(f"Error al obtener instrumentos: {str(e)}")
        
        # Ordenar los instrumentos por tipo y luego por nombre
        instrumentos.sort(key=lambda x: (x[2], x[0]))
        
        return [(nombre, descripcion) for nombre, descripcion, _ in instrumentos]

    def obtener_datos_historicos(self, numero_barras=1000):
        """
        Obtiene datos históricos de precios
        
        Args:
            numero_barras: Número de barras de datos a obtener
            
        Returns:
            DataFrame con los datos históricos
            
        Raises:
            ValueError: Si no se pueden obtener los datos
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
        
        rates = mt5.copy_rates_from_pos(self.par_divisas, self.periodo_tiempo, 0, numero_barras)
        if rates is None or len(rates) == 0:
            raise ValueError(f"No se pudieron obtener datos históricos para {self.par_divisas}")
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
