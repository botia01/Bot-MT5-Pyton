from abc import ABC, abstractmethod
from log import Logger

class EstrategiaBase(ABC):
    """
    Clase base abstracta para todas las estrategias de trading
    """
    def __init__(self, conector, interfaz=None):
        """
        Inicializa la estrategia
        
        Args:
            conector: Instancia del conector MT5
            interfaz: Referencia a la interfaz principal
        """
        self.conector = conector
        self.activo = False
        self.divisa = None
        self.interfaz = interfaz
        self.logger = Logger()
        self.ganancias = 0.0
        self.perdidas = 0.0

    def configurar_divisa(self, divisa):
        """
        Configura la divisa para la estrategia
        
        Args:
            divisa: Par de divisas a usar en la estrategia
        """
        self.divisa = divisa
        self.logger.log_info(f"Configurando divisa {divisa} para estrategia {self.__class__.__name__}")

    def iniciar(self):
        """
        Inicia la ejecución de la estrategia
        """
        self.activo = True
        self.logger.log_info(f"Iniciando estrategia: {self.__class__.__name__}")

    def detener(self):
        """
        Detiene la ejecución de la estrategia
        """
        self.activo = False
        self.logger.log_info(f"Deteniendo estrategia: {self.__class__.__name__}")

    @abstractmethod
    def ejecutar(self):
        """
        Método principal que ejecuta la lógica de la estrategia
        Debe ser implementado por las estrategias específicas
        """
        pass

    def actualizar_estadisticas(self, ganancias, perdidas):
        """
        Actualiza las estadísticas de la estrategia
        
        Args:
            ganancias: Monto de ganancias
            perdidas: Monto de pérdidas
        """
        self.ganancias = ganancias
        self.perdidas = perdidas
