import tkinter as tk
from tkinter import ttk
import os

class Estilos:
    """
    Clase que maneja los estilos de la interfaz
    """
    def __init__(self):
        """
        Inicializa los estilos
        """
        # Definir colores
        self.colores = {
            'fondo': '#1e272e',  # Azul oscuro profundo
            'primario': '#2ed573',  # Verde lima brillante
            'secundario': '#00b894',  # Verde turquesa
            'texto': '#ffffff',  # Texto blanco
            'error': '#ff4757',  # Rosa brillante para errores
            'exito': '#2ed573',  # Verde lima para éxitos
            'advertencia': '#ffa502',  # Naranja brillante para advertencias
            'info': '#74b9ff',  # Azul claro para información
            'ganancias': '#2ed573',  # Verde lima para ganancias
            'perdidas': '#ff4757',  # Rosa brillante para pérdidas
            'linea': '#333333',  # Gris oscuro para líneas
            'fondo_frame': '#2f3640',  # Gris azulado para frames
            'texto_secundario': '#dcdde1'  # Gris claro para texto secundario
        }

        # Definir fuentes
        self.fuentes = {
            'titulo': ('Segoe UI', 14, 'bold'),  # Fuente más moderna
            'normal': ('Segoe UI', 10),
            'pequeña': ('Segoe UI', 9)
        }

        # Crear estilo para ttk
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')  # Usar tema claro

        # Configurar estilos
        self.configurar_estilos()

    def configurar_estilos(self):
        """
        Configura los estilos de ttk
        """
        # Configurar el estilo general
        self.estilo.configure('TFrame', 
                             background=self.colores['fondo'])
        self.estilo.configure('TLabel', 
                             background=self.colores['fondo'],
                             foreground=self.colores['texto'])
        self.estilo.configure('TButton', 
                             background=self.colores['primario'],
                             foreground=self.colores['texto'])
        self.estilo.configure('TCombobox', 
                             fieldbackground=self.colores['texto'],
                             background=self.colores['texto'])
        
        # Estilos para frames
        self.estilo.configure('EstiloFrame.TFrame',
                             background=self.colores['fondo_frame'])
        
        # Estilos para botones
        self.estilo.configure('Conectar.TButton',
                             background=self.colores['primario'],
                             foreground=self.colores['texto'])
        self.estilo.configure('Bot.TButton',
                             background=self.colores['secundario'],
                             foreground=self.colores['texto'])
        
        # Estilos para estadísticas
        self.estilo.configure('Ganancias.TLabel',
                             background=self.colores['fondo_frame'],
                             foreground=self.colores['ganancias'])
        self.estilo.configure('Perdidas.TLabel',
                             background=self.colores['fondo_frame'],
                             foreground=self.colores['perdidas'])
        
        # Estilos para mensajes
        self.estilo.configure('Mensaje.TLabel',
                             background=self.colores['fondo_frame'],
                             foreground=self.colores['info'])
        
        # Estilos para etiquetas secundarias
        self.estilo.configure('Secundario.TLabel',
                             background=self.colores['fondo_frame'],
                             foreground=self.colores['texto_secundario'])

        # Configurar estilos específicos
        self.estilo.configure('Encabezado.TLabel', 
                             font=self.fuentes['titulo'],
                             padding=10)
        self.estilo.configure('Info.TLabel', 
                             font=self.fuentes['normal'])
        self.estilo.configure('Estado.TLabel', 
                             font=self.fuentes['normal'],
                             padding=5)
        self.estilo.configure('Error.TLabel', 
                             foreground=self.colores['error'])
        self.estilo.configure('Exito.TLabel', 
                             foreground=self.colores['exito'])
        self.estilo.configure('Advertencia.TLabel', 
                             foreground=self.colores['advertencia'])
        self.estilo.configure('Info.TLabel', 
                             foreground=self.colores['info'])

        # Configurar el estilo de los frames
        self.estilo.configure('TFrame', 
                             background=self.colores['fondo'])
        self.estilo.configure('Estadisticas.TFrame', 
                             background=self.colores['fondo'])

        # Configurar el estilo de los botones
        self.estilo.configure('Conectar.TButton', 
                             background=self.colores['primario'])
        self.estilo.configure('Bot.TButton', 
                             background=self.colores['secundario'])

        # Configurar el estilo del texto
        self.estilo.configure('TMenubutton', 
                             background=self.colores['primario'],
                             foreground=self.colores['texto'])

    def aplicar_estilo(self, widget, tipo):
        """
        Aplica un estilo específico a un widget
        
        Args:
            widget: El widget al que aplicar el estilo
            tipo: El tipo de estilo a aplicar
        """
        if tipo == 'encabezado':
            widget.configure(style='Encabezado.TLabel')
        elif tipo == 'info':
            widget.configure(style='Mensaje.TLabel')
        elif tipo == 'estado':
            widget.configure(style='Estado.TLabel')
        elif tipo == 'error':
            widget.configure(style='Error.TLabel')
        elif tipo == 'exito':
            widget.configure(style='Exito.TLabel')
        elif tipo == 'advertencia':
            widget.configure(style='Advertencia.TLabel')
        elif tipo == 'conectar':
            widget.configure(style='Conectar.TButton')
        elif tipo == 'bot':
            widget.configure(style='Bot.TButton')
        elif tipo == 'frame':
            widget.configure(style='EstiloFrame.TFrame')
        elif tipo == 'estadisticas':
            widget.configure(style='EstiloFrame.TFrame')
        elif tipo == 'ganancias':
            widget.configure(style='Ganancias.TLabel')
        elif tipo == 'perdidas':
            widget.configure(style='Perdidas.TLabel')

    def obtener_color(self, tipo):
        """
        Obtiene un color específico
        
        Args:
            tipo: El tipo de color
            
        Returns:
            El código del color
        """
        return self.colores.get(tipo, '#ffffff')
