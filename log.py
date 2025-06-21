import logging
import os
from datetime import datetime

class Logger:
    """
    Clase para manejo de logs del bot
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Inicializa el logger
        """
        if self._initialized:
            return
            
        # Crear directorio para logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Configurar logging
        logging.basicConfig(
            filename=os.path.join('logs', 'bot.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Crear logger
        self.logger = logging.getLogger('BotMT5')
        self.logger.setLevel(logging.INFO)
        
        # Configurar handler para archivo
        file_handler = logging.FileHandler(os.path.join('logs', 'bot.log'))
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Configurar handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Registrar inicio
        self.log_info("Sistema iniciado")
        self._initialized = True
        
    def log_info(self, mensaje):
        """
        Registrar un mensaje de información
        
        Args:
            mensaje: Mensaje a registrar
        """
        self.logger.info(mensaje)
        
    def log_error(self, mensaje):
        """
        Registrar un mensaje de error
        
        Args:
            mensaje: Mensaje a registrar
        """
        self.logger.error(mensaje)
        
    def log_warning(self, mensaje):
        """
        Registrar un mensaje de advertencia
        
        Args:
            mensaje: Mensaje a registrar
        """
        self.logger.warning(mensaje)
        
    def log_debug(self, mensaje):
        """
        Registrar un mensaje de debug
        
        Args:
            mensaje: Mensaje de debug
        """
        self.logger.debug(mensaje)
        
    def log_success(self, mensaje):
        """
        Registrar un éxito
        
        Args:
            mensaje: Mensaje de éxito
        """
        self.logger.info(f"✓ {mensaje}")
        
    def get_log_file_path(self):
        """
        Obtener la ruta del archivo de log
        
        Returns:
            Ruta del archivo de log
        """
        return os.path.join('logs', 'bot.log')
