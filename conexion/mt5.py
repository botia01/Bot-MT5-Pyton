import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

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
        
        Returns:
            True si la desconexión fue exitosa, False si hubo un error
        """
        try:
            if self.conectado:
                mt5.shutdown()
                self.conectado = False
                return True
            else:
                return True  # Ya estaba desconectado
        except Exception as e:
            print(f"Error al desconectar: {str(e)}")
            return False

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

    def obtener_datos(self, simbolo, timeframe, cantidad_barras=100):
        """
        Obtiene datos históricos de un símbolo específico
        
        Args:
            simbolo: El símbolo para obtener datos (ej: "EURUSD")
            timeframe: El periodo de tiempo (ej: mt5.TIMEFRAME_M1)
            cantidad_barras: Número de barras a obtener
            
        Returns:
            DataFrame con los datos históricos
            
        Raises:
            ValueError: Si hay un error al obtener los datos
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        try:
            # Verificar si el símbolo existe y está disponible
            if not mt5.symbol_select(simbolo, True):
                raise ValueError(f"El símbolo {simbolo} no está disponible")
                
            # Verificar si el timeframe es válido
            if not hasattr(mt5, 'TIMEFRAME_M1'):
                raise ValueError("Timeframe no válido")
                
            # Obtener datos históricos
            rates = mt5.copy_rates_from_pos(simbolo, timeframe, 0, cantidad_barras)
            if rates is None:
                error_desc = mt5.last_error()
                raise ValueError(f"No se pudieron obtener datos para {simbolo}. Error MT5: {error_desc}")
                
            # Convertir a DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Verificar que hay suficientes datos
            if len(df) < cantidad_barras:
                raise ValueError(f"Se obtuvieron solo {len(df)} barras de {cantidad_barras} solicitadas para {simbolo}")
            
            # Renombrar columnas para mejor claridad
            df = df.rename(columns={
                'time': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'tick_volume': 'volume'
            })
            
            return df
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(mt5, 'last_error'):
                error_msg += f" - Error MT5: {mt5.last_error()}"
            raise ValueError(f"Error al obtener datos para {simbolo}: {error_msg}")

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
                    instrumentos.append((symbol.name, f"{symbol.name} - {tipo}"))
            return instrumentos
        except Exception as e:
            raise ValueError(f"Error al obtener divisas: {str(e)}")

    def puede_operar(self, simbolo):
        """
        Verifica si se puede operar con un símbolo específico
        
        Args:
            simbolo: El símbolo a verificar (ej: "EURUSD")
            
        Returns:
            bool: True si se puede operar, False si no
            
        Raises:
            ValueError: Si hay un error al verificar
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        try:
            # Verificar si el símbolo existe
            if not mt5.symbol_select(simbolo, True):
                return False
                
            # Obtener información del símbolo
            info = mt5.symbol_info(simbolo)
            if info is None:
                return False
                
            # Verificar si está disponible para trading
            if not info.trade_mode == 1:  # 1 es SYMBOL_TRADE_MODE_FOREX
                return False
                
            # Verificar si está habilitado para trading
            if not info.trade_calc_mode == 2:  # 2 es SYMBOL_CALC_MODE_FOREX
                return False
                
            # Verificar si está disponible para operaciones
            if not info.trade_stops_level > 0:
                return False
                
            return True
            
        except Exception as e:
            raise ValueError(f"Error al verificar operaciones: {str(e)}")

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

    def calcular_ganancias(self):
        """
        Calcula las ganancias totales de las operaciones cerradas
        
        Returns:
            float: Monto total de ganancias
            
        Raises:
            ValueError: Si hay un error al calcular
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        try:
            # Obtener la fecha actual en formato Unix
            now = datetime.now().timestamp()
            # Obtener historial de operaciones
            deals = mt5.history_deals_get(0, now)
            if deals is None:
                return 0.0
                
            # Calcular ganancias totales
            ganancias = sum(deal.profit for deal in deals if deal.profit > 0)
            return ganancias
            
        except Exception as e:
            raise ValueError(f"Error al calcular ganancias: {str(e)}")

    def calcular_perdidas(self):
        """
        Calcula las pérdidas totales de las operaciones cerradas
        
        Returns:
            float: Monto total de pérdidas
            
        Raises:
            ValueError: Si hay un error al calcular
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        try:
            # Obtener la fecha actual en formato Unix
            now = datetime.now().timestamp()
            # Obtener historial de operaciones
            deals = mt5.history_deals_get(0, now)
            if deals is None:
                return 0.0
                
            # Calcular pérdidas totales
            perdidas = sum(deal.profit for deal in deals if deal.profit < 0)
            return abs(perdidas)
            
        except Exception as e:
            raise ValueError(f"Error al calcular pérdidas: {str(e)}")

    def ordenar(self, simbolo, tipo, volumen, stop_loss=None, take_profit=None):
        """
        Realiza una orden de trading
        
        Args:
            simbolo: El símbolo para operar
            tipo: Tipo de orden ("BUY" o "SELL")
            volumen: Volumen de la operación
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
            
        Returns:
            Resultado de la orden
            
        Raises:
            ValueError: Si hay un error al realizar la orden
        """
        if not self.conectado:
            raise ValueError("No estás conectado a MetaTrader 5")
            
        try:
            # Verificar tipo de orden
            if tipo == "BUY":
                tipo_orden = mt5.ORDER_TYPE_BUY
            elif tipo == "SELL":
                tipo_orden = mt5.ORDER_TYPE_SELL
            else:
                raise ValueError("Tipo de orden no válido")
                
            # Obtener precio actual
            precio = mt5.symbol_info_tick(simbolo).ask if tipo == "BUY" else mt5.symbol_info_tick(simbolo).bid
            
            # Crear solicitud de orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume": volumen,
                "type": tipo_orden,
                "price": precio,
                "deviation": 20,
                "magic": 234000,
                "comment": "python script order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Agregar stop loss y take profit si están definidos
            if stop_loss is not None:
                request["sl"] = stop_loss
            if take_profit is not None:
                request["tp"] = take_profit
                
            # Enviar orden
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                raise ValueError(f"Error al enviar orden: {result.comment}")
                
            return result
            
        except Exception as e:
            raise ValueError(f"Error al realizar orden: {str(e)}")
