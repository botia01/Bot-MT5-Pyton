class EstrategiaBase:
    """
    Clase base para todas las estrategias de trading
    """
    def __init__(self, conector):
        """
        Inicializa la estrategia
        
        Args:
            conector: Instancia del conector MT5
        """
        self.conector = conector
        self.activo = False

    def iniciar(self):
        """
        Inicia la ejecución de la estrategia
        """
        self.activo = True
        print(f"Iniciando estrategia: {self.__class__.__name__}")

    def detener(self):
        """
        Detiene la ejecución de la estrategia
        """
        self.activo = False
        print(f"Deteniendo estrategia: {self.__class__.__name__}")

    def ejecutar(self):
        """
        Método principal que ejecuta la lógica de la estrategia
        Debe ser implementado por las estrategias específicas
        """
        raise NotImplementedError("Este método debe ser implementado por las estrategias específicas")
