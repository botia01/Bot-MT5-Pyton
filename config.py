import json
from pathlib import Path

class ConfigManager:
    """
    Clase para manejo de configuración del bot
    """
    def __init__(self, archivo_config='config.json'):
        """
        Inicializa el gestor de configuración
        
        Args:
            archivo_config: Nombre del archivo de configuración
        """
        self.archivo_config = archivo_config
        self.config = self.cargar_config()
        
    def cargar_config(self):
        """
        Cargar configuración desde archivo
        
        Returns:
            Configuración como diccionario
        """
        try:
            with open(self.archivo_config, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.crear_config_default()
        except json.JSONDecodeError:
            return self.crear_config_default()
            
    def crear_config_default(self):
        """
        Crear configuración por defecto
        
        Returns:
            Configuración por defecto
        """
        config = {
            "par_defecto": "EURUSD",
            "timeframe": "M5",
            "estrategia": "Estrategia Base",
            "lote_minimo": 0.01,
            "stop_loss": 50,
            "take_profit": 100,
            "modo_simulacion": False
        }
        self.guardar_config(config)
        return config
        
    def guardar_config(self, config):
        """
        Guardar configuración en archivo
        
        Args:
            config: Configuración a guardar
        """
        with open(self.archivo_config, 'w') as f:
            json.dump(config, f, indent=4)
            
    def actualizar_config(self, clave, valor):
        """
        Actualizar un valor en la configuración
        
        Args:
            clave: Clave a actualizar
            valor: Nuevo valor
        """
        self.config[clave] = valor
        self.guardar_config(self.config)
        
    def obtener_config(self):
        """
        Obtener la configuración actual
        
        Returns:
            Configuración actual
        """
        return self.config
        
    def get(self, clave, default=None):
        """
        Obtener un valor de configuración
        
        Args:
            clave: Clave a obtener
            default: Valor por defecto si no existe
        
        Returns:
            Valor de la configuración
        """
        return self.config.get(clave, default)
        
    def set(self, clave, valor):
        """
        Establecer un valor en la configuración
        
        Args:
            clave: Clave a establecer
            valor: Nuevo valor
        """
        self.config[clave] = valor
        self.guardar_config(self.config)
