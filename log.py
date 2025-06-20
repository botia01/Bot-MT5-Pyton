import logging
import os
from datetime import datetime

class Logger:
    """
    Clase para manejo de logs del bot
    """
    def __init__(self, nombre_archivo='bot.log'):
        """
        Inicializa el logger
        
        Args:
            nombre_archivo: Nombre del archivo de log
        """
        # Crear directorio para logs si no existe
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Configurar logging
        logging.basicConfig(
            filename=os.path.join('logs', nombre_archivo),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Crear logger
        self.logger = logging.getLogger('BotMT5')
        
        # Añadir handler para mostrar en consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Registrar inicio
        self.log_info("Sistema iniciado")
        
    def log_info(self, mensaje):
        """
        Registrar un mensaje de información
        
        Args:
            mensaje: Mensaje a registrar
        """
        self.logger.info(mensaje)
        
    def log_error(self, mensaje):
        """
        Registrar un error
        
        Args:
            mensaje: Mensaje de error
        """
        self.logger.error(mensaje)
        
    def log_warning(self, mensaje):
        """
        Registrar una advertencia
        
        Args:
            mensaje: Mensaje de advertencia
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
